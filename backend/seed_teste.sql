-- Dados de teste para aqualog
USE aqualog;

-- Clientes de teste (30 para testar paginação de 20)
INSERT IGNORE INTO clientes (nome, telefone, endereco, numero_casa, bairro, referencia) VALUES
('Ana Silva', '(11) 99999-1111', 'Rua das Flores', '100', 'Centro', 'Prox. a praça'),
('Bruno Santos', '(11) 99999-2222', 'Av. Brasil', '200', 'Jardim América', 'Em frente ao mercado'),
('Carla Oliveira', '(11) 99999-3333', 'Rua da Paz', '300', 'Vila Nova', 'Casa azul'),
('Daniel Costa', '(11) 99999-4444', 'Alameda Santos', '400', 'Jardim Europa', 'Próximo ao parque'),
('Elena Rodrigues', '(11) 99999-5555', 'Rua Augusta', '500', 'Consolação', 'Edifício 15'),
('Fernando Lima', '(11) 99999-6666', 'Av. Paulista', '600', 'Bela Vista', 'Conjunto nacional'),
('Gabriela Souza', '(11) 99999-7777', 'Rua Oscar Freire', '700', 'Jardins', 'Loja de esquina'),
('Henrique Almeida', '(11) 99999-8888', 'Rua Haddock Lobo', '800', 'Cerqueira César', 'Em cima da padaria'),
('Isabela Ferreira', '(11) 99999-9999', 'Rua Bela Cintra', '900', 'Consolação', 'Ao lado da farmácia'),
('João Pereira', '(21) 98888-1111', 'Av. Atlântica', '110', 'Copacabana', 'Prédio 20'),
('Karen Ribeiro', '(21) 98888-2222', 'Rua Barata Ribeiro', '210', 'Copacabana', 'Casa 3'),
('Lucas Martins', '(21) 98888-3333', 'Rua Nascimento Silva', '310', 'Ipanema', 'Esquina com Rua Visconde'),
('Mariana Araújo', '(21) 98888-4444', 'Rua Garcia Dávila', '410', 'Ipanema', 'Em frente ao Natura'),
('Nelson Barbosa', '(21) 98888-5555', 'Av. Vieira Souto', '510', 'Ipanema', 'Prédio 8'),
('Olivia Carvalho', '(31) 97777-1111', 'Rua da Bahia', '610', 'Centro', 'Próximo à praça'),
('Paulo Mendes', '(31) 97777-2222', 'Av. Afonso Pena', '710', 'Centro', 'Edifício A'),
('Quitéria Dias', '(31) 97777-3333', 'Rua Curitiba', '810', 'Centro', 'Casa 5'),
('Roberto Nascimento', '(41) 96666-1111', 'Rua XV de Novembro', '910', 'Centro', 'Loja 12'),
('Sandra Teixeira', '(41) 96666-2222', 'Av. Marechal Deodoro', '1010', 'Centro', 'Em cima do banco'),
('Thiago Campos', '(41) 96666-3333', 'Rua Marechal Floriano', '1110', 'Centro', 'Prox. à catedral'),
('Ursula Monteiro', '(51) 95555-1111', 'Rua dos Andradas', '1210', 'Centro Histórico', 'Mercado Público'),
('Victor Lopes', '(51) 95555-2222', 'Av. Borges de Medeiros', '1310', 'Centro', 'Praça da Matriz'),
('Wanda Freitas', '(51) 95555-3333', 'Rua Voluntários da Pátria', '1410', 'Cidade Baixa', 'Bar do Zé'),
('Xavier Gomes', '(61) 94444-1111', 'SGAN 601', '1510', 'Asa Norte', 'Bloco A'),
('Yara Silva', '(61) 94444-2222', 'SQN 308', '1610', 'Asa Norte', 'Quadra B'),
('Zeca Pinheiro', '(61) 94444-3333', 'SQS 405', '1710', 'Asa Sul', 'Bloco C'),
('Aline Rocha', '(85) 93333-1111', 'Rua 24 de Outubro', '1810', 'Meireles', 'Próximo ao shopping'),
('Bruno Marques', '(85) 93333-2222', 'Av. Beira Mar', '1910', 'Meireles', 'Em frente ao hotel'),
('Camila Reis', '(85) 93333-3333', 'Rua Canuto Queiroz', '2010', 'Aldeota', 'Casa 7'),
('Douglas Pinto', '(85) 93333-4444', 'Av. Monsenhor Tabosa', '2110', 'Centro', 'Edifício 22');

-- Produtos extras para testar paginação de produtos
INSERT IGNORE INTO produtos (nome, preco, estoque, estoque_minimo, ativo) VALUES
('Água Mineral 500ml', 2.50, 100, 10, 1),
('Água com Gás 500ml', 3.00, 80, 10, 1),
('Água Tônica 1L', 5.00, 50, 5, 1),
('Água Saborizada Limão 500ml', 4.50, 60, 8, 1),
('Água Saborizada Laranja 500ml', 4.50, 55, 8, 1),
('Galão 20L', 15.00, 200, 20, 1),
('Saco de gelo 2kg', 8.00, 150, 15, 1),
('Saco de gelo 5kg', 14.00, 100, 10, 1),
('Fardo 12x500ml', 19.90, 70, 5, 1),
('Fardo 6x1L', 22.00, 40, 5, 1),
('Água de coco 1L', 7.50, 30, 5, 0),
('Kit 4 garrafas 500ml', 9.90, 45, 5, 1);

-- Cupons extras
INSERT IGNORE INTO cupons (codigo, percentual, ativo, validade_inicio, validade_fim, valor_minimo, limite_usos, usos) VALUES
('DESCONTO10', 10.00, 1, '2025-01-01', '2026-12-31', 20.00, 100, 15),
('PRIMEIRACOMPRA', 15.00, 1, '2025-01-01', '2026-12-31', 30.00, 50, 8),
('FRETEGRATIS', 5.00, 1, '2025-01-01', '2026-12-31', 50.00, NULL, 3),
('VERAO2025', 20.00, 0, '2025-01-01', '2025-03-31', 40.00, 200, 200);
