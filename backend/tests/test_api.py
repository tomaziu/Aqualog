import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from auth import criar_token, hash_senha

client = TestClient(app)

API_PREFIX = '/api/v1'

ADMIN_TOKEN = criar_token({'tipo': 'admin', 'nome': 'Test'})
ENTREGADOR_TOKEN = criar_token({'tipo': 'entregador', 'id': 1, 'nome': 'Test'})

AUTH_ADMIN = {'Authorization': f'Bearer {ADMIN_TOKEN}'}
AUTH_ENTREGADOR = {'Authorization': f'Bearer {ENTREGADOR_TOKEN}'}


def mock_cursor(fetchone_return=None, fetchall_return=None, rowcount=1, lastrowid=1):
    cur = MagicMock()
    cur.fetchone.return_value = fetchone_return
    cur.fetchall.return_value = fetchall_return if fetchall_return is not None else []
    cur.rowcount = rowcount
    cur.lastrowid = lastrowid
    return cur


def mock_connection(cursor):
    con = MagicMock()
    con.cursor.return_value = cursor
    return con


# ─── Health ──────────────────────────────────────────────────────────

def test_health():
    r = client.get(f'{API_PREFIX}/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


# ─── Admin ─────────────────────────────────────────────────────────

@patch('routes.admin.os.getenv', return_value='admin123')
def test_login_admin_ok(mock_getenv):
    r = client.post(f'{API_PREFIX}/admin/login', json={'senha': 'admin123'})
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data
    assert data['tipo'] == 'admin'


@patch('routes.admin.os.getenv', return_value='admin123')
def test_login_admin_erro(mock_getenv):
    r = client.post(f'{API_PREFIX}/admin/login', json={'senha': 'errada'})
    assert r.status_code == 401


# ─── Entregadores ──────────────────────────────────────────────────

@patch('routes.entregadores.get_connection')
def test_listar_entregadores(mock_get_con):
    cur = mock_cursor(fetchall_return=[
        {'id': 1, 'nome': 'Lucas', 'telefone': '99999', 'veiculo': 'Moto', 'status': 'disponivel'}
    ])
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/entregadores', headers=AUTH_ADMIN)
    assert r.status_code == 200
    data = r.json()
    assert data['success'] is True
    assert len(data['data']) == 1
    assert data['data'][0]['nome'] == 'Lucas'


@patch('routes.entregadores.get_connection')
def test_listar_entregadores_sem_auth(mock_get_con):
    r = client.get(f'{API_PREFIX}/entregadores')
    assert r.status_code == 401


@patch('routes.entregadores.get_connection')
def test_login_entregador_ok(mock_get_con):
    code_hash = hash_senha('lucas123')
    cur = mock_cursor(fetchall_return=[
        {'id': 1, 'nome': 'Lucas', 'veiculo': 'Moto', 'status': 'disponivel', 'codigo_acesso': code_hash}
    ])
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/entregadores/login', json={'codigo_acesso': 'lucas123'})
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data
    assert data['nome'] == 'Lucas'


@patch('routes.entregadores.get_connection')
def test_login_entregador_invalido(mock_get_con):
    cur = mock_cursor(fetchall_return=[])
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/entregadores/login', json={'codigo_acesso': 'invalido'})
    assert r.status_code == 401


@patch('routes.entregadores.get_connection')
def test_criar_entregador(mock_get_con):
    cur = MagicMock()
    cur.lastrowid = 5
    cur.fetchone.return_value = None
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/entregadores', json={
        'nome': 'Novo', 'telefone': '111111111', 'veiculo': 'Carro', 'codigo_acesso': 'novo123'
    }, headers=AUTH_ADMIN)
    assert r.status_code == 200
    data = r.json()
    assert data['success'] is True
    assert data['data']['id'] == 5


@patch('routes.entregadores.get_connection')
def test_pedidos_entregador(mock_get_con):
    cur = mock_cursor(fetchall_return=[
        {'id': 1, 'cliente': 'João', 'status': 'saiu_para_entrega', 'endereco': 'Rua A, 123', 'bairro': 'Centro',
         'produto': 'Galão 20L', 'quantidade': 2, 'forma_pagamento': 'Pix', 'telefone': '99999', 'data_criacao': '2025-01-01T10:00:00'}
    ])
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/entregadores/1/pedidos', headers=AUTH_ENTREGADOR)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]['cliente'] == 'João'


