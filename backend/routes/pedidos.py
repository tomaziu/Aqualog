from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_connection
from delivery_code import gerar_codigo_entrega
from mercado_pago import MercadoPagoError, consultar_pix_order
from models import CancelamentoPedido, Pedido, PedidoEntregadorUpdate
from auth import get_admin_user, get_entregador_user
from sse_manager import notify

router = APIRouter()

PIX_EXPIRACAO_MINUTOS = 60
LIMPEZA_FINALIZADOS_DIAS = 30
STATUS_VALIDOS = ['recebido', 'aguardando_entregador', 'separando', 'em_preparo', 'saiu_para_entrega', 'entregue', 'cancelado']


def _somente_digitos(valor) -> str:
    return ''.join(ch for ch in str(valor or '') if ch.isdigit())


def _confirmacao_inicial(forma_pagamento: str, origem_admin: bool = False) -> str:
    if origem_admin:
        return 'confirmado'
    if forma_pagamento.strip().lower() == 'pix':
        return 'aguardando_pagamento'
    return 'aguardando_confirmacao'


def _validar_liberado_para_operacao(pedido: dict, novo_status: str | None = None):
    if (pedido.get('confirmacao_status') or 'confirmado') == 'confirmado':
        return
    if novo_status and novo_status in ('recebido', 'cancelado'):
        return
    if (pedido.get('forma_pagamento') or '').strip().lower() == 'pix':
        raise HTTPException(400, 'Aguarde o pagamento Pix antes de preparar ou enviar este pedido.')
    raise HTTPException(400, 'Confirme com o cliente antes de preparar ou enviar este pedido.')


def _liberar_entregador_se_sem_ativos(cur, entregador_id):
    if not entregador_id:
        return
    cur.execute("SELECT COUNT(*) total FROM pedidos WHERE entregador_id=%s AND status NOT IN ('entregue','cancelado')",
                (entregador_id,))
    ativos = cur.fetchone()['total']
    if ativos == 0:
        cur.execute('UPDATE entregadores SET status=%s WHERE id=%s', ('disponivel', entregador_id))


def _registrar_movimento_estoque(cur, produto_id: int, pedido_id, tipo: str, quantidade: int, observacao: str):
    cur.execute('SELECT estoque FROM produtos WHERE id=%s', (produto_id,))
    produto = cur.fetchone() or {}
    estoque_novo = produto.get('estoque')
    estoque_anterior = None if estoque_novo is None else int(estoque_novo) - int(quantidade)
    cur.execute('''INSERT INTO estoque_movimentacoes
                   (produto_id, pedido_id, tipo, quantidade, estoque_anterior, estoque_novo, observacao)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (produto_id, pedido_id, tipo, quantidade, estoque_anterior, estoque_novo, observacao))


def _devolver_estoque(cur, pedido: dict):
    if pedido.get('status') in ('cancelado', 'entregue'):
        return
    cur.execute('SELECT produto_id, quantidade FROM pedido_itens WHERE pedido_id=%s', (pedido.get('id'),))
    itens = cur.fetchall() or []
    if not isinstance(itens, list):
        itens = []
    if itens:
        for item in itens:
            cur.execute('UPDATE produtos SET estoque = estoque + %s WHERE id=%s',
                        (item.get('quantidade') or 0, item.get('produto_id')))
            _registrar_movimento_estoque(cur, item.get('produto_id'), pedido.get('id'), 'devolucao', item.get('quantidade') or 0, 'Estoque devolvido no cancelamento/exclusão')
        return
    cur.execute('UPDATE produtos SET estoque = estoque + %s WHERE id=%s',
                (pedido.get('quantidade') or 0, pedido.get('produto_id')))
    _registrar_movimento_estoque(cur, pedido.get('produto_id'), pedido.get('id'), 'devolucao', pedido.get('quantidade') or 0, 'Estoque devolvido no cancelamento/exclusão')


def _cancelar_pedido(cur, pedido: dict, pagamento_status: str | None, observacao: str):
    if pedido.get('status') in ('cancelado', 'entregue'):
        raise HTTPException(400, 'Pedido já está finalizado')

    status_anterior = pedido.get('status')
    _devolver_estoque(cur, pedido)
    cur.execute('''UPDATE pedidos
                   SET status='cancelado',
                       pagamento_status=COALESCE(%s, pagamento_status),
                       entregador_id=NULL,
                       motivo_cancelamento=%s
                   WHERE id=%s''', (pagamento_status, observacao[:255], pedido['id']))
    cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                   VALUES (%s, %s, 'cancelado', %s)''',
                (pedido['id'], status_anterior, observacao))
    _liberar_entregador_se_sem_ativos(cur, pedido.get('entregador_id'))


