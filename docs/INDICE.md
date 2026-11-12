# Índice dos Documentos — ÁquaLog (Apresentação em Grupo)

**Projeto:** ÁquaLog — Sistema de Pedidos e Entregas para Distribuidoras de Água  
**Cidade-base:** Caxias/MA (Brasil)  
**Data:** Novembro 2026  
**Equipe:** 5 integrantes

---

## Lista de Documentos

| # | Arquivo | Título | Integrante | Função | Duração Sugerida |
|---|---------|--------|------------|--------|------------------|
| 1 | `01_o_que_e_aqualog.md` | **O que é o ÁquaLog e como funciona** | **Thomaz** | Visão geral do sistema — para quem nunca viu | 5 min |
| 2 | `02_tecnologias_explicadas.md` | **Tecnologias e infraestrutura, explicadas de forma simples** | **Christian** | O que cada tecnologia faz, com analogias do dia a dia | 5 min |
| 3 | `03_proximos_passos.md` | **Roadmap — O que vem depois (Agora, Em breve, No futuro)** | **Angelo** | Próximas melhorias em fases, com benefício para o cliente | 5 min |
| 4 | `04_modelo_saas.md` | **Transformar em produto para várias empresas (SaaS Multi-tenant)** | **Fernando** | Como o sistema vira plataforma para centenas de distribuidoras | 5 min |
| 5 | `05_precos_e_publico.md` | **Preços, Planos e Público-Alvo** | **Miguel** | Quanto custa, para quem serve, por que contrataria | 5 min |

**Tempo total estimado da apresentação:** 25 minutos (+ perguntas)

---

## Resumo de Cada Documento

### 1. `01_o_que_e_aqualog.md` — Thomaz
**Foco:** Explicar o sistema para quem **nunca viu**.
- Problema real: WhatsApp + caderno + planilha = erros, perdas, retrabalho.
- 3 perfis: Cliente (Dona Maria), Admin (Seu João), Entregador (Carlos).
- Fluxo completo: Site → Painel → Entregador → Confirmação por código de 6 números.
- Ganhos: -90% erro de endereço, rastreamento tempo real, Pix automático, relatório pronto.

### 2. `02_tecnologias_explicadas.md` — Christian
**Foco:** Traduzir **nomes técnicos** para analogias do dia a dia.
- Python/FastAPI = Gerente da loja | MySQL = Caderno organizado | Docker = Caixa de mudança padronizada.
- Fluxo do clique à resposta (navegador → Cloudflare → Nginx → Uvicorn → Python → MySQL → resposta).
- Custos reais: ~R$ 110–175/mês base (single-tenant) → ~R$ 450–1.350 (100 tenants).
- Segurança: HTTPS, bcrypt, JWT, rate limit, backup offsite, variáveis de ambiente.
- Recuperação: backup diário offsite, Docker restart, rollback de versão.

### 3. `03_proximos_passos.md` — Angelo
**Foco:** Roadmap em **3 fases** com critério de priorização (5 pesos).
- **Agora (0–3m):** Testes, backup, rate limit, logs, health check, gaps críticos (editar pedido, importar CSV).
- **Em breve (3–9m):** Rota otimizada (OSRM), navegação + geofencing, WhatsApp/Push/SMS/E-mail, estoque avançado, NF-e via parceiro.
- **Futuro (9–18m+):** BI (Metabase/Superset), Marketplace (fornecedor + ERP + white-label), IA (previsão atraso, otimização dinâmica, chatbot RAG, detecção fraude).
- Critério: Dor do cliente (35%), Esforço (25%), Diferenciação (20%), Receita (15%), Futuro (5%).