# ─── Clientes ─────────────────────────────────────────────────────

@patch('routes.clientes.get_connection')
def test_listar_clientes(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'total': 1}
    cur.fetchall.return_value = [
        {'id': 1, 'nome': 'Maria', 'telefone': '11111', 'endereco': 'Rua X', 'bairro': 'Centro', 'referencia': None}
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/clientes', headers=AUTH_ADMIN)
    assert r.status_code == 200
    data = r.json()
    assert data['success'] is True
    assert len(data['data']) == 1
    assert data['data'][0]['nome'] == 'Maria'


@patch('routes.clientes.get_connection')
def test_criar_cliente(mock_get_con):
    cur = mock_cursor(lastrowid=10)
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/clientes', json={
        'nome': 'João', 'telefone': '99999999', 'endereco': 'Rua ABC', 'bairro': 'Centro'
    }, headers=AUTH_ADMIN)
    assert r.status_code == 200
    assert r.json()['data']['id'] == 10


# ─── Produtos ─────────────────────────────────────────────────────

@patch('routes.produtos.get_connection')
def test_listar_produtos(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'total': 1}
    cur.fetchall.return_value = [
        {'id': 1, 'nome': 'Galão 20L', 'preco': 8.0, 'estoque': 100}
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/produtos', headers=AUTH_ADMIN)
    assert r.status_code == 200
    data = r.json()
    assert data['success'] is True
    assert len(data['data']) == 1
    assert data['data'][0]['nome'] == 'Galão 20L'


@patch('routes.produtos.get_connection')
def test_criar_produto(mock_get_con):
    cur = mock_cursor(lastrowid=6)
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/produtos', json={
        'nome': 'Água 500ml', 'preco': 2.5, 'estoque': 50
    }, headers=AUTH_ADMIN)
    assert r.status_code == 200
    assert r.json()['data']['id'] == 6