def _expirar_pix_pendentes_cur(cur):
    cur.execute('''SELECT id, produto_id, quantidade, entregador_id, status
                   FROM pedidos
                   WHERE LOWER(forma_pagamento)='pix'
                     AND pagamento_status='aguardando_pix'
                     AND status NOT IN ('cancelado', 'entregue')
                     AND data_criacao < DATE_SUB(NOW(), INTERVAL %s MINUTE)''',
                (PIX_EXPIRACAO_MINUTOS,))
    pedidos = cur.fetchall()
    for pedido in pedidos:
        _cancelar_pedido(cur, pedido, 'expirado', f'Pix expirado automaticamente após {PIX_EXPIRACAO_MINUTOS} minutos')
    return len(pedidos)


def _expirar_pix_pendentes():
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        expirados = _expirar_pix_pendentes_cur(cur)
        con.commit()
        if expirados:
            notify('refresh', {'acao': 'pix_expirados', 'total': expirados})
        return expirados
    except Exception:
        con.rollback()
        raise
    finally:
        cur.close(); con.close()


@router.get('/pedidos')
def listar(page: int = Query(1, ge=1), per_page: int = Query(100, ge=1, le=500), admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT COUNT(*) total FROM pedidos')
    total = cur.fetchone()['total']
    offset = (page - 1) * per_page
    cur.execute('''SELECT p.*, c.nome AS cliente, c.telefone AS cliente_telefone,
                          c.endereco, c.numero_casa, c.bairro, c.referencia,
                          e.nome AS entregador, e.status AS entregador_status,
                          COALESCE((
                              SELECT GROUP_CONCAT(CONCAT(pri.nome, ' x', pi.quantidade) ORDER BY pi.id SEPARATOR ', ')
                              FROM pedido_itens pi
                              JOIN produtos pri ON pri.id = pi.produto_id
                              WHERE pi.pedido_id = p.id
                          ), CONCAT(pr.nome, ' x', p.quantidade)) AS produto
                          , COALESCE((SELECT SUM(pi.subtotal) FROM pedido_itens pi WHERE pi.pedido_id = p.id), pr.preco * p.quantidade) AS total_bruto
                          , COALESCE(p.desconto_valor, 0) AS desconto_valor
                          , GREATEST(COALESCE((SELECT SUM(pi.subtotal) FROM pedido_itens pi WHERE pi.pedido_id = p.id), pr.preco * p.quantidade) - COALESCE(p.desconto_valor, 0), 0) AS total
                          , (SELECT COUNT(*) FROM pedido_comprovantes pc WHERE pc.pedido_id = p.id) AS comprovantes
                   FROM pedidos p
                   JOIN clientes c ON c.id = p.cliente_id
                   LEFT JOIN entregadores e ON e.id = p.entregador_id
                   JOIN produtos pr ON pr.id = p.produto_id
                   ORDER BY p.id DESC LIMIT %s OFFSET %s''', (per_page, offset))
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados, 'total': total, 'page': page, 'per_page': per_page}


