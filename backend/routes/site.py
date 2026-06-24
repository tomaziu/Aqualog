import json
import re
import time
import hashlib
import unicodedata
from datetime import date, datetime
from urllib.parse import urlencode
from urllib.request import Request as URLRequest, urlopen
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from database import get_connection
from delivery_code import gerar_codigo_entrega
from mercado_pago import MercadoPagoError, consultar_pix_order, criar_pix_order
from models import ComprovantePix, PedidoSite, SuporteMensagem
from pix_manual import gerar_pix_manual
from routes.configuracoes import _ler_configuracoes
from sse_manager import event_generator, notify

router = APIRouter()

PIX_REUTILIZACAO_MINUTOS = 30
LIMITE_TENTATIVAS_SEGUNDOS = 60
LIMITE_TENTATIVAS_PEDIDO = 5
_TENTATIVAS_PEDIDO_SITE = {}


def _email_pagador(pedido: PedidoSite, telefone: str) -> str:
    email = (pedido.email or '').strip()
    if '@' in email and '.' in email:
        return email
    return f'cliente.{telefone or "semtelefone"}@aqualog.com.br'


def _atualizar_pagamento(cur, pedido_id: int, dados: dict):
    confirmacao_status = 'confirmado' if dados.get('pagamento_status') == 'pago' else None
    cur.execute('''UPDATE pedidos
                   SET pagamento_status=%s,
                       confirmacao_status=COALESCE(%s, confirmacao_status),
                       mp_order_id=COALESCE(%s, mp_order_id),
                       mp_payment_id=COALESCE(%s, mp_payment_id),
                       pix_copia_cola=COALESCE(%s, pix_copia_cola),
                       pix_qrcode_base64=COALESCE(%s, pix_qrcode_base64),
                       pix_ticket_url=COALESCE(%s, pix_ticket_url)
                   WHERE id=%s''',
                (dados.get('pagamento_status'), confirmacao_status, dados.get('mp_order_id'), dados.get('mp_payment_id'),
                 dados.get('pix_copia_cola'), dados.get('pix_qrcode_base64'), dados.get('pix_ticket_url'), pedido_id))


def _codigo_entrega_publico(pedido: dict):
    if pedido.get('confirmacao_status') == 'confirmado':
        return pedido.get('codigo_entrega')
    return None


def _total_pedido(preco, quantidade) -> float:
    return float(preco) * int(quantidade or 1)


def _normalizar_itens_pedido(pedido: PedidoSite) -> list[dict]:
    origem = pedido.itens or []
    if not origem:
        if not pedido.produto_id or not pedido.quantidade:
            raise HTTPException(400, 'Adicione pelo menos um produto ao pedido.')
        origem = [{'produto_id': pedido.produto_id, 'quantidade': pedido.quantidade}]

    itens_por_produto = {}
    for item in origem:
        produto_id = int(item.produto_id if hasattr(item, 'produto_id') else item['produto_id'])
        quantidade = int(item.quantidade if hasattr(item, 'quantidade') else item['quantidade'])
        if quantidade <= 0:
            raise HTTPException(400, 'Quantidade inválida no carrinho.')
        itens_por_produto[produto_id] = itens_por_produto.get(produto_id, 0) + quantidade

    if not itens_por_produto:
        raise HTTPException(400, 'Adicione pelo menos um produto ao pedido.')
    return [{'produto_id': produto_id, 'quantidade': quantidade}
            for produto_id, quantidade in sorted(itens_por_produto.items())]


def _normalizar_codigo_cupom(codigo: str | None) -> str:
    return ''.join(ch for ch in str(codigo or '').strip().upper() if ch.isalnum() or ch in ('-', '_'))[:40]


def _hash_carrinho(itens: list[dict], cupom_codigo: str = '') -> str:
    assinatura = '|'.join(f'{item["produto_id"]}:{item["quantidade"]}' for item in itens)
    if cupom_codigo:
        assinatura += f'|cupom:{cupom_codigo}'
    return hashlib.sha256(assinatura.encode('utf-8')).hexdigest()


def _loja_pode_receber_pedido(cur) -> tuple[bool, str]:
    cfg = _ler_configuracoes(cur)
    if not cfg.get('loja_aberta'):
        return False, 'A loja está fechada para novos pedidos no momento.'
    return True, ''