@patch('routes.produtos.get_connection')
def test_inativar_produto(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'id': 1}
    mock_get_con.return_value = mock_connection(cur)

    r = client.delete(f'{API_PREFIX}/produtos/1', headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert r.json()['data']['mensagem'] == 'Produto inativado'
    sqls = [' '.join(str(call.args[0]).split()) for call in cur.execute.call_args_list]
    assert any('UPDATE produtos SET ativo=0' in sql for sql in sqls)


@patch('routes.configuracoes.get_connection')
def test_obter_configuracoes(mock_get_con):
    cur = mock_cursor(fetchall_return=[
        {'chave': 'nome_loja', 'valor': 'Minha Loja'},
        {'chave': 'subtitulo_loja', 'valor': 'Pedido online'},
        {'chave': 'aviso_cliente', 'valor': 'Atendimento ate 20h'},
        {'chave': 'pix_chave', 'valor': 'pix@loja.com'},
        {'chave': 'estoque_minimo_padrao', 'valor': '7'},
    ])
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/configuracoes', headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert r.json()['data']['nome_loja'] == 'Minha Loja'
    assert r.json()['data']['estoque_minimo_padrao'] == 7


@patch('routes.configuracoes.get_connection')
def test_salvar_configuracoes(mock_get_con):
    cur = mock_cursor()
    mock_get_con.return_value = mock_connection(cur)

    r = client.put(f'{API_PREFIX}/configuracoes', json={
        'nome_loja': 'Minha Loja',
        'subtitulo_loja': 'Pedido online',
        'aviso_cliente': '',
        'pix_chave': 'pix@loja.com',
        'estoque_minimo_padrao': 3
    }, headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert cur.execute.call_count == 7


# ─── Pedidos ─────────────────────────────────────────────────────

@patch('routes.pedidos.get_connection')
def test_listar_pedidos(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'total': 1}
    cur.fetchall.return_value = [
        {'id': 1, 'cliente': 'João', 'entregador': 'Lucas', 'entregador_status': 'disponivel',
         'bairro': 'Centro', 'produto': 'Galão 20L', 'status': 'recebido', 'data_criacao': '2025-01-01T10:00:00'}
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/pedidos', headers=AUTH_ADMIN)
    assert r.status_code == 200
    data = r.json()
    assert data['success'] is True
    assert len(data['data']) == 1


@patch('routes.pedidos.get_connection')
def test_criar_pedido(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'estoque': 100}
    cur.lastrowid = 20
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/pedidos', json={
        'cliente_id': 1, 'entregador_id': 1, 'produto_id': 1,
        'quantidade': 2, 'forma_pagamento': 'Pix'
    }, headers=AUTH_ADMIN)
    assert r.status_code == 200
    assert r.json()['data']['id'] == 20


@patch('routes.site.get_connection')
def test_site_listar_produtos(mock_get_con):
    cur = mock_cursor(fetchall_return=[
        {'id': 1, 'nome': 'Galão 20L', 'preco': 8.0, 'estoque': 100}
    ])
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/site/produtos')

    assert r.status_code == 200
    assert r.json()['success'] is True
    assert r.json()['data'][0]['nome'] == 'Galão 20L'


@patch('routes.cupons.get_connection')
def test_validar_cupom_com_regras(mock_get_con):
    cur = mock_cursor(fetchone_return={
        'codigo': 'BEMVINDO10',
        'percentual': 10,
        'ativo': 1,
        'validade_inicio': None,
        'validade_fim': None,
        'valor_minimo': 20,
        'limite_usos': 5,
        'usos': 2,
    })
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/site/cupons/BEMVINDO10?total=50')

    assert r.status_code == 200
    data = r.json()['data']
    assert data['desconto'] == 5
    assert data['total_com_desconto'] == 45


@patch('routes.cupons.get_connection')
def test_validar_cupom_bloqueia_minimo(mock_get_con):
    cur = mock_cursor(fetchone_return={
        'codigo': 'BEMVINDO10',
        'percentual': 10,
        'ativo': 1,
        'validade_inicio': None,
        'validade_fim': None,
        'valor_minimo': 20,
        'limite_usos': None,
        'usos': 0,
    })
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/site/cupons/BEMVINDO10?total=10')

    assert r.status_code == 400
    assert 'pedido mínimo' in r.json()['detail']


@patch('routes.configuracoes.get_connection')
def test_site_config(mock_get_con):
    cur = mock_cursor(fetchall_return=[
        {'chave': 'nome_loja', 'valor': 'Minha Loja'},
        {'chave': 'subtitulo_loja', 'valor': 'Pedido online'},
        {'chave': 'aviso_cliente', 'valor': ''},
        {'chave': 'pix_chave', 'valor': 'pix@loja.com'},
        {'chave': 'estoque_minimo_padrao', 'valor': '5'},
    ])
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/site/config')

    assert r.status_code == 200
    assert r.json()['data']['pix_chave'] == 'pix@loja.com'


def test_site_webhook_get_health():
    r = client.get(f'{API_PREFIX}/site/mercado-pago/webhook')

    assert r.status_code == 200
    assert r.json()['success'] is True


@patch('routes.site.criar_pix_order')
@patch('routes.site.notify')
@patch('routes.site.get_connection')
def test_site_criar_pedido(mock_get_con, mock_notify, mock_pix):
    mock_pix.return_value = {
        'mp_order_id': 'mp-123',
        'mp_payment_id': 'pay-456',
        'pagamento_status': 'aguardando_pix',
        'pix_copia_cola': '00020126580014br.gov.bcb.pix0136test@test.com52040000530398654041.005802BR5913AQUALOG6006CAXIAS62070503A0163041234',
        'pix_qrcode_base64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        'pix_ticket_url': 'https://mercadopago.com/pix/test',
    }
    cur = MagicMock()
    cur.fetchone.side_effect = [
        {'id': 1, 'nome': 'Galão 20L', 'preco': 8.0, 'estoque': 100},
        None,
        None,
        None,
        {'data_criacao': '2026-05-31T10:00:00'},
    ]
    cur.fetchall.side_effect = [
        [{'chave': 'pix_chave', 'valor': 'pix@loja.com'}],
        [{
            'produto_id': 1,
            'produto': 'Galão 20L',
            'quantidade': 2,
            'preco_unitario': 8.0,
            'subtotal': 16.0,
        }],
    ]
    cur.lastrowid = 30
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/site/pedidos', json={
        'nome': 'Cliente Site',
        'telefone': '99999999',
        'endereco': 'Rua Site',
        'numero_casa': '123',
        'bairro': 'Centro',
        'produto_id': 1,
        'quantidade': 2,
        'forma_pagamento': 'Pix',
    })

    assert r.status_code == 200
    data = r.json()['data']
    assert data['id'] == 30
    assert data['total'] == 16.0
    assert data['codigo_entrega'] is None
    assert data['pagamento_status'] == 'aguardando_pix'
    assert data['confirmacao_status'] == 'aguardando_pagamento'
    assert data['pix_copia_cola']
    assert data['pix_qrcode_base64']
    assert data['pix_ticket_url'] == 'https://mercadopago.com/pix/test'
    mock_pix.assert_called_once()
    mock_notify.assert_called_once()
    _, payload = mock_notify.call_args.args
    assert payload['acao'] == 'pedido_site_criado'
    assert payload['pedido_id'] == 30
    assert payload['tem_pix'] is False


