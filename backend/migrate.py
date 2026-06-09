"""Migração: ajusta coluna codigo_acesso para suportar hashes bcrypt."""
import mysql.connector
from database import get_connection

print("Aplicando migrações...")

con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE entregadores MODIFY codigo_acesso VARCHAR(255) NOT NULL UNIQUE")
    print("  OK - codigo_acesso alterado para VARCHAR(255)")
except mysql.connector.Error as e:
    print(f"  AVISO: {e}")

try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedido_historico (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id INT NOT NULL,
            status_anterior VARCHAR(30),
            status_novo VARCHAR(30) NOT NULL,
            observacao VARCHAR(255),
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
            INDEX idx_historico_pedido (pedido_id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """)
    print("  OK - tabela pedido_historico criada")
except mysql.connector.Error as e:
    print(f"  AVISO: {e}")

con.commit()
cur.close()
con.close()

print("Migrações concluídas!")
