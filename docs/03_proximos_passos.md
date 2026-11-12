# Roadmap — O que vem depois (Agora, Em breve, No futuro)

**Integrante:** Angelo  
**Função:** Próximas melhorias do ÁquaLog, explicadas como novidades para o cliente  
**Duração sugerida:** 5 minutos

---

## Para quem está lendo

Este documento mostra o caminho de evolução do ÁquaLog em três fases: **Agora** (o que estamos fazendo hoje para deixar o sistema sólido), **Em breve** (novidades que o cliente vai sentir nos próximos meses) e **No futuro** (grandes saltos que transformam o negócio).

Quem deve ler: todos os integrantes, professores e avaliadores que querem entender **para onde o produto vai** sem termos técnicos.

---

## Em uma frase

O roadmap do ÁquaLog segue a lógica: **primeiro conserta o que existe, depois adiciona o que o cliente pede, por fim cria o que ninguém tem** — sempre medindo se a novidade realmente ajuda a distribuidora a vender mais e trabalhar menos.

---

## Roteiro de apresentação

| Bloco | O que mostrar na tela | O que falar (resumo) | Tempo |
|-------|----------------------|----------------------|-------|
| 1 | Linha do tempo: Agora → Em breve → Futuro | "Dividimos em 3 fases. Agora: base sólida. Em breve: GPS inteligente, WhatsApp, nota fiscal. Futuro: IA, marketplace." | 1 min |
| 2 | Lista "Agora" com checkmarks | "Testes automáticos, backup diário, logs, correção de bugs — o invisível que garante que não para." | 1 min |
| 3 | Demonstração conceitual: Rota otimizada | "Entregador recebe a melhor ordem de entregas, economiza combustível e tempo." | 1 min |
| 4 | Mockup: Notificação WhatsApp + Nota fiscal | "Cliente avisa 'Seu pedido saiu', nota fiscal sai automática — sem digitação." | 1 min |
| 5 | Visão de futuro: IA + Marketplace | "Sistema prevê demanda, sugere compra, conecta fornecedor — distribuidora vira plataforma." | 1 min |

---

## Conteúdo principal

### 1. Como decidimos o que entra no roadmap

Não colocamos ideias aleatórias. Usamos 5 critérios com peso:

| Critério | Peso | Pergunta que a gente faz |
|----------|------|--------------------------|
| **Resolve dor real do cliente?** | 35% | "Isso faz o dono dormir mais tranquilo ou o entregador chegar mais rápido?" |
| **Esforço para construir** | 25% | "Vai levar 2 semanas ou 6 meses? Vale a pena agora?" |
| **Diferencia da concorrência** | 20% | "Outros sistemas de água já têm isso? Se não, é nosso diferencial." |
| **Gera receita ou upsell** | 15% | "Permite cobrar mais no plano Pro/Enterprise?" |
| **Prepara o futuro (SaaS)** | 5% | "Ajuda a transformar em produto para várias empresas?" |

**Regra prática:** Se a soma der **acima de 70**, entra no "Agora". Entre **50 e 70**, "Em breve". Abaixo de **50**, fica no "Futuro" ou no baú de ideias.

> **Em resumo:** Priorizamos o que **ajuda o cliente hoje**, com **esforço razoável**, e que **ninguém mais tem**.

---

### 2. FASE 1 — AGORA (0 a 3 meses) — "Base Sólida"

O foco é **o que o cliente não vê, mas sente se faltar**: estabilidade, segurança, velocidade.

| Melhoria | O que é | Benefício para a distribuidora | Esforço |
|----------|---------|--------------------------------|---------|
| **Testes automáticos (CI/CD)** | Robô que testa o sistema a cada mudança no código | Evita que atualização quebre o que já funciona | 2–3 semanas |
| **Backup diário automático + fora do servidor** | Cópia do banco vai para nuvem (Wasabi) toda madrugada | Se o servidor queimar, restaura ontem em 30 min | 3 dias |
| **Rate limit (proteção contra abuso)** | Bloqueia quem tenta acessar 100+ vezes por minuto | Site não cai por ataque ou robô | 1 semana |
| **Logs estruturados + alerta** | Erros salvos de forma organizada, avisa no WhatsApp do dev | Descobre bug antes do cliente reclamar | 1 semana |
| **Health check completo** | Verifica se banco, Mercado Pago, mapas estão vivos | Painel mostra "Tudo ok" ou "Atenção: mapa fora" | 2 dias |
| **Correção de gaps críticos** | Editar pedido depois de criado, cancelar com motivo, importar CSV | Operação real: cliente liga pedindo mudança | 2–3 semanas |