@patch('routes.site.criar_pix_order')
@patch('routes.site.notify')
@patch('routes.site.get_connection')
def test_site_criar_pedido_com_carrinho(mock_get_con, mock_notify, mock_pix):
    mock_pix.return_value = {
        'mp_order_id': 'mp-789',
        'mp_payment_id': 'pay-012',
        'pagamento_status': 'aguardando_pix',
        'pix_copia_cola': '00020126580014br.gov.bcb.pix0136test@test.com52040000530398654041.005802BR5913AQUALOG6006CAXIAS62070503A0163041234',
        'pix_qrcode_base64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        'pix_ticket_url': None,
    }
    cur = MagicMock()
    cur.fetchall.side_effect = [
        [{'chave': 'pix_chave', 'valor': 'pix@loja.com'}],
        [
            {'id': 1, 'nome': 'Galão 20L', 'preco': 8.0, 'estoque': 100},
            {'id': 2, 'nome': 'Fardo 12x500ml', 'preco': 18.0, 'estoque': 50},
        ],
        [{'chave': 'pix_chave', 'valor': 'pix@loja.com'}],
    ]
    cur.fetchone.side_effect = [
        None,
        None,
        None,
        {'data_criacao': '2026-05-31T10:00:00'},
    ]
    cur.lastrowid = 31
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/site/pedidos', json={
        'nome': 'Cliente Site',
        'telefone': '99999997',
        'endereco': 'Rua Site',
        'numero_casa': '123',
        'bairro': 'Centro',
        'itens': [
            {'produto_id': 1, 'quantidade': 2},
            {'produto_id': 2, 'quantidade': 1},
        ],
        'forma_pagamento': 'Pix',
    })

    assert r.status_code == 200
    data = r.json()['data']
    assert data['id'] == 31
    assert data['total'] == 34.0
    assert data['quantidade'] == 3
    assert len(data['itens']) == 2
    assert 'Galão 20L x2' in data['produto']
    assert data['pix_copia_cola']
    assert data['pix_qrcode_base64']
    assert data['pix_ticket_url'] is None
    mock_pix.assert_called_once()
    sqls = [' '.join(str(call.args[0]).split()) for call in cur.execute.call_args_list]
    assert sum('INSERT INTO pedido_itens' in sql for sql in sqls) == 2
    assert sum('UPDATE produtos SET estoque = estoque - %s' in sql for sql in sqls) == 2
    mock_notify.assert_called_once()