def _data_cupom(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return datetime.strptime(str(valor)[:10], '%Y-%m-%d').date()


def _validar_cupom_regras(cupom: dict, total: float):
    hoje = date.today()
    inicio = _data_cupom(cupom.get('validade_inicio'))
    fim = _data_cupom(cupom.get('validade_fim'))
    valor_minimo = float(cupom.get('valor_minimo') or 0)
    limite_usos = cupom.get('limite_usos')
    usos = int(cupom.get('usos') or 0)

    if inicio and hoje < inicio:
        raise HTTPException(400, 'Cupom ainda não está disponível.')
    if fim and hoje > fim:
        raise HTTPException(400, 'Cupom expirado.')
    if valor_minimo > 0 and float(total or 0) < valor_minimo:
        raise HTTPException(400, f'Cupom exige pedido mínimo de R$ {valor_minimo:.2f}.')
    if limite_usos is not None and int(limite_usos) > 0 and usos >= int(limite_usos):
        raise HTTPException(400, 'Cupom atingiu o limite de usos.')


def _buscar_cupom(cur, codigo: str, total: float = 0):
    codigo = _normalizar_codigo_cupom(codigo)
    if not codigo:
        return None
    cur.execute('''SELECT codigo, percentual, ativo, validade_inicio, validade_fim,
                          valor_minimo, limite_usos, usos
                   FROM cupons WHERE codigo=%s LIMIT 1''', (codigo,))
    cupom = cur.fetchone()
    if not cupom or not cupom.get('ativo'):
        raise HTTPException(400, 'Cupom inválido ou inativo.')
    _validar_cupom_regras(cupom, total)
    return cupom


def _clientes_tem_colunas_geo(cur) -> bool:
    cur.execute("SHOW COLUMNS FROM clientes LIKE 'latitude'")
    tem_latitude = cur.fetchone() is not None
    cur.execute("SHOW COLUMNS FROM clientes LIKE 'longitude'")
    tem_longitude = cur.fetchone() is not None
    return tem_latitude and tem_longitude


def _registrar_movimento_estoque(cur, item: dict, pedido_id: int, observacao: str):
    estoque_anterior = int(item.get('estoque') or 0)
    quantidade = int(item.get('quantidade') or 0)
    estoque_novo = estoque_anterior - quantidade
    cur.execute('''INSERT INTO estoque_movimentacoes
                   (produto_id, pedido_id, tipo, quantidade, estoque_anterior, estoque_novo, observacao)
                   VALUES (%s, %s, 'saida', %s, %s, %s, %s)''',
                (item.get('produto_id'), pedido_id, -quantidade, estoque_anterior, estoque_novo, observacao))


def _buscar_produtos_do_carrinho(cur, itens: list[dict], validar_estoque: bool = True) -> list[dict]:
    ids = [item['produto_id'] for item in itens]
    if len(ids) == 1:
        cur.execute('SELECT id, nome, preco, estoque, ativo FROM produtos WHERE id=%s', (ids[0],))
        produto = cur.fetchone()
        produtos = [produto] if produto else []
    else:
        placeholders = ','.join(['%s'] * len(ids))
        cur.execute(f'SELECT id, nome, preco, estoque, ativo FROM produtos WHERE id IN ({placeholders})', tuple(ids))
        produtos = cur.fetchall() or []
        if not isinstance(produtos, list):
            produtos = []

    mapa = {int(produto['id']): produto for produto in produtos}
    resultado = []
    for item in itens:
        produto = mapa.get(item['produto_id'])
        if not produto:
            raise HTTPException(404, f'Produto #{item["produto_id"]} não encontrado')
        if produto.get('ativo') in (0, False):
            raise HTTPException(400, f'{produto["nome"]} está indisponível para novos pedidos.')
        if validar_estoque and produto['estoque'] < item['quantidade']:
            raise HTTPException(400, f'Estoque insuficiente para {produto["nome"]}. Disponível: {produto["estoque"]}')
        preco = float(produto['preco'])
        resultado.append({
            'produto_id': item['produto_id'],
            'produto': produto['nome'],
            'quantidade': item['quantidade'],
            'preco_unitario': preco,
            'subtotal': preco * item['quantidade'],
            'estoque': produto['estoque'],
        })
    return resultado


def _validar_estoque_carrinho(itens: list[dict]):
    for item in itens:
        if item['estoque'] < item['quantidade']:
            raise HTTPException(400, f'Estoque insuficiente para {item["produto"]}. Disponível: {item["estoque"]}')


def _resumo_itens(itens: list[dict]) -> str:
    if not itens:
        return 'Pedido'
    return ', '.join(f'{item["produto"]} x{item["quantidade"]}' for item in itens)


def _itens_do_pedido(cur, pedido_id: int, fallback: dict | None = None) -> list[dict]:
    cur.execute('''SELECT pi.produto_id, pr.nome AS produto, pi.quantidade,
                          pi.preco_unitario, pi.subtotal
                   FROM pedido_itens pi
                   JOIN produtos pr ON pr.id = pi.produto_id
                   WHERE pi.pedido_id=%s
                   ORDER BY pi.id''', (pedido_id,))
    itens = cur.fetchall() or []
    if not isinstance(itens, list):
        itens = []
    if itens:
        return [{
            'produto_id': item['produto_id'],
            'produto': item['produto'],
            'quantidade': item['quantidade'],
            'preco_unitario': float(item['preco_unitario']),
            'subtotal': float(item['subtotal']),
        } for item in itens]
    if fallback:
        return [{
            'produto_id': fallback.get('produto_id'),
            'produto': fallback.get('produto') or fallback.get('nome') or 'Produto',
            'quantidade': fallback.get('quantidade') or 1,
            'preco_unitario': float(fallback.get('preco') or 0),
            'subtotal': _total_pedido(fallback.get('preco') or 0, fallback.get('quantidade') or 1),
        }]
    return []


def _resposta_pedido_site(pedido: dict, produto_nome: str, preco, reutilizado: bool = False):
    itens = pedido.get('itens') or []
    confirmacao_status = pedido.get('confirmacao_status') or 'aguardando_pagamento'
    subtotal = sum(float(item.get('subtotal') or 0) for item in itens) if itens else _total_pedido(preco, pedido.get('quantidade'))
    desconto = float(pedido.get('desconto_valor') or 0)
    return {
        'id': pedido.get('id'),
        'status': pedido.get('status') or 'recebido',
        'pagamento_status': pedido.get('pagamento_status') or 'aguardando_pix',
        'confirmacao_status': confirmacao_status,
        'subtotal': subtotal,
        'desconto_valor': desconto,
        'desconto_percentual': float(pedido.get('desconto_percentual') or 0),
        'cupom_codigo': pedido.get('cupom_codigo'),
        'total': max(0, subtotal - desconto),
        'produto': _resumo_itens(itens) if itens else produto_nome,
        'quantidade': sum(int(item.get('quantidade') or 0) for item in itens) if itens else pedido.get('quantidade'),
        'itens': itens,
        'codigo_entrega': _codigo_entrega_publico(pedido),
        'data_criacao': pedido.get('data_criacao'),
        'pix_copia_cola': pedido.get('pix_copia_cola'),
        'pix_qrcode_base64': pedido.get('pix_qrcode_base64'),
        'pix_ticket_url': pedido.get('pix_ticket_url'),
        'reutilizado': reutilizado,
        'mensagem': 'Pix já gerado para este pedido' if reutilizado else 'Pedido recebido',
    }


def _pedido_pix_pendente_recente(cur, cliente_id: int, carrinho_hash: str, produto_id: int, quantidade: int):
    cur.execute('''SELECT p.id, p.status, p.pagamento_status, p.confirmacao_status, p.quantidade,
                          p.forma_pagamento, p.codigo_entrega, p.pix_copia_cola, p.pix_qrcode_base64,
                          p.pix_ticket_url, p.data_criacao, p.produto_id, p.cupom_codigo,
                          p.desconto_percentual, p.desconto_valor, pr.nome AS produto, pr.preco
                   FROM pedidos p
                   JOIN produtos pr ON pr.id = p.produto_id
                   WHERE p.cliente_id=%s
                     AND (p.carrinho_hash=%s OR (p.carrinho_hash IS NULL AND p.produto_id=%s AND p.quantidade=%s))
                     AND LOWER(p.forma_pagamento)='pix'
                     AND p.pagamento_status='aguardando_pix'
                     AND p.confirmacao_status='aguardando_pagamento'
                     AND p.status='recebido'
                     AND p.data_criacao >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
                   ORDER BY p.id DESC
                   LIMIT 1''', (cliente_id, carrinho_hash, produto_id, quantidade, PIX_REUTILIZACAO_MINUTOS))
    pedido = cur.fetchone()
    if pedido:
        pedido['itens'] = _itens_do_pedido(cur, pedido['id'], pedido)
    return pedido


def _pedido_pix_pendente_qualquer_recente(cur, cliente_id: int):
    cur.execute('''SELECT p.id, p.status, p.pagamento_status, p.confirmacao_status, p.quantidade,
                          p.forma_pagamento, p.codigo_entrega, p.pix_copia_cola, p.pix_qrcode_base64,
                          p.pix_ticket_url, p.data_criacao, p.produto_id, p.cupom_codigo,
                          p.desconto_percentual, p.desconto_valor, pr.nome AS produto, pr.preco
                   FROM pedidos p
                   JOIN produtos pr ON pr.id = p.produto_id
                   WHERE p.cliente_id=%s
                     AND LOWER(p.forma_pagamento)='pix'
                     AND p.pagamento_status='aguardando_pix'
                     AND p.confirmacao_status='aguardando_pagamento'
                     AND p.status='recebido'
                     AND p.data_criacao >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
                   ORDER BY p.id DESC
                   LIMIT 1''', (cliente_id, PIX_REUTILIZACAO_MINUTOS))
    pedido = cur.fetchone()
    if pedido:
        pedido['itens'] = _itens_do_pedido(cur, pedido['id'], pedido)
    return pedido


def _pedido_por_telefone(cur, pedido_id: int, telefone: str):
    telefone_limpo = ''.join(ch for ch in telefone if ch.isdigit())
    cur.execute('''SELECT p.*, c.nome AS cliente, c.telefone, c.id AS cliente_id
                   FROM pedidos p
                   JOIN clientes c ON c.id = p.cliente_id
                   WHERE p.id=%s AND c.telefone=%s''', (pedido_id, telefone_limpo))
    return cur.fetchone()


def _ids_webhook_mercado_pago(payload: dict, query: dict) -> set[str]:
    ids = set()

    def adicionar(valor):
        if valor is None:
            return
        texto = str(valor).strip()
        if not texto:
            return
        match = re.search(r'([^/\s?]+)$', texto)
        ids.add(match.group(1) if match else texto)

    adicionar(query.get('id'))
    adicionar(query.get('data.id'))
    adicionar(query.get('resource'))
    adicionar(payload.get('id'))
    adicionar(payload.get('resource'))
    adicionar(payload.get('order_id'))
    adicionar(payload.get('external_reference'))

    data = payload.get('data') if isinstance(payload.get('data'), dict) else {}
    adicionar(data.get('id'))
    adicionar(data.get('resource'))

    order = payload.get('order') if isinstance(payload.get('order'), dict) else {}
    adicionar(order.get('id'))

    return ids


def _pedido_por_ids_mercado_pago(cur, ids: set[str]):
    for identificador in ids:
        match = re.search(r'aqualog-pedido-(\d+)', identificador)
        if match:
            cur.execute('SELECT id, mp_order_id, status FROM pedidos WHERE id=%s', (int(match.group(1)),))
            pedido = cur.fetchone()
            if pedido:
                return pedido

    for identificador in ids:
        cur.execute('SELECT id, mp_order_id, status FROM pedidos WHERE mp_order_id=%s OR mp_payment_id=%s LIMIT 1',
                    (identificador, identificador))
        pedido = cur.fetchone()
        if pedido:
            return pedido
    return None


def _registrar_tentativa_site(telefone: str, request: Request):
    ip = request.client.host if request.client else 'sem-ip'
    chave = f'{ip}:{telefone}'
    agora = time.time()
    tentativas = [t for t in _TENTATIVAS_PEDIDO_SITE.get(chave, []) if agora - t < LIMITE_TENTATIVAS_SEGUNDOS]
    if len(tentativas) >= LIMITE_TENTATIVAS_PEDIDO:
        _TENTATIVAS_PEDIDO_SITE[chave] = tentativas
        raise HTTPException(429, 'Muitas tentativas seguidas. Aguarde um pouco antes de gerar outro Pix.')
    tentativas.append(agora)
    _TENTATIVAS_PEDIDO_SITE[chave] = tentativas


@router.get('/site/produtos')
def listar_produtos_site():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id, nome, preco, estoque, imagem FROM produtos WHERE ativo=1 AND estoque > 0 ORDER BY nome')
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados}


