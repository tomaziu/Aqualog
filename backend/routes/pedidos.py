from fastapi import APIRouter, HTTPException
from database import get_connection
from models import Pedido

router = APIRouter()


@router.get('/pedidos')
def listar():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT p.*, c.nome AS cliente, c.bairro, e.nome AS entregador, pr.nome AS produto
                   FROM pedidos p
                   JOIN clientes c ON c.id = p.cliente_id
                   LEFT JOIN entregadores e ON e.id = p.entregador_id
                   JOIN produtos pr ON pr.id = p.produto_id
                   ORDER BY p.id DESC''')
    dados = cur.fetchall(); cur.close(); con.close()
    return dados


@router.post('/pedidos')
def criar(pedido: Pedido):
    con = get_connection(); cur = con.cursor()
    cur.execute('''INSERT INTO pedidos (cliente_id, entregador_id, produto_id, quantidade, forma_pagamento, status)
                   VALUES (%s,%s,%s,%s,%s,%s)''',
                (pedido.cliente_id, pedido.entregador_id, pedido.produto_id, pedido.quantidade, pedido.forma_pagamento, pedido.status))
    cur.execute('UPDATE produtos SET estoque = estoque - %s WHERE id=%s AND estoque >= %s',
                (pedido.quantidade, pedido.produto_id, pedido.quantidade))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'id': novo_id, 'mensagem': 'Pedido criado'}


@router.patch('/pedidos/{id}/status')
def atualizar_status(id: int, status: str):
    if status not in ['recebido', 'em_preparo', 'saiu_para_entrega', 'entregue', 'cancelado']:
        raise HTTPException(400, 'Status inválido')
    entrega = ', data_entrega = NOW()' if status == 'entregue' else ''
    con = get_connection(); cur = con.cursor()
    cur.execute(f'UPDATE pedidos SET status=%s {entrega} WHERE id=%s', (status, id))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Pedido não encontrado')
    return {'mensagem': 'Status atualizado'}


@router.delete('/pedidos/{id}')
def excluir(id: int):
    con = get_connection(); cur = con.cursor()
    cur.execute('DELETE FROM pedidos WHERE id=%s', (id,))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Pedido não encontrado')
    return {'mensagem': 'Pedido excluído'}


@router.get('/dashboard')
def dashboard():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) total FROM pedidos")
    total = cur.fetchone()['total']
    cur.execute("SELECT status, COUNT(*) total FROM pedidos GROUP BY status")
    por_status = cur.fetchall()
    cur.execute("SELECT ROUND(AVG(TIMESTAMPDIFF(MINUTE, data_criacao, data_entrega)), 1) tempo_medio FROM pedidos WHERE data_entrega IS NOT NULL")
    tempo = cur.fetchone()['tempo_medio'] or 0
    cur.execute("SELECT c.bairro, COUNT(*) entregas FROM pedidos p JOIN clientes c ON c.id=p.cliente_id GROUP BY c.bairro ORDER BY entregas DESC")
    rotas = cur.fetchall()
    cur.close(); con.close()
    return {'total_pedidos': total, 'por_status': por_status, 'tempo_medio_minutos': tempo, 'roteirizacao_por_bairro': rotas}
