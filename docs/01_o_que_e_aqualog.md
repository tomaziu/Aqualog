# O que é o ÁquaLog e como funciona

**Integrante:** Thomaz  
**Função:** Visão geral do sistema — para quem nunca viu o ÁquaLog  
**Duração sugerida:** 5 minutos

---

## Para quem está lendo

Este documento explica o que é o ÁquaLog em linguagem simples, para qualquer pessoa da turma entender — mesmo quem nunca trabalhou com tecnologia. Ele serve de base para a apresentação do integrante 1.

Quem deve ler: todos os integrantes, professores e avaliadores que precisam entender o sistema antes de entrar nos detalhes técnicos.

---

## Em uma frase

O ÁquaLog é um sistema que organiza todo o processo de venda e entrega de água — do pedido do cliente no celular até a confirmação na porta de casa — substituindo WhatsApp, caderno e planilha por um fluxo único, rápido e sem erros.

---

## Roteiro de apresentação

| Bloco | O que mostrar na tela | O que falar (resumo) | Tempo |
|-------|----------------------|----------------------|-------|
| 1 | Página inicial do site do cliente | "Aqui o cliente entra, escolhe a água, informa o endereço e paga no Pix. Tudo em menos de 2 minutos." | 1 min |
| 2 | Painel do administrador (lista de pedidos) | "O dono da distribuidora vê todos os pedidos chegando em tempo real, atribui para o entregador e acompanha o status." | 1 min |
| 3 | Tela do entregador (celular com GPS) | "O entregador abre no celular, vê a rota, marca que saiu para entrega e finaliza digitando o código que o cliente recebeu." | 1 min |
| 4 | Acompanhamento do cliente (status + mapa) | "O cliente também vê onde está o pedido, como no aplicativo de delivery, e recebe o código de 6 números para confirmar a entrega." | 1 min |
| 5 | Resumo do fluxo completo (setas no quadro) | "Do pedido ao dinheiro no caixa: cliente pede → admin confirma → entregador leva → cliente recebe → tudo registrado." | 1 min |

---

## Conteúdo principal

### 1. O problema real que o ÁquaLog resolve

Hoje, a maioria das distribuidoras de água em Caxias e região funciona assim:

- O cliente manda mensagem no **WhatsApp** do dono: *"Quero 2 galões de 20 litros"*.
- O dono anota no **caderno** ou numa **planilha Excel**.
- Alguém liga para o entregador: *"Vai na Rua das Flores, 123, Centro"*.
- O entregador vai de **memória** ou anota no papel.
- Na hora de cobrar: *"Paga no Pix pra chave fulano@email.com"* — e o cliente manda o comprovante por WhatsApp.
- No fim do dia, o dono **confere tudo manualmente**: quem pagou, quem não pagou, o que faltou no estoque.

**O que dá errado:**
- Pedidos perdidos no meio de tanta conversa no WhatsApp.
- Endereço errado porque alguém digitou errado no caderno.
- Entregador vai na rua errada ou esquece um pedido.
- Cliente diz que pagou, mas o comprovante sumiu na conversa.
- O dono não sabe **quanto vendeu de verdade** até fechar a planilha à noite.

> **Em resumo:** O ÁquaLog substitui WhatsApp + caderno + planilha + ligações por **um único sistema** onde tudo acontece sozinho, sem papel, sem memória e sem erro de digitação.

---

### 2. Quem usa o sistema (os 3 perfis)

| Perfil | O que faz no sistema | Exemplo real |
|--------|---------------------|--------------|
| **Cliente (Dona Maria)** | Entra no site pelo celular, escolhe a água, digita o endereço, paga no Pix e acompanha a entrega. | Dona Maria pede 2 galões de 20L às 10h, paga R$ 24 no Pix e vê no mapa que o entregador está a 5 minutos. |
| **Administrador (Seu João, dono)** | Vê todos os pedidos na tela do computador, escolhe qual entregador leva cada um, responde dúvidas pelo chat e vê relatórios de venda. | Seu João abre o painel, vê 15 pedidos novos, clica em "Atribuir" para o entregador Carlos e acompanha tudo em tempo real. |
| **Entregador (Carlos)** | Abre no celular, vê a lista de entregas do dia, marca "Saiu para entrega", segue o GPS e finaliza digitando o código de 6 números que o cliente mostra. | Carlos chega na casa da Dona Maria, ela mostra o código **847291** no celular, ele digita no app e a entrega fica "Concluída" na hora. |

> **Em resumo:** Três pessoas, três telas diferentes, mas **um só sistema** conectando tudo.

---

### 3. O caminho do pedido — do começo ao fim

```
Cliente acessa o site
      │
      ▼
Escolhe produtos (galões, garrafas, gás)
      │
      ▼
Preenche endereço (CEP preenche rua/bairro automaticamente)
      │
      ▼
Escolhe pagamento: Pix (gera QR Code) ou "Pagamento teste"
      │
      ▼
Confirma o pedido
      │
      ▼
Sistema cria o pedido → Gera código de 6 números (ex: 847291)
      │
      ▼
Administrador vê o pedido chegar na hora (som de notificação)
      │
      ▼
Se Pix: administrador confirma pagamento → código libera
      │
      ▼
Administrador atribui para o entregador (ex: Carlos)
      │
      ▼
Entregador recebe no celular → Marca "Saiu para entrega"
      │
      ▼
GPS liga → Cliente vê o entregador no mapa em tempo real
      │
      ▼
Entregador chega → Cliente mostra código de 6 números
      │
      ▼
Entregador digita código → Entrega "Concluída" na hora
      │
      ▼
Sistema baixa do estoque → Relatório de venda atualizado
```

