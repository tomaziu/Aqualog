# Transformar em produto para várias empresas (SaaS Multi-tenant)

**Integrante:** Fernando  
**Função:** Explicar como o ÁquaLog vira uma plataforma que atende várias distribuidoras ao mesmo tempo  
**Duração sugerida:** 5 minutos

---

## Para quem está lendo

Este documento explica, em linguagem de negócio, o que significa transformar o ÁquaLog de "sistema de uma empresa" para "plataforma que serve centenas de distribuidoras". Usa a analogia do **prédio de apartamentos** para tornar claro o isolamento de dados.

Quem deve ler: todos os integrantes, professores e avaliadores que precisam entender o **modelo de negócio SaaS** sem termos de arquitetura de software.

---

## Em uma frase

O ÁquaLog deixa de ser "um sistema instalado no computador de cada distribuidora" e passa a ser **um serviço na nuvem** onde cada distribuidora tem seu "apartamento" isolado — mesma estrutura, chaves diferentes, contas separadas, manutenção única.

---

## Roteiro de apresentação

| Bloco | O que mostrar na tela | O que falar (resumo) | Tempo |
|-------|----------------------|----------------------|-------|
| 1 | Desenho: Casa própria vs Prédio de apartamentos | "Hoje: cada um constrói sua casa. SaaS: todos moram no mesmo prédio, apartamentos isolados." | 1 min |
| 2 | Tela de login: subdomínio (aguajoao.aqualog.app) | "Cliente acessa pelo seu endereço, vê sua marca, seus dados — não vê ninguém mais." | 1 min |
| 3 | Painel Super-Admin (lista de distribuidoras) | "A gente (plataforma) vê todos os 'apartamentos', controla planos, suspende se não pagou." | 1 min |
| 4 | Onboarding: cadastro → trial 14 dias → primeiro pedido | "Distribuidora se cadastra sozinha, testa 14 dias grátis, faz primeiro pedido em 30 min." | 1 min |
| 5 | Domínio próprio + Branding (aguajoao.com.br) | "Cliente pode usar seu próprio domínio, logo, cores — parece sistema dele, não nosso." | 1 min |

---

## Conteúdo principal

### 1. A analogia do prédio de apartamentos

| Hoje (Single-tenant) | Futuro SaaS (Multi-tenant) |
|----------------------|----------------------------|
| Cada distribuidora **instala** o sistema no próprio computador/servidor | Todas usam o **mesmo sistema na nuvem** |
| Cada uma **cuida do seu servidor** (backup, atualização, segurança) | **A gente cuida de tudo** (servidor, backup, atualização, segurança) |
| Se quer mudar algo, **precisa de técnico** | Mudança **vale para todos** de uma vez (deploy único) |
| Dados ficam **no computador de cada uma** | Dados ficam **no mesmo banco**, mas **isolados por "chave"** |
| Atualização: **instala em cada lugar** | Atualização: **sobe uma vez, todos recebem** |
| Custo: **servidor próprio + técnico** | Custo: **mensalidade fixa** (inclui tudo) |

**A analogia do prédio:**
- O **prédio** = infraestrutura (servidor, banco de dados, segurança, backup).
- Cada **apartamento** = uma distribuidora (dados isolados, chave própria).
- O **porteiro** = autenticação (só entra no seu apartamento).
- O **síndico** = Super-Admin (a gente, que gerencia o prédio).
- A **conta de água/luz** = mensalidade do plano (inclui manutenção do prédio).

> **Em resumo:** Multi-tenant é **economia de escala** — uma estrutura serve centenas, cada uma com privacidade total.

---

### 2. Como fica o acesso para cada distribuidora