@router.post('/pedidos')
def criar(pedido: Pedido, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT estoque, ativo FROM produtos WHERE id=%s', (pedido.produto_id,))
        produto = cur.fetchone()
        if not produto:
            raise HTTPException(404, 'Produto não encontrado')
        if produto.get('ativo') in (0, False):
            raise HTTPException(400, 'Produto inativo. Reative o produto antes de criar pedido.')
        if produto['estoque'] < pedido.quantidade:
            raise HTTPException(400, f'Estoque insuficiente. Disponível: {produto["estoque"]}, solicitado: {pedido.quantidade}')

        codigo_entrega = gerar_codigo_entrega()
        pagamento_status = 'aguardando_pix' if pedido.forma_pagamento.strip().lower() == 'pix' else 'nao_aplicavel'
        confirmacao_status = _confirmacao_inicial(pedido.forma_pagamento, origem_admin=True)
        cur.execute('''INSERT INTO pedidos (cliente_id, entregador_id, produto_id, quantidade, forma_pagamento, pagamento_status, confirmacao_status, status, codigo_entrega)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                    (pedido.cliente_id, pedido.entregador_id, pedido.produto_id, pedido.quantidade, pedido.forma_pagamento, pagamento_status, confirmacao_status, pedido.status, codigo_entrega))
        novo_id = cur.lastrowid

        cur.execute('UPDATE produtos SET estoque = estoque - %s WHERE id=%s', (pedido.quantidade, pedido.produto_id))
        _registrar_movimento_estoque(cur, pedido.produto_id, novo_id, 'saida', -pedido.quantidade, 'Baixa automática por pedido manual')
        cur.execute('''INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
                       SELECT %s, id, %s, preco, preco * %s FROM produtos WHERE id=%s''',
                    (novo_id, pedido.quantidade, pedido.quantidade, pedido.produto_id))

        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, NULL, %s, 'Pedido criado')''', (novo_id, pedido.status))

        con.commit()
        notify('refresh', {'acao': 'criar_pedido', 'id': novo_id})
        return {'success': True, 'data': {'id': novo_id, 'codigo_entrega': codigo_entrega, 'mensagem': 'Pedido criado'}}
    except HTTPException:
        con.rollback()
        raise
    finally:
        cur.close(); con.close()


@router.post('/pedidos/pix/expirar')
def expirar_pix(admin=Depends(get_admin_user)):
    expirados = _expirar_pix_pendentes()
    return {'success': True, 'data': {'total_expirados': expirados}}


@router.delete('/pedidos/limpeza/finalizados')
def limpar_finalizados_antigos(dias: int = Query(LIMPEZA_FINALIZADOS_DIAS, ge=1, le=365), admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT COUNT(*) total
                   FROM pedidos
                   WHERE status IN ('entregue', 'cancelado')
                     AND data_criacao < DATE_SUB(NOW(), INTERVAL %s DAY)''', (dias,))
    total = cur.fetchone()['total']
    cur.execute('''DELETE FROM pedidos
                   WHERE status IN ('entregue', 'cancelado')
                     AND data_criacao < DATE_SUB(NOW(), INTERVAL %s DAY)''', (dias,))
    con.commit(); cur.close(); con.close()
    if total:
        notify('refresh', {'acao': 'limpeza_pedidos', 'total': total})
    return {'success': True, 'data': {'total_removidos': total}}


@router.patch('/pedidos/{id}/cancelar')
def cancelar_pedido(id: int, payload: CancelamentoPedido | None = None, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('''SELECT id, produto_id, quantidade, entregador_id, status, forma_pagamento, pagamento_status
                       FROM pedidos WHERE id=%s''', (id,))
        pedido = cur.fetchone()
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado')

        pagamento_status = 'expirado' if (
            (pedido.get('forma_pagamento') or '').strip().lower() == 'pix'
            and pedido.get('pagamento_status') == 'aguardando_pix'
        ) else None
        motivo = (payload.motivo if payload else '') or 'Sem motivo informado'
        _cancelar_pedido(cur, pedido, pagamento_status, f'Pedido cancelado pelo admin: {motivo}')
        con.commit()
    except HTTPException:
        con.rollback()
        raise
    finally:
        cur.close(); con.close()

    notify('refresh', {'acao': 'pedido_cancelado', 'pedido_id': id})
    return {'success': True, 'data': {'mensagem': 'Pedido cancelado e estoque devolvido'}}


@router.patch('/pedidos/{id}/entregador')
def atribuir_entregador(id: int, payload: PedidoEntregadorUpdate, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT entregador_id, status, forma_pagamento, pagamento_status, confirmacao_status FROM pedidos WHERE id=%s', (id,))
        pedido = cur.fetchone()
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado')
        if pedido['status'] in ('entregue', 'cancelado'):
            raise HTTPException(400, 'Não é possível alterar entregador de pedido finalizado')
        if payload.entregador_id:
            _validar_liberado_para_operacao(pedido)

        entregador_id_anterior = pedido['entregador_id']
        novo_entregador_id = payload.entregador_id
        nome_entregador = None

        if novo_entregador_id:
            cur.execute('SELECT id, nome FROM entregadores WHERE id=%s', (novo_entregador_id,))
            entregador = cur.fetchone()
            if not entregador:
                raise HTTPException(404, 'Entregador não encontrado')
            nome_entregador = entregador['nome']

        cur.execute('UPDATE pedidos SET entregador_id=%s WHERE id=%s', (novo_entregador_id, id))

        observacao = 'Entregador removido via admin'
        if novo_entregador_id:
            observacao = f'Entregador atribuído via admin: {nome_entregador}'
        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, %s, %s, %s)''',
                    (id, pedido['status'], pedido['status'], observacao))

        if entregador_id_anterior and entregador_id_anterior != novo_entregador_id:
            cur.execute("SELECT COUNT(*) total FROM pedidos WHERE entregador_id=%s AND status NOT IN ('entregue','cancelado')",
                        (entregador_id_anterior,))
            ativos = cur.fetchone()['total']
            if ativos == 0:
                cur.execute('UPDATE entregadores SET status=%s WHERE id=%s', ('disponivel', entregador_id_anterior))

        if novo_entregador_id and pedido['status'] == 'saiu_para_entrega':
            cur.execute('UPDATE entregadores SET status=%s WHERE id=%s', ('ocupado', novo_entregador_id))

        con.commit()
    except HTTPException:
        con.rollback()
        raise
    finally:
        cur.close(); con.close()

    notify('refresh', {'acao': 'atribuir_entregador', 'pedido_id': id, 'entregador_id': novo_entregador_id})
    return {'success': True, 'data': {'mensagem': 'Entregador atualizado'}}


@router.patch('/pedidos/{id}/pagamento/atualizar')
def atualizar_pagamento_admin(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT id, mp_order_id, status, confirmacao_status FROM pedidos WHERE id=%s', (id,))
        pedido = cur.fetchone()
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado')
        if not pedido.get('mp_order_id'):
            dados = {'pagamento_status': 'pago', 'confirmacao_status': 'confirmado', 'modo': 'pix_manual'}
            cur.execute('''UPDATE pedidos
                           SET pagamento_status='pago', confirmacao_status='confirmado'
                           WHERE id=%s''', (id,))
            cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                           VALUES (%s, %s, %s, 'Pix manual confirmado pelo admin')''',
                        (id, pedido['status'], pedido['status']))
            con.commit()
            notify('refresh', {'acao': 'pagamento_atualizado', 'pedido_id': id, 'status': 'pago', 'confirmacao_status': 'confirmado'})
            return {'success': True, 'data': dados}

        dados = consultar_pix_order(pedido['mp_order_id'])
        dados['mp_order_id'] = dados.get('mp_order_id') or pedido['mp_order_id']
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
                     dados.get('pix_copia_cola'), dados.get('pix_qrcode_base64'), dados.get('pix_ticket_url'), id))
        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, %s, %s, %s)''',
                    (id, pedido['status'], pedido['status'],
                     f'Pagamento Pix verificado pelo admin: {dados.get("pagamento_status")}'))
        con.commit()
        dados['confirmacao_status'] = 'confirmado' if dados.get('pagamento_status') == 'pago' else pedido.get('confirmacao_status')
    except MercadoPagoError as exc:
        raise HTTPException(400, str(exc))
    finally:
        cur.close(); con.close()

    notify('refresh', {'acao': 'pagamento_atualizado', 'pedido_id': id, 'status': dados.get('pagamento_status')})
    return {'success': True, 'data': dados}


@router.patch('/pedidos/{id}/confirmacao')
def confirmar_pedido(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT status, forma_pagamento, pagamento_status, confirmacao_status FROM pedidos WHERE id=%s', (id,))
        pedido = cur.fetchone()
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado')
        if pedido['status'] in ('entregue', 'cancelado'):
            raise HTTPException(400, 'Não é possível confirmar pedido finalizado')
        if (pedido.get('forma_pagamento') or '').strip().lower() == 'pix' and pedido.get('pagamento_status') != 'pago':
            raise HTTPException(400, 'Pedido Pix só é confirmado após pagamento aprovado.')
        if pedido.get('confirmacao_status') == 'confirmado':
            return {'success': True, 'data': {'mensagem': 'Pedido já confirmado'}}

        cur.execute('UPDATE pedidos SET confirmacao_status=%s WHERE id=%s', ('confirmado', id))
        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, %s, %s, 'Pedido confirmado pelo admin')''',
                    (id, pedido['status'], pedido['status']))
        con.commit()
    except HTTPException:
        con.rollback()
        raise
    finally:
        cur.close(); con.close()

    notify('refresh', {'acao': 'pedido_confirmado', 'pedido_id': id})
    return {'success': True, 'data': {'mensagem': 'Pedido confirmado'}}


@router.patch('/pedidos/{id}/status')
def atualizar_status(id: int, status: str = Query(...), admin=Depends(get_admin_user)):
    status = status.strip().lower()
    if status not in STATUS_VALIDOS:
        raise HTTPException(400, 'Status inválido')
    entrega = ', data_entrega = NOW()' if status == 'entregue' else ''
    con = get_connection(); cur = con.cursor(dictionary=True)

    cur.execute('''SELECT id, entregador_id, produto_id, quantidade, status, forma_pagamento,
                          pagamento_status, confirmacao_status
                   FROM pedidos WHERE id=%s''', (id,))
    pedido = cur.fetchone()
    if not pedido:
        cur.close(); con.close()
        raise HTTPException(404, 'Pedido não encontrado')

    status_anterior = pedido['status']
    entregador_id = pedido['entregador_id']
    _validar_liberado_para_operacao(pedido, status)

    if status == 'cancelado':
        pagamento_status = 'expirado' if (
            (pedido.get('forma_pagamento') or '').strip().lower() == 'pix'
            and pedido.get('pagamento_status') == 'aguardando_pix'
        ) else None
        _cancelar_pedido(cur, pedido, pagamento_status, 'Pedido cancelado via admin; estoque devolvido')
    else:
        cur.execute(f'UPDATE pedidos SET status=%s {entrega} WHERE id=%s', (status, id))

        cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                       VALUES (%s, %s, %s, 'Status alterado via admin')''',
                    (id, status_anterior, status))

    if entregador_id and status == 'saiu_para_entrega':
        cur.execute('UPDATE entregadores SET status=%s WHERE id=%s', ('ocupado', entregador_id))
    elif entregador_id and status in ('entregue', 'cancelado'):
        _liberar_entregador_se_sem_ativos(cur, entregador_id)

    con.commit(); cur.close(); con.close()

    notify('refresh', {'acao': 'status_admin', 'pedido_id': id, 'status': status})
    return {'success': True, 'data': {'mensagem': 'Status atualizado'}}


