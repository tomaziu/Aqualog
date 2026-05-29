from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

class AdminLogin(BaseModel):
    senha: str
from typing import Optional
import os
from pathlib import Path
from database import get_connection
import mysql.connector.errors

app = FastAPI(title='ÁquaLog API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class Cliente(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    endereco: str = Field(min_length=3)
    bairro: str = Field(min_length=2)
    referencia: Optional[str] = None

class Entregador(BaseModel):
    nome: str = Field(min_length=3)
    telefone: str = Field(min_length=8)
    veiculo: str = Field(min_length=2)
    codigo_acesso: str = Field(min_length=4)
    status: str = 'disponivel'

class EntregadorLogin(BaseModel):
    codigo_acesso: str

class Produto(BaseModel):
    nome: str = Field(min_length=2)
    preco: float = Field(gt=0)
    estoque: int = Field(ge=0)

class Pedido(BaseModel):
    cliente_id: int
    entregador_id: Optional[int] = None
    produto_id: int
    quantidade: int = Field(gt=0)
    forma_pagamento: str = Field(min_length=2)
    status: str = 'recebido'

# Clientes
@app.get('/clientes')
def listar_clientes():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT * FROM clientes ORDER BY id DESC')
    dados = cur.fetchall(); cur.close(); con.close()
    return dados

@app.post('/clientes')
def criar_cliente(cliente: Cliente):
    con = get_connection(); cur = con.cursor()
    cur.execute('INSERT INTO clientes (nome, telefone, endereco, bairro, referencia) VALUES (%s,%s,%s,%s,%s)',
                (cliente.nome, cliente.telefone, cliente.endereco, cliente.bairro, cliente.referencia))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'id': novo_id, 'mensagem': 'Cliente cadastrado'}

@app.put('/clientes/{id}')
def editar_cliente(id: int, cliente: Cliente):
    con = get_connection(); cur = con.cursor()
    cur.execute('UPDATE clientes SET nome=%s, telefone=%s, endereco=%s, bairro=%s, referencia=%s WHERE id=%s',
                (cliente.nome, cliente.telefone, cliente.endereco, cliente.bairro, cliente.referencia, id))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Cliente não encontrado')
    return {'mensagem': 'Cliente atualizado'}

@app.delete('/clientes/{id}')
def excluir_cliente(id: int):
    con = get_connection(); cur = con.cursor()
    try:
        cur.execute('DELETE FROM clientes WHERE id=%s', (id,))
        con.commit(); linhas = cur.rowcount
        if linhas == 0: raise HTTPException(404, 'Cliente não encontrado')
        return {'mensagem': 'Cliente excluído'}
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(400, 'Este cliente possui pedidos. Exclua os pedidos primeiro.')
    finally:
        cur.close(); con.close()

# Admin
@app.post('/admin/login')
def admin_login(login: AdminLogin):
    if login.senha != os.getenv('ADMIN_PASSWORD', 'admin123'):
        raise HTTPException(401, 'Senha incorreta')
    return {'mensagem': 'OK'}

# Entregadores
@app.get('/entregadores')
def listar_entregadores():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT * FROM entregadores ORDER BY id DESC')
    dados = cur.fetchall(); cur.close(); con.close()
    return dados

@app.post('/entregadores')
def criar_entregador(entregador: Entregador):
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

@app.put('/entregadores/{id}')
def editar_entregador(id: int, entregador: Entregador):
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

@app.delete('/entregadores/{id}')
def excluir_entregador(id: int):
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

@app.post('/entregadores/login')
def login_entregador(login: EntregadorLogin):
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT id, nome, veiculo, status FROM entregadores WHERE codigo_acesso=%s', (login.codigo_acesso,))
    dado = cur.fetchone(); cur.close(); con.close()
    if not dado: raise HTTPException(401, 'Código de acesso inválido')
    return dado

@app.get('/entregadores/{id}/pedidos')
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

# Produtos
@app.get('/produtos')
def listar_produtos():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('SELECT * FROM produtos ORDER BY id DESC')
    dados = cur.fetchall(); cur.close(); con.close()
    return dados

@app.post('/produtos')
def criar_produto(produto: Produto):
    con = get_connection(); cur = con.cursor()
    cur.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (%s,%s,%s)',
                (produto.nome, produto.preco, produto.estoque))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'id': novo_id, 'mensagem': 'Produto cadastrado'}


@app.put('/produtos/{id}')
def editar_produto(id: int, produto: Produto):
    con = get_connection(); cur = con.cursor()
    cur.execute('UPDATE produtos SET nome=%s, preco=%s, estoque=%s WHERE id=%s',
                (produto.nome, produto.preco, produto.estoque, id))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Produto não encontrado')
    return {'mensagem': 'Produto atualizado'}

@app.delete('/produtos/{id}')
def excluir_produto(id: int):
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

# Pedidos
@app.get('/pedidos')
def listar_pedidos():
    con = get_connection(); cur = con.cursor(dictionary=True)
    cur.execute('''SELECT p.*, c.nome AS cliente, c.bairro, e.nome AS entregador, pr.nome AS produto
                   FROM pedidos p
                   JOIN clientes c ON c.id = p.cliente_id
                   LEFT JOIN entregadores e ON e.id = p.entregador_id
                   JOIN produtos pr ON pr.id = p.produto_id
                   ORDER BY p.id DESC''')
    dados = cur.fetchall(); cur.close(); con.close()
    return dados

@app.post('/pedidos')
def criar_pedido(pedido: Pedido):
    con = get_connection(); cur = con.cursor()
    cur.execute('''INSERT INTO pedidos (cliente_id, entregador_id, produto_id, quantidade, forma_pagamento, status)
                   VALUES (%s,%s,%s,%s,%s,%s)''',
                (pedido.cliente_id, pedido.entregador_id, pedido.produto_id, pedido.quantidade, pedido.forma_pagamento, pedido.status))
    cur.execute('UPDATE produtos SET estoque = estoque - %s WHERE id=%s AND estoque >= %s',
                (pedido.quantidade, pedido.produto_id, pedido.quantidade))
    con.commit(); novo_id = cur.lastrowid; cur.close(); con.close()
    return {'id': novo_id, 'mensagem': 'Pedido criado'}

@app.patch('/pedidos/{id}/status')
def atualizar_status(id: int, status: str):
    if status not in ['recebido','em_preparo','saiu_para_entrega','entregue','cancelado']:
        raise HTTPException(400, 'Status inválido')
    entrega = ', data_entrega = NOW()' if status == 'entregue' else ''
    con = get_connection(); cur = con.cursor()
    cur.execute(f'UPDATE pedidos SET status=%s {entrega} WHERE id=%s', (status, id))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Pedido não encontrado')
    return {'mensagem': 'Status atualizado'}

@app.delete('/pedidos/{id}')
def excluir_pedido(id: int):
    con = get_connection(); cur = con.cursor()
    cur.execute('DELETE FROM pedidos WHERE id=%s', (id,))
    con.commit(); linhas = cur.rowcount; cur.close(); con.close()
    if linhas == 0: raise HTTPException(404, 'Pedido não encontrado')
    return {'mensagem': 'Pedido excluído'}

@app.get('/dashboard')
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

app.mount('/', StaticFiles(directory=str(Path(__file__).resolve().parent.parent / 'frontend'), html=True))

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', '8000'))
    uvicorn.run('main:app', host='0.0.0.0', port=port)
