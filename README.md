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
  - escolhe forma de pagamento
  - recebe a orientação de Pix manual quando escolhe Pix
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
DB_PASSWORD=sua_senha
DB_NAME=aqualog
JWT_SECRET=troque-este-segredo
ADMIN_PASSWORD=admin123
PIX_CHAVE=sua-chave-pix
MERCADO_PAGO_ACCESS_TOKEN=
```

### 3. Rodar API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Ou use:

```text
C:\Users\Admin\Downloads\aqualog_projeto\iniciar_tudo.bat
```

## Pagamento

O site permite escolher **Pix**, **Dinheiro** ou **Cartão**.

Com Pix, o fluxo principal é manual e gratuito: o cliente visualiza a chave configurada em `PIX_CHAVE`, envia o comprovante pelo suporte e o admin confirma o pagamento no painel. Integrações antigas com provedor de pagamento podem continuar existindo para pedidos legados, mas novos pedidos do site não dependem de Mercado Pago.

## Rodar Testes

```bash
cd backend
.\venv\Scripts\activate
pytest tests/ -v
```