@router.patch('/pedidos/{id}/status/entregador')
def atualizar_status_entregador(id: int, status: str = Query(...), codigo: Optional[str] = Query(None), user=Depends(get_entregador_user)):
    status = status.strip().lower()
    print(f"\n>>> [SERVIDOR] Requisição de status recebida: Pedido {id} -> {status}")
    if status not in STATUS_VALIDOS:
        raise HTTPException(400, 'Status inválido')
    entrega = ', data_entrega = NOW()' if status == 'entregue' else ''
    con = get_connection(); cur = con.cursor(dictionary=True)

    cur.execute('SELECT entregador_id, status, codigo_entrega, forma_pagamento, pagamento_status, confirmacao_status FROM pedidos WHERE id=%s', (id,))
    pedido = cur.fetchone()
    if not pedido:
        cur.close(); con.close()
        raise HTTPException(404, 'Pedido não encontrado')

    if pedido['entregador_id'] != user.get('id'):
        cur.close(); con.close()
        raise HTTPException(403, 'Este pedido não está atribuído a você')

    _validar_liberado_para_operacao(pedido, status)

    if status == 'entregue':
        codigo_salvo = _somente_digitos(pedido.get('codigo_entrega'))
        codigo_informado = _somente_digitos(codigo)
        if not codigo_salvo:
            cur.close(); con.close()
            raise HTTPException(400, 'Este pedido ainda não possui código de entrega')
        if not codigo_informado:
            cur.close(); con.close()
            raise HTTPException(400, 'Informe o código de entrega do cliente')
        if codigo_informado != codigo_salvo:
            cur.close(); con.close()
            raise HTTPException(400, 'Código de entrega inválido')

    status_anterior = pedido['status']
    entregador_id = pedido['entregador_id']

    cur.execute(f'UPDATE pedidos SET status=%s {entrega} WHERE id=%s', (status, id))

    cur.execute('''INSERT INTO pedido_historico (pedido_id, status_anterior, status_novo, observacao)
                   VALUES (%s, %s, %s, 'Status alterado pelo entregador')''',
                (id, status_anterior, status))

    if entregador_id and status == 'saiu_para_entrega':
        cur.execute('UPDATE entregadores SET status=%s WHERE id=%s', ('ocupado', entregador_id))
    elif entregador_id and status in ('entregue', 'cancelado'):
        cur.execute("SELECT COUNT(*) total FROM pedidos WHERE entregador_id=%s AND status NOT IN ('entregue','cancelado')", (entregador_id,))
        ativos = cur.fetchone()['total']
        if ativos == 0:
            cur.execute('UPDATE entregadores SET status=%s WHERE id=%s', ('disponivel', entregador_id))

    con.commit(); cur.close(); con.close()

    notify('refresh', {'acao': 'status_entregador', 'pedido_id': id, 'status': status})
    return {'success': True, 'data': {'mensagem': 'Status atualizado'}}



