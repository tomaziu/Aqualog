# Changelog

## [4.2.0] — 2026-05-31
### Adicionado
- Abas no site do cliente: Pedido, Acompanhar e Conversa
- Campo separado para número da casa no cadastro do cliente
- Data de criação do pedido na confirmação e na consulta
- Exibição de data nos pedidos salvos localmente
- Layout de chat com bolhas, horário por mensagem e campo de envio dedicado

### Modificado
- Conversa de suporte do cliente ficou em uma aba dedicada
- Suporte do admin ficou visualmente alinhado com o chat do cliente
- Endereço do entregador passa a exibir rua, número e bairro separadamente
- Botões principais do cliente ficaram coloridos, com símbolos e atalhos visuais

## [4.1.0] — 2026-05-31
### Adicionado
- Código de entrega gerado pelo site no momento do pedido
- Validação do código ao entregador finalizar a entrega
- Atribuição de entregador diretamente na tabela de pedidos do admin
- Campo `codigo_entrega` em `pedidos`
- Pix Mercado Pago com QR Code, copia e cola e link de pagamento
- Status de pagamento separado do status de entrega
- Suporte por conversa entre cliente e admin
- Sessão local do cliente com dados e últimos pedidos salvos no aparelho

### Modificado
- Cliente continua sem escolher entregador; a loja atribui pelo painel admin
- Consulta de pedido no site mostra o código enquanto o pedido está ativo
- Criação de pedido no admin fica como fluxo manual/balcão, não como caminho principal

## [4.0.0] — 2026-05-30
### Adicionado
- Site público do cliente em `/cliente.html`
- API pública para pedido online:
  - `GET /api/v1/site/produtos`
  - `GET /api/v1/site/config`
  - `POST /api/v1/site/pedidos`
  - `GET /api/v1/site/pedidos/{id}?telefone=...`
- Criação de pedido pelo site com cadastro/atualização de cliente por telefone
- Consulta de status pelo cliente no site
- Abertura automática da tela do cliente no `iniciar_tudo.bat`

### Modificado
- Fluxo principal passa a ser site do cliente + painel admin + tela do entregador
- Entregador confirma entrega sem envio externo de mensagem
- Documentação atualizada para o novo fluxo baseado no site do cliente

### Removido
- Bot de mensagens externo
- Integração de envio externo
- Webhooks e simulador de mensagens externas
- Código de segurança enviado por mensagens externas
- Scripts e testes específicos dessas integrações

## [3.0.0] — 2026-05-30
### Adicionado
- Autenticação JWT + bcrypt
- Pool de conexões MySQL
- Paginação nos endpoints
- Validação de estoque ao criar pedido
- Histórico de status do pedido
- SSE para atualização em tempo real do admin
- Dashboard e relatórios PDF/XLSX
