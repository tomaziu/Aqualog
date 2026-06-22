import sys
import os
import random
sys.path.insert(0, os.path.dirname(__file__))
from database import get_connection

NOMES = [
    'Ana Silva', 'Bruno Santos', 'Carla Oliveira', 'Daniel Costa', 'Elena Rodrigues',
    'Fernando Lima', 'Gabriela Souza', 'Henrique Almeida', 'Isabela Ferreira', 'Joao Pereira',
    'Karen Ribeiro', 'Lucas Martins', 'Mariana Araujo', 'Nelson Barbosa', 'Olivia Carvalho',
    'Paulo Mendes', 'Quitaria Dias', 'Roberto Nascimento', 'Sandra Teixeira', 'Thiago Campos',
    'Ursula Monteiro', 'Victor Lopes', 'Wanda Freitas', 'Xavier Gomes', 'Yara Silva',
    'Zeca Pinheiro', 'Aline Rocha', 'Bruno Marques', 'Camila Reis', 'Douglas Pinto',
    'Eduarda Melo', 'Fabio Alves', 'Graziela Castro', 'Hugo Ferreira', 'Iris Martins',
    'Jorge Lima', 'Keila Santos', 'Leonardo Pinto', 'Monica Rocha', 'Nathan Gomes',
    'Patricia Dias', 'Rafael Barbosa', 'Silvia Nascimento', 'Thales Oliveira', 'Vanessa Campos',
    'Wagner Reis', 'Ximena Silva', 'Yuri Teixeira', 'Zilda Moura', 'Adriana Lopes',
    'Breno Cardoso', 'Cristina Mendes', 'Diego Araujo', 'Elaine Freitas', 'Flavio Ribeiro',
    'Giovanna Costa', 'Helio Barros', 'Ivone Pereira', 'Julio Correia', 'Larissa Monteiro',
    'Marcos Vieira', 'Natalia Souza', 'Oscar Lima', 'Priscila Martins', 'Renato Dias',
    'Simone Albuquerque', 'Tarcisio Rocha', 'Valeria Gomes', 'Wesley Santos', 'Zilma Campos',
    'Adrielson Pinto', 'Bruna Ferreira', 'Claudio Reis', 'Daniela Nascimento', 'Edson Oliveira',
    'Fernanda Silva', 'Gustavo Henrique', 'Helena Cardoso', 'Igor Mendes', 'Juliana Araujo',
    'Leandro Freitas', 'Marina Ribeiro', 'Nelson Costa', 'Olga Barros', 'Paulo Henrique',
    'Renata Pereira', 'Sergio Correia', 'Tatiana Monteiro', 'Ulisses Vieira', 'Vivian Souza',
    'Washington Lima', 'Xuxa Martins', 'Yamada Dias', 'Zenaide Albuquerque', 'Aderbal Rocha',
    'Bianca Gomes', 'Cezar Santos', 'Dagmar Pinto', 'Elias Ferreira', 'Francisca Reis',
    'Gilberto Nascimento', 'Heloisa Oliveira', 'Ivanete Silva', 'Joaquim Henrique', 'Lidiane Cardoso',
    'Mauricio Mendes', 'Neusa Araujo', 'Orlando Freitas', 'Polyana Ribeiro', 'Reginaldo Costa',
    'Sueli Barros', 'Tobias Pereira', 'Umbelina Correia', 'Valdir Monteiro', 'Wilma Vieira',
    'Xerxes Souza', 'Yolanda Lima', 'Zenilda Martins', 'Agnaldo Dias', 'Beta Albuquerque',
    'Cleber Rocha', 'Doralice Gomes', 'Edvaldo Santos', 'Fatima Pinto', 'Geraldo Ferreira',
    'Hermelinda Reis', 'Iracema Nascimento', 'Joelma Oliveira', 'Kleber Silva', 'Luzia Henrique',
    'Mamerto Cardoso', 'Nair Mendes', 'Odorico Araujo', 'Paraskeva Freitas', 'Quiteria Ribeiro',
    'Raimundo Costa', 'Socorro Barros', 'Teodoro Pereira', 'Ubirajara Correia', 'Vanda Monteiro',
    'Xisto Vieira', 'Yone Souza', 'Zuleica Lima', 'Aldo Martins', 'Benedita Dias',
    'Cassio Albuquerque', 'Doris Rocha', 'Emerson Gomes', 'Floripes Santos', 'Graciliano Pinto',
    'Hercilia Ferreira', 'Irenice Reis', 'Josenildo Nascimento', 'Leila Oliveira', 'Maximo Silva',
    'Noemia Henrique', 'Odair Cardoso', 'Porfirio Mendes', 'Raquel Araujo', 'Salvador Freitas',
    'Terezinha Ribeiro', 'Urbano Costa', 'Vanilde Barros', 'Waldemar Pereira', 'Xenon Correia',
    'Yolanda Monteiro', 'Zoraide Vieira', 'Arildo Souza', 'Brasilina Lima', 'Claudomiro Martins',
    'Dorotéia Dias', 'Epaminondas Albuquerque', 'Fidélia Rocha', 'Gercina Gomes', 'Hermogenes Santos',
    'Ivoneide Pinto', 'Jailson Ferreira', 'Laudelino Reis', 'Marcilene Nascimento', 'Nivaldo Oliveira',
    'Orlandina Silva', 'Perpetua Henrique', 'Raimunda Cardoso', 'Simeao Mendes', 'Tereza Araujo',
    'Venancio Freitas', 'Walquiria Ribeiro', 'Xisto Costa', 'Yoneide Barros', 'Zenon Pereira',
    'Ailton Correia', 'Belmira Monteiro', 'Clovis Vieira', 'Divina Souza', 'Eurico Lima',
    'Fátima Martins', 'Geralda Dias', 'Heitor Albuquerque', 'Iolanda Rocha', 'Jubileu Gomes',
    'Klebia Santos', 'Luzinete Pinto', 'Modesto Ferreira', 'Nair Reis', 'Osmar Nascimento',
    'Pompilia Oliveira', 'Regina Silva', 'Santino Henrique', 'Terezinha Cardoso', 'Ubiracir Mendes',
    'Valderez Araujo', 'Wanderley Freitas', 'Xenaira Ribeiro', 'Yvone Costa', 'Zacarias Barros',
]

