from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_connection
from models import Produto
from auth import get_admin_user

router = APIRouter()


@router.get('/produtos')
def listar(page: int = Query(1, ge=1), per_page: int = Query(200, ge=1, le=500), admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT COUNT(*) total FROM produtos')
    total = cur.fetchone()['total']
    offset = (page - 1) * per_page
    cur.execute('''SELECT *,
                          CASE WHEN estoque <= estoque_minimo THEN 1 ELSE 0 END AS estoque_baixo
                   FROM produtos
                   ORDER BY ativo DESC, estoque_baixo DESC, id DESC
                   LIMIT %s OFFSET %s''', (per_page, offset))
    dados = cur.fetchall(); cur.close(); con.close()
    return {'success': True, 'data': dados, 'total': total, 'page': page, 'per_page': per_page}


@router.post('/produtos')
def criar(produto: Produto, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor()
    cur.execute('''INSERT INTO produtos (nome, preco, estoque, estoque_minimo, ativo)
                   VALUES (%s,%s,%s,%s,%s)''',
                (produto.nome, produto.preco, produto.estoque, produto.estoque_minimo, 1 if produto.ativo else 0))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'success': True, 'data': {'id': novo_id, 'mensagem': 'Produto cadastrado'}}


@router.put('/produtos/{id}')
def editar(id: int, produto: Produto, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT estoque FROM produtos WHERE id=%s', (id,))
    atual = cur.fetchone()
    if not atual:
        cur.close(); con.close()
        raise HTTPException(404, 'Produto não encontrado')
    cur.execute('''UPDATE produtos
                   SET nome=%s, preco=%s, estoque=%s, estoque_minimo=%s, ativo=%s
                   WHERE id=%s''',
                (produto.nome, produto.preco, produto.estoque, produto.estoque_minimo, 1 if produto.ativo else 0, id))
    if int(atual.get('estoque') or 0) != int(produto.estoque):
        cur.execute('''INSERT INTO estoque_movimentacoes
                       (produto_id, pedido_id, tipo, quantidade, estoque_anterior, estoque_novo, observacao)
                       VALUES (%s, NULL, 'ajuste_manual', %s, %s, %s, 'Ajuste manual no cadastro de produto')''',
                    (id, int(produto.estoque) - int(atual.get('estoque') or 0), int(atual.get('estoque') or 0), int(produto.estoque)))
    con.commit(); cur.close(); con.close()
    return {'success': True, 'data': {'mensagem': 'Produto atualizado'}}


@router.delete('/produtos/{id}')
def excluir(id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id FROM produtos WHERE id=%s', (id,))
    if not cur.fetchone():
        cur.close(); con.close()
        raise HTTPException(404, 'Produto não encontrado')
    cur.execute('UPDATE produtos SET ativo=0 WHERE id=%s', (id,))
    con.commit(); cur.close(); con.close()
    return {'success': True, 'data': {'mensagem': 'Produto inativado'}}
