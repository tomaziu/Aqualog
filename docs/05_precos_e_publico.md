# Preços, Planos e Público-Alvo

**Integrante:** Miguel  
**Função:** Quanto custa, para quem serve e por que contrataria  
**Duração sugerida:** 5 minutos

---

## Para quem está lendo

Este documento explica, em linguagem de negócio simples: **quanto custa cada plano**, **o que está incluso**, **para quem o ÁquaLog foi feito** e **por que uma distribuidora contrataria** — sem promessas de lucro garantido, com números realistas e riscos claros.

Quem deve ler: todos os integrantes, professores, avaliadores e potenciais investidores que querem entender o **modelo comercial** do ÁquaLog.

---

## Em uma frase

O ÁquaLog vende **assinatura mensal fixa** (a partir de R$ 149) para distribuidoras de água/gás/bebidas que hoje perdem tempo e dinheiro no WhatsApp + planilha — com preço baseado no custo real de manter o sistema no ar, margem saudável e upsell natural conforme a distribuidora cresce.

---

## Roteiro de apresentação

| Bloco | O que mostrar na tela | O que falar (resumo) | Tempo |
|-------|----------------------|----------------------|-------|
| 1 | Tabela de 3 planos (Básico/Pro/Enterprise) | "Três planos, limites claros, upsell natural: começa no Básico, migra pro Pro quando cresce." | 1 min |
| 2 | Custo real por cliente (infra + taxas) | "A gente sabe exatamente quanto custa servir 1 cliente: ~R$ 46 fixo + variável. Por isso o preço fecha." | 1 min |
| 3 | Perfil do cliente ideal (ICP) + 3 Personas | "Dona Maria (pequena), Seu João (médio), Carlos (entregador) — cada um com dor e ganho claro." | 1 min |
| 4 | Comparação: ÁquaLog vs WhatsApp vs ERP vs App de delivery | "Não concorre com ERP gigante nem com iFood. É nicho: feito P/ÁGUA." | 1 min |
| 5 | Go-to-Market: Indicação + Contador + Associação | "CAC near zero: indicação, parceria contador 10%, feira local. Meta: 50 clientes em 12 meses." | 1 min |

---

## Conteúdo principal

### 1. Os 3 Planos — simples, transparentes, com upsell natural

| Recurso / Limite | **Básico** | **Profissional** | **Enterprise** |
|------------------|------------|------------------|----------------|
| **Mensalidade** | **R$ 149** | **R$ 399** | **R$ 999** |
| **Anual (10% desc.)** | R$ 1.609 (R$ 134/mês) | R$ 4.309 (R$ 359/mês) | R$ 10.789 (R$ 899/mês) |
| **Taxa Implantação (Setup)** | R$ 299 | R$ 499 | R$ 999 (inclui migração de dados) |
| **Entregadores Ativos** | 3 | 15 | Ilimitado |
| **Pedidos/Mês Inclusos** | 500 | 5.000 | Ilimitado |
| **Admins (Usuários Painel)** | 1 | 5 | 20 |
| **Anexos Chat (GB)** | 1 | 10 | 100 |
| **Domínio Próprio + SSL** | Não | Sim (1) | Sim (5) |
| **Branding Customizado** | Logo apenas | Completo (cores, logo, favicon, e-mail) | Completo + CSS custom + white-label total |
| **Rotas Otimizadas** | Não | Sim | Sim + Simulador Capacidade |
| **Geofencing + Histórico Trajetos** | Não | Sim | Sim + Heatmap + KPIs |
| **API Webhooks (saída)** | Não | 100 req/dia | 10.000 req/dia |
| **Integração ERP (Tiny/Bling/Omie)** | Não | Sim (1) | Sim (ilimitado) |
| **NF-e / NFC-e (via parceiro)** | Não | Add-on R$ 199/mês | Incluído (até 1.000 notas/mês) |
| **Suporte** | E-mail (48h úteis) | WhatsApp + E-mail (24h úteis) | Dedicado (SLA 4h + Gerente Sucesso) |
| **Trial** | 14 dias | 14 dias | 30 dias + Onboarding assistido |

#### Adicionais por uso (Overages) — só paga se ultrapassar