@patch('routes.site.criar_pix_order')
@patch('routes.site.notify')
@patch('routes.site.get_connection')
def test_site_reutiliza_pix_pendente_recente(mock_get_con, mock_notify, mock_pix):
    cur = MagicMock()
    cur.fetchone.side_effect = [
        {'id': 1, 'nome': 'Galão 20L', 'preco': 8.0, 'estoque': 0},
        None,
        None,
        {'id': 10},
        {
            'id': 30,
            'status': 'recebido',
            'pagamento_status': 'aguardando_pix',
            'confirmacao_status': 'aguardando_pagamento',
            'quantidade': 2,
            'forma_pagamento': 'Pix',
            'codigo_entrega': '123456',
            'pix_copia_cola': '000201',
            'pix_qrcode_base64': 'abc123',
            'pix_ticket_url': 'https://mercadopago.test/pix',
            'data_criacao': '2026-05-31T10:00:00',
            'produto': 'Galão 20L',
            'preco': 8.0,
        },
    ]
    cur.fetchall.side_effect = [
        [{'chave': 'pix_chave', 'valor': 'pix@loja.com'}],
        [{
            'produto_id': 1,
            'produto': 'Galão 20L',
            'quantidade': 2,
            'preco_unitario': 8.0,
            'subtotal': 16.0,
        }],
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/site/pedidos', json={
        'nome': 'Cliente Site',
        'telefone': '99999999',
        'endereco': 'Rua Site',
        'numero_casa': '123',
        'bairro': 'Centro',
        'produto_id': 1,
        'quantidade': 2,
        'forma_pagamento': 'Pix',
    })

    assert r.status_code == 200
    data = r.json()['data']
    assert data['id'] == 30
    assert data['total'] == 16.0
    assert data['reutilizado'] is True
    assert data['codigo_entrega'] is None
    assert data['pix_copia_cola'] == '000201'
    sqls = [' '.join(str(call.args[0]).split()) for call in cur.execute.call_args_list]
    assert not any('INSERT INTO pedidos' in sql for sql in sqls)
    assert not any('UPDATE produtos SET estoque' in sql for sql in sqls)
    mock_pix.assert_not_called()
    mock_notify.assert_not_called()


@patch('routes.site.criar_pix_order')
@patch('routes.site.notify')
@patch('routes.site.get_connection')
def test_site_bloqueia_outro_pix_pendente_mesmo_telefone(mock_get_con, mock_notify, mock_pix):
    cur = MagicMock()
    cur.fetchone.side_effect = [
        {'id': 1, 'nome': 'Galão 20L', 'preco': 8.0, 'estoque': 100},
        None,
        None,
        {'id': 10},
        None,
        {
            'id': 29,
            'status': 'recebido',
            'pagamento_status': 'aguardando_pix',
            'confirmacao_status': 'aguardando_pagamento',
            'quantidade': 1,
            'forma_pagamento': 'Pix',
            'codigo_entrega': '123456',
            'pix_copia_cola': '000201',
            'pix_qrcode_base64': 'abc123',
            'pix_ticket_url': 'https://mercadopago.test/pix',
            'data_criacao': '2026-05-31T10:00:00',
            'produto': 'Fardo 12x500ml',
            'preco': 19.9,
        },
    ]
    cur.fetchall.side_effect = [
        [{'chave': 'pix_chave', 'valor': 'pix@loja.com'}],
        [{
            'produto_id': 2,
            'produto': 'Fardo 12x500ml',
            'quantidade': 1,
            'preco_unitario': 19.9,
            'subtotal': 19.9,
        }],
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/site/pedidos', json={
        'nome': 'Cliente Site',
        'telefone': '99999998',
        'endereco': 'Rua Site',
        'numero_casa': '123',
        'bairro': 'Centro',
        'produto_id': 1,
        'quantidade': 2,
        'forma_pagamento': 'Pix',
    })

    assert r.status_code == 429
    assert 'Pix pendente' in r.json()['detail']
    sqls = [' '.join(str(call.args[0]).split()) for call in cur.execute.call_args_list]
    assert not any('INSERT INTO pedidos' in sql for sql in sqls)
    mock_pix.assert_not_called()
    mock_notify.assert_not_called()


