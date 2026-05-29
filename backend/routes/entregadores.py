from typing import Optional
from fastapi import APIRouter, HTTPException
from database import get_connection
from models import Entregador, EntregadorLogin
import mysql.connector.errors

router = APIRouter()


@router.get('/entregadores')
def listar():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT * FROM entregadores ORDER BY id DESC')
    dados = cur.fetchall(); cur.close(); con.close()
    return dados


@router.post('/entregadores')
def criar(entregador: Entregador):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('INSERT INTO entregadores (nome, telefone, veiculo, codigo_acesso, status) VALUES (%s,%s,%s,%s,%s)',
                    (entregador.nome, entregador.telefone, entregador.veiculo, entregador.codigo_acesso, entregador.status))
        con.commit(); novo_id = cur.lastrowid
        return {'id': novo_id, 'mensagem': 'Entregador cadastrado'}
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(400, 'Já existe um entregador com esse código de acesso.')
    finally:
        cur.close(); con.close()


@router.put('/entregadores/{id}')
def editar(id: int, entregador: Entregador):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('UPDATE entregadores SET nome=%s, telefone=%s, veiculo=%s, codigo_acesso=%s, status=%s WHERE id=%s',
                    (entregador.nome, entregador.telefone, entregador.veiculo, entregador.codigo_acesso, entregador.status, id))
        con.commit(); linhas = cur.rowcount
        if linhas == 0: raise HTTPException(404, 'Entregador não encontrado')
        return {'mensagem': 'Entregador atualizado'}
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(400, 'Já existe um entregador com esse código de acesso.')
    finally:
        cur.close(); con.close()


@router.delete('/entregadores/{id}')
def excluir(id: int):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('DELETE FROM entregadores WHERE id=%s', (id,))
        con.commit(); linhas = cur.rowcount
        if linhas == 0: raise HTTPException(404, 'Entregador não encontrado')
        return {'mensagem': 'Entregador excluído'}
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(400, 'Este entregador está vinculado a pedidos. Reatribua os pedidos primeiro.')
    finally:
        cur.close(); con.close()


@router.post('/entregadores/login')
def login(login: EntregadorLogin):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id, nome, veiculo, status FROM entregadores WHERE codigo_acesso=%s', (login.codigo_acesso,))
    dado = cur.fetchone(); cur.close(); con.close()
    if not dado: raise HTTPException(401, 'Código de acesso inválido')
    return dado


@router.get('/entregadores/{id}/pedidos')
def pedidos_entregador(id: int, status: Optional[str] = None):
    con = get_connection(); cur = con.cursor(dictionary=True)
    sql = '''SELECT p.id, p.status, p.data_criacao, c.nome AS cliente,
                    c.endereco, c.bairro, c.referencia, c.telefone,
                    pr.nome AS produto, p.quantidade, p.forma_pagamento
             FROM pedidos p
             JOIN clientes c ON c.id = p.cliente_id
             JOIN produtos pr ON pr.id = p.produto_id
             WHERE p.entregador_id = %s'''
    params = [id]
    if status:
        sql += ' AND p.status = %s'
        params.append(status)
    sql += ' ORDER BY p.data_criacao DESC'
    cur.execute(sql, params)
    dados = cur.fetchall(); cur.close(); con.close()
    return dados