| Item | Preço Unitário | Quando cobra |
|------|----------------|--------------|
| Entregador Extra | R$ 29/mês | > limite do plano |
| Pacote 1.000 Pedidos Extra | R$ 99 | > limite mensal |
| Admin Extra | R$ 19/mês | > limite do plano |
| GB Anexos Extra | R$ 19/GB | > limite do plano |
| Domínio Extra | R$ 29/mês | > limite do plano |
| 1.000 Requisições API Extra | R$ 19 | > limite diário |
| 1.000 Notas Fiscais Extra | R$ 149 | > limite Enterprise |
| WhatsApp Conversa Extra | R$ 0,80 | > 500 conversas/mês (incluídas no Pro/Ent) |
| SMS Extra | R$ 0,12 | > 200 SMS/mês (incluídos no Pro/Ent) |

> **Em resumo:** Planos pensados para **crescer junto** — começa no Básico (R$ 149), quando passa 3 entregadores ou 500 pedidos, sobe pro Pro (R$ 399). Sem surpresa, sem taxa escondida.

---

### 2. Por que custa isso? — Custo real por cliente (estimativa, nov/2026)

A gente **sabe exatamente quanto custa servir 1 cliente**. Não chuta.

| Componente | Custo Fixo/Mês | Custo Variável (por uso) | Observação |
|------------|----------------|--------------------------|------------|
| **VPS (servidor na nuvem)** | R$ 8,00 | — | Dividido por 50 clientes no mesmo servidor |
| **Banco de Dados Gerenciado** | R$ 12,00 | — | RDS/CloudSQL dividido por 50 |
| **Redis (cache, filas)** | R$ 4,00 | — | ElastiCache dividido por 50 |
| **Armazenamento (logos, PDFs, anexos)** | R$ 1,50 | R$ 0,19/GB | Wasabi 1 TB = US$ 6,99/mês |
| **CDN / SSL (Cloudflare)** | R$ 0,50 | — | Plano Pro US$ 20 ÷ 50 |
| **Monitoramento (Grafana Cloud)** | R$ 3,00 | — | Free tier até 10k séries |
| **E-mail Transacional (AWS SES)** | R$ 0,50 | R$ 0,10/1.000 emails | US$ 0,10/1.000 |
| **WhatsApp Business API** | R$ 0,00 | **R$ 0,35–0,80/conversa** | Meta + provedor (Zenvia/Wati) |
| **SMS (Twilio/Zenvia)** | R$ 0,00 | **R$ 0,07–0,15/SMS** | Brasil, volume baixo |
| **Mapas (OSRM/Photon self-hosted)** | **Incluso no VPS** | — | Roda no próprio servidor, custo zero marginal |
| **Mercado Pago (Taxa Pix)** | — | **1,99% + R$ 0,60** por venda | Taxa oficial MP (cliente paga, não a gente) |
| **Split MP (Nossa taxa)** | — | **Receita** (0,8% TPV) | A gente *recebe*, não paga |
| **Suporte Humano (N1/N2)** | R$ 15,00 | R$ 50/chamado complexo | 1 agente ÷ 50 clientes |
| **CI/CD + DevOps (amortizado)** | R$ 2,00 | — | GitHub Actions + ferramentas ÷ 50 |
| **TOTAL CUSTO BASE / CLIENTE / MÊS** | **~R$ 46,50** | **Variável por volume** | **Sem impostos (PIS/COFINS/ISS/IRPJ)** |

> **Observação importante:** O **Google Maps Places API** custa **US$ 17/1.000 requisições** — tornaria o Básico/Pro inviáveis. Por isso usamos **OSRM/Photon self-hosted** (open source, roda no nosso VPS, custo zero marginal). Google Maps só no Enterprise se o cliente exigir.

#### Margem por plano (cenário médio, usando OSRM)

| Item | Básico | Profissional | Enterprise |
|------|--------|--------------|------------|
| **Mensalidade** | R$ 149 | R$ 399 | R$ 999 |
| **Receita Split MP (0,8% TPV médio)** | R$ 108 | R$ 1.200 | R$ 6.600 |
| **Receita Total** | **R$ 257** | **R$ 1.599** | **R$ 7.599** |
| **Custo Fixo** | R$ 46,50 | R$ 46,50 | R$ 46,50 |
| **Custo Variável (WhatsApp, SMS, etc.)** | R$ 141,50 | R$ 796,50 | R$ 3.156,50 |
| **Custo Total** | R$ 188 | R$ 843 | R$ 3.203 |
| **Lucro Líquido** | **R$ 69 (27%)** | **R$ 756 (47%)** | **R$ 4.396 (58%)** |

