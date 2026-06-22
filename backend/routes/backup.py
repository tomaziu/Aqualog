from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from auth import get_admin_user
from database import get_connection

router = APIRouter()


def _identificador_sql(nome: str) -> str:
    return '`' + str(nome).replace('`', '``') + '`'


def _valor_sql(valor) -> str:
    if valor is None:
        return 'NULL'
    if isinstance(valor, bool):
        return '1' if valor else '0'
    if isinstance(valor, bytes):
        return "X'" + valor.hex() + "'"
    if isinstance(valor, (int, float, Decimal)):
        return str(valor)
    if isinstance(valor, datetime):
        valor = valor.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(valor, date):
        valor = valor.strftime('%Y-%m-%d')
    texto = str(valor)
    texto = (texto
             .replace('\\', '\\\\')
             .replace("'", "''")
             .replace('\0', '\\0')
             .replace('\n', '\\n')
             .replace('\r', '\\r')
             .replace('\x1a', '\\Z'))
    return "'" + texto + "'"


def _ordenar_tabelas(tabelas: list[str]) -> list[str]:
    ordem_preferida = [
        'clientes',
        'entregadores',
        'produtos',
        'configuracoes',
        'cupons',
        'pedidos',
        'pedido_itens',
        'suporte_mensagens',
        'pedido_comprovantes',
        'estoque_movimentacoes',
        'pedido_historico',
    ]
    prioridade = {nome: indice for indice, nome in enumerate(ordem_preferida)}
    return sorted(tabelas, key=lambda nome: (prioridade.get(nome, len(ordem_preferida)), nome))


def _gerar_backup_sql() -> str:
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute('SHOW TABLES')
        tabelas = _ordenar_tabelas([linha[0] for linha in cur.fetchall()])

        linhas = [
            '-- Backup Aqualog',
            '-- Gerado em ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'SET NAMES utf8mb4;',
            'SET FOREIGN_KEY_CHECKS=0;',
            '',
        ]

        for tabela in reversed(tabelas):
            linhas.append('DROP TABLE IF EXISTS ' + _identificador_sql(tabela) + ';')
        linhas.append('')

        for tabela in tabelas:
            cur.execute('SHOW CREATE TABLE ' + _identificador_sql(tabela))
            create_table = cur.fetchone()[1]
            linhas.append(create_table + ';')
            linhas.append('')

            cur.execute('SELECT * FROM ' + _identificador_sql(tabela))
            colunas = [_identificador_sql(col[0]) for col in cur.description]
            prefixo = 'INSERT INTO ' + _identificador_sql(tabela) + ' (' + ', '.join(colunas) + ') VALUES '
            registros = cur.fetchall()
            for registro in registros:
                valores = ', '.join(_valor_sql(valor) for valor in registro)
                linhas.append(prefixo + '(' + valores + ');')
            if registros:
                linhas.append('')

        linhas.append('SET FOREIGN_KEY_CHECKS=1;')
        linhas.append('')
        return '\n'.join(linhas)
    finally:
        cur.close()
        con.close()


@router.get('/backup/sql')
def baixar_backup_sql(admin=Depends(get_admin_user)):
    conteudo = _gerar_backup_sql()
    nome = 'aqualog_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.sql'
    return Response(
        content=conteudo.encode('utf-8'),
        media_type='application/sql; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="' + nome + '"'},
    )