### 4. `04_modelo_saas.md` — Fernando
**Foco:** Transformar em **plataforma multi-tenant** (prédio de apartamentos).
- Analogia: Prédio = infra | Apartamento = tenant (dados isolados) | Porteiro = auth | Síndico = Super-Admin.
- Isolamento em 3 camadas: Banco (`tenant_id`), Backend (JWT com `tid`), Frontend (config por tenant).
- Super-Admin: CRUD tenants, impersonate, planos/limites, feature flags, billing, auditoria.
- Onboarding self-service: Cadastro → Trial 14d → Wizard 30 min → Primeiro pedido.
- Domínio próprio + SSL automático (Let's Encrypt) + Branding total (logo, cores, e-mail).
- Mercado Pago Master (Facilitador) + Split automático (0,8% pra plataforma).
- Custos: ~R$ 415 base (1 cliente) → ~R$ 1.500–2.000 (100 clientes) → custo/cliente cai de R$ 415 para ~R$ 15–20.
- LGPD built-in: DPA digital, exclusão/anonymização, criptografia, DPO.
- Cronograma 6 meses → GA com 10 pilotos validando.

### 5. `05_precos_e_publico.md` — Miguel
**Foco:** Modelo comercial — **quanto custa, para quem, por que contrataria**.
- **3 Planos:** Básico R$ 149 (3 entregadores, 500 pedidos) | Pro R$ 399 (15, 5.000) | Enterprise R$ 999 (ilimitado).
- Setup: R$ 299 / 499 / 999. Anual 10% desc. Overages claros (entregador extra R$ 29, 1k pedidos R$ 99).
- Custo real/cliente: ~R$ 46,50 fixo + variável (WhatsApp, SMS). **OSRM self-hosted = custo zero mapas**.
- Margem (OSRM): Básico 27% | Pro 47% | Enterprise 58%. **Google Maps inviabiliza Básico/Pro**.
- Simulação: 50 clientes → MRR R$ 56k, Lucro R$ 36k (64% margem).
- ICP: Distribuidoras água/gás/bebidas, 2–20 entregadores, 50–5k pedidos/mês, MA/PI/CE.
- 3 Personas: João (dono raiz), Carlos (gestor moderno), Maria (entregadora experiente).
- GTM: Indicação (CAC R$ 0) + Contador (10% MRR) + Associações + WhatsApp grupos = **CAC near zero**.
- Funil consultivo: Lead magnet → Demo 20min → Trial 14d guiado → Fechamento.
- Concorrência: ERP genérico (sem logística água), Apps delivery (taxa alta 12–25%), Nicho local (legado), Planilha (grátis mas erra).
- Métricas: 50 clientes Mês 12, MRR R$ 25k, CAC < R$ 250, LTV/CAC > 5x, Churn < 3%, NPS > 50.
- Riscos: Dependência fundadores nas vendas, concorrente grande, entregador idoso, LGPD, sazonalidade.

---

## Premissas Comuns a Todos os Documentos

- Sistema em **desenvolvimento (MVP)** — sem clientes pagantes hoje.
- Cidade-base: **Caxias/MA** → expansão Nordeste (MA, PI, CE, RN, PB, PE, AL, SE, BA).
- Pagamento principal: **Pix via Mercado Pago** (Checkout API + Webhook + fallback manual).
- Mapas/Geocoding: **OSRM/Photon self-hosted** (grátis, open source) — Google Maps só Enterprise se exigido.
- Infra: **VPS + Docker Compose** (backend + MySQL) → evolução para SaaS com RDS/Redis gerenciados.
- Custos baseados em preços públicos **novembro 2026** (Hetzner, Wasabi, AWS, MP, Cloudflare, Asaas).
- Regime tributário: **Lucro Presumido** (~16–20% sobre receita bruta).
- LGPD: DPA digital, exclusão/anonymização, criptografia, DPO indicado.
- Equipe: **5 integrantes**, bootstrapped (sem investidor externo), dono do próprio ritmo.

---

## Como Usar na Apresentação

1. **Ordem recomendada:** 1 → 2 → 3 → 4 → 5 (lógica: o que é → como funciona → para onde vai → como escala → quanto custa/vende).
2. **Cada integrante fala 5 minutos** — use o "Roteiro de apresentação" de cada doc como guia.
3. **Slides sugeridos:** 1 slide por bloco do roteiro (mostrar tela / falar / tempo).
4. **Perguntas no final:** Cada doc tem seção "Perguntas que a turma pode fazer" com respostas prontas.
5. **Glossário:** Termos técnicos explicados em cada doc — use se a turma perguntar "o que é X?".

---

## Checklist Final Antes de Apresentar

- [ ] Todos os 5 arquivos `.md` estão na pasta `docs/`
- [ ] Nomes dos integrantes preenchidos nas capas (Thomaz, Christian, Angelo, Fernando, Miguel)
- [ ] Roteiro de cada integrante ensaiado (5 min cada)
- [ ] Slides/demos prontos para cada bloco "O que mostrar na tela"
- [ ] Respostas das "Perguntas que a turma pode fazer" revisadas
- [ ] Premissas alinhadas entre a equipe (custos, taxas, prazos)
- [ ] Backup dos arquivos (GitHub, Drive, pen drive)

---

## Contato / Dúvidas

Se precisar ajustar algum documento, edite o `.md` correspondente na pasta `docs/`.  
Para converter em PDF: use `pandoc`, `markdown-pdf` (VS Code) ou imprima do navegador.

**Boa apresentação!**