> **Em resumo:** Margem saudável em **todos os planos** porque a gente **controla o custo de infraestrutura** (OSRM self-hosted, VPS próprio, economia de escala). Impostos não incluídos (Lucro Presumido ~16–20% sobre receita bruta).

---

### 3. Simulação de Receita — Crescimento Realista (Cenário OSRM)

| Clientes Ativos | Distribuição (Básico/Pro/Ent) | MRR Mensalidades | MRR Split MP | MRR Total | Custos Totais | Lucro Líquido | Margem |
|-----------------|-------------------------------|------------------|--------------|-----------|---------------|---------------|--------|
| **5** (Mês 3) | 3 / 2 / 0 | R$ 1.245 | R$ 2.508 | R$ 3.753 | R$ 1.542 | **R$ 2.211** | **59%** |
| **20** (Mês 6) | 10 / 8 / 2 | R$ 5.970 | R$ 14.940 | R$ 20.910 | R$ 8.120 | **R$ 12.790** | **61%** |
| **50** (Mês 12) | 20 / 20 / 10 | R$ 14.950 | R$ 41.580 | R$ 56.530 | R$ 20.450 | **R$ 36.080** | **64%** |
| **100** (Mês 18) | 40 / 40 / 20 | R$ 29.900 | R$ 83.160 | R$ 113.060 | R$ 40.900 | **R$ 72.160** | **64%** |

**Premissas:** 0% churn, 100% adimplência, OSRM self-hosted, split MP 0,8%, custos fixos diluem com escala. **Impostos não incluídos** (Lucro Presumido ~16–20%).

> **Em resumo:** Com **50 clientes ativos**, o ÁquaLog gera **~R$ 56k MRR** e **~R$ 36k lucro/mês** — negocio saudável, escalável, sem depender de investidor.

---

### 4. Público-Alvo — Para quem o ÁquaLog foi feito

#### Perfil do Cliente Ideal (ICP)

| Critério | Definição |
|----------|-----------|
| **Segmento Principal** | Distribuidoras de **água mineral (galões 20L/10L/5L)**, **gás GLP (botijão 13kg/P45)**, **bebidas (cerveja, refrigerante, suco)** |
| **Porte** | **Pequeno a Médio**: 2–20 entregadores, 50–5.000 pedidos/mês, faturamento R$ 30k–R$ 500k/mês |
| **Região Inicial** | **Maranhão** (Caxias, Timon, Teresina/PI, São Luís, Imperatriz, Codó) → expansão Nordeste |
| **Modelo Operacional** | Entrega própria (frota própria ou agregados), venda direto ao consumidor (B2C) e pequeno varejo (B2B) |
| **Dores Atuais** | Pedidos no WhatsApp → erros, perdidos, sem prioridade; Planilha → versão única, erros; Caderneta → ilegível; Financeiro → "quanto vendi ontem?"; Entregador → "onde fica essa rua?"; Fiscal → notas manuais |
| **Tecnologia Atual** | Smartphone, WhatsApp Business, Planilha Google Sheets/Excel, às vezes sistema fiscal separado |
| **Budget Tech** | **R$ 150–800/mês** (já pagam contador, sistema fiscal, às vezes app genérico) |
| **Decisor** | **Sócio-proprietário** (dono) — decide sozinho ou com sócio |

#### 3 Personas — Quem decide, quem usa, quem entrega