BAIRROS = [
    'Centro', 'Jardim America', 'Vila Nova', 'Jardim Europa', 'Consolacao',
    'Bela Vista', 'Jardins', 'Cerqueira Cesar', 'Copacabana', 'Ipanema',
    'Meireles', 'Aldeota', 'Asa Norte', 'Asa Sul', 'Cidade Baixa',
    'Centro Historico', 'Boa Vista', 'Santa Cecilia', 'Liberdade', 'Mooca',
    'Tatuape', 'Vila Mariana', 'Pinheiros', 'Brooklin', 'Itaim Bibi',
    'Moema', 'Vila Olimpia', 'Campo Belo', 'Brooklin Novo', 'Saude',
]

RUAS = [
    'Rua das Flores', 'Av. Brasil', 'Rua da Paz', 'Alameda Santos', 'Rua Augusta',
    'Av. Paulista', 'Rua Oscar Freire', 'Rua Haddock Lobo', 'Rua Bela Cintra', 'Av. Atlantica',
    'Rua Barata Ribeiro', 'Rua Nascimento Silva', 'Rua Garcia Davila', 'Av. Vieira Souto', 'Rua da Bahia',
    'Av. Afonso Pena', 'Rua Curitiba', 'Rua XV de Novembro', 'Av. Marechal Deodoro', 'Rua Marechal Floriano',
    'Rua dos Andradas', 'Av. Borges de Medeiros', 'Rua Voluntarios da Patria', 'SGAN 601', 'SQN 308',
    'Rua 24 de Outubro', 'Av. Beira Mar', 'Rua Canuto Queiroz', 'Av. Monsenhor Tabosa', 'Rua Senador Facio',
]