@router.get('/site/config')
def config_site():
    from routes.configuracoes import configuracoes_publicas
    return configuracoes_publicas()


@router.get('/site/enderecos/sugestoes')
def sugestoes_enderecos(q: str = Query('', max_length=80)):
    termo = (q or '').strip()
    if len(termo) < 2:
        return {'success': True, 'data': []}
    like = '%' + termo + '%'
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('''
            SELECT endereco, bairro,
                   MAX(numero_casa) AS numero_casa,
                   MAX(referencia) AS referencia,
                   COUNT(*) AS vezes_usado
            FROM clientes
            WHERE endereco LIKE %s OR bairro LIKE %s
            GROUP BY endereco, bairro
            ORDER BY vezes_usado DESC, endereco ASC
            LIMIT 8
        ''', (like, like))
        return {'success': True, 'data': cur.fetchall() or []}
    finally:
        cur.close(); con.close()


def _texto_geo(valor):
    texto = unicodedata.normalize('NFKD', str(valor or '').lower())
    return ''.join(ch for ch in texto if not unicodedata.combining(ch))


def _resultado_em_caxias_ma(props):
    cidade = _texto_geo(props.get('city') or props.get('county') or props.get('district') or props.get('name'))
    estado = _texto_geo(props.get('state'))
    pais = _texto_geo(props.get('country'))
    return 'caxias' in cidade and ('maranhao' in estado or estado == 'ma') and ('brasil' in pais or 'brazil' in pais)