| Persona | Perfil | Dor Principal | Gatilho de Compra | Objeção Comum |
|---------|--------|---------------|-------------------|---------------|
| **João "Distribuidor Raiz"** (45 anos, dono operacional) | Fundou há 15 anos, conhece cada cliente, trabalha 12h/dia no balcão | "Perco 3–4 pedidos/semana no WhatsApp. Entregador volta com galão errado. Não sei meu lucro real." | Perdeu cliente grande por erro de entrega. Concorrente usou sistema e "organizou tudo". | "Sistema é coisa de grande. Meu filho mexe nisso, eu não. Custa caro pro meu tamanho." |
| **Carlos "Gestor Moderno"** (35 anos, sócio administrativo) | Formado em Adm/Logística, cuida de finanças, compras, RH, quer escalar 3 filiais em 3 anos | "Planilha quebra toda semana. Não tenho visibilidade tempo real. Onboarding entregador demora 1 semana." | Planejando abrir filial. Investidor pediu profissionalização. Feira tech (ExpoLog, NRF). | "Preciso integrar com meu ERP fiscal (Tiny/Bling). API aberta é obrigatório." |
| **Maria "Entregadora Experiente"** (38 anos, 10 anos de rua) | Conhece cada beco, usa WhatsApp no pessoal, smartphone Android 3 anos | "Endereço errado = volta 5km. Cliente não atende, não tem troco. Papel molha/rasga." | Dono impõe. Colega de outra distribuidora disse "facilitou minha vida". App fala por voz. | "App gasta bateria/dados. Não sei mexer em mapa. Prefiro meu jeito." |

> **Em resumo:** O ÁquaLog resolve a dor de **três pessoas ao mesmo tempo** — dono para de perder pedido, gestor ganha visibilidade, entregador para de voltar na rua errada.

---

### 5. Por que contratam — e por que NÃO contratam

#### ✅ Motivos para Contratar (Buy Signals)

| Gatilho | Frase Real do Cliente | Resposta do ÁquaLog |
|---------|----------------------|---------------------|
| **Erro crônico** | "Perdi 3 clientes mês passado por entrega errada" | Endereço validado pelo CEP + GPS + código 6 dígitos = **-90% erro** |
| **Crescimento** | "Vou abrir filial em Timon, preciso padronizar" | Plano Profissional + multi-filial (roadmap) |
| **Profissionalização** | "Meu contador disse que preciso de sistema sério" | Trial 14 dias + onboarding assistido 30 min |
| **Concorrente modernizou** | "O 'Água do Zé' usa sistema e dobrou entregas" | Case study local + referência |
| **Dor fiscal** | "Levei multa por nota errada; contador cobra caro" | Add-on NF-e via parceiro (2–3 meses) |
| **Controle financeiro** | "Não sei meu lucro real; caixa fecha no feeling" | Dashboard tempo real + relatórios PDF/Excel |
| **Cliente pede rastreio** | "Cliente liga: 'cadê minha água?' 10x/dia" | Link rastreamento + código 6 dígitos = **zero ligação** |

#### ❌ Motivos para NÃO Contratar (Objeções Reais) — e como contornar

| Objeção | Raiz | Contorno Honesto |
|---------|------|------------------|
| **"Caro pro meu tamanho"** | Percepção valor vs. custo fixo | "R$ 149 = 3 galões/mês. Evita 1 erro = paga o mês." + Trial 14d grátis |
| **"Meus entregadores não usam app"** | Idade / tech literacy | "App leve, roda Android antigo. Modo voz. Treinamos presencial 1h." |
| **"Já uso Tiny/Bling"** | Fidelidade ERP | "Integramos via API: pedidos caem no Tiny automaticamente. Melhor dos 2 mundos." |
| **"Não tenho internet boa no depósito"** | Infra local | "Funciona offline-first (PWA). Sincroniza quando volta. Site roda no 4G do cliente." |
| **"Não confio em nuvem / dados"** | Segurança / LGPD | "Dados seus, isolados. Backup diário. LGPD compliant. Contrato DPA. Exporta tudo quando quiser." |
| **"Preciso de nota fiscal AGORA"** | Urgência fiscal | "Add-on NF-e ativa em 24h com parceiro certificado. Enquanto isso exporta CSV pro contador." |
| **"Vou esperar concorrente lançar mais barato"** | Comoditização | "Somos **especialistas água**. Genérico não faz rota galão + código 6 dígitos + split Pix." |

> **Em resumo:** Objeções reais têm **resposta técnica e comercial** — não ignoramos, enfrentamos com prova.

---

### 6. Concorrência — Onde o ÁquaLog ganha (e onde não joga)