> **Em resumo:** Nesta fase, **o cliente não vê novidade na tela**, mas o sistema **para de dar susto no dono** — não cai, não perde dado, não quebra sem aviso.

---

### 3. FASE 2 — EM BREVE (3 a 9 meses) — "O que o cliente pede"

Aqui entram as funcionalidades que **o cliente vê, usa e elogia**.

#### 3.1 GPS Inteligente — Rota otimizada + Geofencing

```
Hoje: Entregador decide a ordem na cabeça → vai e volta desnecessário
Futuro: Sistema calcula a melhor ordem → economiza 30% combustível + tempo
```

| Novidade | O que faz | Ganho real |
|----------|-----------|------------|
| **Rota otimizada (OSRM)** | Sistema monta a melhor sequência de entregas do dia | -30% km rodados, -20% tempo na rua |
| **Navegação no celular (MapLibre)** | Setas, voz, recálculo se sair da rota | Entregador não erra rua, não precisa decorar |
| **Geofencing (cerca virtual)** | Detecta quando chegou/saiu do endereço automaticamente | Status "Entregue" vira sozinho, sem digitar código |
| **Histórico de trajetos (heatmap)** | Mapa de calor: onde passa mais, onde demora mais | Dono vê gargalo: "Sempre atrasa no bairro X" |
| **Simulador de capacidade** | "Se eu contratar +1 entregador, quantos pedidos a mais entrego?" | Decisão de contratação baseada em dados |

> **Em resumo:** O entregador vira **motorista de app** — rota pronta, navegação por voz, prova de entrega automática.

#### 3.2 Notificações Multicanal — WhatsApp, Push, SMS, E-mail

| Canal | Quando usa | Exemplo real |
|-------|------------|--------------|
| **WhatsApp** (principal) | Confirma pedido, avisa "saiu para entrega", código de entrega, pesquisa satisfação | "Seu pedido #123 saiu para entrega! Carlos chega em ~15 min. Código: 847291" |
| **Push no celular** | Tempo real: "Entregador a 5 min" | Cliente vê notificação sem abrir WhatsApp |
| **SMS** (reserva) | WhatsApp falhou / cliente sem internet | "Pedido #123 a caminho. Código: 847291" |
| **E-mail** | Relatórios semanais, backup, recuperação de senha | "Relatório semanal: 87 pedidos, R$ 2.340,00" |

**Regra:** Tenta WhatsApp → se falha, Push → se falha, SMS → e-mail. Tudo automático, sem o dono clicar em nada.

> **Em resumo:** O cliente **nunca fica sem saber** — a mensagem chega pelo canal que ele tem na mão.

#### 3.3 Controle de Estoque Avançado

| Necessidade | Solução |
|-------------|---------|
| Vários depósitos (filial Centro, filial Bairro) | Estoque por depósito + transferência entre eles |
| Galões retornáveis (vazios que voltam) | Controle de lote/validade (FIFO: o que entrou primeiro sai primeiro) |
| Ponto de reposição | Alerta automático: "Galão 20L abaixo de 10 unidades — hora de comprar" |
| Inventário rápido | Contagem por amostragem no celular + relatório de divergência |
| Leitura de código de barras/QR | Câmera do celular lê etiqueta → baixa no estoque na hora |

> **Em resumo:** Acaba o "não sei quantos galões tenho" — estoque vira **número confiável** na tela.

#### 3.4 Nota Fiscal (NF-e / NFC-e) — via parceiro

| Opção | Como funciona | Esforço |
|-------|---------------|---------|
| **Integrar emissor SaaS (NFe.io, Focus NFe, Arquivei)** | API pronta: sistema manda dados → emissor autoriza na SEFAZ → devolve XML + DANFE PDF | 2–3 meses |
| **Próprio emissor (certificado A1/A3)** | Sistema assina, envia para SEFAZ, gera DANFE, guarda XML, SPED Fiscal | 6–8 meses |

**Recomendação:** Começar com **parceiro SaaS** — onboarding em dias, suporte fiscal incluso, custo por nota.