@patch('routes.site.get_connection')
def test_site_consulta_esconde_codigo_ate_confirmar(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {
        'id': 30,
        'status': 'recebido',
        'pagamento_status': 'aguardando_pix',
        'confirmacao_status': 'aguardando_pagamento',
        'quantidade': 2,
        'forma_pagamento': 'Pix',
        'codigo_entrega': '123456',
        'pix_copia_cola': '000201',
        'pix_qrcode_base64': 'abc123',
        'pix_ticket_url': 'https://mercadopago.test/pix',
        'data_criacao': '2026-05-31T10:00:00',
        'cliente': 'Cliente Site',
        'telefone': '99999999',
        'endereco': 'Rua Site',
        'numero_casa': '123',
        'bairro': 'Centro',
        'produto': 'Galão 20L',
        'preco': 8.0,
    }
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/site/pedidos/30?telefone=99999999')

    assert r.status_code == 200
    data = r.json()['data']
    assert data['codigo_entrega'] is None
    assert data['confirmacao_status'] == 'aguardando_pagamento'


@patch('routes.pedidos.get_connection')
def test_criar_pedido_estoque_insuficiente(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'estoque': 1}
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/pedidos', json={
        'cliente_id': 1, 'entregador_id': 1, 'produto_id': 1,
        'quantidade': 5, 'forma_pagamento': 'Pix'
    }, headers=AUTH_ADMIN)
    assert r.status_code == 400


@patch('routes.pedidos.get_connection')
def test_atualizar_status(mock_get_con):
    cur = MagicMock()
    cur.fetchone.side_effect = [
        {'entregador_id': 1, 'status': 'em_preparo', 'forma_pagamento': 'Dinheiro',
         'pagamento_status': 'nao_aplicavel', 'confirmacao_status': 'confirmado'},
        {'total': 1}
    ]
    cur.rowcount = 1
    mock_get_con.return_value = mock_connection(cur)

    r = client.patch(f'{API_PREFIX}/pedidos/1/status?status=saiu_para_entrega', headers=AUTH_ADMIN)
    assert r.status_code == 200
    assert r.json()['data']['mensagem'] == 'Status atualizado'


