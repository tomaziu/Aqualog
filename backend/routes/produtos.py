from fastapi import APIRouter, HTTPException
from database import get_connection
from models import Produto
import mysql.connector.errors

router = APIRouter()


@router.get('/produtos')
def listar():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT * FROM produtos ORDER BY id DESC')
    dados = cur.fetchall(); cur.close(); con.close()
    return dados


@router.post('/produtos')
def criar(produto: Produto):
    con = get_connection(); cur = con.cursor()
    cur.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (%s,%s,%s)',
                (produto.nome, produto.preco, produto.estoque))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'id': novo_id, 'mensagem': 'Produto cadastrado'}


@router.put('/produtos/{id}')
def editar(id: int, produto: Produto):
    con = get_connection(); cur = con.cursor()
    cur.execute('UPDATE produtos SET nome=%s, preco=%s, estoque=%s WHERE id=%s',
                (produto.nome, produto.preco, produto.estoque, id))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Produto não encontrado')
    return {'mensagem': 'Produto atualizado'}


@router.delete('/produtos/{id}')
def excluir(id: int):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('DELETE FROM produtos WHERE id=%s', (id,))
        con.commit(); linhas = cur.rowcount
        if linhas == 0: raise HTTPException(404, 'Produto não encontrado')
        return {'mensagem': 'Produto excluído'}
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(400, 'Este produto está em pedidos. Exclua os pedidos primeiro.')
    finally:
        cur.close(); con.close()