@router.get('/site/enderecos/mapa-sugestoes')
def sugestoes_enderecos_mapa(q: str = Query('', max_length=120), lat: float = Query(None), lon: float = Query(None)):
    termo = (q or '').strip()
    if len(termo) < 3:
        return {'success': True, 'data': []}
    params = {
        'q': f'{termo}, Caxias, Maranhão, Brasil',
        'limit': 12,
    }
    params['lat'] = lat if lat is not None else -4.8589
    params['lon'] = lon if lon is not None else -43.3554
    url = 'https://photon.komoot.io/api/?' + urlencode(params)
    req = URLRequest(url, headers={'User-Agent': 'AquaLog/1.0 address autocomplete'})
    try:
        with urlopen(req, timeout=8) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except Exception:
        return sugestoes_enderecos(termo)

    sugestoes = []
    for item in payload.get('features') or []:
        props = item.get('properties') or {}
        coords = (item.get('geometry') or {}).get('coordinates') or []
        rua = props.get('street') or props.get('name') or ''
        bairro = props.get('district') or props.get('suburb') or props.get('city') or props.get('county') or ''
        cidade = props.get('city') or props.get('county') or ''
        estado = props.get('state') or ''
        pais = props.get('country') or ''
        if not rua and not bairro:
            continue
        if not _resultado_em_caxias_ma(props):
            continue
        sugestoes.append({
            'endereco': rua,
            'bairro': bairro,
            'numero_casa': props.get('housenumber') or '',
            'referencia': ', '.join([x for x in [cidade, estado] if x]),
            'cidade': cidade,
            'estado': estado,
            'pais': pais,
            'latitude': coords[1] if len(coords) >= 2 else None,
            'longitude': coords[0] if len(coords) >= 2 else None,
            'origem': 'mapa',
        })
    return {'success': True, 'data': sugestoes}