@patch('routes.pedidos.get_connection')
def test_atribuir_entregador(mock_get_con):
    cur = MagicMock()
    cur.fetchone.side_effect = [
        {'entregador_id': None, 'status': 'recebido', 'forma_pagamento': 'Dinheiro',
         'pagamento_status': 'nao_aplicavel', 'confirmacao_status': 'confirmado'},
        {'id': 2, 'nome': 'Rafael'},
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.patch(f'{API_PREFIX}/pedidos/1/entregador', json={'entregador_id': 2}, headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert r.json()['data']['mensagem'] == 'Entregador atualizado'


@patch('routes.pedidos.get_connection')
def test_atribuir_entregador_bloqueia_sem_confirmacao(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'entregador_id': None, 'status': 'recebido', 'forma_pagamento': 'Dinheiro',
                                'pagamento_status': 'nao_aplicavel', 'confirmacao_status': 'aguardando_confirmacao'}
    mock_get_con.return_value = mock_connection(cur)

    r = client.patch(f'{API_PREFIX}/pedidos/1/entregador', json={'entregador_id': 2}, headers=AUTH_ADMIN)

    assert r.status_code == 400
    assert 'Confirme com o cliente' in r.json()['detail']


@patch('routes.pedidos.get_connection')
def test_confirmar_pedido_manual(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'status': 'recebido', 'forma_pagamento': 'Dinheiro',
                                'pagamento_status': 'nao_aplicavel', 'confirmacao_status': 'aguardando_confirmacao'}
    mock_get_con.return_value = mock_connection(cur)

    r = client.patch(f'{API_PREFIX}/pedidos/1/confirmacao', headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert r.json()['data']['mensagem'] == 'Pedido confirmado'


@patch('routes.pedidos.notify')
@patch('routes.pedidos.get_connection')
def test_cancelar_pedido_devolve_estoque(mock_get_con, mock_notify):
    cur = MagicMock()
    cur.fetchone.return_value = {
        'id': 1,
        'produto_id': 2,
        'quantidade': 3,
        'entregador_id': None,
        'status': 'recebido',
        'forma_pagamento': 'Pix',
        'pagamento_status': 'aguardando_pix',
    }
    mock_get_con.return_value = mock_connection(cur)

    r = client.patch(f'{API_PREFIX}/pedidos/1/cancelar', headers=AUTH_ADMIN)

    assert r.status_code == 200
    sqls = [' '.join(str(call.args[0]).split()) for call in cur.execute.call_args_list]
    assert any('UPDATE produtos SET estoque = estoque + %s' in sql for sql in sqls)
    assert any("SET status='cancelado'" in sql for sql in sqls)
    mock_notify.assert_called_once()


@patch('routes.pedidos.notify')
@patch('routes.pedidos.get_connection')
def test_expirar_pix_pendentes_devolve_estoque(mock_get_con, mock_notify):
    cur = MagicMock()
    cur.fetchall.return_value = [{
        'id': 1,
        'produto_id': 2,
        'quantidade': 3,
        'entregador_id': None,
        'status': 'recebido',
    }]
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/pedidos/pix/expirar', headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert r.json()['data']['total_expirados'] == 1
    sqls = [' '.join(str(call.args[0]).split()) for call in cur.execute.call_args_list]
    assert any('DATE_SUB(NOW(), INTERVAL %s MINUTE)' in sql for sql in sqls)
    assert any('UPDATE produtos SET estoque = estoque + %s' in sql for sql in sqls)
    mock_notify.assert_called_once()


@patch('routes.pedidos.get_connection')
def test_entregador_finaliza_com_codigo(mock_get_con):
    cur = MagicMock()
    cur.fetchone.side_effect = [
        {'entregador_id': 1, 'status': 'saiu_para_entrega', 'codigo_entrega': '123456',
         'forma_pagamento': 'Dinheiro', 'pagamento_status': 'nao_aplicavel', 'confirmacao_status': 'confirmado'},
        {'total': 0},
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.patch(f'{API_PREFIX}/pedidos/1/status/entregador?status=entregue&codigo=123456', headers=AUTH_ENTREGADOR)

    assert r.status_code == 200
    assert r.json()['data']['mensagem'] == 'Status atualizado'


@patch('routes.pedidos.get_connection')
def test_entregador_nao_finaliza_com_codigo_errado(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'entregador_id': 1, 'status': 'saiu_para_entrega', 'codigo_entrega': '123456',
                                'forma_pagamento': 'Dinheiro', 'pagamento_status': 'nao_aplicavel',
                                'confirmacao_status': 'confirmado'}
    mock_get_con.return_value = mock_connection(cur)

    r = client.patch(f'{API_PREFIX}/pedidos/1/status/entregador?status=entregue&codigo=000000', headers=AUTH_ENTREGADOR)

    assert r.status_code == 400


@patch('routes.suporte.get_connection')
def test_listar_suporte_admin(mock_get_con):
    cur = MagicMock()
    cur.fetchall.return_value = [
        {'pedido_id': 1, 'cliente': 'João', 'telefone': '99999', 'status': 'recebido',
         'pagamento_status': 'aguardando_pix', 'ultima_data': '2026-05-31T10:00:00', 'pendentes': 1}
    ]
    cur.fetchone.return_value = {'mensagem': 'Preciso de ajuda', 'autor': 'cliente'}
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/suporte', headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert r.json()['data'][0]['ultima_mensagem'] == 'Preciso de ajuda'


@patch('routes.suporte.notify')
@patch('routes.suporte.get_connection')
def test_apagar_suporte_admin(mock_get_con, mock_notify):
    cur = mock_cursor(rowcount=2)
    mock_get_con.return_value = mock_connection(cur)

    r = client.delete(f'{API_PREFIX}/suporte/1', headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert r.json()['data']['mensagem'] == 'Chat apagado'
    cur.execute.assert_called_once_with('DELETE FROM suporte_mensagens WHERE pedido_id=%s', (1,))
    mock_notify.assert_called_once()


@patch('routes.site.get_connection')
def test_site_enviar_suporte_cliente(mock_get_con):
    cur = MagicMock()
    cur.fetchone.return_value = {'id': 1, 'cliente_id': 1, 'telefone': '99999999'}
    mock_get_con.return_value = mock_connection(cur)

    r = client.post(f'{API_PREFIX}/site/pedidos/1/suporte?telefone=99999999', json={'mensagem': 'Ajuda'})

    assert r.status_code == 200
    assert r.json()['data']['mensagem'] == 'Mensagem enviada'


@patch('routes.pedidos.get_connection')
def test_atualizar_status_invalido(mock_get_con):
    r = client.patch(f'{API_PREFIX}/pedidos/1/status?status=invalido', headers=AUTH_ADMIN)
    assert r.status_code == 400


@patch('routes.pedidos.get_connection')
def test_dashboard(mock_get_con):
    cur = MagicMock()
    cur.fetchone.side_effect = [
        {'total': 50},
        {'aguardando_pix': 4, 'pagos': 20, 'pix_expirados': 2, 'sem_entregador': 3},
        {'tempo_medio': 45.0},
        {'total_vendido': 240.0, 'pedidos_pagos': 20},
        {'total': 40.0, 'pedidos': 4},
        {'total': 30.0, 'pedidos': 3},
        {'total': 120.0, 'pedidos': 10},
        {'total': 240.0, 'pedidos': 20},
    ]
    cur.fetchall.side_effect = [
        [{'status': 'recebido', 'total': 10}, {'status': 'entregue', 'total': 30}],
        [{'bairro': 'Centro', 'entregas': 20}],
        [{'produto': 'Galão 20L', 'quantidade': 15, 'total': 180.0}],
        [{'id': 2, 'nome': 'Água 500ml', 'estoque': 2, 'estoque_minimo': 5}],
        [{'codigo': 'BEMVINDO10', 'percentual': 10, 'ativo': 1, 'usos': 3, 'limite_usos': 10,
          'pedidos': 3, 'desconto_total': 18.0, 'total_final': 162.0}],
        [{'id': 1, 'nome': 'Lucas', 'entregas': 12, 'tempo_medio': 40.0}],
    ]
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/dashboard', headers=AUTH_ADMIN)
    assert r.status_code == 200
    data = r.json()
    assert data['success'] is True
    assert data['data']['total_pedidos'] == 50
    assert data['data']['tempo_medio_minutos'] == 45.0
    assert data['data']['indicadores']['aguardando_pix'] == 4
    assert data['data']['indicadores']['sem_entregador'] == 3
    assert data['data']['financeiro']['total_vendido'] == 240.0
    assert data['data']['financeiro']['ticket_medio'] == 12.0
    assert data['data']['financeiro_periodos']['hoje']['total'] == 40.0
    assert len(data['data']['entregadores_relatorio']) == 1
    assert len(data['data']['produtos_mais_vendidos']) == 1
    assert len(data['data']['estoque_baixo']) == 1
    assert len(data['data']['cupons_relatorio']) == 1
    assert len(data['data']['por_status']) == 2
    assert len(data['data']['roteirizacao_por_bairro']) == 1


@patch('routes.backup.get_connection')
def test_baixar_backup_sql(mock_get_con):
    cur = MagicMock()
    cur.fetchall.side_effect = [
        [('clientes',)],
        [(1, 'João')],
    ]
    cur.fetchone.return_value = ('clientes', 'CREATE TABLE `clientes` (`id` int, `nome` varchar(120))')
    cur.description = [('id',), ('nome',)]
    mock_get_con.return_value = mock_connection(cur)

    r = client.get(f'{API_PREFIX}/backup/sql', headers=AUTH_ADMIN)

    assert r.status_code == 200
    assert 'application/sql' in r.headers['content-type']
    assert 'CREATE TABLE `clientes`' in r.text
    assert "INSERT INTO `clientes` (`id`, `nome`) VALUES (1, 'João');" in r.text


# ─── Sem autenticação ─────────────────────────────────────────────

def test_rota_sem_token():
    r = client.get(f'{API_PREFIX}/pedidos')
    assert r.status_code == 401

def test_rota_token_invalido():
    r = client.get(f'{API_PREFIX}/pedidos', headers={'Authorization': 'Bearer token_invalido'})
    assert r.status_code == 401