| Concorrente | Modelo | Preço Inicial | Diferencial | Gap do ÁquaLog |
|-------------|--------|---------------|-------------|----------------|
| **ERP Genérico (Tiny, Bling, Omie)** | Mensalidade + módulos | R$ 100–300 | Fiscal completo, estoque, NF-e nativa | Não tem logística água (rotas, código entrega, GPS entregador) |
| **Apps Delivery (iFood, Rappi Partner)** | % sobre pedido | 12–25% TPV | Marketplace, volume | Caro para água; sem branding próprio; taxa alta |
| **Softwares Nicho Água (regionais)** | Licença + mensalidade | R$ 300–800 | Conhece regra água | Legado, sem app entregador, sem API, suporte fraco |
| **Planilha / WhatsApp** | Grátis / Tempo | R$ 0 | Zero custo | Erros, sem rastreio, não escala, sem fiscal |
| **ÁquaLog (Proposta)** | **SaaS plano fixo + split MP** | **R$ 149/mês** | **Especializado água: rotas, código 6 dígitos, GPS, Pix automático, branding próprio** | **Melhor custo-benefício para distribuidoras 50–5.000 pedidos/mês** |

> **Posicionamento:** **"O primeiro sistema feito *para* distribuidora de água, não adaptado."** — Preço fixo acessível + features nativas logística água + branding próprio + suporte humano.

---

### 6. Go-to-Market — Como chegamos no cliente (CAC near zero)

| Canal | CAC Estimado | Tempo Conversão | Escala | Ação Imediata |
|-------|--------------|-----------------|--------|---------------|
| **Indicação Cliente (Referral)** | **R$ 0–50** | 15–30 dias | Alta (viral) | Programa: 1 mês grátis p/ indicador + indicado |
| **Parceria Contador/Contabilidade** | R$ 100–200 | 30–60 dias | Média/Alta | 5 contadores Caxias → co-marketing + comissão 10% 1º ano |
| **Associações (ACIM, Sindigás, CDL)** | R$ 50–150 | 60–90 dias | Média | Palestra "Gestão Moderna Distribuidora" + stand feira |
| **WhatsApp Grupos Setoriais** | R$ 0–50 | 15–45 dias | Alta | Participação ativa (não spam) + cases reais |
| **Google Ads (Brand + Long Tail)** | R$ 200–400 | 7–21 dias | Controlada | "sistema distribuidora água caxias", "app entregador água" |
| **Instagram/LinkedIn B2B Orgânico** | R$ 50–100 (tempo) | 30–90 dias | Média | Conteúdo: "Como reduzi erros 90%", "Dia de entregador" |
| **Feiras/Eventos Regionais** | R$ 500–1.000 | 60–120 dias | Baixa/Média | ExpoLog Nordeste, Feira ACIM, Encontro Sindigás |

**Regra 80/20:** 80% esforço em **Indicação + Contadores + WhatsApp Grupos** (CAC baixo, confiança alta). 20% em Ads/Eventos para volume.

#### Funil de Vendas (Consultivo, não agressivo)

```
Visitante (Site/Indicação/Evento)
    ↓ Lead Magnet: "Checklist 10 Erros que Perdem Cliente na Entrega de Água" (WhatsApp/E-mail)
    ↓ Agendamento Demo 20 min (Calendly/Link WhatsApp)
    ↓ Demo Consultiva: "Me mostra seu WhatsApp de pedidos hoje" → Mapeia dores → Mostra fluxo ÁquaLog
    ↓ Trial 14 dias (Setup guiado 30 min) + Onboarding WhatsApp ativo
    ↓ Acompanhamento: Dia 3, 7, 10 (CS liga/WhatsApp: "Conseguiu fazer primeiro pedido?")
    ↓ Fechamento: Escolhe plano → Pagamento (Pix/Boleto/Cartão) → Contrato digital (ClickSign)
    ↓ Sucesso: Primeiros 30 dias = CS dedicado + NPS 30d
```

#### Programa de Indicação (Referral)

| Quem Indica | Benefício Indicador | Benefício Indicado | Regras |
|-------------|---------------------|-------------------|--------|
| **Cliente Ativo** | 1 mês grátis (crédito fatura) | 14 dias trial → 30 dias | Crédito após 1º pagamento do indicado |
| **Contador Parceiro** | 10% MRR 1º ano (pago mensal) | Setup grátis + 30 dias trial | Contrato parceria + NDA |
| **Entregador/Funcionário** | R$ 50 Pix (após 30 dias ativo) | Mesmo benefício cliente | Validação: indicado usa 30 dias |

---

### 7. Métricas de Sucesso (KPIs Comerciais)