> **Em resumo:** O pedido nasce no site do cliente, passa pelo administrador, vai para o entregador e volta confirmado — tudo **automático**, com rastro digital em cada etapa.

---

### 4. O que o cliente ganha com isso

| Antes (WhatsApp + caderno) | Depois (ÁquaLog) |
|---------------------------|------------------|
| Pedido pode sumir na conversa | Pedido fica salvo, ninguém perde |
| Endereço escrito à mão, pode errar | CEP preenche tudo, cliente só confere |
| Não sabe onde está a entrega | Vê no mapa em tempo real |
| Pagamento confuso (qual chave Pix?) | QR Code na tela, paga em 1 clique |
| Comprovante perdido no WhatsApp | Tudo registrado no sistema |
| Dono descobre venda só à noite | Dono vê venda na hora que acontece |

> **Em resumo:** O cliente pede mais rápido, paga com segurança, acompanha a entrega e tem a certeza de que a água vai chegar.

---

### 5. O que a distribuidora ganha

- **Menos erro:** Endereço validado pelo CEP, código de 6 números prova a entrega.
- **Menos tempo no celular:** Não precisa ficar respondendo WhatsApp o dia todo.
- **Controle de estoque:** Quando o pedido é confirmado, o sistema já baixa da quantidade disponível.
- **Relatório pronto:** Vendas do dia, da semana, por entregador, por produto — sem digitar nada.
- **Profissionalismo:** O cliente vê um site com a marca da distribuidora, não um número de WhatsApp pessoal.

> **Em resumo:** A distribuidora passa de "anotação no caderno" para **gestão profissional**, sem precisar contratar programador nem comprar servidor.

---

## Palavras que você vai ouvir (glossário)

| Termo | Definição simples | Exemplo no ÁquaLog |
|-------|-------------------|-------------------|
| **Sistema** | Programa que roda na internet e faz várias tarefas organizadas | O ÁquaLog inteiro (site + painel + app do entregador) |
| **Pedido** | Solicitação de compra feita pelo cliente | "2 galões de 20L para Rua das Flores, 123" |
| **Painel (Dashboard)** | Tela principal onde o administrador vê tudo | Lista de pedidos, botões de ação, gráficos de venda |
| **Pix** | Pagamento instantâneo do Banco Central, dinheiro cai na hora | Cliente escaneia QR Code, paga, sistema confirma em segundos |
| **QR Code** | Código quadrado que o celular lê para pagar | Aparece na tela do cliente após confirmar o pedido |
| **GPS** | Sistema de localização por satélite (como no Google Maps) | Entregador vê a rota; cliente vê o entregador se movendo no mapa |
| **Código de 6 números** | Senha única que prova que a entrega foi feita | Cliente recebe **847291**, entregador digita, entrega fecha |
| **Estoque** | Quantidade de produtos disponíveis para vender | Sistema avisa: "Só tem 3 galões de 20L" |
| **Relatório** | Resumo organizado dos dados (vendas, entregas, estoque) | "Vendemos 120 galões essa semana" |
| **Status** | Etapa atual do pedido | Recebido → Em preparo → Saiu para entrega → Entregue |

---

## Perguntas que a turma pode fazer (e como responder)

**1. "Mas o cliente precisa ter internet para pedir?"**  
> Sim, precisa de internet no celular para acessar o site. Mas a maioria das pessoas já tem 4G ou Wi-Fi. Se não tiver, a distribuidora ainda pode anotar no caderno — o sistema não obriga, só facilita.

**2. "E se o entregador não souber mexer no celular?"**  
> A tela do entregador é bem simples: botões grandes, poucas opções. Dá para treinar em 10 minutos. E se realmente não der, o administrador pode acompanhar pelo computador e avisar por rádio ou telefone.

**3. "O sistema funciona sem internet no depósito?"**  
> O painel do administrador precisa de internet para receber os pedidos em tempo real. Mas se a internet cair por alguns minutos, os pedidos já feitos ficam salvos e o sistema atualiza assim que volta. Não perde nada.

**4. "Quanto custa para a distribuidora usar?"**  
> Isso é o tema do integrante 5 (Miguel). Mas adianto: o custo é uma mensalidade fixa, bem mais barato que contratar um programador ou comprar um sistema caro de grande empresa.

---

## Próximos passos

- Melhorar o site do cliente para funcionar bem em celulares antigos.
- Adicionar opção de pagamento em dinheiro ou cartão na entrega (hoje só Pix).
- Criar relatório de "água que voltou" (galões vazios que o cliente devolve).
- Permitir que o cliente agende a entrega para outro dia/horário.

---

## Premissas usadas neste documento

- O sistema já roda em desenvolvimento (não está em produção real).
- A cidade-base é Caxias/MA, mas serve para qualquer cidade.
- O pagamento principal é Pix (Mercado Pago ou chave manual).
- Não há app nativo na loja (Android/iOS) — roda no navegador (PWA).
- A equipe tem 5 integrantes, cada um com uma função definida.