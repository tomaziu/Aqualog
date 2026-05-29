CREATE DATABASE IF NOT EXISTS aqualog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aqualog;

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(180) NOT NULL,
    bairro VARCHAR(80) NOT NULL,
    referencia VARCHAR(180)
);

CREATE TABLE IF NOT EXISTS entregadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    veiculo VARCHAR(80) NOT NULL,
    codigo_acesso VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('disponivel', 'ocupado') DEFAULT 'disponivel'
);

CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    estoque INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    entregador_id INT,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    forma_pagamento VARCHAR(50) NOT NULL,
    status ENUM('recebido', 'em_preparo', 'saiu_para_entrega', 'entregue', 'cancelado') DEFAULT 'recebido',
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_entrega DATETIME NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (entregador_id) REFERENCES entregadores(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

INSERT INTO produtos (nome, preco, estoque) VALUES
('Galão de água 20L', 8.00, 100),
('Fardo de água mineral', 18.00, 60),
('Saco de gelo', 10.00, 40),
('Garrafão 10L', 5.00, 80),
('Água com gás 500ml', 3.50, 120);

INSERT INTO clientes (nome, telefone, endereco, bairro, referencia) VALUES
('João Oliveira', '(99) 99999-0001', 'Rua Grande, 120', 'Centro', 'Próximo à praça'),
('Maria Santos', '(99) 99999-0002', 'Av. Presidente Médici, 500', 'Seriema', 'Ao lado do hospital'),
('Carlos Pereira', '(99) 99999-0003', 'Rua da Estação, 300', 'Ponte', 'Em frente à garagem'),
('Ana Costa', '(99) 99999-0004', 'Rua do Matadouro, 150', 'Matadouro Novo', 'Próximo ao mercado'),
('Pedro Almeida', '(99) 99999-0005', 'Rua Nova, 80', 'Nova Caxias', 'Esquina com a padaria'),
('Lúcia Ferreira', '(99) 99999-0006', 'Av. São Francisco, 400', 'São Francisco', 'Condomínio Solar'),
('Roberto Lima', '(99) 99999-0007', 'Rua do Salobo, 60', 'Salobo', 'Casa amarela'),
('Fernanda Souza', '(99) 99999-0008', 'Rua do Aeroporto, 200', 'Aeroporto Velho', 'Prox. ao aeroporto'),
('Gustavo Oliveira', '(99) 99999-0009', 'Rua da Trizidela, 700', 'Trizidela', 'Edifício Brisa'),
('Juliana Ribeiro', '(99) 99999-0010', 'Rua do Campo, 350', 'Campo de Belém', 'Próximo à feira'),
('Roberto Costa', '(99) 99999-0011', 'Rua do Piquizeiro, 50', 'Piquizeiro', 'Prox. à praça'),
('Patrícia Lima', '(99) 99999-0012', 'Av. Castelo Branco, 300', 'Castelo Branco', 'Condomínio Verde'),
('Fernando Silva', '(99) 99999-0013', 'Rua do Cangalheiro, 180', 'Cangalheiro', 'Final da rua'),
('Amanda Oliveira', '(99) 99999-0014', 'Travessa da Baixinha, 90', 'Baixinha', 'Casa azul'),
('Lucas Pereira', '(99) 99999-0015', 'Rua da Refinaria, 400', 'Refinaria', 'Prox. ao posto');

INSERT INTO entregadores (nome, telefone, veiculo, codigo_acesso) VALUES
('Lucas Mendes', '(99) 98888-0001', 'Fiorino', 'lucas123'),
('Rafael Santos', '(99) 98888-0002', 'Moto', 'rafael123'),
('Diego Costa', '(99) 98888-0003', 'Kombi', 'diego123');

INSERT INTO pedidos (cliente_id, entregador_id, produto_id, quantidade, forma_pagamento, status, data_criacao, data_entrega) VALUES
(1, 1, 1, 2, 'Pix', 'entregue', NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 45 MINUTE),
(2, 1, 2, 1, 'Dinheiro', 'entregue', NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 2 DAY + INTERVAL 1 HOUR),
(3, 2, 3, 3, 'Cartão', 'entregue', NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 30 MINUTE),
(4, 2, 1, 4, 'Pix', 'entregue', NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 1 DAY + INTERVAL 50 MINUTE),
(5, 1, 2, 2, 'Dinheiro', 'saiu_para_entrega', NOW() - INTERVAL 3 HOUR, NULL),
(6, 1, 1, 3, 'Pix', 'saiu_para_entrega', NOW() - INTERVAL 2 HOUR, NULL),
(7, 2, 4, 1, 'Cartão', 'saiu_para_entrega', NOW() - INTERVAL 1 HOUR, NULL),
(8, 2, 5, 6, 'Pix', 'saiu_para_entrega', NOW() - INTERVAL 30 MINUTE, NULL),
(9, 1, 1, 2, 'Pix', 'em_preparo', NOW() - INTERVAL 15 MINUTE, NULL),
(10, 2, 3, 2, 'Dinheiro', 'em_preparo', NOW(), NULL),
(11, 3, 1, 3, 'Pix', 'recebido', NOW(), NULL),
(12, 3, 2, 2, 'Cartão', 'recebido', NOW(), NULL),
(13, 1, 5, 4, 'Pix', 'entregue', NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 1 HOUR),
(14, 2, 1, 1, 'Dinheiro', 'entregue', NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY + INTERVAL 35 MINUTE),
(15, 3, 3, 3, 'Pix', 'recebido', NOW(), NULL);
