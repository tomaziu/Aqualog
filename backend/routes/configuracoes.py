import os
from fastapi import APIRouter, Depends
from auth import get_admin_user
from database import get_connection
from models import ConfiguracoesLoja

router = APIRouter()

CONFIG_PADRAO = {
    'nome_loja': 'ÁquaLog',
    'subtitulo_loja': 'Pedido online da distribuidora',
    'aviso_cliente': '',
    'pix_chave': os.getenv('PIX_CHAVE', ''),
    'estoque_minimo_padrao': '5',
    'loja_aberta': '1',
    'som_novo_pedido': '1',
}


def _garantir_configuracoes(cur):
    for chave, valor in CONFIG_PADRAO.items():
        cur.execute('INSERT IGNORE INTO configuracoes (chave, valor) VALUES (%s, %s)', (chave, str(valor)))


def _ler_configuracoes(cur):
    _garantir_configuracoes(cur)
    cur.execute('SELECT chave, valor FROM configuracoes')
    dados = {
        row['chave']: row['valor']
        for row in (cur.fetchall() or [])
        if isinstance(row, dict) and 'chave' in row
    }

    def booleano(chave: str, padrao: bool = True) -> bool:
        valor = str(dados.get(chave, CONFIG_PADRAO.get(chave, '1' if padrao else '0'))).strip().lower()
        return valor in ('1', 'true', 'sim', 'yes', 'on')

    return {
        'nome_loja': dados.get('nome_loja') or CONFIG_PADRAO['nome_loja'],
        'subtitulo_loja': dados.get('subtitulo_loja') or CONFIG_PADRAO['subtitulo_loja'],
        'aviso_cliente': dados.get('aviso_cliente') or '',
        'pix_chave': dados.get('pix_chave') or CONFIG_PADRAO['pix_chave'],
        'estoque_minimo_padrao': int(dados.get('estoque_minimo_padrao') or CONFIG_PADRAO['estoque_minimo_padrao']),
        'loja_aberta': booleano('loja_aberta'),
        'som_novo_pedido': booleano('som_novo_pedido'),
    }


@router.get('/configuracoes')
def obter_configuracoes(admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    dados = _ler_configuracoes(cur)
    con.commit(); cur.close(); con.close()
    return {'success': True, 'data': dados}


@router.put('/configuracoes')
def salvar_configuracoes(config: ConfiguracoesLoja, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    dados = config.model_dump() if hasattr(config, 'model_dump') else config.dict()
    for chave, valor in dados.items():
        cur.execute('''INSERT INTO configuracoes (chave, valor)
                       VALUES (%s, %s)
                       ON DUPLICATE KEY UPDATE valor=VALUES(valor)''',
                    (chave, '' if valor is None else str(valor)))
    con.commit(); cur.close(); con.close()
    return {'success': True, 'data': {'mensagem': 'Configurações salvas'}}


@router.get('/site/configuracoes')
def configuracoes_publicas():
    con = get_connection(); cur = con.cursor(dictionary=True)
    dados = _ler_configuracoes(cur)
    con.commit(); cur.close(); con.close()
    return {'success': True, 'data': dados}
