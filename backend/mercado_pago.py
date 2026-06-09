import json
import os
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE = 'https://api.mercadopago.com'


class MercadoPagoError(Exception):
    pass


def _token() -> str:
    token = os.getenv('MERCADO_PAGO_ACCESS_TOKEN', '').strip()
    if not token:
        raise MercadoPagoError('Token do Mercado Pago não configurado.')
    return token


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {_token()}',
    }
    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        headers['X-Idempotency-Key'] = str(uuid.uuid4())

    req = Request(API_BASE + path, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=20) as res:
            body = res.read().decode('utf-8')
            return json.loads(body) if body else {}
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        try:
            erro = json.loads(body)
            detalhe = erro.get('message') or erro.get('error') or body
        except json.JSONDecodeError:
            detalhe = body or str(exc)
        raise MercadoPagoError(f'Mercado Pago: {detalhe}')
    except URLError as exc:
        raise MercadoPagoError(f'Falha de conexão com Mercado Pago: {exc.reason}')


def _dados_pix(order: dict) -> dict:
    pagamentos = (order.get('transactions') or {}).get('payments') or []
    pagamento = pagamentos[0] if pagamentos else {}
    metodo = pagamento.get('payment_method') or {}
    return {
        'mp_order_id': order.get('id'),
        'mp_payment_id': pagamento.get('id'),
        'mp_status': pagamento.get('status') or order.get('status'),
        'mp_status_detail': pagamento.get('status_detail') or order.get('status_detail'),
        'pix_ticket_url': metodo.get('ticket_url'),
        'pix_copia_cola': metodo.get('qr_code'),
        'pix_qrcode_base64': metodo.get('qr_code_base64') or metodo.get('qr_code_based64'),
    }


def status_local(status: str | None, status_detail: str | None = None) -> str:
    status = (status or '').lower()
    status_detail = (status_detail or '').lower()
    if status in ('approved', 'processed', 'paid') or status_detail in ('accredited', 'paid'):
        return 'pago'
    if status in ('rejected', 'cancelled', 'canceled') or status_detail in ('expired', 'rejected'):
        return 'recusado'
    if status in ('expired',):
        return 'expirado'
    return 'aguardando_pix'


def criar_pix_order(pedido_id: int, total: float, descricao: str, email: str) -> dict:
    valor = f'{float(total):.2f}'
    payload = {
        'type': 'online',
        'total_amount': valor,
        'external_reference': f'aqualog-pedido-{pedido_id}',
        'processing_mode': 'automatic',
        'transactions': {
            'payments': [{
                'amount': valor,
                'payment_method': {
                    'id': 'pix',
                    'type': 'bank_transfer',
                },
                'expiration_time': 'PT30M',
            }]
        },
        'payer': {
            'email': email,
        },
    }
    dados = _dados_pix(_request('POST', '/v1/orders', payload))
    dados['pagamento_status'] = status_local(dados.get('mp_status'), dados.get('mp_status_detail'))
    return dados


def consultar_pix_order(mp_order_id: str) -> dict:
    dados = _dados_pix(_request('GET', f'/v1/orders/{mp_order_id}'))
    dados['pagamento_status'] = status_local(dados.get('mp_status'), dados.get('mp_status_detail'))
    return dados
