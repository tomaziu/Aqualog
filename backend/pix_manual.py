import base64
import re
import unicodedata
from io import BytesIO

import qrcode


def _campo(id_campo: str, valor: str) -> str:
    valor = str(valor or '')
    return f'{id_campo}{len(valor):02d}{valor}'


def _limpar_texto(valor: str, limite: int) -> str:
    texto = unicodedata.normalize('NFKD', str(valor or ''))
    texto = ''.join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r'[^A-Za-z0-9 ]+', '', texto).upper().strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto[:limite] or 'AQUALOG'


def _crc16_ccitt(payload: str) -> str:
    crc = 0xFFFF
    for char in payload.encode('utf-8'):
        crc ^= char << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f'{crc:04X}'


def gerar_payload_pix(chave: str, valor: float, nome: str, cidade: str = 'CAXIAS', txid: str = 'AQUALOG') -> str:
    chave = str(chave or '').strip()
    if not chave:
        return ''

    merchant_account = (
        _campo('00', 'br.gov.bcb.pix') +
        _campo('01', chave) +
        _campo('02', _limpar_texto(txid, 30))
    )
    additional_data = _campo('05', _limpar_texto(txid, 25))
    payload = (
        _campo('00', '01') +
        _campo('01', '12') +
        _campo('26', merchant_account) +
        _campo('52', '0000') +
        _campo('53', '986') +
        _campo('54', f'{float(valor or 0):.2f}') +
        _campo('58', 'BR') +
        _campo('59', _limpar_texto(nome, 25)) +
        _campo('60', _limpar_texto(cidade, 15)) +
        _campo('62', additional_data)
    )
    payload_crc = payload + '6304'
    return payload_crc + _crc16_ccitt(payload_crc)


def gerar_qrcode_base64(texto: str) -> str:
    if not texto:
        return ''
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def gerar_pix_manual(chave: str, valor: float, nome: str, cidade: str = 'CAXIAS', txid: str = 'AQUALOG') -> dict:
    payload = gerar_payload_pix(chave, valor, nome, cidade, txid)
    if not payload:
        return {'pix_copia_cola': None, 'pix_qrcode_base64': None}
    return {
        'pix_copia_cola': payload,
        'pix_qrcode_base64': gerar_qrcode_base64(payload),
    }