> **Em resumo:** Nota fiscal sai **automática** quando o pedido é confirmado — contador recebe XML, cliente recebe DANFE, dono não digita nada.

---

### 4. FASE 3 — NO FUTURO (9 a 18+ meses) — "Salto de patamar"

Coisas que **ninguém tem no mercado de água** e viram **produto à parte**.

#### 4.1 Business Intelligence (BI) — Painel de dono inteligente

| Módulo | Pergunta que responde |
|--------|----------------------|
| **Dashboard executivo** | "Qual meu lucro real essa semana? Qual cliente mais lucrativo?" |
| **Logística analytics** | "Qual rota mais eficiente? Qual entregador mais rápido? Custo por km?" |
| **Previsão de demanda** | "Vou vender quantos galões 20L na próxima semana? (base: histórico + clima + feriado)" |
| **Análise de coorte** | "Clientes que entraram em janeiro ainda compram em junho?" |

**Tech:** Metabase ou Apache Superset (grátis, open source) + dbt (transformação de dados).

> **Em resumo:** Dono para de chutar e **toma decisão com dados**.

#### 4.2 Marketplace & Ecossistema

- **Portal do Fornecedor:** Fábrica de galões vê pedidos de reposição automáticos (baseado no ponto de reposição).
- **Integração ERPs:** API aberta para Tiny, Bling, Omie, ContaAzul — pedido cai no ERP do contador automaticamente.
- **White-label total:** Domínio próprio, logo, cores, e-mail transacional, CSS customizado — cliente nem sabe que é ÁquaLog.

> **Em resumo:** ÁquaLog vira **plataforma** que conecta distribuidora ↔ fornecedor ↔ contador ↔ cliente final.

#### 4.3 IA Aplicada — O que dá para fazer com os dados

| Caso de uso | Como funciona | Dado necessário |
|-------------|---------------|-----------------|
| **Previsão de atraso** | "Entregador Carlos vai atrasar 15 min na entrega #456" (trânsito + histórico + clima) | GPS histórico + OpenWeather + pedidos |
| **Otimização dinâmica de carga** | Recalcula rotas em tempo real se entra pedido urgente ou entregador quebra | Simulador + dados reais |
| **Chatbot de suporte (RAG)** | Cliente pergunta "Onde está meu pedido?" → IA responde com dados do sistema (sem humano) | Base de conhecimento + pedidos em tempo real |
| **Detecção de fraude no Pix** | "Pagamento atípico: valor alto, horário madrugada, IP diferente do endereço" | Logs de transação + device fingerprint |

> **Em resumo:** IA não é mágica — é **padrão nos dados** que o sistema já guarda. Quando tiver volume (10k+ pedidos/mês), esses modelos viram **produto vendível**.

---

### 5. Visão consolidada — Linha do tempo

```
MES:    1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18
        │──┤  │──┤  │──┤  │──┤  │──┤  │──┤  │──┤  │──┤  │──┤
AGORA   ████████  (Testes, Backup, Logs, Rate limit, Health, Gaps)
EM BREVE      ████████████████  (Rota otimizada, WhatsApp, Estoque, NF-e)
FUTURO                    ████████████████████  (BI, Marketplace, IA)
```

> **Em resumo:** Não tentamos fazer tudo junto. **Entregamos valor a cada fase**, medimos, aprendemos e decidimos o próximo passo.

---

## Palavras que você vai ouvir (glossário)

