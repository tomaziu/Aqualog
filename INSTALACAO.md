# ÁquaLog — Guia de Instalação

Guia completo para instalar e rodar o **ÁquaLog** (sistema de pedidos e entregas para distribuidora de água). Qualquer pessoa pode seguir este documento, mesmo sem conhecer o projeto.

---

## 1. O que é o projeto

Sistema com três interfaces:

| Interface | URL | Para quem é |
|-----------|-----|-------------|
| **Cliente** | `http://127.0.0.1:8000/cliente.html` | Público: faz pedidos online |
| **Admin** | `http://127.0.0.1:8000` | Gestor: dashboard, pedidos, clientes, relatórios |
| **Entregador** | `http://127.0.0.1:8000/entregador.html` | Entregador: vê pedidos e finaliza com código |

---

## 2. Tecnologias

| Camada | Tecnologia | Para que serve |
|--------|------------|----------------|
| **Backend** | Python 3.11 + FastAPI | API REST (`/api/v1`) |
| **Servidor** | Uvicorn | Executa a API (porta 8000) |
| **Banco de dados** | MySQL 8.0 | Armazena clientes, pedidos, produtos etc. |
| **Autenticação** | JWT (python-jose) + bcrypt | Login de admin e entregador |
| **Frontend** | HTML, CSS e JavaScript vanilla | Telas do site (sem framework) |
| **Tempo real** | SSE + WebSocket | Atualizações do admin e GPS do entregador |
| **Pagamento** | Pix (chave manual) + Mercado Pago (opcional) | Cobrança do pedido |
| **Testes** | pytest + httpx | Testes de API |
| **Lint** | Ruff | Padronização de código Python |


### Dependências Python (`backend/requirements.txt`)

- `fastapi` — framework da API  
- `uvicorn` — servidor ASGI  
- `mysql-connector-python` — conexão com MySQL  
- `python-dotenv` — lê o arquivo `.env`  
- `pydantic` — validação de dados  
- `python-jose[cryptography]` — tokens JWT  
- `bcrypt` — senhas com hash  
- `qrcode[pil]` — QR Code Pix  
- `python-multipart` — upload de arquivos  
- `loguru` — logs  
- `pytest`, `httpx` — testes  
- `ruff` — lint  

### Frontend (via CDN, sem npm)

- **Phosphor Icons** — ícones  
- **Chart.js** — gráficos do dashboard  
- **Google Fonts (Outfit)** — tipografia  

---

## 3. Pré-requisitos

### Pré-requisitos