@router.post('/site/mercado-pago/webhook')
async def webhook_mercado_pago(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    ids = _ids_webhook_mercado_pago(payload, dict(request.query_params))
    if not ids:
        return {'success': True, 'data': {'mensagem': 'Webhook recebido sem pedido identificado'}}

    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        pedido = _pedido_por_ids_mercado_pago(cur, ids)
        if not pedido or not pedido.get('mp_order_id'):
            return {'success': True, 'data': {'mensagem': 'Pedido não encontrado para este webhook'}}

        dados = consultar_pix_order(pedido['mp_order_id'])
        dados['mp_order_id'] = dados.get('mp_order_id') or pedido['mp_order_id']
        _atualizar_pagamento(cur, pedido['id'], dados)
        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, %s, %s, %s)''',
                    (pedido['id'], pedido['status'], pedido['status'],
                     f'Pagamento Pix atualizado pelo webhook: {dados.get("pagamento_status")}'))
        con.commit()

        confirmacao_status = 'confirmado' if dados.get('pagamento_status') == 'pago' else None
        notify('refresh', {
            'acao': 'pagamento_atualizado',
            'pedido_id': pedido['id'],
            'status': dados.get('pagamento_status'),
            'confirmacao_status': confirmacao_status,
        })
        return {'success': True, 'data': {'pedido_id': pedido['id'], 'pagamento_status': dados.get('pagamento_status')}}
    except MercadoPagoError as exc:
        raise HTTPException(400, str(exc))
    finally:
        cur.close(); con.close()


@router.get('/site/mercado-pago/webhook')
def testar_webhook_mercado_pago():
    return {'success': True, 'data': {'mensagem': 'Webhook do Mercado Pago ativo. Use esta URL no Mercado Pago como POST.'}}


@router.post('/site/pedidos')
def criar_pedido_site(pedido: PedidoSite, request: Request):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        forma = pedido.forma_pagamento.strip().lower()
        if forma != 'pix' and forma != 'pagamento teste':
            raise HTTPException(400, 'No site do cliente, o pagamento é feito somente por Pix.')

        loja_ok, motivo_fechado = _loja_pode_receber_pedido(cur)
        if not loja_ok:
            raise HTTPException(403, motivo_fechado)

        telefone = ''.join(ch for ch in pedido.telefone if ch.isdigit())
        _registrar_tentativa_site(telefone, request)

        itens_pedido = _normalizar_itens_pedido(pedido)
        cupom_codigo = _normalizar_codigo_cupom(pedido.cupom_codigo)
        carrinho_hash = _hash_carrinho(itens_pedido, cupom_codigo)
        itens_detalhados = _buscar_produtos_do_carrinho(cur, itens_pedido, validar_estoque=False)
        item_principal = itens_detalhados[0]
        quantidade_total = sum(item['quantidade'] for item in itens_detalhados)
        subtotal = sum(item['subtotal'] for item in itens_detalhados)
        cupom = _buscar_cupom(cur, cupom_codigo, subtotal) if cupom_codigo else None
        desconto_percentual = float(cupom['percentual']) if cupom else 0
        desconto_valor = round(subtotal * desconto_percentual / 100, 2) if cupom else 0
        total = max(0, round(subtotal - desconto_valor, 2))
        resumo_produtos = _resumo_itens(itens_detalhados)

        clientes_geo = _clientes_tem_colunas_geo(cur)
        cur.execute('SELECT id FROM clientes WHERE telefone=%s LIMIT 1', (telefone,))
        cliente = cur.fetchone()
        if cliente:
            cliente_id = cliente['id']
            if clientes_geo:
                cur.execute('''UPDATE clientes
                               SET nome=%s, endereco=%s, numero_casa=%s, bairro=%s, referencia=%s,
                                   latitude=COALESCE(%s, latitude), longitude=COALESCE(%s, longitude)
                               WHERE id=%s''',
                            (pedido.nome, pedido.endereco, pedido.numero_casa, pedido.bairro, pedido.referencia,
                             pedido.latitude, pedido.longitude, cliente_id))
            else:
                cur.execute('''UPDATE clientes SET nome=%s, endereco=%s, numero_casa=%s, bairro=%s, referencia=%s WHERE id=%s''',
                            (pedido.nome, pedido.endereco, pedido.numero_casa, pedido.bairro, pedido.referencia, cliente_id))
        else:
            if clientes_geo:
                cur.execute('''INSERT INTO clientes (nome, telefone, endereco, numero_casa, bairro, referencia, latitude, longitude)
                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
                            (pedido.nome, telefone, pedido.endereco, pedido.numero_casa, pedido.bairro,
                             pedido.referencia, pedido.latitude, pedido.longitude))
            else:
                cur.execute('''INSERT INTO clientes (nome, telefone, endereco, numero_casa, bairro, referencia)
                               VALUES (%s,%s,%s,%s,%s,%s)''',
                            (pedido.nome, telefone, pedido.endereco, pedido.numero_casa, pedido.bairro, pedido.referencia))
            cliente_id = cur.lastrowid

        if cliente:
            pedido_existente = _pedido_pix_pendente_recente(
                cur,
                cliente_id,
                carrinho_hash,
                item_principal['produto_id'],
                quantidade_total,
            )
            if pedido_existente:
                con.commit()
                return {'success': True, 'data': _resposta_pedido_site(
                    pedido_existente,
                    pedido_existente.get('produto') or item_principal['produto'],
                    pedido_existente.get('preco') or item_principal['preco_unitario'],
                    reutilizado=True,
                )}
            outro_pedido_pendente = _pedido_pix_pendente_qualquer_recente(cur, cliente_id)
            if outro_pedido_pendente:
                raise HTTPException(
                    429,
                    f'Você já tem Pix pendente no pedido #{outro_pedido_pendente["id"]}. Envie o comprovante pelo suporte ou peça ao admin para cancelar antes de gerar outro.'
                )

        _validar_estoque_carrinho(itens_detalhados)

        codigo_entrega = gerar_codigo_entrega()
        pix_pedido = pedido.forma_pagamento.strip().lower() == 'pix'
        pagamento_teste = pedido.forma_pagamento.strip().lower() == 'pagamento teste'
        pagamento_status = 'aguardando_pix' if pix_pedido else ('pago' if pagamento_teste else 'nao_aplicavel')
        confirmacao_status = 'aguardando_pagamento' if pix_pedido else ('confirmado' if pagamento_teste else 'aguardando_confirmacao')
        cur.execute('''INSERT INTO pedidos (cliente_id, entregador_id, produto_id, quantidade, forma_pagamento,
                                             pagamento_status, confirmacao_status, status, codigo_entrega, carrinho_hash,
                                             cupom_codigo, desconto_percentual, desconto_valor)
                       VALUES (%s, NULL, %s, %s, %s, %s, %s, 'recebido', %s, %s, %s, %s, %s)''',
                    (cliente_id, item_principal['produto_id'], quantidade_total, pedido.forma_pagamento,
                     pagamento_status, confirmacao_status, codigo_entrega, carrinho_hash,
                     cupom_codigo or None, desconto_percentual, desconto_valor))
        pedido_id = cur.lastrowid
        if cupom:
            cur.execute('UPDATE cupons SET usos = usos + 1 WHERE codigo=%s', (cupom['codigo'],))

        for item in itens_detalhados:
            cur.execute('UPDATE produtos SET estoque = estoque - %s WHERE id=%s',
                        (item['quantidade'], item['produto_id']))
            _registrar_movimento_estoque(cur, item, pedido_id, 'Baixa automática por pedido do cliente')
            cur.execute('''INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
                           VALUES (%s, %s, %s, %s, %s)''',
                        (pedido_id, item['produto_id'], item['quantidade'], item['preco_unitario'], item['subtotal']))

        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, NULL, 'recebido', 'Pedido criado pelo site do cliente')''', (pedido_id,))

        con.commit()
        notify('refresh', {
            'acao': 'pedido_site_criado',
            'id': pedido_id,
            'pedido_id': pedido_id,
            'origem': 'site',
            'pagamento_status': pagamento_status,
            'tem_pix': False,
        })
        cur.execute('SELECT data_criacao FROM pedidos WHERE id=%s', (pedido_id,))
        pedido_criado = cur.fetchone() or {}
        resposta_confirmacao = confirmacao_status
        resposta_codigo = codigo_entrega if resposta_confirmacao == 'confirmado' else None
        configuracoes = _ler_configuracoes(cur)
        chave_pix = configuracoes.get('pix_chave', '')

        pix_copia_cola = None
        pix_qrcode_base64 = None
        pix_ticket_url = None

        if pix_pedido:
            try:
                mp_dados = criar_pix_order(
                    pedido_id,
                    total,
                    f'Pedido #{pedido_id} - AquaLog',
                    f'cliente{pedido_id}@aqualog.com',
                )
                pix_copia_cola = mp_dados.get('pix_copia_cola')
                pix_qrcode_base64 = mp_dados.get('pix_qrcode_base64')
                pix_ticket_url = mp_dados.get('pix_ticket_url')
                cur.execute('''UPDATE pedidos SET mp_order_id=%s, mp_payment_id=%s
                               WHERE id=%s''',
                            (mp_dados.get('mp_order_id'), mp_dados.get('mp_payment_id'), pedido_id))
                con.commit()
            except MercadoPagoError:
                pix_manual = gerar_pix_manual(
                    chave_pix,
                    total,
                    configuracoes.get('nome_loja') or 'AquaLog',
                    'CAXIAS',
                    f'AQUALOG{pedido_id}',
                )
                pix_copia_cola = pix_manual.get('pix_copia_cola')
                pix_qrcode_base64 = pix_manual.get('pix_qrcode_base64')
            except Exception:
                pix_manual = gerar_pix_manual(
                    chave_pix,
                    total,
                    configuracoes.get('nome_loja') or 'AquaLog',
                    'CAXIAS',
                    f'AQUALOG{pedido_id}',
                )
                pix_copia_cola = pix_manual.get('pix_copia_cola')
                pix_qrcode_base64 = pix_manual.get('pix_qrcode_base64')

        return {'success': True, 'data': {
            'id': pedido_id,
            'status': 'recebido',
            'pagamento_status': pagamento_status,
            'confirmacao_status': resposta_confirmacao,
            'subtotal': subtotal,
            'desconto_valor': desconto_valor,
            'desconto_percentual': desconto_percentual,
            'cupom_codigo': cupom_codigo or None,
            'total': total,
            'produto': resumo_produtos,
            'quantidade': quantidade_total,
            'itens': itens_detalhados,
            'codigo_entrega': resposta_codigo,
            'data_criacao': pedido_criado.get('data_criacao'),
            'pix_copia_cola': pix_copia_cola,
            'pix_qrcode_base64': pix_qrcode_base64,
            'pix_ticket_url': pix_ticket_url,
            'pix_chave': chave_pix,
            'mensagem': 'Pedido recebido'
        }}
    except HTTPException:
        con.rollback()
        raise
    finally:
        cur.close(); con.close()


@router.get('/site/pedidos/{id}')
def consultar_pedido_site(id: int, telefone: str = Query(..., min_length=8)):
    telefone_limpo = ''.join(ch for ch in telefone if ch.isdigit())
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT p.id, p.status, p.pagamento_status, p.confirmacao_status, p.quantidade, p.forma_pagamento,
                          p.produto_id,
                          p.codigo_entrega, p.pix_copia_cola, p.pix_qrcode_base64, p.pix_ticket_url, p.data_criacao,
                          c.nome AS cliente, c.telefone, c.endereco, c.numero_casa, c.bairro, pr.nome AS produto, pr.preco,
                          p.cupom_codigo, p.desconto_percentual, p.desconto_valor
                   FROM pedidos p
                   JOIN clientes c ON c.id = p.cliente_id
                   JOIN produtos pr ON pr.id = p.produto_id
                   WHERE p.id=%s AND c.telefone=%s''', (id, telefone_limpo))
    pedido = cur.fetchone()
    if not pedido:
        cur.close(); con.close()
        raise HTTPException(404, 'Pedido não encontrado para este telefone')
    itens = _itens_do_pedido(cur, id, pedido)
    cur.close(); con.close()
    pedido['itens'] = itens
    subtotal = sum(float(item['subtotal']) for item in itens) if itens else float(pedido['preco']) * pedido['quantidade']
    pedido['subtotal'] = subtotal
    pedido['desconto_valor'] = float(pedido.get('desconto_valor') or 0)
    pedido['desconto_percentual'] = float(pedido.get('desconto_percentual') or 0)
    pedido['total'] = max(0, subtotal - pedido['desconto_valor'])
    pedido['produto'] = _resumo_itens(itens) if itens else pedido['produto']
    pedido['quantidade'] = sum(int(item['quantidade']) for item in itens) if itens else pedido['quantidade']
    pedido['codigo_entrega'] = _codigo_entrega_publico(pedido)
    return {'success': True, 'data': pedido}