| Termo | Definição simples | Exemplo no roadmap |
|-------|-------------------|-------------------|
| **Roadmap** | Mapa do caminho — o que vem agora, depois, depois | Este documento |
| **CI/CD** | Integração contínua / Deploy contínuo — robô que testa e publica | "Push na main → roda testes → sobe pro servidor" |
| **OSRM** | Motor de rota open source (OpenStreetMap) — calcula melhor caminho | Rota otimizada do entregador |
| **Geofencing** | Cerca virtual no mapa — dispara ação ao entrar/sair | "Chegou no endereço → status vira Entregue" |
| **Heatmap** | Mapa de calor — cor mostra intensidade (vermelho = muito, azul = pouco) | Onde o entregador mais passa / demora |
| **FIFO / FEFO** | First In First Out / First Expired First Out — controle de lote/validade | Galão que entrou primeiro sai primeiro |
| **NF-e / NFC-e** | Nota Fiscal Eletrônica / Nota Fiscal Consumidor Eletrônica | Nota automática na SEFAZ |
| **SEFAZ** | Secretaria da Fazenda estadual — autoriza notas fiscais | Órgão que valida a NF-e |
| **Certificado A1/A3** | Certificado digital ICP-Brasil (A1 = arquivo, A3 = token) | Assina a NF-e digitalmente |
| **SPED / EFD** | Escrituração Fiscal Digital — arquivo que o contador entrega pro governo | Bloco C, K, H do SPED |
| **BI (Business Intelligence)** | Painel que transforma dados em decisões | "Lucro por cliente", "Previsão de demanda" |
| **dbt** | Ferramenta que transforma dados brutos em tabelas prontas para BI | Limpa, junta, calcula — tudo versionado |
| **RAG (Retrieval-Augmented Generation)** | IA que busca na sua base antes de responder | Chatbot que lê o manual + pedidos reais |
| **White-label** | Produto com a marca do cliente (domínio, logo, cores) | aguajoao.com.br roda ÁquaLog por baixo |
| **Marketplace** | Plataforma que conecta compradores e vendedores | Fornecedor vê pedido de reposição automático |

---

## Perguntas que a turma pode fazer (e como responder)

**1. "Por que não faz tudo de uma vez?"**  
> Porque **software grande feito tudo junto falha**. A gente entrega pedaços que funcionam, mede se o cliente usa, corrige, e só então vai pro próximo. Menos risco, aprendizado real.

**2. "E se o cliente não quiser WhatsApp (prefere SMS)?"**  
> O sistema tenta WhatsApp → se não entrega, manda SMS → se não entrega, manda e-mail. O cliente recebe pelo canal que funcionar. A gente não obriga um só.

**3. "Nota fiscal é obrigatório? Dá para lançar depois?"**  
> Para distribuidora de água/gás, **sim, é obrigatório** por lei. Hoje muita gente faz manual ou no contador. A integração tira o trabalho manual e o risco de erro. Pode lançar depois, mas automatizado é mais seguro.

**4. "IA não é modinha? Dá retorno?"**  
> IA só faz sentido **com volume de dados** (10k+ pedidos/mês). Antes disso, heurística simples (regras) resolve. No roadmap, IA entra no "Futuro" — só quando tiver dado para treinar. Não é modinha, é consequência de escala.

**5. "Como mede se a novidade valeu a pena?"**  
> Métricas por feature: **adoção** (% de clientes que usam), **NPS** (satisfação), **redução de tempo/erro** (ex: rota otimizada → -30% km). Se não move a agulha, a gente remove ou melhora.

---

## Próximos passos (ações concretas)

| Semana | Ação | Responsável | Entregável |
|--------|------|-------------|------------|
| 1–2 | Configurar GitHub Actions (CI/CD) + testes mínimos | Dev | Pipeline verde no push |
| 3–4 | Backup automático offsite (Wasabi) + restauração testada | Dev | Backup de ontem restaurado em < 30 min |
| 5–6 | Rate limit + Health check + Logs estruturados | Dev | Alertas no WhatsApp do dev |
| 7–10 | Gaps críticos: editar pedido, cancelar, importar CSV | Dev + PO | Demo para piloto |
| 11–14 | Spike OSRM (Docker local) + protótipo rota 10 pedidos | Dev | Mapa com rota otimizada |
| 15–18 | PWA Push + WhatsApp API (provedor) + Geofencing | Dev | Notificação real no celular |
| 19+ | Decisão: App nativo vs PWA avançado (baseado em adoção) | PO + Tech | ADR documentado |

---

## Premissas usadas neste documento

- Roadmap baseado em critérios ponderados (dor do cliente 35%, esforço 25%, diferenciação 20%, receita 15%, futuro 5%).
- Fases: Agora (0–3m), Em breve (3–9m), Futuro (9–18m+).
- Tecnologias citadas: OSRM (rota), MapLibre (mapa), WhatsApp Cloud API (Meta), parceiro NF-e (NFe.io/Focus), Metabase/Superset (BI), dbt (transformação).
- Custos de APIs externas (WhatsApp, SMS, Mapas, NF-e) são estimativas — validar no site oficial.
- IA só entra quando houver volume de dados suficiente (>10k pedidos/mês) para treino.
- Time técnico pequeno (2–3 devs) — escopo ajustado à capacidade real.
- Medição de sucesso por feature: adoção, NPS, redução de tempo/erro.