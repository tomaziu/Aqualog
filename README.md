# ÁquaLog - Sistema de Controle de Entregas

Sistema para distribuidora de água com pedido online, painel administrativo, tela do entregador, controle de estoque, status de entrega e relatórios.

## Tecnologias

- **Backend:** Python + FastAPI
- **Banco de dados:** MySQL
- **Frontend:** HTML, CSS e JavaScript vanilla
- **Testes:** pytest + httpx

## Telas

- **Cliente:** `http://127.0.0.1:8000/cliente.html`
  - escolhe produto
  - informa endereço
  - informa número da casa separadamente
  - paga via Pix (chave manual)
  - recebe um código de entrega
  - acompanha status do pedido
  - vê a data de criação do pedido
  - conversa com o atendimento e envia comprovantes pela aba Conversa
- **Admin:** `http://127.0.0.1:8000`
  - dashboard
  - CRUD de clientes, entregadores e produtos
  - gerenciamento de pedidos
  - atribuição de entregador para pedidos feitos no site
  - confirmação manual de pagamento Pix
  - suporte por conversa com cliente
  - relatórios PDF/XLSX
- **Entregador:** `http://127.0.0.1:8000/entregador.html`
  - login por código
  - visualiza pedidos atribuídos
  - finaliza entrega com o código informado pelo cliente

## Estrutura

```
aqualog/
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── sse_manager.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── clientes.py
│   │   ├── entregadores.py
│   │   ├── pedidos.py
│   │   ├── produtos.py
│   │   └── site.py
│   ├── tests/
│   ├── requirements.txt
│   └── schema.sql
├── frontend/
│   ├── index.html
│   ├── cliente.html
│   ├── entregador.html
│   ├── style.css
│   └── js/
└── docs/
```

## Fluxo Do Pedido

```
Cliente cria pedido → Admin atribui entregador → Entregador sai para entrega → Cliente informa código → Pedido entregue
```

O fluxo principal é o site do cliente. A criação de pedido no admin permanece como pedido manual para atendimento por telefone, balcão ou testes.

## Como Rodar

### 1. Criar banco MySQL

Execute `backend/schema.sql` no MySQL.

### 2. Configurar backend

```bash
cd backend
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Configure o `.env`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=<defina-aqui>
DB_NAME=aqualog
JWT_SECRET=<defina-aqui>
ADMIN_PASSWORD=<defina-aqui>
PIX_CHAVE=<defina-aqui>
```

### 3. Rodar API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Ou use:

```text
C:\Users\Admin\Downloads\aqualog_projeto\iniciar_tudo.bat
```

### 4. Docker (alternativa)

Pré-requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando.

```bash
# Criar o arquivo .env
cp backend/.env.example backend/.env
# Edite com suas credenciais

# Subir tudo (backend + MySQL)
docker compose up --build
```

Acesse: `http://localhost:8000`

Comandos úteis:

```bash
docker compose up --build -d    # rodar em background
docker compose down             # parar e remover containers
docker compose logs backend     # ver logs do backend
docker compose restart backend  # reiniciar backend
```

## Pagamento

O pagamento é feito exclusivamente por **Pix**. O cliente visualiza a chave configurada em `PIX_CHAVE`, envia o comprovante pelo suporte e o admin confirma o pagamento no painel.

## Rodar Testes

```bash
cd backend
.\venv\Scripts\activate
pytest tests/ -v
```