REFERENCIAS = [
    'Prox. a praca', 'Em frente ao mercado', 'Casa azul', 'Proximo ao parque', 'Edificio 15',
    'Conjunto nacional', 'Loja de esquina', 'Em cima da padaria', 'Ao lado da farmacia', 'Predio 20',
    'Casa 3', 'Esquina com Rua Visconde', 'Em frente ao Natura', 'Predio 8', 'Proximo a praca',
    'Edificio A', 'Casa 5', 'Loja 12', 'Em cima do banco', 'Prox. a catedral',
    'Mercado Publico', 'Praca da Matriz', 'Bar do Ze', 'Bloco A', 'Quadra B',
    'Bloco C', 'Proximo ao shopping', 'Em frente ao hotel', 'Casa 7', 'Edificio 22',
]

DDD = ['11', '21', '31', '41', '51', '61', '85', '71', '91', '48', '62', '86', '92', '81', '34']


def gerar_cliente(idx):
    nome = random.choice(NOMES) + ' ' + str(idx)
    ddd = random.choice(DDD)
    parte1 = str(random.randint(90000, 99999))
    parte2 = str(random.randint(1000, 9999))
    telefone = '(' + ddd + ') ' + parte1 + '-' + parte2
    rua = random.choice(RUAS)
    numero = str(random.randint(1, 2500))
    bairro = random.choice(BAIRROS)
    referencia = random.choice(REFERENCIAS)
    return (nome, telefone, rua, numero, bairro, referencia)


def seed():
    con = get_connection()
    cur = con.cursor()

    clientes = [gerar_cliente(i) for i in range(1, 201)]
    for c in clientes:
        cur.execute(
            'INSERT IGNORE INTO clientes (nome, telefone, endereco, numero_casa, bairro, referencia) VALUES (%s,%s,%s,%s,%s,%s)',
            c
        )

    produtos = [
        ('Agua Mineral 500ml', 2.50, 100, 10, 1),
        ('Agua com Gas 500ml', 3.00, 80, 10, 1),
        ('Agua Tonica 1L', 5.00, 50, 5, 1),
        ('Agua Saborizada Limao 500ml', 4.50, 60, 8, 1),
        ('Agua Saborizada Laranja 500ml', 4.50, 55, 8, 1),
        ('Galao 20L', 15.00, 200, 20, 1),
        ('Saco de gelo 2kg', 8.00, 150, 15, 1),
        ('Saco de gelo 5kg', 14.00, 100, 10, 1),
        ('Fardo 12x500ml', 19.90, 70, 5, 1),
        ('Fardo 6x1L', 22.00, 40, 5, 1),
        ('Agua de coco 1L', 7.50, 30, 5, 0),
        ('Kit 4 garrafas 500ml', 9.90, 45, 5, 1),
    ]
    for p in produtos:
        cur.execute('INSERT IGNORE INTO produtos (nome, preco, estoque, estoque_minimo, ativo) VALUES (%s,%s,%s,%s,%s)', p)

    cupons = [
        ('DESCONTO10', 10.00, 1, '2025-01-01', '2026-12-31', 20.00, 100, 15),
        ('PRIMEIRACOMPRA', 15.00, 1, '2025-01-01', '2026-12-31', 30.00, 50, 8),
        ('FRETEGRATIS', 5.00, 1, '2025-01-01', '2026-12-31', 50.00, None, 3),
        ('VERAO2025', 20.00, 0, '2025-01-01', '2025-03-31', 40.00, 200, 200),
    ]
    for c in cupons:
        cur.execute(
            'INSERT IGNORE INTO cupons (codigo, percentual, ativo, validade_inicio, validade_fim, valor_minimo, limite_usos, usos) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            c
        )

    con.commit()
    cur.close()
    con.close()
    print('Seed concluido: ' + str(len(clientes)) + ' clientes, ' + str(len(produtos)) + ' produtos, ' + str(len(cupons)) + ' cupons.')


if __name__ == '__main__':
    seed()