@router.post('/site/pedidos/{id}/comprovante')
def enviar_comprovante_site(id: int, comprovante: ComprovantePix, telefone: str = Query(..., min_length=8)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        pedido = _pedido_por_telefone(cur, id, telefone)
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado para este telefone')
        cur.execute('''INSERT INTO pedido_comprovantes (pedido_id, cliente_id, arquivo_nome, conteudo)
                       VALUES (%s, %s, %s, %s)''',
                    (id, pedido['cliente_id'], comprovante.arquivo_nome, comprovante.conteudo))
        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, %s, %s, 'Comprovante Pix enviado pelo cliente')''',
                    (id, pedido.get('status'), pedido.get('status')))
        con.commit()
        notify('refresh', {'acao': 'comprovante_pix', 'pedido_id': id, 'origem': 'cliente'})
        return {'success': True, 'data': {'mensagem': 'Comprovante recebido'}}
    finally:
        cur.close(); con.close()


@router.get('/site/pedidos/{id}/events')
def eventos_pedido_site(id: int, telefone: str = Query(..., min_length=8)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    pedido = _pedido_por_telefone(cur, id, telefone)
    cur.close(); con.close()
    if not pedido:
        raise HTTPException(404, 'Pedido não encontrado para este telefone')

    return StreamingResponse(
        event_generator(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )


@router.post('/site/pedidos/{id}/pagamento/atualizar')
def atualizar_pagamento_site(id: int, telefone: str = Query(..., min_length=8)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        pedido = _pedido_por_telefone(cur, id, telefone)
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado para este telefone')
        if not pedido.get('mp_order_id'):
            raise HTTPException(400, 'Este pedido não possui Pix gerado pelo Mercado Pago')

        dados = consultar_pix_order(pedido['mp_order_id'])
        dados['mp_order_id'] = dados.get('mp_order_id') or pedido['mp_order_id']
        _atualizar_pagamento(cur, id, dados)
        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, %s, %s, %s)''',
                    (id, pedido['status'], pedido['status'],
                     f'Pagamento Pix consultado pelo cliente: {dados.get("pagamento_status")}'))
        con.commit()
        dados['confirmacao_status'] = 'confirmado' if dados.get('pagamento_status') == 'pago' else pedido.get('confirmacao_status')
        notify('refresh', {'acao': 'pagamento_atualizado', 'pedido_id': id, 'status': dados.get('pagamento_status')})
        return {'success': True, 'data': dados}
    except MercadoPagoError as exc:
        raise HTTPException(400, str(exc))
    finally:
        cur.close(); con.close()


