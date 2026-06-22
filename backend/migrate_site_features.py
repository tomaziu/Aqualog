"""Migração idempotente para recursos do site: Pix, suporte e sessão de pedidos."""
from database import get_connection
from delivery_code import gerar_codigo_entrega


def coluna_existe(cur, tabela: str, coluna: str) -> bool:
    cur.execute("""
        SELECT COUNT(*) total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
    """, (tabela, coluna))
    return bool(cur.fetchone()['total'])


def adicionar_coluna(cur, tabela: str, coluna: str, definicao: str):
    if not coluna_existe(cur, tabela, coluna):
        cur.execute(f'ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}')
        print(f'OK - coluna criada: {tabela}.{coluna}')


def indice_existe(cur, tabela: str, indice: str) -> bool:
    cur.execute("""
        SELECT COUNT(*) total
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND INDEX_NAME = %s
    """, (tabela, indice))
    return bool(cur.fetchone()['total'])


def adicionar_indice(cur, tabela: str, indice: str, definicao: str):
    if not indice_existe(cur, tabela, indice):
        cur.execute(f'ALTER TABLE {tabela} ADD INDEX {indice} {definicao}')
        print(f'OK - índice criado: {tabela}.{indice}')


con = get_connection()
cur = con.cursor(dictionary=True)

adicionar_coluna(cur, 'pedidos', 'codigo_entrega', 'VARCHAR(6) NULL AFTER status')
adicionar_coluna(cur, 'pedidos', 'pagamento_status', "VARCHAR(30) NOT NULL DEFAULT 'nao_aplicavel' AFTER forma_pagamento")
adicionar_coluna(cur, 'pedidos', 'confirmacao_status', "VARCHAR(30) NOT NULL DEFAULT 'aguardando_confirmacao' AFTER pagamento_status")
adicionar_coluna(cur, 'pedidos', 'mp_order_id', 'VARCHAR(80) NULL AFTER pagamento_status')
adicionar_coluna(cur, 'pedidos', 'mp_payment_id', 'VARCHAR(80) NULL AFTER mp_order_id')
adicionar_coluna(cur, 'pedidos', 'pix_copia_cola', 'TEXT NULL AFTER mp_payment_id')
adicionar_coluna(cur, 'pedidos', 'pix_qrcode_base64', 'LONGTEXT NULL AFTER pix_copia_cola')
adicionar_coluna(cur, 'pedidos', 'pix_ticket_url', 'TEXT NULL AFTER pix_qrcode_base64')
adicionar_coluna(cur, 'pedidos', 'carrinho_hash', 'VARCHAR(64) NULL AFTER pix_ticket_url')
adicionar_coluna(cur, 'pedidos', 'cupom_codigo', 'VARCHAR(40) NULL AFTER carrinho_hash')
adicionar_coluna(cur, 'pedidos', 'desconto_percentual', 'DECIMAL(5,2) NOT NULL DEFAULT 0 AFTER cupom_codigo')
adicionar_coluna(cur, 'pedidos', 'desconto_valor', 'DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER desconto_percentual')
adicionar_coluna(cur, 'pedidos', 'motivo_cancelamento', 'VARCHAR(255) NULL AFTER desconto_valor')
adicionar_indice(cur, 'pedidos', 'idx_pedido_pagamento', '(pagamento_status)')
adicionar_indice(cur, 'pedidos', 'idx_pedido_confirmacao', '(confirmacao_status)')
adicionar_indice(cur, 'pedidos', 'idx_pedido_carrinho', '(carrinho_hash)')
adicionar_indice(cur, 'pedidos', 'idx_pedido_cupom', '(cupom_codigo)')
adicionar_coluna(cur, 'clientes', 'numero_casa', 'VARCHAR(20) NULL AFTER endereco')
adicionar_coluna(cur, 'produtos', 'estoque_minimo', 'INT NOT NULL DEFAULT 5 AFTER estoque')
adicionar_coluna(cur, 'produtos', 'ativo', 'TINYINT(1) NOT NULL DEFAULT 1 AFTER estoque_minimo')
adicionar_indice(cur, 'produtos', 'idx_produto_ativo', '(ativo)')