| Tipo de acesso | Exemplo | Como funciona |
|----------------|---------|---------------|
| **Subdomínio padrão** | `aguajoao.aqualog.app` | Criado automaticamente no cadastro. Grátis. |
| **Domínio próprio** | `aguajoao.com.br` ou `entregas.joao.com.br` | Cliente aponta DNS para a gente. A gente emite SSL grátis (Let's Encrypt). |
| **Aplicativo (futuro)** | App "Água do João" na Play Store | Mesmo sistema, mesma conta, interface nativa. |

**O que o cliente vê ao entrar:**
- Logo da **Água do João** (não do ÁquaLog).
- Cores da **Água do João**.
- Domínio **aguajoao.com.br**.
- Seus produtos, seus clientes, seus entregadores.
- **Zero** dado de outra distribuidora.

> **Em resumo:** Cada distribuidora tem **a cara dela**, no **endereço dela**, vendo **só os dados dela**.

---

### 3. Isolamento de dados — a "chave do apartamento"

**Pergunta:** "Se todo mundo usa o mesmo banco de dados, uma distribuidora vê os dados da outra?"

**Resposta:** **Não.** O isolamento funciona em **3 camadas**:

| Camada | Como funciona | Analogia |
|--------|---------------|----------|
| **Banco de dados** | Toda tabela tem coluna `tenant_id` (ID da distribuidora). Queries **sempre** filtram por esse ID. | Cada apartamento tem fechadura na porta — só abre com a chave certa. |
| **Backend (API)** | Toda requisição traz o `tenant_id` no token (JWT). O código **nunca** permite acessar dado sem esse ID. | O porteiro confere o crachá antes de deixar entrar no corredor. |
| **Frontend** | Site carrega configuração do `tenant_id` (logo, cores, domínio). Nunca mistura. | A decoração do apartamento é sua — não vê a do vizinho. |

**Exemplo prático:**
```
SELECT * FROM pedidos WHERE tenant_id = 'uuid-da-agua-do-joao' AND id = 123
```
→ Só retorna pedido 123 **se** for da Água do João. Se for da Água do Zé, retorna **vazio**.

> **Em resumo:** O isolamento é **técnico, automático e testado** — impossível vazar dado de um para outro sem bug gravíssimo (que a gente testa todo dia).

---

### 4. Painel Super-Admin — a visão do síndico

A gente (equipe ÁquaLog) tem um painel **só nosso** para gerenciar o "prédio":

| Função | O que faz |
|--------|-----------|
| **Lista de distribuidoras** | Nome, subdomínio, domínio próprio, plano, status (ativo/trial/suspenso), MRR, último acesso |
| **Criar nova distribuidora** | Preenche nome → gera subdomínio → cria admin → envia e-mail com credenciais |
| **Impersonate (entrar como)** | A gente "entra no apartamento" do cliente para ver o que ele vê, ajudar, debugar |
| **Planos e limites** | Define: Básico (3 entregadores, 500 pedidos), Pro (15, 5.000), Enterprise (ilimitado) |
| **Feature flags** | Liga/desliga funcionalidade por plano (ex: rota otimizada só no Pro/Enterprise) |
| **Billing / Uso** | Vê consumo vs limite: pedidos do mês, entregadores ativos, GB de anexos |
| **Logs de auditoria** | Quem criou, suspendeu, mudou plano, fez impersonate — tudo rastreado |
| **Saúde da plataforma** | Status do banco, Redis, workers, webhooks, versão do deploy por distribuidora |

> **Em resumo:** A gente gerencia **centenas de distribuidoras** de um lugar só, sem entrar no dado de ninguém (só com `impersonate` auditado).

---

### 5. Onboarding Self-Service — o cliente entra sozinho

**Fluxo do cadastro ao primeiro pedido:**

```
1. Distribuidora acessa aqualog.app/cadastro
        │
        ▼
2. Preenche: Nome da loja, WhatsApp, E-mail, Cidade/UF, Plano (trial 14 dias)
        │
        ▼
3. Sistema cria:
   - Tenant (distribuidora) com status "trial" (14 dias)
   - Subdomínio: aguajoao.aqualog.app
   - Admin padrão (e-mail informado, senha temporária)
   - Configs padrão (loja fechada, Pix vazio, estoque mínimo 5)
        │
        ▼
4. E-mail de boas-vindas + credenciais + link: aguajoao.aqualog.app/admin
        │
        ▼
5. Primeiro acesso (Wizard guiado 30 min):
   a) Define senha definitiva
   b) Cadastra chave Pix (Mercado Pago ou manual)
   c) Cadastra 1+ produtos (nome, preço, estoque)
   d) Cadastra 1+ entregadores (nome, veículo, código)
   e) Personaliza branding (logo, cores, nome da loja) — opcional
   f) Configura domínio próprio (aguajoao.com.br) — opcional
   g) Faz pedido teste (cliente fictício) → vê fluxo completo
        │
        ▼
6. Pronto! Distribuidora operando em < 30 minutos.
```

**Métrica alvo:** **Time-to-First-Value < 30 min** (do cadastro ao primeiro pedido real processado).

> **Em resumo:** Onboarding **sem humano da nossa parte** — distribuidora entra, configura, testa e decide se assina.

---

### 6. Domínio próprio + Branding — "Parece sistema deles"

| Item | O que personaliza | Como aplica |
|------|-------------------|-------------|
| **Logo** | Aparece no site do cliente, painel, e-mails, PDFs | Upload no painel admin → salva no storage (Wasabi/S3) |
| **Cores** | Primária, secundária, fundo | CSS custom properties (`--brand-primary`) injetadas no site |
| **Favicon** | Ícone na aba do navegador | Upload → serve via CDN |
| **E-mail remetente** | `pedidos@aguajoao.com.br` (não `@aqualog.app`) | Configura no painel → valida DNS (SPF/DKIM) |
| **WhatsApp** | Número que aparece no site/cliente | Campo no painel |
| **Mensagens** | Boas-vindas, termos, privacidade | Editáveis no painel |
| **Domínio próprio** | `aguajoao.com.br` ou `entregas.joao.com.br` | Cliente cria CNAME → a gente valida → emite SSL grátis (Let's Encrypt) |

**SSL automático para domínio próprio:**
- Cliente aponta `CNAME entregas.joao.com.br → aqualog.app`
- A gente detecta → roda ACME (Let's Encrypt) via Cloudflare API → emite certificado → renova sozinho a cada 90 dias.
- **Zero custo, zero toque humano.**

> **Em resumo:** O cliente **acha que é sistema dele** — domínio, marca, cores, e-mail. A gente só cuida da infraestrutura.

---

### 7. Mercado Pago: uma conta master (facilitador) vs conta por distribuidora

| Modelo | Como funciona | Vantagem | Desvantagem |
|--------|---------------|----------|-------------|
| **Conta Master (Facilitador)** — **Recomendado** | A gente tem 1 conta Mercado Pago master. Cada distribuidora é um "seller" subordinado. Split automático: taxa da plataforma + resto pro lojista. | Onboarding **instantâneo** (sem KYC por distribuidora). Split automático. Taxa única negociada. | A gente responde pela conta master (risco regulatório). |
| **Conta por distribuidora** | Cada uma cria conta MP, passa KYC, conecta via OAuth. | Autonomia total. Cada uma negocia sua taxa. | Onboarding **lento** (dias/semanas). KYC por distribuidora. Suporte fragmentado. |

**Recomendação:** Começar com **Conta Master + Split**. Negocia taxa com MP (ex: 0,8% do TPV fica pra plataforma, resto pro lojista). Distribuidora paga a taxa normal do MP (1,99% Pix) — a gente fatia nossa parte por trás.

> **Em resumo:** Com **Conta Master**, a distribuidora **começa a receber Pix no mesmo dia** do cadastro. Sem burocracia.

---

### 8. Custos da plataforma (estimativa, novembro 2026)

| Item | Custo base (1 distribuidora) | Custo para 100 distribuidoras | Observação |
|------|------------------------------|-------------------------------|------------|
| VPS maior (8 vCPU, 16 GB RAM) | R$ 100 | R$ 300 | Escala vertical |
| Redis (filas, cache, rate limit) | Incluso no VPS | R$ 100–300 | ElastiCache ou self-hosted |
| MySQL Gerenciado (RDS/CloudSQL) | R$ 150 | R$ 400 | Backup, HA, replica gerenciados |
| Object Storage (logos, PDFs, anexos) | R$ 5 | R$ 50–200 | Wasabi 1 TB = US$ 6,99/mês |
| SSL domínios próprios | Grátis | R$ 0–50 | Let's Encrypt (limite 50/semana) |
| E-mail transacional (SendGrid/SES) | R$ 5 | R$ 50–200 | 100k e-mails/mês |
| Monitoramento (Grafana Cloud) | Grátis | R$ 100–500 | Logs + métricas + traces |
| **Total estimado / mês** | **~R$ 415** | **~R$ 1.500–2.000** | **Custo por cliente cai de R$ 415 para ~R$ 15–20** |

> **Em resumo:** Economia de escala brutal — **infraestrutura fixa dividida por centenas de clientes**.

---

### 9. LGPD e contratos — o que a lei exige

| Requisito | Como atende no ÁquaLog |
|-----------|------------------------|
| **DPA (Data Processing Agreement)** | Contrato padrão assinado no cadastro (termo digital). A gente é **operador**, distribuidora é **controladora**. |
| **Direito de exclusão** | Botão "Excluir minha conta" no painel → anonimiza dados em 30 dias (backup mantém 90 dias por segurança). |
| **Consentimento cookies** | Banner no site do cliente (opt-in para analytics). |
| **Criptografia** | HTTPS em tudo, senhas com bcrypt, dados sensíveis (Pix, CPF) criptografados no banco. |
| **DPO (Encarregado)** | Indicado nos termos (pode ser sócio da ÁquaLog ou terceirizado). |
| **Relatório de incidente** | Plano de resposta: avisa cliente em 48h, ANPD em 72h se vazamento de dado sensível. |
| **Backup e retenção** | Backup diário (30 dias), mensal (12 meses), anual (7 anos) — conforme legislação fiscal. |

> **Em resumo:** LGPD não é opcional — está **construída no produto** desde o cadastro até a exclusão.

---

### 10. Cronograma de migração para SaaS (4–6 meses)

| Fase | Duração | Entregáveis | Critério de saída |
|------|---------|-------------|-------------------|
| **0. Preparação** | 2 semanas | Repo `aqualog-saas`, CI/CD, testes de isolamento, ADR aprovado | Pipeline verde, 0 vazamento cross-tenant em 10k testes |
| **1. Banco + Auth** | 3 semanas | `tenant_id` em 14 tabelas, JWT com `tid`, middleware resolve tenant, RLS views | Login multi-tenant funciona, 0 acesso cruzado |
| **2. Super-Admin** | 3 semanas | CRUD tenants, impersonate, planos/limites, feature flags, billing stub | Cria tenant → admin entra → faz pedido completo |
| **3. Onboarding & Branding** | 2 semanas | Landing cadastro, wizard 30 min, branding JSON, domínio próprio + SSL auto | Tenant trial cria sozinho → primeiro pedido em < 30 min |
| **4. Piloto 10 clientes** | 4 semanas | Convida 10 distribuidoras (Caxias/MA + região), suporte dedicado | 8/10 ativos após 30 dias, NPS > 40, 0 incidente cross-tenant |
| **5. GA (General Availability)** | 2 semanas | Billing real (Asaas/Stripe), docs público, marketing site, SLA Enterprise | 50+ tenants, MRR > R$ 15k, churn < 5%/mês |

> **Em resumo:** Em **6 meses** a gente tem uma plataforma pronta para vender, com 10 pilotos validando e dinheiro entrando.

---

## Palavras que você vai ouvir (glossário)

| Termo | Definição simples | Exemplo no SaaS |
|-------|-------------------|-----------------|
| **SaaS (Software as a Service)** | Software como serviço — aluga o uso, não compra a licença | ÁquaLog cobra mensalidade, cuida do servidor |
| **Multi-tenant (Multi-inquilino)** | Uma instalação serve vários clientes isolados | 100 distribuidoras no mesmo banco, dados separados |
| **Single-tenant** | Uma instalação para um cliente só | Versão atual do ÁquaLog |
| **Tenant (Inquilino)** | Cada cliente/distribuidora na plataforma | Água do João = tenant A, Água do Zé = tenant B |
| **Shared Database + Shared Schema** | Modelo multi-tenant: mesmo banco, mesmas tabelas, isolamento por coluna `tenant_id` | Nossa escolha — barato, simples, escalável |
| **Row Level Security (RLS)** | Banco filtra linhas automaticamente por política | `SELECT * FROM pedidos WHERE tenant_id = current_tenant()` |
| **Impersonate** | Super-admin entra como admin do tenant para ajudar/debugar | "Entrar como Água do João" |
| **Feature Flag** | Chave liga/desliga funcionalidade por plano | Rota otimizada = ON no Pro/Enterprise, OFF no Básico |
| **Split de Pagamento (Marketplace)** | Mercado Pago divide valor: taxa plataforma + resto pro lojista | 0,8% pra gente, 99,2% pro lojista |
| **Facilitador de Pagamento (PayFac)** | Entidade que sub-adquire lojistas sob sua conta master | Nossa conta MP Master |
| **KYC (Know Your Customer)** | Verificação de identidade obrigatória para contas financeiras | CPF, selfie, comprovante endereço |
| **DPA (Data Processing Agreement)** | Contrato controlador-operador de dados (LGPD Art. 7º) | Assinado digitalmente no cadastro |
| **Wildcard DNS / SSL** | `*.dominio.com` aponta para mesmo IP; certificado cobre todos subdomínios | `*.aqualog.app` |
| **ACME / DNS Challenge** | Protocolo automático (Let's Encrypt) valida DNS TXT para emitir SSL | Domínio próprio `aguajoao.com.br` |
| **Time-to-First-Value (TTFV)** | Tempo do cadastro ao primeiro resultado real | Meta: < 30 min |
| **MRR (Monthly Recurring Revenue)** | Receita recorrente mensal — soma das assinaturas ativas | 50 clientes × R$ 399 = R$ 19.950 MRR |
| **Churn** | Taxa de cancelamento por mês | Meta: < 3%/mês |
| **CAC (Customer Acquisition Cost)** | Custo para adquirir 1 cliente (marketing + vendas / novos) | Indicação = R$ 0, Ads = R$ 200 |

---

## Perguntas que a turma pode fazer (e como responder)

**1. "E se um cliente não pagar? Como suspende?"**  
> No Super-Admin, muda status para `suspenso`. O sistema bloqueia login, para webhooks, devolve 403 nas APIs. Dados ficam guardados 90 dias. Se pagar, reativa em 1 clique.

**2. "Cliente pode exportar todos os dados e ir embora?"**  
> Sim. Botão "Exportar tudo" no painel admin → gera ZIP com CSV de todas as tabelas + PDFs de relatórios + anexos. LGPD garante portabilidade.

**3. "E se der bug que vaza dado de um tenant pro outro?"**  
> Testes de contrato rodam **todo push** (10k queries aleatórias cross-tenant → devem retornar vazio). RLS no banco como segunda barreira. Se mesmo assim vazar: alerta imediato, correção em minutos, auditoria completa, aviso ao cliente e ANPD se dado sensível.

**4. "Precisa de advogado para fazer o DPA e termos?"**  
> Sim. Modelo base feito por advogado SaaS/LGPD. A gente usa o mesmo para todos. Custo único ~R$ 5–10k. Vale a pena — evita multa de 2% do faturamento (LGPD Art. 52).

**5. "Como cobra a mensalidade? Boleto? Cartão? Pix?"**  
> Integração com **Asaas** ou **Stripe Billing** (brasileiro). Emite boleto, Pix, cartão. Régua de cobrança automática: 5 dias antes (aviso), dia do vencimento, 3 dias depois (2ª via), 7 dias (suspensão). Tudo automático.

---

## Próximos passos

1. **Semana 1:** ADR aprovado (shared DB + tenant_id), branch `saas-mvp`, Alembic configurado.
2. **Semana 2–4:** Migração banco + middleware auth + testes cross-tenant (meta: 0 vazamentos).
3. **Semana 5–7:** Super-Admin CRUD + Impersonate + Planos/Limites + Feature Flags.
4. **Semana 8–10:** Onboarding público + Branding + Domínio próprio + SSL auto.
5. **Semana 11–14:** Piloto 10 clientes (convite direto Caxias/MA), suporte WhatsApp dedicado.
6. **Semana 15+:** Billing real (Asaas), docs público, marketing site, SLA Enterprise → GA.

---

## Premissas usadas neste documento

- Modelo multi-tenant: **Shared Database + Shared Schema** (coluna `tenant_id` + RLS).
- Autenticação: JWT com claim `tid` (tenant_id) + resolução por subdomínio/domínio/Header.
- Conta Mercado Pago **Master (Facilitador)** com split automático — onboarding instantâneo.
- Onboarding **self-service** com trial 14 dias + wizard guiado 30 min.
- Domínio próprio com **SSL automático (Let's Encrypt via Cloudflare API)**.
- LGPD built-in: DPA digital, exclusão/anonymização, criptografia, DPO.
- Custos de infra baseados em preços públicos nov/2026 (Hetzner, AWS, Wasabi, Cloudflare, Asaas).
- Migração em 6 meses para GA com 10 pilotos validando.
- Medição de sucesso: TTFV < 30 min, NPS > 40, 0 incidente cross-tenant.