| Métrica | Target Mês 6 | Target Mês 12 | Frequência |
|---------|--------------|---------------|------------|
| **Clientes Ativos Pagos** | 20 | 50 | Semanal |
| **MRR** | R$ 8.000 | R$ 25.000 | Semanal |
| **CAC Blended** | < R$ 300 | < R$ 250 | Mensal |
| **LTV / CAC** | > 3x | > 5x | Mensal |
| **Churn Mensal** | < 5% | < 3% | Mensal |
| **NPS (30d / 90d)** | > 40 / > 50 | > 50 / > 60 | Trimestral |
| **TTFV (Time-to-First-Value)** | < 45 min | < 30 min | Por cohort |
| **Ativação Trial → Pago** | > 40% | > 55% | Semanal |
| **Indicação / Novo Cliente** | > 30% | > 40% | Mensal |

---

### 8. Riscos Comerciais — e mitigação honesta

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Dependência fundadores nas vendas iniciais** | Alta | Escala travada | Contratar 1 SDR (Mês 4) + documentar playbook |
| **Concorrente grande lança "módulo água" barato** | Média | Pressão preço | Diferenciação: especialização + suporte humano + white-label + split Pix |
| **Entregadores recusam app (idade/tech)** | Média | Adoção falha | Modo voz + treinamento presencial 1h + "campeão interno" por cliente |
| **WhatsApp Business API bloqueia número** | Baixa | Canal suporte cai | Provedor gerenciado (Zenvia/Wati) + fallback SMS/E-mail |
| **LGPD / Vazamento dados cliente final** | Baixa | Jurídico + Reputação | DPO nomeado, DPA, criptografia, auditoria anual, seguro cyber |
| **Sazonalidade (verão = mais água, inverno = menos)** | Certa | Caixa flutua | Plano anual com desconto suaviza; reserva caixa 3 meses opex |
| **Dependência Mercado Pago (single point)** | Baixa | Pagamentos param | Fallback Pix manual nativo (`pix_manual.py`); monitorar SLA MP |

---

## Palavras que você vai ouvir (glossário)

| Termo | Definição simples | Exemplo no comercial |
|-------|-------------------|---------------------|
| **ICP (Ideal Customer Profile)** | Perfil do cliente perfeito: quem mais valor extrai e paga feliz | Distribuidora 2–20 entregadores, 50–5k pedidos/mês |
| **Persona** | Representação semi-fictícia do comprador/usuário baseada em dados reais | João (dono raiz), Carlos (gestor), Maria (entregadora) |
| **Proposta de Valor** | Declaração clara do benefício único que o produto entrega | "Sistema feito *para* distribuidora de água" |
| **Go-to-Market (GTM)** | Estratégia de como levar o produto ao mercado e adquirir clientes | Indicação + Contador + Associação + WhatsApp |
| **CAC (Customer Acquisition Cost)** | Custo total marketing+vendas para adquirir 1 cliente | Indicação = R$ 0, Ads = R$ 200 |
| **LTV (Lifetime Value)** | Receita líquida esperada de um cliente durante toda relação | R$ 399 × 24 meses = ~R$ 9.500 (Pro) |
| **Churn** | Taxa de cancelamento de clientes/receita por período | Meta: < 3%/mês |
| **NPS (Net Promoter Score)** | Métrica lealdade: % Promotores (9–10) - % Detratores (0–6) | Meta: > 50 |
| **TTFV (Time-to-First-Value)** | Tempo do cadastro ao primeiro resultado tangível | Meta: < 30 min |
| **SDR (Sales Development Representative)** | Pré-vendas: qualifica leads, agenda demos, não fecha | 1 SDR no Mês 4 |
| **Inside Sales** | Vendas remotas (telefone/vídeo), ciclo curto, ticket médio baixo/médio | Demo 20 min via Meet/WhatsApp |
| **White-label** | Produto rebrandado com marca do cliente (domínio, logo, cores) | `aguajoao.com.br` roda ÁquaLog por baixo |
| **Split de Pagamento** | Divisão automática do valor (plataforma + lojista) | 0,8% pra gente, 99,2% pro lojista |
| **Facilitador de Pagamento (PayFac)** | Entidade que sub-adquire lojistas sob sua conta master | Nossa conta MP Master |
| **LGPD (Lei 13.709/2018)** | Lei Geral de Proteção de Dados Pessoais — Brasil | DPA, consentimento, exclusão, criptografia |
| **DPA (Data Processing Agreement)** | Contrato controlador-operador de dados (Art. 7º LGPD) | Assinado digital no cadastro |
| **Sindigás** | Sindicato Nacional das Empresas Distribuidoras de Gás GLP | Parceria para eventos/acesso a associados |
| **ACIM / CDL** | Associação Comercial / Câmara de Dirigentes Lojistas (entidades locais) | Palestra + stand em feira local |

