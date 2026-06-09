# ÁquaLog — Guia para IA

## Visão geral
Sistema de controle de pedidos e entregas para distribuidora de água.
Backend: Python + FastAPI | Frontend: HTML/CSS/JS vanilla | BD: MySQL

## Estrutura
```
backend/
  main.py              # App FastAPI + static mount + API prefix /api/v1
  auth.py              # JWT + bcrypt
  database.py          # Pool de conexões MySQL
  models.py            # Pydantic models
  sse_manager.py       # SSE para admin em tempo real
  routes/              # admin, clientes, entregadores, pedidos, produtos, site
  tests/test_api.py    # Testes unitários
  schema.sql           # Schema MySQL
frontend/
  index.html           # Admin
  cliente.html         # Site público para cliente fazer pedido
  entregador.html      # Tela do entregador
  style.css
  js/
```

## Fluxo principal
1. Cliente acessa `/cliente.html`, escolhe produto, endereço, pagamento e confirma.
2. Se for Pix, backend cria uma order no Mercado Pago e salva QR Code/link no pedido.
3. Sistema gera `codigo_entrega`, mostra ao cliente e cria pedido como `recebido`.
4. Cliente acompanha pedido e suporte pelas abas do site.
5. Admin acompanha pagamento, responde suporte, atribui entregador e altera status.
6. Entregador acessa `/entregador.html`, marca saída e só finaliza com o código informado pelo cliente.

## Regras de negócio
- Status: `recebido → em_preparo → saiu_para_entrega → entregue`
- Ao sair para entrega, entregador fica `ocupado`.
- Ao entregar/cancelar todos os pedidos ativos, entregador volta para `disponivel`.
- Estoque é reduzido ao criar pedido.
- Site público cria/atualiza cliente por telefone.
- Cadastro do cliente usa `endereco` e `numero_casa` separados.
- Cliente não escolhe entregador; a atribuição é feita no painel admin.
- O código de entrega fica em `pedidos.codigo_entrega`.
- Status de pagamento fica separado em `pedidos.pagamento_status`.
- Conversas de suporte ficam em `suporte_mensagens`.
- Admin e entregador usam JWT.
- Admin usa SSE em `/api/v1/events`.

## API
- Prefixo: `/api/v1`
- Admin protegidas por JWT: clientes, entregadores, produtos, pedidos, dashboard.
- Site público:
  - `GET /api/v1/site/produtos`
  - `GET /api/v1/site/config`
  - `POST /api/v1/site/pedidos`
  - `GET /api/v1/site/pedidos/{id}?telefone=...`
  - `POST /api/v1/site/pedidos/{id}/pagamento/atualizar?telefone=...`
  - `GET/POST /api/v1/site/pedidos/{id}/suporte?telefone=...`
- Admin suporte:
  - `GET /api/v1/suporte`
  - `GET /api/v1/suporte/{pedido_id}`
  - `POST /api/v1/suporte/{pedido_id}`

## Pagamento
- O site permite Pix, Dinheiro e Cartão.
- `MERCADO_PAGO_ACCESS_TOKEN` gera Pix via Mercado Pago.
- `PIX_CHAVE` permanece apenas para fallback/manual.

## Manutenção
- Ao mudar regras, atualizar `README.md`, `CHANGELOG.md` e este arquivo.
- Rodar testes:
```bash
cd backend
.\venv\Scripts\activate
pytest tests/ -v
```
