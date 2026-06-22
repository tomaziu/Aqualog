from database import get_connection


STATEMENTS = [
    """
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
    ) ENGINE=InnoDB
    """,
    """
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
    ) ENGINE=InnoDB
    """,
    """
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
    ) ENGINE=InnoDB
    """,
    """
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
    ) ENGINE=InnoDB
    """,
    """
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
    ) ENGINE=InnoDB
    """,
    """
    INSERT IGNORE INTO drivers (entregador_id, nome, telefone, veiculo)
    SELECT id, nome, telefone, veiculo FROM entregadores
    """,
]


def main():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("SHOW COLUMNS FROM clientes LIKE 'latitude'")
        if not cur.fetchone():
            cur.execute('ALTER TABLE clientes ADD COLUMN latitude DECIMAL(10,7) NULL AFTER referencia')
        cur.execute("SHOW COLUMNS FROM clientes LIKE 'longitude'")
        if not cur.fetchone():
            cur.execute('ALTER TABLE clientes ADD COLUMN longitude DECIMAL(10,7) NULL AFTER latitude')
        for statement in STATEMENTS:
            cur.execute(statement)
        con.commit()
        print('Migração de rastreamento aplicada com sucesso.')
    finally:
        cur.close()
        con.close()


if __name__ == '__main__':
    main()
