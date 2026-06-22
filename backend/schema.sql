SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS aqualog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aqualog;

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(180) NOT NULL,
    numero_casa VARCHAR(20),
    bairro VARCHAR(80) NOT NULL,
    referencia VARCHAR(180),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cliente_bairro (bairro),
    INDEX idx_cliente_nome (nome(50))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS entregadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    veiculo VARCHAR(80) NOT NULL,
    codigo_acesso VARCHAR(255) NOT NULL UNIQUE,
    status ENUM('disponivel', 'ocupado') DEFAULT 'disponivel',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entregador_status (status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    estoque INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 5,
    imagem VARCHAR(500) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_produto_nome (nome(50)),
    INDEX idx_produto_ativo (ativo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS configuracoes (
    chave VARCHAR(80) PRIMARY KEY,
    valor TEXT,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    entregador_id INT,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    forma_pagamento VARCHAR(50) NOT NULL,
    pagamento_status VARCHAR(30) NOT NULL DEFAULT 'nao_aplicavel',
    confirmacao_status VARCHAR(30) NOT NULL DEFAULT 'aguardando_confirmacao',
    mp_order_id VARCHAR(80),
    mp_payment_id VARCHAR(80),
    pix_copia_cola TEXT,
    pix_qrcode_base64 LONGTEXT,
    pix_ticket_url TEXT,
    carrinho_hash VARCHAR(64),
    cupom_codigo VARCHAR(40),
    desconto_percentual DECIMAL(5,2) NOT NULL DEFAULT 0,
    desconto_valor DECIMAL(10,2) NOT NULL DEFAULT 0,
    motivo_cancelamento VARCHAR(255),
    status VARCHAR(30) DEFAULT 'recebido',
    codigo_entrega VARCHAR(6),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_entrega DATETIME NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (entregador_id) REFERENCES entregadores(id) ON DELETE SET NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT,
    INDEX idx_pedido_cliente (cliente_id),
    INDEX idx_pedido_entregador (entregador_id),
    INDEX idx_pedido_produto (produto_id),
    INDEX idx_pedido_status (status),
    INDEX idx_pedido_pagamento (pagamento_status),
    INDEX idx_pedido_confirmacao (confirmacao_status),
    INDEX idx_pedido_carrinho (carrinho_hash),
    INDEX idx_pedido_cupom (cupom_codigo),
    INDEX idx_pedido_data (data_criacao)
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pedido_historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    status_anterior VARCHAR(30),
    status_novo VARCHAR(30) NOT NULL,
    observacao VARCHAR(255),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    INDEX idx_historico_pedido (pedido_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('admin', 'cliente', 'entregador') NOT NULL,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160),
    telefone VARCHAR(20),
    senha_hash VARCHAR(255),
    cliente_id INT,
    entregador_id INT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_tipo (tipo),
    INDEX idx_users_cliente (cliente_id),
    INDEX idx_users_entregador (entregador_id),
    CONSTRAINT fk_users_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
    CONSTRAINT fk_users_entregador FOREIGN KEY (entregador_id) REFERENCES entregadores(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entregador_id INT NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    veiculo VARCHAR(80) NOT NULL,
    foto_url VARCHAR(255),
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_drivers_entregador FOREIGN KEY (entregador_id) REFERENCES entregadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS deliveries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT,
    cliente_id INT NOT NULL,
    entregador_id INT,
    origem_endereco VARCHAR(255) NOT NULL,
    origem_latitude DECIMAL(10,7) NOT NULL,
    origem_longitude DECIMAL(10,7) NOT NULL,
    destino_endereco VARCHAR(255) NOT NULL,
    destino_latitude DECIMAL(10,7) NOT NULL,
    destino_longitude DECIMAL(10,7) NOT NULL,
    status ENUM('aguardando_coleta','coletado','em_rota','proximo_destino','entregue','cancelado') NOT NULL DEFAULT 'aguardando_coleta',
    eta_seconds INT,
    distance_meters INT,
    observacoes VARCHAR(500),
    started_at DATETIME,
    collected_at DATETIME,
    delivered_at DATETIME,
    canceled_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_deliveries_status (status),
    INDEX idx_deliveries_cliente (cliente_id),
    INDEX idx_deliveries_entregador (entregador_id),
    INDEX idx_deliveries_pedido (pedido_id),
    CONSTRAINT fk_deliveries_pedido FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE SET NULL,
    CONSTRAINT fk_deliveries_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    CONSTRAINT fk_deliveries_entregador FOREIGN KEY (entregador_id) REFERENCES entregadores(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS delivery_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_id INT NOT NULL,
    entregador_id INT NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    accuracy DECIMAL(10,2),
    heading DECIMAL(8,2),
    speed DECIMAL(8,2),
    source VARCHAR(40) DEFAULT 'browser',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_delivery_locations_delivery (delivery_id, created_at),
    INDEX idx_delivery_locations_entregador (entregador_id, created_at),
    CONSTRAINT fk_delivery_locations_delivery FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE,
    CONSTRAINT fk_delivery_locations_entregador FOREIGN KEY (entregador_id) REFERENCES entregadores(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS delivery_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    delivery_id INT NOT NULL,
    status_old VARCHAR(40),
    status_new VARCHAR(40) NOT NULL,
    actor_type ENUM('admin', 'entregador', 'system') NOT NULL DEFAULT 'system',
    actor_id INT,
    note VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_delivery_status_history_delivery (delivery_id, created_at),
    CONSTRAINT fk_delivery_status_history_delivery FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE
) ENGINE=InnoDB;

INSERT INTO produtos (nome, preco, estoque, estoque_minimo, ativo) VALUES
('Galão de água 20L', 8.00, 100, 10, 1),
('Fardo de água mineral', 18.00, 60, 8, 1),
('Saco de gelo', 10.00, 40, 6, 1),
('Garrafão 10L', 5.00, 80, 10, 1),
('Água com gás 500ml', 3.50, 120, 20, 1);

INSERT INTO configuracoes (chave, valor) VALUES
('nome_loja', 'ÁquaLog'),
('subtitulo_loja', 'Pedido online da distribuidora'),
('aviso_cliente', ''),
('pix_chave', ''),
('estoque_minimo_padrao', '5'),
('loja_aberta', '1'),
('som_novo_pedido', '1')
ON DUPLICATE KEY UPDATE valor=VALUES(valor);

INSERT INTO cupons (codigo, percentual, ativo, validade_inicio, validade_fim, valor_minimo, limite_usos, usos) VALUES
('BEMVINDO10', 10.00, 1, NULL, NULL, 0.00, NULL, 0)
ON DUPLICATE KEY UPDATE codigo=VALUES(codigo);

INSERT INTO clientes (nome, telefone, endereco, numero_casa, bairro, referencia) VALUES
('João Oliveira', '(99) 99999-0001', 'Rua Grande', '120', 'Centro', 'Próximo à praça'),
('Maria Santos', '(99) 99999-0002', 'Av. Presidente Médici', '500', 'Seriema', 'Ao lado do hospital'),
('Carlos Pereira', '(99) 99999-0003', 'Rua da Estação', '300', 'Ponte', 'Em frente à garagem'),
('Ana Costa', '(99) 99999-0004', 'Rua do Matadouro', '150', 'Matadouro Novo', 'Próximo ao mercado'),
('Pedro Almeida', '(99) 99999-0005', 'Rua Nova', '80', 'Nova Caxias', 'Esquina com a padaria'),
('Lúcia Ferreira', '(99) 99999-0006', 'Av. São Francisco', '400', 'São Francisco', 'Condomínio Solar'),
('Roberto Lima', '(99) 99999-0007', 'Rua do Salobo', '60', 'Salobo', 'Casa amarela'),
('Fernanda Souza', '(99) 99999-0008', 'Rua do Aeroporto', '200', 'Aeroporto Velho', 'Prox. ao aeroporto'),
('Gustavo Oliveira', '(99) 99999-0009', 'Rua da Trizidela', '700', 'Trizidela', 'Edifício Brisa'),
('Juliana Ribeiro', '(99) 99999-0010', 'Rua do Campo', '350', 'Campo de Belém', 'Próximo à feira'),
('Roberto Costa', '(99) 99999-0011', 'Rua do Piquizeiro', '50', 'Piquizeiro', 'Prox. à praça'),
('Patrícia Lima', '(99) 99999-0012', 'Av. Castelo Branco', '300', 'Castelo Branco', 'Condomínio Verde'),
('Fernando Silva', '(99) 99999-0013', 'Rua do Cangalheiro', '180', 'Cangalheiro', 'Final da rua'),
('Amanda Oliveira', '(99) 99999-0014', 'Travessa da Baixinha', '90', 'Baixinha', 'Casa azul'),
('Lucas Pereira', '(99) 99999-0015', 'Rua da Refinaria', '400', 'Refinaria', 'Prox. ao posto');

-- ATENÇÃO: códigos em texto puro abaixo. Execute reset_db.py para gerar hashes bcrypt.
INSERT INTO entregadores (nome, telefone, veiculo, codigo_acesso) VALUES
('Lucas Mendes', '(99) 98888-0001', 'Fiorino', 'lucas123'),
('Rafael Santos', '(99) 98888-0002', 'Moto', 'rafael123'),
('Diego Costa', '(99) 98888-0003', 'Kombi', 'diego123');

INSERT IGNORE INTO drivers (entregador_id, nome, telefone, veiculo)
SELECT id, nome, telefone, veiculo FROM entregadores;

INSERT INTO pedidos (cliente_id, entregador_id, produto_id, quantidade, forma_pagamento, pagamento_status, confirmacao_status, status, codigo_entrega, data_criacao, data_entrega) VALUES
(1, 1, 1, 2, 'Pix', 'pago', 'confirmado', 'entregue', '481926', NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 45 MINUTE),
(2, 1, 2, 1, 'Dinheiro', 'nao_aplicavel', 'confirmado', 'entregue', '719304', NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 1 HOUR),
(3, 2, 3, 3, 'Cartão', 'nao_aplicavel', 'confirmado', 'entregue', '265180', NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 30 MINUTE),
(4, 2, 1, 4, 'Pix', 'pago', 'confirmado', 'entregue', '903517', NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 50 MINUTE),
(5, 1, 2, 2, 'Dinheiro', 'nao_aplicavel', 'confirmado', 'saiu_para_entrega', '158642', NOW() - INTERVAL 3 HOUR, NULL),
(6, NULL, 1, 3, 'Pix', 'aguardando_pix', 'aguardando_pagamento', 'recebido', '604291', NOW() - INTERVAL 2 HOUR, NULL),
(7, 2, 4, 1, 'Cartão', 'nao_aplicavel', 'confirmado', 'saiu_para_entrega', '837205', NOW() - INTERVAL 1 HOUR, NULL),
(8, NULL, 5, 6, 'Pix', 'aguardando_pix', 'aguardando_pagamento', 'recebido', '392846', NOW() - INTERVAL 30 MINUTE, NULL),
(9, NULL, 1, 2, 'Pix', 'aguardando_pix', 'aguardando_pagamento', 'recebido', '740159', NOW() - INTERVAL 15 MINUTE, NULL),
(10, 2, 3, 2, 'Dinheiro', 'nao_aplicavel', 'confirmado', 'em_preparo', '516873', NOW(), NULL),
(11, NULL, 1, 3, 'Pix', 'aguardando_pix', 'aguardando_pagamento', 'recebido', '284930', NOW(), NULL),
(12, NULL, 2, 2, 'Cartão', 'nao_aplicavel', 'aguardando_confirmacao', 'recebido', '671425', NOW(), NULL),
(13, 1, 5, 4, 'Pix', 'pago', 'confirmado', 'entregue', '498271', NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 1 HOUR),
(14, 2, 1, 1, 'Dinheiro', 'nao_aplicavel', 'confirmado', 'entregue', '930864', NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 35 MINUTE),
(15, NULL, 3, 3, 'Pix', 'aguardando_pix', 'aguardando_pagamento', 'recebido', '105628', NOW(), NULL);

INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
SELECT p.id, p.produto_id, p.quantidade, pr.preco, pr.preco * p.quantidade
FROM pedidos p
JOIN produtos pr ON pr.id = p.produto_id;

UPDATE pedidos
SET carrinho_hash = SHA2(CONCAT(produto_id, ':', quantidade), 256);
