from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_connection
from models import Cliente
from auth import get_admin_user
import mysql.connector.errors

router = APIRouter()


@router.get('/clientes')
def listar(page: int = Query(1, ge=1), per_page: int = Query(200, ge=1, le=500), admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT COUNT(*) total FROM clientes')
    total = cur.fetchone()['total']
    offset = (page - 1) * per_page
    cur.execute('SELECT * FROM clientes ORDER BY id DESC LIMIT %s OFFSET %s', (per_page, offset))
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados, 'total': total, 'page': page, 'per_page': per_page}


@router.post('/clientes')
def criar(cliente: Cliente, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    cur.execute('INSERT INTO clientes (nome, telefone, endereco, numero_casa, bairro, referencia) VALUES (%s,%s,%s,%s,%s,%s)',
                (cliente.nome, cliente.telefone, cliente.endereco, cliente.numero_casa, cliente.bairro, cliente.referencia))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'success': True, 'data': {'id': novo_id, 'mensagem': 'Cliente cadastrado'}}


@router.put('/clientes/{id}')
def editar(id: int, cliente: Cliente, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    cur.execute('UPDATE clientes SET nome=%s, telefone=%s, endereco=%s, numero_casa=%s, bairro=%s, referencia=%s WHERE id=%s',
                (cliente.nome, cliente.telefone, cliente.endereco, cliente.numero_casa, cliente.bairro, cliente.referencia, id))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Cliente não encontrado')
    return {'success': True, 'data': {'mensagem': 'Cliente atualizado'}}


@router.delete('/clientes/{id}')
def excluir(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('DELETE FROM clientes WHERE id=%s', (id,))
        con.commit(); linhas = cur.rowcount
        if linhas == 0: raise HTTPException(404, 'Cliente não encontrado')
        return {'success': True, 'data': {'mensagem': 'Cliente excluído'}}
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(400, 'Este cliente possui pedidos. Exclua os pedidos primeiro.')
    finally:
        cur.close(); con.close()