@router.get('/site/pedidos/{id}/suporte')
def listar_suporte_cliente(id: int, telefone: str = Query(..., min_length=8)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    pedido = _pedido_por_telefone(cur, id, telefone)
    if not pedido:
        cur.close(); con.close()
        raise HTTPException(404, 'Pedido não encontrado para este telefone')
    cur.execute('''SELECT id, autor, mensagem, arquivo_nome, arquivo_conteudo, criado_em
                   FROM suporte_mensagens
                   WHERE pedido_id=%s
                   ORDER BY criado_em ASC, id ASC''', (id,))
    mensagens = cur.fetchall()
    cur.close(); con.close()
    return {'success': True, 'data': mensagens}


@router.post('/site/pedidos/{id}/suporte')
def enviar_suporte_cliente(id: int, msg: SuporteMensagem, telefone: str = Query(..., min_length=8)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        pedido = _pedido_por_telefone(cur, id, telefone)
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado para este telefone')
        cur.execute('''INSERT INTO suporte_mensagens
                       (pedido_id, cliente_id, autor, mensagem, arquivo_nome, arquivo_conteudo)
                       VALUES (%s, %s, 'cliente', %s, %s, %s)''',
                    (id, pedido['cliente_id'], msg.mensagem.strip(), msg.arquivo_nome, msg.arquivo_conteudo))
        con.commit()
        notify('refresh', {'acao': 'mensagem_suporte', 'pedido_id': id, 'origem': 'cliente'})
        return {'success': True, 'data': {'mensagem': 'Mensagem enviada'}}
    finally:
        cur.close(); con.close()
