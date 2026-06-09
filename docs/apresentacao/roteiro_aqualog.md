# Roteiro de apresentação - AquaLog

Tempo sugerido: 8 a 10 minutos

## Slide 1 - Abertura

"Boa [tarde/noite]. O nosso projeto se chama AquaLog, um sistema pensado para distribuidoras de água controlarem pedidos, pagamentos, suporte e entregas em um único lugar."

"A ideia principal é transformar um processo que normalmente acontece por mensagens soltas em um fluxo organizado, com cliente, administrador e entregador conectados."

## Slide 2 - Problema

"Antes do sistema, o pedido podia se perder entre WhatsApp, anotação manual e confirmação informal. Isso cria três problemas: falta de controle do pagamento, dificuldade de saber em que etapa está a entrega e risco de finalizar uma entrega sem garantia."

"No começo a ideia envolvia WhatsApp, mas a integração ficou instável para apresentar com segurança. Então evoluímos para um site completo, mantendo a parte mais importante da proposta: o código de entrega."

## Slide 3 - Solução

"A solução foi dividir o sistema em três áreas. O cliente faz o pedido no site, o administrador acompanha e gerencia tudo, e o entregador usa uma tela simples para executar as entregas."

"O pedido passa por um fluxo claro: escolher produto, pagar por Pix, liberar o código, atribuir entregador, sair para rota e finalizar com conferência do código."

## Slide 4 - Site do cliente

"Aqui vemos a tela do cliente. Ele escolhe o produto, preenche nome, telefone, endereço, número da casa, bairro e referência. O objetivo foi deixar o pedido simples, mas completo o suficiente para evitar erro na entrega."

"Também existe a aba de acompanhar pedido, para o cliente não perder o status mesmo se fechar e abrir o site depois."

## Slide 5 - Pix e código de entrega

"Para reduzir pedidos falsos ou sem garantia, o fluxo principal usa Pix. Com Mercado Pago, o sistema gera o pagamento e só libera o código quando o pagamento está confirmado."

"Esse código é importante porque o entregador só finaliza a entrega quando o cliente informa o código correto. Assim, o sistema cria uma confirmação simples, mas eficiente."

## Slide 6 - Painel administrativo

"No painel do administrador temos dashboard, cadastro de clientes, entregadores, produtos, pedidos e suporte. A aba de pedidos mostra pagamento, confirmação, entregador, status, data e código."

"Mantivemos a criação manual de pedido no admin para telefone, balcão ou teste, mas o fluxo principal recomendado é o cliente pedir pelo site."

## Slide 7 - Suporte em tempo real

"O suporte funciona como um chat entre cliente e administrador. Se o cliente tiver dúvida sobre pagamento ou entrega, ele conversa direto pelo site."

"O admin recebe as conversas na aba Suporte, pode responder e também apagar chats antigos. As atualizações usam eventos em tempo real, então o sistema não depende de ficar atualizando a página manualmente."

## Slide 8 - Tela do entregador

"A tela do entregador foi feita para ser bem visual e funcionar no celular. Ele faz login por código, vê quantos pedidos tem em cada status e abre os pedidos atribuídos."

"Quando sai para entrega, o status muda para o cliente. No final, o entregador pede o código de entrega e só conclui se estiver correto."

## Slide 9 - Tecnologias e arquitetura

"Tecnicamente, o projeto foi dividido em camadas. O HTML, CSS e JavaScript formam a camada de interface: cliente, administrador e entregador. Essas telas não acessam o banco diretamente; elas se comunicam com o backend por requisições HTTP, usando `fetch`, JSON e endpoints REST."

"De forma simples, `fetch` é a função do JavaScript que chama o backend; JSON é o formato dos dados enviados e recebidos; e endpoint REST é o endereço da API, como `/api/v1/pedidos` ou `/api/v1/produtos`."

"O FastAPI fica como camada de aplicação. Ele concentra as regras do sistema: autenticação, permissões, criação do pedido, validação do pagamento, atribuição do entregador, mudança de status e conferência do código de entrega."

"O MySQL é a camada de persistência. Ele armazena clientes, produtos, entregadores, pedidos, mensagens de suporte, status e dados de pagamento. Isso permite que o pedido continue salvo mesmo se o usuário fechar o site."

"A integração com Mercado Pago acontece pelo backend. Primeiro, a API cria uma cobrança Pix e retorna os dados para o cliente pagar. Depois, quando o pagamento é confirmado, o Mercado Pago chama o webhook do sistema. Esse webhook atualiza o pedido no MySQL e libera o código de entrega."

"Para evitar atualização manual da página, usamos SSE, que significa Server-Sent Events. É um canal HTTP aberto do servidor para o navegador. Quando muda pagamento, suporte ou status da entrega, o backend envia um evento e as telas atualizam a informação em tempo real."

## Slide 10 - Fechamento

"Para resumir: o AquaLog organiza o processo inteiro de uma distribuidora, desde o pedido até a entrega. O cliente tem clareza, o admin tem controle e o entregador tem uma tela objetiva."

"Como próximos passos, poderíamos melhorar o histórico financeiro, criar notificações mais completas e preparar uma versão online com domínio fixo. Obrigado, agora podemos mostrar rapidamente o sistema funcionando."

