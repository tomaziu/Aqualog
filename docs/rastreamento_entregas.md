# Rastreamento de Entregas em Tempo Real

Este módulo adiciona rastreamento de entregas para o AquaLog sem alterar o fluxo atual de pedidos.

## Banco de dados

Para bancos novos, o `backend/schema.sql` já contém as tabelas:

- `users`
- `drivers`
- `deliveries`
- `delivery_locations`
- `delivery_status_history`

Para bancos existentes, execute:

```bash
cd backend
python migrate_delivery_tracking.py
```

## APIs principais

Todas as rotas usam o prefixo `/api/v1`.

- `GET /deliveries`: lista entregas para o admin, com filtros `status` e `q`.
- `POST /deliveries`: cria uma entrega com origem, destino, cliente e entregador opcional.
- `PATCH /deliveries/{id}/driver`: associa entregador.
- `PATCH /deliveries/{id}/status`: altera status pelo admin.
- `PATCH /deliveries/{id}/status/driver`: altera status pelo entregador autenticado.
- `POST /deliveries/driver/location`: recebe GPS do entregador autenticado.
- `GET /deliveries/{id}/locations`: histórico de localização.
- `GET /site/deliveries/{id}?telefone=...`: consulta autorizada do cliente.
- `WS /deliveries/ws/{id}`: canal WebSocket para atualizações em tempo real.

Status disponíveis:

- `aguardando_coleta`
- `coletado`
- `em_rota`
- `proximo_destino`
- `entregue`
- `cancelado`

## Frontend

Admin:

- Aba `Rastreamento` no painel administrativo.
- Lista entregas em andamento e histórico.
- Filtra por status e busca cliente, entregador ou endereço.
- Exibe ETA, distância restante, tempo decorrido e posição do entregador.
- Cria rastreamento automaticamente a partir de um pedido: a origem vem da localização atual do navegador e o destino vem do endereço cadastrado do cliente.

Entregador:

- O app solicita permissão de localização pelo navegador.
- Usa `navigator.geolocation.watchPosition()`.
- Envia latitude/longitude automaticamente a cada 5 segundos enquanto houver entrega ativa.
- Mostra indicadores: localização ativa, desativada, GPS fraco e sem conexão.
- Permite iniciar e finalizar o compartilhamento.

Cliente:

- Página `/rastreamento.html`.
- Consulta por número da entrega e telefone.
- Recebe atualizações em tempo real via WebSocket.
- Ao fazer pedido pelo site, a localização do cliente é capturada automaticamente se ele permitir o navegador.

## Mapa gratuito

O módulo usa Leaflet com OpenStreetMap, sem chave de API, sem cartão e sem cobrança por chamada.

O mapa é carregado por CDN:

- `https://unpkg.com/leaflet@1.9.4`
- `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`

Para alto volume em produção, considere hospedar um servidor próprio de tiles OpenStreetMap ou contratar um provedor compatível com OSM. Isso evita depender dos limites de uso justo dos tiles públicos.

## Geocodificação automática

Ao criar uma entrega pelo pedido, o sistema usa primeiro a localização real salva do cliente. Se ela não existir, o backend usa o Nominatim/OpenStreetMap para transformar o endereço cadastrado em latitude e longitude. Não há token. O endereço precisa estar preenchido corretamente no cadastro do cliente.

## Autocomplete de endereços

O autocomplete do cliente e do admin consulta o Photon/Komoot, um serviço de busca baseado em dados do OpenStreetMap e feito para sugestões enquanto digita. Não exige token. Se o serviço externo não responder, o sistema usa os endereços já salvos no AquaLog como fallback.

## Segurança

- Admin acessa as entregas com JWT de admin.
- Entregador só envia localização com JWT de entregador.
- Cliente só consulta uma entrega quando informa telefone compatível com o pedido.
- WebSocket valida token do admin/entregador ou telefone do cliente antes de aceitar conexão.

## Implantação

1. Atualize o código no servidor.
2. Execute `python backend/migrate_delivery_tracking.py`.
3. Reinicie a API FastAPI.
4. Configure `JWT_SECRET` em produção.
5. Teste em navegador com HTTPS, pois geolocalização em celulares exige contexto seguro.