---

## Perguntas que a turma pode fazer (e como responder)

**1. "Vocês já têm cliente pagando?"**  
> Não — o sistema está em desenvolvimento (MVP). A meta é primeiro piloto em 3 meses, primeiro pagamento em 4 meses. Números aqui são **projeção baseada em custos reais e pesquisa de mercado**, não faturamento atual.

**2. "Como garante que o cliente não cancela no mês seguinte?"**  
> Onboarding assistido (30 dias), TTFV < 30 min, NPS trimestral, health score semanal (pedidos/semana, login). Se cliente para de usar, a gente liga **antes** dele cancelar. Churn alvo < 3%/mês.

**3. "E se o Mercado Pago mudar a taxa do Pix?"**  
> Cláusula no contrato: repasse automático da diferença. A gente monitora comunicados do MP mensalmente. Taxa do Pix hoje é 1,99% — se subir para 2,5%, a gente avisa o cliente 30 dias antes e ajusta se necessário.

**4. "Vocês vão ter suporte 24/7?"**  
> Não no início. Plano Básico: e-mail 48h. Pro: WhatsApp + e-mail 24h (horário comercial). Enterprise: SLA 4h + gerente dedicado. Suporte 24/7 só se tiver volume para justificar (custo alto).

**5. "Qual a meta de faturamento no primeiro ano?"**  
> **50 clientes ativos** → MRR ~R$ 25k → ARR ~R$ 300k. Conservador, baseado em CAC near zero (indicação + contador) e mercado endereçável no MA/PI/CE (centenas de distribuidoras). Não promete "unicórnio" — promete **negócio saudável, lucrativo, dono do próprio nariz**.

---

## Próximos passos Comerciais (90 Dias)

| Semana | Ação | Responsável | Entregável |
|--------|------|-------------|------------|
| 1–2 | Finalizar Alpha: 3 pilotos Caxias + onboarding assistido | Founder + Dev | 3 clientes rodando; feedback documentado |
| 3–4 | Criar Landing Page + Lead Magnet + Calendly Demo | Mkt + Dev | Site no ar; agendamento funcionando |
| 5–6 | Fechar 2 Parcerias Contador (Caxias/Timon) | Founder | Contrato assinado; 1º lead qualificado |
| 7–8 | Programa Indicação ativo (automatizado no painel) | Dev + CS | Link referral + crédito automático |
| 9–10 | Google Ads + Instagram Orgânico (teste R$ 500) | Mkt | CAC real medido; otimizar criativos |
| 11–12 | Feira ACIM / Encontro Sindigás (stand/palestra) | Founder | 20+ leads qualificados; 3 demos agendadas |
| Contínuo | Weekly Review: Funil + Métricas + Feedback Cliente | Todos | Decisões baseadas em dados; pivô rápido se necessário |

---

## Premissas usadas neste documento

- Faturamento médio distribuidora: R$ 30k–500k/mês (Pequeno a Médio).
- Taxas Mercado Pago: oficiais atuais (Pix 1,99% + R$ 0,60; Cartão 3,99% + R$ 0,60; confirmar nov/2026).
- Sistema em desenvolvimento (MVP) — sem clientes pagantes hoje.
- Custos de infra baseados em preços públicos nov/2026 (Hetzner, Wasabi, AWS, MP, Cloudflare).
- Split MP Master 0,8% TPV (negociável 0,5–1,5%).
- OSRM/Photon self-hosted para mapas/rota (custo zero marginal).
- Regime tributário Lucro Presumido (~16–20% receita bruta).
- CAC blended < R$ 300 (80% canais orgânicos: indicação, contador, WhatsApp).
- Churn alvo < 3%/mês com onboarding assistido + health score.
- Meta conservadora: 50 clientes ativos em 12 meses (não "unicórnio").
- Não há investidor externo — bootstrapped, dono do próprio ritmo.