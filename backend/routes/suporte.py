from fastapi import APIRouter, Depends, HTTPException
from auth import get_admin_user
from database import get_connection
from models import SuporteMensagem
from sse_manager import notify

router = APIRouter()


@router.get('/suporte')
def listar_threads(admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT m.pedido_id, c.nome AS cliente, c.telefone, p.status,
                          p.pagamento_status, MAX(m.criado_em) AS ultima_data,
                          SUM(CASE WHEN m.autor='cliente' AND m.lida=0 THEN 1 ELSE 0 END) AS pendentes
                   FROM suporte_mensagens m
                   JOIN pedidos p ON p.id = m.pedido_id
                   JOIN clientes c ON c.id = p.cliente_id
                   GROUP BY m.pedido_id, c.nome, c.telefone, p.status, p.pagamento_status
                   ORDER BY ultima_data DESC''')
    threads = cur.fetchall()
    for thread in threads:
        cur.execute('''SELECT mensagem, autor
                       FROM suporte_mensagens
                       WHERE pedido_id=%s
                       ORDER BY criado_em DESC, id DESC
                       LIMIT 1''', (thread['pedido_id'],))
        ultima = cur.fetchone() or {}
        thread['ultima_mensagem'] = ultima.get('mensagem', '')
        thread['ultimo_autor'] = ultima.get('autor', '')
    cur.close(); con.close()
    return {'success': True, 'data': threads}


@router.get('/suporte/{pedido_id}')
def listar_mensagens(pedido_id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT p.id AS pedido_id, c.nome AS cliente, c.telefone
                   FROM pedidos p
                   JOIN clientes c ON c.id = p.cliente_id
                   WHERE p.id=%s''', (pedido_id,))
    pedido = cur.fetchone()
    if not pedido:
        cur.close(); con.close()
        raise HTTPException(404, 'Pedido não encontrado')

    cur.execute('UPDATE suporte_mensagens SET lida=1 WHERE pedido_id=%s AND autor=%s', (pedido_id, 'cliente'))
    con.commit()

    cur.execute('''SELECT id, autor, mensagem, criado_em
                   FROM suporte_mensagens
                   WHERE pedido_id=%s
                   ORDER BY criado_em ASC, id ASC''', (pedido_id,))
    mensagens = cur.fetchall()
    cur.close(); con.close()
    return {'success': True, 'data': {'pedido': pedido, 'mensagens': mensagens}}


@router.post('/suporte/{pedido_id}')
def responder(pedido_id: int, msg: SuporteMensagem, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('SELECT cliente_id FROM pedidos WHERE id=%s', (pedido_id,))
        pedido = cur.fetchone()
        if not pedido:
            raise HTTPException(404, 'Pedido não encontrado')
        cur.execute('''INSERT INTO suporte_mensagens (pedido_id, cliente_id, autor, mensagem, lida)
                       VALUES (%s, %s, 'admin', %s, 0)''',
                    (pedido_id, pedido['cliente_id'], msg.mensagem.strip()))
        con.commit()
        notify('refresh', {'acao': 'mensagem_suporte', 'pedido_id': pedido_id, 'origem': 'admin'})
        return {'success': True, 'data': {'mensagem': 'Resposta enviada'}}
    finally:
        cur.close(); con.close()


@router.delete('/suporte/{pedido_id}')
def apagar_thread(pedido_id: int, admin=Depends(get_admin_user)):
    con = get_connection(); cur = con.cursor(dictionary=True)
    try:
        cur.execute('DELETE FROM suporte_mensagens WHERE pedido_id=%s', (pedido_id,))
        apagadas = cur.rowcount
        if not apagadas:
            raise HTTPException(404, 'Conversa de suporte não encontrada')
        con.commit()
        notify('refresh', {'acao': 'suporte_apagado', 'pedido_id': pedido_id})
        return {'success': True, 'data': {'mensagem': 'Chat apagado'}}
    finally:
        cur.close(); con.close()