- **Python 3.11** — [python.org](https://www.python.org/downloads/)  
  - Marque *“Add Python to PATH”* na instalação  
- **MySQL 8.0** — [dev.mysql.com](https://dev.mysql.com/downloads/mysql/)  
  - Anote usuário (ex.: `root`) e senha  
- (Opcional) **Git** — para clonar o repositório  
- Controle de acesso ao banco MySQL (usuário e senha)  
- Editor de texto (para editar `.env`)  

---

## 4. Estrutura do projeto

```
aqualog_projeto/
├── backend/                 # API Python (FastAPI)
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── auth.py              # JWT + bcrypt
│   ├── database.py          # Pool de conexões MySQL
│   ├── models.py            # Modelos Pydantic
│   ├── routes/              # Rotas da API
│   ├── schema.sql           # Cria as tabelas no MySQL
│   ├── .env.example         # Modelo de configuração
│   ├── requirements.txt     # Dependências Python
│   └── tests/               # Testes (pytest)
├── frontend/                # Telas HTML/CSS/JS
│   ├── index.html           # Painel admin
│   ├── cliente.html         # Site do cliente
│   ├── entregador.html      # Tela do entregador
│   ├── style.css
│   └── js/                  # JavaScript do admin
├── Makefile                 # Atalhos (make dev, make test…)
├── iniciar_tudo.bat         # Sobe tudo no Windows (com tunnel)
├── README.md                # Visão geral do projeto
└── INSTALACAO.md            # Este guia
```

> O frontend é servido **pelo próprio backend** (FastAPI). Não é preciso instalar Node.js nem npm.

---


---

## 6. Instalação manual (Windows)

### 6.1 Criar o banco MySQL

1. Abra o **MySQL Workbench** ou o terminal `mysql`.
2. Execute o arquivo `backend/schema.sql`:

```bash
mysql -u root -p < backend/schema.sql
```

Isso cria o banco `aqualog` e as tabelas com dados de exemplo (seed).

### 6.2 Configurar o backend

```powershell
cd backend

# Criar ambiente virtual
py -m venv venv

# Ativar o ambiente virtual
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 6.3 Configurar o `.env`

Copie o exemplo e edite:

```powershell
Copy-Item .env.example .env
```

Edite `backend/.env`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=<sua-senha-do-mysql>
DB_NAME=aqualog

ADMIN_PASSWORD=<defina-uma-senha-de-admin>
JWT_SECRET=<texto-longo-e-aleatorio>
PIX_CHAVE=<sua-chave-pix>

MERCADO_PAGO_ACCESS_TOKEN=

PORT=8000
```

**No modo manual, `DB_HOST` é `localhost`** (não `db`).

### 6.4 (Opcional) Aplicar migrações extras

Alguns recursos usam migrações além do `schema.sql`:

```powershell
# Ainda com o venv ativo, dentro de backend/
python migrate_site_features.py
```

### 6.5 Iniciar o servidor

```powershell
# Ainda com o venv ativo, dentro de backend/
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Ou use o atalho da raiz do projeto:

```text
iniciar_tudo.bat
```

Esse script:

1. Aplica migrações  
2. Sobe o servidor na porta 8000  
3. Abre um túnel Cloudflare (link público)  
4. Abre as três telas no navegador  

### 6.6 Acessar

| Tela | URL |
|------|-----|
| Admin | http://127.0.0.1:8000 |
| Cliente | http://127.0.0.1:8000/cliente.html |
| Entregador | http://127.0.0.1:8000/entregador.html |
| API docs | http://127.0.0.1:8000/docs |

### 6.7 Parar o servidor

- Ctrl+C no terminal onde o uvicorn está rodando, ou  
- `parar_server.bat` / `parar_server.ps1` na raiz  

---

## 7. Variáveis de arquivo `.env`

Arquivo: `backend/.env` (copia de `.env.example`)

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DB_HOST` | Sim | Host do MySQL (`localhost` ou `db` no Docker) |
| `DB_USER` | Sim | Usuário do MySQL |
| `DB_PASSWORD` | Sim | Senha do MySQL |
| `DB_NAME` | Sim | Nome do banco (padrão: `aqualog`) |
| `JWT_SECRET` | Sim | Segredo para assinar tokens JWT (use texto longo) |
| `ADMIN_PASSWORD` | Sim | Senha de login do painel admin |
| `PIX_CHAVE` | Sim* | Chave Pix exibida ao cliente (*ou use Mercado Pago) |
| `MERCADO_PAGO_ACCESS_TOKEN` | Não | Token Mercado Pago para Pix automático |
| `PORT` | Não | Porta da API (padrão: 8000) |
| `DATABASE_URL` | Não | String completa de conexão (alternativa) |

**Nunca suba o `.env` com senhas reais para o Git.** Ele deve estar no `.gitignore`.

---

## 8. Login padrão

Após o seed do `schema.sql`:

- **Admin:** a senha é a de `ADMIN_PASSWORD` no `.env` (verifique o usuário cadastrado nas rotas de login / seed).
- **Entregador:** código de acesso gerado no cadastro de entregadores (painel admin).

---

## 9. Rodar os testes

```powershell
cd backend
venv\Scripts\activate
pytest tests/ -v
```


---

## 10. Lint (padronização de código)

```powershell
cd backend
venv\Scripts\activate
ruff check .
```

Ou:

```bash
make lint
```

---


---

## 12. Fluxo resumido do sistema

```
Cliente faz pedido (cliente.html)
        ↓
Pedido entra como "recebido" (+ código de entrega)
        ↓
Admin confere pagamento e atribui entregador
        ↓
Entregador sai para entrega (status "ocupado")
        ↓
Cliente informa o código na tela do entregador
        ↓
Pedido "entregue" → entregador volta a "disponível"
```

**Status do pedido:**  
`recebido` → `em_preparo` → `saiu_para_entrega` → `entregue`

---

## 13. Solução de problemas

| Problema | Causa provável | Solução |
|----------|----------------|---------|
| `Can't connect to MySQL` | Banco fora do ar ou credenciais erradas | Confira `DB_*` no `.env`; no Docker use `DB_HOST=db` |
| Porta 8000 ocupada | Outro processo na porta | Mude a porta no comando uvicorn ou mate o processo |
| Tabelas não existem | `schema.sql` não executado | Execute o schema no MySQL (seção 6.1 ou 5.3) |
| Erro de import no Python | venv não ativado | Ative com `venv\Scripts\activate` (Windows) |
| Frontend 404 | Servidor não iniciado | Confirme que o uvicorn está rodando |
| Senha admin não funciona | `ADMIN_PASSWORD` diferente no `.env` | Reinicie o servidor após editar o `.env` |

---

## 14. Checklist rápido

- [ ] Python 3.11 instalado  
- [ ] MySQL 8.0 acessível  
- [ ] `backend/.env` criado e preenchido  
- [ ] `schema.sql` executado (tabelas criadas)  
- [ ] Dependências instaladas (`pip install -r requirements.txt`)  
- [ ] Servidor rodando na porta 8000  
- [ ] Telas abertas: admin, cliente e entregador  

---

## 15. Onde obter mais ajuda

- **Visão geral:** [`README.md`](README.md)  
- **Regras de negócio e API:** [`AGENTS.md`](AGENTS.md)  
- **Contexto técnico do time:** [`CONTEXT.md`](CONTEXT.md)  
- **Mudanças recentes:** [`CHANGELOG.md`](CHANGELOG.md)  

Após alterar regras do sistema, atualize também `README.md`, `CHANGELOG.md` e `AGENTS.md`.