@router.delete('/pedidos/{id}')
def excluir(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id, produto_id, quantidade, entregador_id, status FROM pedidos WHERE id=%s', (id,))
    pedido = cur.fetchone()
    if not pedido:
        cur.close(); con.close()
        raise HTTPException(404, 'Pedido não encontrado')
    _devolver_estoque(cur, pedido)
    cur.execute('DELETE FROM pedidos WHERE id=%s', (id,))
    linhas = cur.rowcount
    _liberar_entregador_se_sem_ativos(cur, pedido.get('entregador_id'))
    con.commit()
    cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Pedido não encontrado')
    notify('refresh', {'acao': 'excluir_pedido', 'id': id})
    return {'success': True, 'data': {'mensagem': 'Pedido excluído'}}


@router.get('/pedidos/{id}/historico')
def historico(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT * FROM pedido_historico WHERE pedido_id=%s ORDER BY criado_em ASC''', (id,))
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados}


@router.get('/pedidos/{id}/comprovantes')
def comprovantes(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT id, arquivo_nome, conteudo, criado_em
                   FROM pedido_comprovantes
                   WHERE pedido_id=%s
                   ORDER BY id DESC''', (id,))
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados}


@router.get('/dashboard')
def dashboard(admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)

    def financeiro_periodo(condicao: str):
        cur.execute(f'''SELECT COALESCE(SUM(t.total_final), 0) total, COUNT(*) pedidos
                        FROM (
                          SELECT p.id,
                                 GREATEST(COALESCE(SUM(pi.subtotal), 0) - COALESCE(p.desconto_valor, 0), 0) total_final
                          FROM pedidos p
                          LEFT JOIN pedido_itens pi ON pi.pedido_id = p.id
                          WHERE p.pagamento_status='pago'
                            AND p.status <> 'cancelado'
                            AND {condicao}
                          GROUP BY p.id, p.desconto_valor
                        ) t''')
        linha = cur.fetchone() or {}
        return {'total': float(linha.get('total') or 0), 'pedidos': linha.get('pedidos') or 0}

    cur.execute("SELECT COUNT(*) total FROM pedidos")
    total = cur.fetchone()['total']
    cur.execute("SELECT status, COUNT(*) total FROM pedidos GROUP BY status")
    por_status = cur.fetchall()
    cur.execute('''SELECT
                      SUM(CASE WHEN pagamento_status='aguardando_pix' THEN 1 ELSE 0 END) aguardando_pix,
                      SUM(CASE WHEN pagamento_status='pago' THEN 1 ELSE 0 END) pagos,
                      SUM(CASE WHEN pagamento_status='expirado' THEN 1 ELSE 0 END) pix_expirados,
                      SUM(CASE WHEN status NOT IN ('entregue','cancelado') AND entregador_id IS NULL THEN 1 ELSE 0 END) sem_entregador
                   FROM pedidos''')
    indicadores = cur.fetchone() or {}
    cur.execute("SELECT ROUND(AVG(TIMESTAMPDIFF(MINUTE, data_criacao, data_entrega)), 1) tempo_medio FROM pedidos WHERE data_entrega IS NOT NULL")
    tempo = cur.fetchone()['tempo_medio'] or 0
    cur.execute("SELECT c.bairro, COUNT(*) entregas FROM pedidos p JOIN clientes c ON c.id=p.cliente_id GROUP BY c.bairro ORDER BY entregas DESC")
    rotas = cur.fetchall()
    cur.execute('''SELECT COALESCE(SUM(t.total_final), 0) total_vendido,
                          COUNT(*) pedidos_pagos
                   FROM (
                     SELECT p.id,
                            GREATEST(COALESCE(SUM(pi.subtotal), 0) - COALESCE(p.desconto_valor, 0), 0) total_final
                     FROM pedidos p
                     LEFT JOIN pedido_itens pi ON pi.pedido_id = p.id
                     WHERE p.pagamento_status='pago'
                       AND p.status <> 'cancelado'
                     GROUP BY p.id, p.desconto_valor
                   ) t''')
    financeiro = cur.fetchone() or {}
    pedidos_pagos = financeiro.get('pedidos_pagos') or 0
    total_vendido = float(financeiro.get('total_vendido') or 0)
    cur.execute('''SELECT pr.nome AS produto,
                          SUM(pi.quantidade) quantidade,
                          COALESCE(SUM(pi.subtotal), 0) total
                   FROM pedidos p
                   JOIN pedido_itens pi ON pi.pedido_id = p.id
                   JOIN produtos pr ON pr.id = pi.produto_id
                   WHERE p.pagamento_status='pago'
                     AND p.status <> 'cancelado'
                   GROUP BY pr.id, pr.nome
                   ORDER BY quantidade DESC, total DESC
                   LIMIT 6''')
    produtos_mais_vendidos = cur.fetchall()
    cur.execute('''SELECT id, nome, estoque, estoque_minimo
                   FROM produtos
                   WHERE ativo=1 AND estoque <= estoque_minimo
                   ORDER BY estoque ASC, nome ASC
                   LIMIT 8''')
    estoque_baixo = cur.fetchall()
    cur.execute('''SELECT c.codigo, c.percentual, c.ativo, c.usos, c.limite_usos,
                          COUNT(t.id) pedidos,
                          COALESCE(SUM(t.desconto_valor), 0) desconto_total,
                          COALESCE(SUM(t.total_final), 0) total_final
                   FROM cupons c
                   LEFT JOIN (
                     SELECT p.id, p.cupom_codigo, COALESCE(p.desconto_valor, 0) desconto_valor,
                            GREATEST(COALESCE(SUM(pi.subtotal), 0) - COALESCE(p.desconto_valor, 0), 0) total_final
                     FROM pedidos p
                     LEFT JOIN pedido_itens pi ON pi.pedido_id = p.id
                     WHERE p.cupom_codigo IS NOT NULL
                       AND p.cupom_codigo <> ''
                       AND p.status <> 'cancelado'
                     GROUP BY p.id, p.cupom_codigo, p.desconto_valor
                   ) t ON t.cupom_codigo = c.codigo
                   GROUP BY c.id, c.codigo, c.percentual, c.ativo, c.usos, c.limite_usos
                   ORDER BY desconto_total DESC, pedidos DESC, c.codigo ASC
                   LIMIT 8''')
    cupons_relatorio = cur.fetchall()
    financeiro_periodos = {
        'hoje': financeiro_periodo('DATE(p.data_criacao)=CURDATE()'),
        'ontem': financeiro_periodo('DATE(p.data_criacao)=DATE_SUB(CURDATE(), INTERVAL 1 DAY)'),
        'semana': financeiro_periodo('p.data_criacao >= DATE_SUB(NOW(), INTERVAL 7 DAY)'),
        'mes': financeiro_periodo('p.data_criacao >= DATE_SUB(NOW(), INTERVAL 30 DAY)'),
    }
    cur.execute('''SELECT e.id, e.nome,
                          COUNT(p.id) entregas,
                          COALESCE(ROUND(AVG(TIMESTAMPDIFF(MINUTE, p.data_criacao, p.data_entrega)), 1), 0) tempo_medio
                   FROM entregadores e
                   LEFT JOIN pedidos p ON p.entregador_id=e.id
                                      AND p.status='entregue'
                                      AND p.data_entrega IS NOT NULL
                   GROUP BY e.id, e.nome
                   ORDER BY entregas DESC, tempo_medio ASC
                   LIMIT 8''')
    entregadores_relatorio = cur.fetchall()
    cur.close(); con.close()
    return {'success': True, 'data': {
        'total_pedidos': total,
        'por_status': por_status,
        'tempo_medio_minutos': tempo,
        'roteirizacao_por_bairro': rotas,
        'financeiro': {
            'total_vendido': total_vendido,
            'ticket_medio': round(total_vendido / pedidos_pagos, 2) if pedidos_pagos else 0,
            'pedidos_pagos': pedidos_pagos,
        },
        'financeiro_periodos': financeiro_periodos,
        'entregadores_relatorio': entregadores_relatorio,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'estoque_baixo': estoque_baixo,
        'cupons_relatorio': cupons_relatorio,
        'indicadores': {
            'aguardando_pix': indicadores.get('aguardando_pix') or 0,
            'pagos': indicadores.get('pagos') or 0,
            'pix_expirados': indicadores.get('pix_expirados') or 0,
            'sem_entregador': indicadores.get('sem_entregador') or 0,
        }
    }}
