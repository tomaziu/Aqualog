# ÁquaLog — Contexto do Projeto

## O que é

Sistema de controle de pedidos e entregas para distribuidora de água em Caxias/MA. Três interfaces: site público do cliente, painel administrativo e tela do entregador. O cliente faz pedido online, o admin gerencia e atribui entregador, o entregador finalize com código de validação.

## Stack

- **Backend:** Python 3.11 + FastAPI, uvicorn, MySQL (mysql-connector-python), JWT (python-jose), bcrypt, SSE (asyncio.Queue)
- **Frontend:** HTML/CSS/JS vanilla (sem frameworks), Phosphor Icons, Chart.js (dashboard), Google Fonts (Outfit)
- **Banco:** MySQL 8.0, 15 tabelas (schema.sql com seed)
- **Pagamento:** Pix manual (chave Pix) + integração Mercado Pago (Checkout API /v1/orders)
- **Infra:** Docker Compose (backend + MySQL), scripts .bat para Windows

## Estrutura

```
aqualog_projeto/
├── aqualog/
│   ├── backend/
│   │   ├── main.py              # FastAPI app, CORS, routers, static mount, SSE endpoint
│   │   ├── auth.py              # JWT (HS256), bcrypt, middleware admin/entregador
│   │   ├── database.py          # Pool MySQL (mysql.connector.pooling)
│   │   ├── models.py            # Pydantic models (PedidoSite, ComprovantePix, etc)
│   │   ├── sse_manager.py       # SSE broadcast para admin (asyncio.Queue)
│   │   ├── delivery_realtime.py # WebSocket para GPS em tempo real
│   │   ├── mercado_pago.py      # API Mercado Pago (criar/consultar Pix order)
│   │   ├── pix_manual.py        # Gerador PIX BR Code (payload + CRC16 + QR base64)
│   │   ├── delivery_code.py     # Gera código 6 dígitos (secrets.randbelow)
│   │   ├── logger.py            # Loguru
│   │   ├── schema.sql           # DDL + INSERTs (seed com 15 clientes, 3 entregadores, 15 pedidos)
│   │   ├── routes/
│   │   │   ├── admin.py         # Login admin
│   │   │   ├── site.py          # Fluxo público: pedidos, pagamento, suporte, webhook MP
│   │   │   ├── pedidos.py       # CRUD pedidos (admin), status, atribuição
│   │   │   ├── clientes.py      # CRUD clientes (admin)
│   │   │   ├── entregadores.py  # CRUD entregadores (admin)
│   │   │   ├── produtos.py      # CRUD produtos (admin)
│   │   │   ├── suporte.py       # Chat suporte (admin)
│   │   │   ├── configuracoes.py # Config loja (pix_chave, nome, etc)
│   │   │   ├── cupons.py        # CRUD cupons
│   │   │   ├── backup.py        # Backup SQL
│   │   │   └── deliveries.py    # Delivery tracking (GPS, WebSocket, histórico)
│   │   ├── tests/
│   │   │   ├── test_api.py      # 45 testes (unitários + integração)
│   │   │   └── test_integration.py
│   │   ├── migrate*.py          # Scripts de migração (delivery tracking, seed, site features)
│   │   └── venv/
│   ├── frontend/
│   │   ├── index.html           # Painel admin (SPA com abas via JS)
│   │   ├── cliente.html         # Site público do cliente (~2600 linhas)
│   │   ├── entregador.html      # Tela do entregador (login + pedidos)
│   │   ├── rastreamento.html    # Página de rastreamento para cliente
│   │   ├── style.css            # Estilos globais do admin (~2600 linhas)
│   │   ├── entregador.js        # JS do entregador (GPS, pedidos, modal código)
│   │   └── js/
│   │       ├── api.js           # Wrapper fetch (apiGet, apiSend, apiDelete, toast)
│   │       ├── utils.js         # Helpers ($, escapeHtml, formatarData, etc)
│   │       ├── app.js           # Core admin (carregarTudo, SSE, filtros, confirmações)
│   │       ├── login.js         # Login admin/entregador
│   │       ├── dashboard.js     # Dashboard (cards, gráficos Chart.js, métricas)
│   │       ├── clientes.js      # CRUD clientes
│   │       ├── entregadores.js  # CRUD entregadores
│   │       ├── produtos.js      # CRUD produtos
│   │       ├── pedidos.js       # Gerenciamento de pedidos
│   │       ├── suporte.js       # Chat suporte admin
│   │       ├── cupons.js        # CRUD cupons
│   │       ├── configuracoes.js # Config loja
│   │       ├── relatorio.js     # PDF/XLSX/SQL
│   │       ├── rastreamento.js  # Lógica de rastreamento
│   │       └── tracking-cliente.js
│   ├── docs/
│   │   └── rastreamento_entregas.md
│   └── logs/
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── iniciar_tudo.bat
```

## Convenções e Decisões de Arquitetura

- **API prefixo:** `/api/v1` — todas as rotas backend usam esse prefixo
- **Auth:** JWT com `HS256`, tokens em `sessionStorage`, 24h expiração
- **Admin protegido:** rotas admin usam `Depends(get_admin_user)`, entregador usa `Depends(get_entregador_user)`
- **Site público:** rotas em `routes/site.py`, não precisa de auth (usa telefone como identificador)
- **SSE:** `sse_manager.py` com `asyncio.Queue`, ping a cada 15s, notificações via `notify('refresh', payload)`
- **WebSocket:** `delivery_realtime.py` para GPS em tempo real (entregador → cliente)
- **Frontend:** SPA vanilla — admin carrega todas as seções e mostra/esconde via `.ativa` no CSS
- **Estilo:** dark theme (#0a0e1a), cor primária #06b6d4 (cyan), variáveis CSS em `:root`
- **Grid:** `auto-fit` com `minmax` para layouts responsivos
- **Padrão de rotas:** `apiGet` / `apiSend` / `apiDelete` em `api.js` — wrappers com lock de duplicatas
- **Banco:** pool de 10 conexões, queries com `%s` (mysql-connector), commit manual
- **Pix:** Mercado Pago优先 quando `MERCADO_PAGO_ACCESS_TOKEN` existe, fallback para `pix_manual.py`

## O que está funcionando

- Fluxo completo: cliente → pedido → Pix → admin → entregador → entrega com código
- CRUD de clientes, entregadores, produtos, cupons
- Dashboard com gráficos (Chart.js), métricas, skeleton loading, tendências
- Suporte por chat (cliente ↔ admin) com anexos e lightbox
- SSE para atualização em tempo real do admin
- Webhook Mercado Pago para confirmação automática de pagamento
- Backup SQL, relatórios PDF/Excel
- GPS tracking (entregador envia localização, backend salva, WebSocket transmite)
- Rastreamento para cliente (página dedicada)
- Filtros persistidos no localStorage
- Confirmação antes de ações destrutivas
- Indicador de última atualização no dashboard

## GITHUB

- Ao final de cada sessão fazer commit e se possível push