try:
    cur.execute("ALTER TABLE pedidos MODIFY status VARCHAR(30) DEFAULT 'recebido'")
    print('OK - pedidos.status aceita status detalhados')
except Exception as exc:
    print(f'Aviso - não foi possível ajustar pedidos.status: {exc}')

cur.execute("""
    CREATE TABLE IF NOT EXISTS pedido_itens (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pedido_id INT NOT NULL,
        produto_id INT NOT NULL,
        quantidade INT NOT NULL,
        preco_unitario DECIMAL(10,2) NOT NULL,
        subtotal DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT,
        INDEX idx_pedido_item_pedido (pedido_id),
        INDEX idx_pedido_item_produto (produto_id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")
print('OK - tabela pedido_itens pronta')

cur.execute("""
    CREATE TABLE IF NOT EXISTS configuracoes (
        chave VARCHAR(80) PRIMARY KEY,
        valor TEXT,
        atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")
print('OK - tabela configuracoes pronta')

for chave, valor in {
    'nome_loja': 'ÁquaLog',
    'subtitulo_loja': 'Pedido online da distribuidora',
    'aviso_cliente': '',
    'pix_chave': '',
    'estoque_minimo_padrao': '5',
    'loja_aberta': '1',
    'som_novo_pedido': '1',
}.items():
    cur.execute('INSERT IGNORE INTO configuracoes (chave, valor) VALUES (%s, %s)', (chave, valor))

cur.execute("DELETE FROM configuracoes WHERE chave IN ('horario_abertura', 'horario_fechamento')")

cur.execute("""
    CREATE TABLE IF NOT EXISTS cupons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        codigo VARCHAR(40) NOT NULL UNIQUE,
        percentual DECIMAL(5,2) NOT NULL,
        ativo TINYINT(1) NOT NULL DEFAULT 1,
        validade_inicio DATE NULL,
        validade_fim DATE NULL,
        valor_minimo DECIMAL(10,2) NOT NULL DEFAULT 0,
        limite_usos INT NULL,
        usos INT NOT NULL DEFAULT 0,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_cupom_codigo (codigo),
        INDEX idx_cupom_ativo (ativo),
        INDEX idx_cupom_validade (validade_inicio, validade_fim)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")
adicionar_coluna(cur, 'cupons', 'validade_inicio', 'DATE NULL AFTER ativo')
adicionar_coluna(cur, 'cupons', 'validade_fim', 'DATE NULL AFTER validade_inicio')
adicionar_coluna(cur, 'cupons', 'valor_minimo', 'DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER validade_fim')
adicionar_coluna(cur, 'cupons', 'limite_usos', 'INT NULL AFTER valor_minimo')
adicionar_coluna(cur, 'cupons', 'usos', 'INT NOT NULL DEFAULT 0 AFTER limite_usos')
adicionar_indice(cur, 'cupons', 'idx_cupom_validade', '(validade_inicio, validade_fim)')
print('OK - tabela cupons pronta')

cur.execute("""
    CREATE TABLE IF NOT EXISTS suporte_mensagens (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pedido_id INT NOT NULL,
        cliente_id INT NOT NULL,
        autor ENUM('cliente', 'admin') NOT NULL,
        mensagem TEXT NOT NULL,
        arquivo_nome VARCHAR(120),
        arquivo_conteudo LONGTEXT,
        lida TINYINT(1) DEFAULT 0,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
        INDEX idx_suporte_pedido (pedido_id),
        INDEX idx_suporte_lida (autor, lida),
        INDEX idx_suporte_data (criado_em)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")
adicionar_coluna(cur, 'suporte_mensagens', 'arquivo_nome', 'VARCHAR(120) NULL AFTER mensagem')
adicionar_coluna(cur, 'suporte_mensagens', 'arquivo_conteudo', 'LONGTEXT NULL AFTER arquivo_nome')
print('OK - tabela suporte_mensagens pronta')

cur.execute("""
    CREATE TABLE IF NOT EXISTS pedido_comprovantes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pedido_id INT NOT NULL,
        cliente_id INT NOT NULL,
        arquivo_nome VARCHAR(120),
        conteudo LONGTEXT NOT NULL,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
        INDEX idx_comprovante_pedido (pedido_id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")
print('OK - tabela pedido_comprovantes pronta')

cur.execute("""
    CREATE TABLE IF NOT EXISTS estoque_movimentacoes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        produto_id INT NOT NULL,
        pedido_id INT NULL,
        tipo VARCHAR(30) NOT NULL,
        quantidade INT NOT NULL,
        estoque_anterior INT NULL,
        estoque_novo INT NULL,
        observacao VARCHAR(255),
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE SET NULL,
        INDEX idx_estoque_produto (produto_id),
        INDEX idx_estoque_pedido (pedido_id)
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")
print('OK - tabela estoque_movimentacoes pronta')

cur.execute("UPDATE pedidos SET pagamento_status='aguardando_pix' WHERE LOWER(forma_pagamento)='pix' AND pagamento_status='nao_aplicavel'")
cur.execute('UPDATE produtos SET ativo=1 WHERE ativo IS NULL')
cur.execute("""
    INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
    SELECT p.id, p.produto_id, p.quantidade, pr.preco, pr.preco * p.quantidade
    FROM pedidos p
    JOIN produtos pr ON pr.id = p.produto_id
    WHERE NOT EXISTS (
        SELECT 1 FROM pedido_itens pi WHERE pi.pedido_id = p.id
    )
""")
cur.execute("""
    UPDATE pedidos
    SET carrinho_hash = SHA2(CONCAT(produto_id, ':', quantidade), 256)
    WHERE carrinho_hash IS NULL OR carrinho_hash = ''
""")
cur.execute("""UPDATE pedidos
               SET confirmacao_status='aguardando_pagamento'
               WHERE LOWER(forma_pagamento)='pix'
                 AND pagamento_status <> 'pago'
                 AND confirmacao_status <> 'confirmado'""")
cur.execute("""UPDATE pedidos
               SET confirmacao_status='confirmado'
               WHERE (LOWER(forma_pagamento) <> 'pix' OR pagamento_status='pago')
                 AND confirmacao_status='aguardando_confirmacao'""")
cur.execute("""UPDATE pedidos
               SET entregador_id=NULL, status='recebido'
               WHERE confirmacao_status <> 'confirmado'
                 AND status NOT IN ('entregue', 'cancelado')""")
cur.execute("""UPDATE entregadores e
               SET status='disponivel'
               WHERE NOT EXISTS (
                   SELECT 1 FROM pedidos p
                   WHERE p.entregador_id=e.id
                     AND p.status NOT IN ('entregue', 'cancelado')
               )""")
cur.execute("SELECT id, endereco FROM clientes WHERE (numero_casa IS NULL OR numero_casa='') AND endereco LIKE '%,%'")
for row in cur.fetchall():
    rua, numero = str(row['endereco']).split(',', 1)
    cur.execute('UPDATE clientes SET endereco=%s, numero_casa=%s WHERE id=%s',
                (rua.strip(), numero.strip()[:20], row['id']))
cur.execute("SELECT id FROM pedidos WHERE codigo_entrega IS NULL OR codigo_entrega=''")
for row in cur.fetchall():
    cur.execute('UPDATE pedidos SET codigo_entrega=%s WHERE id=%s', (gerar_codigo_entrega(), row['id']))
cur.execute("""UPDATE cupons c
               SET usos = (
                   SELECT COUNT(*)
                   FROM pedidos p
                   WHERE p.cupom_codigo = c.codigo
                     AND p.status <> 'cancelado'
               )""")

con.commit()
cur.close()
con.close()
print('Migração concluída.')
