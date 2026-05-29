# ÁquaLog - Sistema de Controle de Entregas

Sistema completo para uma distribuidora de água, com controle de clientes, entregadores, produtos, pedidos, status de entrega, roteirização simples por bairro e relatório com exportação PDF/XLSX.

## Tecnologias

- **Backend:** Python + FastAPI
- **Banco de dados:** MySQL (charset utf8mb4)
- **Frontend:** HTML, CSS e JavaScript vanilla (modular)

## Estrutura do projeto

```
aqualog/
├── backend/
│   ├── main.py              # Montagem da app e roteadores
│   ├── models.py            # Pydantic models
│   ├── database.py          # Conexão MySQL
│   ├── routes/
│   │   ├── admin.py         # Login do admin
│   │   ├── clientes.py      # CRUD clientes
│   │   ├── entregadores.py  # CRUD + login + pedidos do entregador
│   │   ├── pedidos.py       # CRUD + status + dashboard
│   │   └── produtos.py      # CRUD produtos
│   ├── requirements.txt
│   └── schema.sql
├── frontend/
│   ├── index.html           # Admin (com login por senha)
│   ├── entregador.html      # Tela do entregador (login com código)
│   ├── style.css
│   └── js/
│       ├── api.js           # Requisições HTTP
│       ├── utils.js         # Funções utilitárias
│       ├── login.js         # Login do admin
│       ├── dashboard.js     # Dashboard
│       ├── clientes.js      # CRUD + filtro clientes
│       ├── entregadores.js  # CRUD + filtro entregadores
│       ├── produtos.js      # CRUD + filtro produtos
│       ├── pedidos.js       # CRUD + filtro + status pedidos
│       ├── relatorio.js     # Exportação PDF e Excel
│       └── app.js           # Orquestração e formulários
└── docs/
```

## Funcionalidades

### Admin (`/`)
- Dashboard com total de pedidos, tempo médio, status e roteirização por bairro
- Botões para exportar relatório em **PDF** (abre para impressão) e **Excel** (.xlsx com abas: Pedidos, Clientes, Entregadores, Produtos, Roteirização)
- CRUD de Clientes (com bairros reais de Caxias-MA)
- CRUD de Entregadores (com código de acesso para login)
- CRUD de Produtos
- Gerenciamento de Pedidos (criação, filtro por nome/entregador/bairro/produto/status, alteração de status)
- Edição inline nas tabelas
- Filtros em todas as listas
- **Proteção por senha** (configurável via `ADMIN_PASSWORD`)

### Entregador (`/entregador.html`)
- Login com código de acesso
- Visualiza apenas os pedidos atribuídos a ele
- Vê endereço, bairro, referência, telefone do cliente e produto
- Botões: "Saiu p/ entrega" e "Entregue"
- Filtros: Todos / Em rota / Preparando / Entregues

## Como rodar local

### 1. Criar banco MySQL

```bash
# Execute no MySQL Workbench ou terminal:
backend/schema.sql
```

### 2. Configurar backend

```bash
cd backend
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Configure o arquivo `.env` com seu usuário e senha do MySQL.

### 3. Rodar API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API em `http://127.0.0.1:8000` e docs em `http://127.0.0.1:8000/docs`.

### 4. Acessar

- **Admin:** `http://127.0.0.1:8000` (login com senha)
- **Entregador:** `http://127.0.0.1:8000/entregador.html` (login com código de acesso)

## Deploy online (Cloudflare Tunnel)

O sistema pode ser exposto na internet sem hospedagem paga:

1. Instale o `cloudflared`:
   ```powershell
   winget install Cloudflare.cloudflared
   ```

2. Inicie o servidor:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. Inicie o túnel (em outro terminal):
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```

4. Um URL público será gerado. Compartilhe com os entregadores.

## Fluxo do pedido

```
Recebido → Em preparo → Saiu para entrega → Entregue
```

## Entregadores (dados de exemplo)

| Nome | Código | Veículo |
|------|--------|---------|
| Lucas Mendes | lucas123 | Fiorino |
| Rafael Santos | rafael123 | Moto |
| Diego Costa | diego123 | Kombi |

## Acessar do celular

1. Descubra o IP do computador na rede (ex: 10.0.0.129)
2. No celular (mesma rede Wi-Fi), abra `http://SEU_IP:8000`
3. Se não conectar, libere a porta 8000 no firewall do Windows
