import os
import sys
from unittest.mock import patch
from pathlib import Path

# Ensure backend is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from database import get_connection
from main import app

client = TestClient(app)

API_PREFIX = '/api/v1'

pytestmark = pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != '1',
    reason='Defina RUN_INTEGRATION_TESTS=1 para rodar testes com banco real.',
)


def cleanup_test_data(telefone: str, produto_id: int | None = None):
    con = get_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT id FROM clientes WHERE telefone=%s', (telefone,))
        cliente = cur.fetchone()
        if cliente:
            cur.execute('SELECT id FROM pedidos WHERE cliente_id=%s', (cliente['id'],))
            pedido_ids = [row['id'] for row in cur.fetchall()]
            for pedido_id in pedido_ids:
                cur.execute('DELETE FROM pedido_historico WHERE pedido_id=%s', (pedido_id,))
                cur.execute('DELETE FROM suporte_mensagens WHERE pedido_id=%s', (pedido_id,))
                cur.execute('DELETE FROM pedidos WHERE id=%s', (pedido_id,))
            cur.execute('DELETE FROM clientes WHERE id=%s', (cliente['id'],))
        if produto_id:
            cur.execute('DELETE FROM produtos WHERE id=%s', (produto_id,))
        con.commit()
    finally:
        cur.close()
        con.close()


def test_site_create_pedido_and_admin_list():
    """Cria pedido pelo site, lista no admin e avança status usando banco real."""
    telefone = '999888777'
    produto_id = None
    pedido_id = None

    from routes.admin import os as admin_os
    with patch.object(admin_os, 'getenv', return_value='admin123'):
        login_resp = client.post(f'{API_PREFIX}/admin/login', json={'senha': 'admin123'})
        assert login_resp.status_code == 200
        admin_token = login_resp.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}

    try:
        create_prod = client.post(
            f'{API_PREFIX}/produtos',
            json={'nome': 'Produto Integracao', 'preco': 8.0, 'estoque': 100},
            headers=admin_headers,
        )
        assert create_prod.status_code == 200
        produto_id = create_prod.json()['data']['id']

        site_payload = {
            'nome': 'Cliente Integracao',
            'telefone': telefone,
            'endereco': 'Rua Integracao',
            'numero_casa': '123',
            'bairro': 'Bairro Teste',
            'produto_id': produto_id,
            'quantidade': 2,
            'forma_pagamento': 'Pix',
        }
        pix_mock = {
            'mp_order_id': 'order-integracao',
            'mp_payment_id': 'payment-integracao',
            'pagamento_status': 'aguardando_pix',
            'pix_copia_cola': 'pix-copia-cola',
            'pix_qrcode_base64': None,
            'pix_ticket_url': 'https://example.test/pix',
        }
        with patch('routes.site.criar_pix_order', return_value=pix_mock):
            create_resp = client.post(f'{API_PREFIX}/site/pedidos', json=site_payload)
        assert create_resp.status_code == 200, f'Create failed: {create_resp.text}'
        data = create_resp.json()['data']
        pedido_id = data['id']
        assert data['status'] == 'recebido'
        assert data['pagamento_status'] == 'aguardando_pix'
        assert data['confirmacao_status'] == 'aguardando_pagamento'
        assert data['codigo_entrega'] is None

        list_resp = client.get(f'{API_PREFIX}/pedidos', headers=admin_headers)
        assert list_resp.status_code == 200
        pedidos = list_resp.json()['data']
        assert any(p['id'] == pedido_id for p in pedidos), f'Pedido {pedido_id} not found in admin list'

        pagamento_mock = {
            'mp_order_id': 'order-integracao',
            'mp_payment_id': 'payment-integracao',
            'pagamento_status': 'pago',
        }
        with patch('routes.pedidos.consultar_pix_order', return_value=pagamento_mock):
            update_pag_resp = client.patch(
                f'{API_PREFIX}/pedidos/{pedido_id}/pagamento/atualizar',
                headers=admin_headers,
            )
        assert update_pag_resp.status_code == 200

        confirm_resp = client.patch(f'{API_PREFIX}/pedidos/{pedido_id}/confirmacao', headers=admin_headers)
        assert confirm_resp.status_code == 200

        status_resp = client.patch(
            f'{API_PREFIX}/pedidos/{pedido_id}/status?status=em_preparo',
            headers=admin_headers,
        )
        assert status_resp.status_code == 200

        list_resp = client.get(f'{API_PREFIX}/pedidos', headers=admin_headers)
        pedido = next(p for p in list_resp.json()['data'] if p['id'] == pedido_id)
        assert pedido['status'] == 'em_preparo'
    finally:
        cleanup_test_data(telefone, produto_id)

if __name__ == '__main__':
    test_site_create_pedido_and_admin_list()
    print('Integration test passed')
