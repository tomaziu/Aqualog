from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from database import get_connection
from models import Entregador, EntregadorUpdate, EntregadorLogin
from auth import criar_token, hash_senha, verificar_senha, get_admin_user, get_entregador_user
import mysql.connector.errors

router = APIRouter()


@router.get('/entregadores')
def listar(admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id, nome, telefone, veiculo, status, codigo_acesso FROM entregadores ORDER BY id DESC')
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados}


@router.post('/entregadores')
def criar(entregador: Entregador, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('SELECT codigo_acesso FROM entregadores')
        for row in cur.fetchall():
            stored = row[0] or ''
            if stored.startswith('$2b$') or stored.startswith('$2a$'):
                if verificar_senha(entregador.codigo_acesso, stored):
                    cur.close(); con.close()
                    raise HTTPException(400, 'Já existe um entregador com esse código de acesso.')
            else:
                if entregador.codigo_acesso == stored:
                    cur.close(); con.close()
                    raise HTTPException(400, 'Já existe um entregador com esse código de acesso.')
        codigo_hash = hash_senha(entregador.codigo_acesso)
        cur.execute('INSERT INTO entregadores (nome, telefone, veiculo, codigo_acesso, status) VALUES (%s,%s,%s,%s,%s)',
                    (entregador.nome, entregador.telefone, entregador.veiculo, codigo_hash, entregador.status))
        con.commit(); novo_id = cur.lastrowid
        return {'success': True, 'data': {'id': novo_id, 'mensagem': 'Entregador cadastrado'}}
    finally:
        cur.close(); con.close()


@router.put('/entregadores/{id}')
def editar(id: int, entregador: EntregadorUpdate, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('SELECT id FROM entregadores WHERE id=%s', (id,))
        if not cur.fetchone():
            cur.close(); con.close()
            raise HTTPException(404, 'Entregador não encontrado')
        if entregador.codigo_acesso and len(entregador.codigo_acesso) >= 4:
            cur.execute('SELECT id, codigo_acesso FROM entregadores WHERE id != %s', (id,))
            for row in cur.fetchall():
                stored = row[1] or ''
                if stored.startswith('$2b$') or stored.startswith('$2a$'):
                    if verificar_senha(entregador.codigo_acesso, stored):
                        cur.close(); con.close()
                        raise HTTPException(400, 'Já existe um entregador com esse código de acesso.')
                else:
                    if entregador.codigo_acesso == stored:
                        cur.close(); con.close()
                        raise HTTPException(400, 'Já existe um entregador com esse código de acesso.')
            codigo_hash = hash_senha(entregador.codigo_acesso)
            cur.execute('UPDATE entregadores SET nome=%s, telefone=%s, veiculo=%s, codigo_acesso=%s, status=%s WHERE id=%s',
                        (entregador.nome, entregador.telefone, entregador.veiculo, codigo_hash, entregador.status, id))
        else:
            cur.execute('UPDATE entregadores SET nome=%s, telefone=%s, veiculo=%s, status=%s WHERE id=%s',
                        (entregador.nome, entregador.telefone, entregador.veiculo, entregador.status, id))
        con.commit()
        return {'success': True, 'data': {'mensagem': 'Entregador atualizado'}}
    finally:
        cur.close(); con.close()


@router.delete('/entregadores/{id}')
def excluir(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('DELETE FROM entregadores WHERE id=%s', (id,))
        con.commit(); linhas = cur.rowcount
        if linhas == 0: raise HTTPException(404, 'Entregador não encontrado')
        return {'success': True, 'data': {'mensagem': 'Entregador excluído'}}
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(400, 'Este entregador está vinculado a pedidos. Reatribua os pedidos primeiro.')
    finally:
        cur.close(); con.close()


@router.post('/entregadores/login')
def login(login: EntregadorLogin):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id, nome, veiculo, status, codigo_acesso FROM entregadores WHERE status IS NOT NULL')
    todos = cur.fetchall(); cur.close(); con.close()
    for e in todos:
        stored = e['codigo_acesso'] or ''
        if stored.startswith('$2b$') or stored.startswith('$2a$'):
            if verificar_senha(login.codigo_acesso, stored):
                token = criar_token({'tipo': 'entregador', 'id': e['id'], 'nome': e['nome']})
                return {'access_token': token, 'tipo': 'entregador', 'id': e['id'], 'nome': e['nome'], 'veiculo': e['veiculo']}
        else:
            if login.codigo_acesso == stored:
                token = criar_token({'tipo': 'entregador', 'id': e['id'], 'nome': e['nome']})
                return {'access_token': token, 'tipo': 'entregador', 'id': e['id'], 'nome': e['nome'], 'veiculo': e['veiculo']}
    raise HTTPException(401, 'Código de acesso inválido')


@router.get('/entregadores/{id}/pedidos')
def pedidos_entregador(id: int, status: Optional[str] = None, user=Depends(get_entregador_user)):
    if user.get('id') != id:
        raise HTTPException(403, 'Você só pode ver seus próprios pedidos')
    con = get_connection(); cur = con.cursor(dictionary=True)
    sql = '''SELECT p.id, p.status, p.data_criacao, c.nome AS cliente,
                    c.endereco, c.numero_casa, c.bairro, c.referencia, c.telefone,
                    COALESCE((
                        SELECT GROUP_CONCAT(CONCAT(pri.nome, ' x', pi.quantidade) ORDER BY pi.id SEPARATOR ', ')
                        FROM pedido_itens pi
                        JOIN produtos pri ON pri.id = pi.produto_id
                        WHERE pi.pedido_id = p.id
                    ), CONCAT(pr.nome, ' x', p.quantidade)) AS produto,
                    COALESCE((
                        SELECT SUM(pi.subtotal)
                        FROM pedido_itens pi
                        WHERE pi.pedido_id = p.id
                    ), pr.preco * p.quantidade) AS total,
                    pr.preco, p.quantidade, p.forma_pagamento,
                    p.pagamento_status, p.confirmacao_status
             FROM pedidos p
             JOIN clientes c ON c.id = p.cliente_id
             JOIN produtos pr ON pr.id = p.produto_id
             WHERE p.entregador_id = %s
               AND p.confirmacao_status = 'confirmado' '''
    params = [id]
    if status:
        sql += ' AND p.status = %s'
        params.append(status)
    sql += ' ORDER BY p.data_criacao DESC'
    cur.execute(sql, params)
    dados = cur.fetchall(); cur.close(); con.close()
    return dados
