import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from database import get_connection
from logger import logger


def migrar():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("SHOW COLUMNS FROM produtos LIKE 'imagem'")
        if cur.fetchone():
            logger.info("Coluna 'imagem' já existe na tabela produtos")
            return

        cur.execute("ALTER TABLE produtos ADD COLUMN imagem VARCHAR(500) NULL AFTER estoque_minimo")
        con.commit()
        logger.info("Coluna 'imagem' adicionada à tabela produtos")
        print("OK: Coluna 'imagem' adicionada com sucesso")
    except Exception as e:
        con.rollback()
        logger.exception(f"Erro na migração: {e}")
        print(f"Erro: {e}")
    finally:
        cur.close()
        con.close()


if __name__ == '__main__':
    migrar()
