from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException

from auth import get_admin_user
from database import get_connection
from models import Cupom

router = APIRouter()


def _normalizar_codigo(codigo: str) -> str:
    return ''.join(ch for ch in str(codigo or '').strip().upper() if ch.isalnum() or ch in ('-', '_'))[:40]


def _data_cupom(valor):
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return datetime.strptime(str(valor)[:10], '%Y-%m-%d').date()


def _validar_datas(cupom: Cupom):
    inicio = _data_cupom(cupom.validade_inicio)
    fim = _data_cupom(cupom.validade_fim)
    if inicio and fim and inicio > fim:
        raise HTTPException(400, 'A data inicial do cupom não pode ser maior que a data final.')


def _validar_cupom_regras(cupom: dict, total: float):
    hoje = date.today()
    inicio = _data_cupom(cupom.get('validade_inicio'))
    fim = _data_cupom(cupom.get('validade_fim'))
    valor_minimo = float(cupom.get('valor_minimo') or 0)
    limite_usos = cupom.get('limite_usos')
    usos = int(cupom.get('usos') or 0)

    if inicio and hoje < inicio:
        raise HTTPException(404, 'Cupom ainda não está disponível')
    if fim and hoje > fim:
        raise HTTPException(404, 'Cupom expirado')
    if valor_minimo > 0 and float(total or 0) < valor_minimo:
        raise HTTPException(400, f'Cupom exige pedido mínimo de R$ {valor_minimo:.2f}')
    if limite_usos is not None and int(limite_usos) > 0 and usos >= int(limite_usos):
        raise HTTPException(404, 'Cupom atingiu o limite de usos')


@router.get('/cupons')
def listar_cupons(admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT * FROM cupons ORDER BY ativo DESC, id DESC')
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados}


@router.post('/cupons')
def criar_cupom(cupom: Cupom, admin=Depends(get_admin_user)):
    codigo = _normalizar_codigo(cupom.codigo)
    if len(codigo) < 2:
        raise HTTPException(400, 'Código do cupom inválido')
    _validar_datas(cupom)
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''INSERT INTO cupons
                   (codigo, percentual, ativo, validade_inicio, validade_fim, valor_minimo, limite_usos)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (codigo, cupom.percentual, 1 if cupom.ativo else 0, cupom.validade_inicio,
                 cupom.validade_fim, cupom.valor_minimo, cupom.limite_usos))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'success': True, 'data': {'id': novo_id, 'mensagem': 'Cupom criado'}}


@router.put('/cupons/{id}')
def editar_cupom(id: int, cupom: Cupom, admin=Depends(get_admin_user)):
    codigo = _normalizar_codigo(cupom.codigo)
    if len(codigo) < 2:
        raise HTTPException(400, 'Código do cupom inválido')
    _validar_datas(cupom)
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''UPDATE cupons
                   SET codigo=%s, percentual=%s, ativo=%s, validade_inicio=%s, validade_fim=%s,
                       valor_minimo=%s, limite_usos=%s
                   WHERE id=%s''',
                (codigo, cupom.percentual, 1 if cupom.ativo else 0, cupom.validade_inicio,
                 cupom.validade_fim, cupom.valor_minimo, cupom.limite_usos, id))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0:
        raise HTTPException(404, 'Cupom não encontrado')
    return {'success': True, 'data': {'mensagem': 'Cupom atualizado'}}


@router.delete('/cupons/{id}')
def excluir_cupom(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    cur.execute('DELETE FROM cupons WHERE id=%s', (id,))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0:
        raise HTTPException(404, 'Cupom não encontrado')
    return {'success': True, 'data': {'mensagem': 'Cupom excluído'}}


@router.get('/site/cupons/{codigo}')
def validar_cupom_publico(codigo: str, total: float = 0):
    codigo_normalizado = _normalizar_codigo(codigo)
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT codigo, percentual, ativo, validade_inicio, validade_fim,
                          valor_minimo, limite_usos, usos
                   FROM cupons WHERE codigo=%s LIMIT 1''', (codigo_normalizado,))
    cupom = cur.fetchone(); cur.close(); con.close()
    if not cupom or not cupom.get('ativo'):
        raise HTTPException(404, 'Cupom inválido ou inativo')
    _validar_cupom_regras(cupom, total)
    desconto = round(max(0, float(total or 0)) * float(cupom['percentual']) / 100, 2)
    return {'success': True, 'data': {
        'codigo': cupom['codigo'],
        'percentual': float(cupom['percentual']),
        'desconto': desconto,
        'total_com_desconto': round(max(0, float(total or 0)) - desconto, 2),
        'valor_minimo': float(cupom.get('valor_minimo') or 0),
        'validade_fim': cupom.get('validade_fim'),
    }}
