# Tecnologias e infraestrutura, explicadas de forma simples

**Integrante:** Christian  
**Função:** Explicar o que cada tecnologia faz usando analogias do dia a dia  
**Duração sugerida:** 5 minutos

---

## Para quem está lendo

Este documento traduz os "nomes técnicos" do ÁquaLog para linguagem do dia a dia. Cada tecnologia é comparada a algo que todo mundo conhece: caderno, loja, aluguel, carteiro, etc.

Quem deve ler: todos os integrantes, professores e avaliadores que querem entender **o que sustenta o sistema** sem precisar saber programar.

---

## Em uma frase

O ÁquaLog roda sobre tecnologias modernas e confiáveis — Python, banco de dados MySQL, containers Docker e hospedagem em nuvem — que funcionam juntas como uma equipe bem organizada: cada uma cuida de uma parte, e o resultado é um sistema rápido, seguro e barato de manter.

---

## Roteiro de apresentação

| Bloco | O que mostrar na tela | O que falar (resumo) | Tempo |
|-------|----------------------|----------------------|-------|
| 1 | Diagrama simples: Navegador → Servidor → Banco de Dados | "Quando o cliente abre o site, o navegador pede ao servidor, que busca no banco de dados e devolve a resposta." | 1 min |
| 2 | Tabela: Tecnologia ↔ Analogia | "Python é o gerente, MySQL é o caderno organizado, Docker é a caixa que leva tudo igual para qualquer lugar." | 1 min |
| 3 | Custos mensais (tabela com reais) | "Para manter no ar: servidor ~R$ 100, banco ~R$ 12, backups ~R$ 5. Total ~R$ 120/mês estimativa." | 1 min |
| 4 | Segurança: HTTPS, senha criptografada, Pix seguro | "Tudo que passa pela internet vai criptografado. Senha não fica salva em texto. Pix usa padrão do Banco Central." | 1 min |
| 5 | O que acontece se der problema (backup, reinício) | "Backup diário automático. Se o servidor cair, sobe outro em minutos com os mesmos dados." | 1 min |

---

## Conteúdo principal

### 1. A equipe invisível por trás do site

Imagine que o ÁquaLog é uma **distribuidora de água funcionando 24 horas**. Para atender o cliente, várias "pessoas" trabalham nos bastidores. Na tecnologia, cada "pessoa" é um componente:

| Componente técnico | Analogia do dia a dia | O que faz no ÁquaLog |
|--------------------|----------------------|----------------------|
| **Python + FastAPI** | O **gerente da loja** | Recebe os pedidos, organiza a fila, decide o que fazer, responde para o cliente |
| **MySQL (banco de dados)** | O **caderno organizado** | Guarda todos os pedidos, clientes, produtos, entregadores, estoque — sem perder nada |
| **Docker** | A **caixa de mudança padronizada** | Empacota o sistema inteiro (código + configurações) para rodar igual em qualquer computador |
| **Uvicorn** | O **porteiro da loja** | Fica na porta ouvindo quem chega (navegador) e entrega para o gerente (Python) |
| **Nginx / Cloudflare Tunnel** | O **segurança da entrada** | Protege contra ataques, coloca cadeado (HTTPS), esconde o endereço real do servidor |
| **HTML + CSS + JavaScript (navegador)** | A **vitrine e o balcão** | O que o cliente vê e clica — site do pedido, painel do dono, tela do entregador |
| **Chart.js** | O **quadro de gráficos na parede** | Mostra vendas do dia, semana, mês em gráficos bonitos no painel do administrador |
| **Phosphor Icons** | As **plaquinhas de sinalização** | Ícones bonitos e leves (carrinho, mapa, caminhão, usuário) |

> **Em resumo:** Cada tecnologia tem um papel claro. Juntas, formam um sistema que **não para, não perde dados e responde rápido**.

---

### 2. Como a informação viaja — do clique à resposta

```
Cliente clica "Confirmar pedido" no celular
                │
                ▼
Navegador envia dados pela internet (HTTPS = carta fechada com cadeado)
                │
                ▼
Cloudflare Tunnel recebe → protege → encaminha para o servidor
                │
                ▼
Nginx (porteiro) organiza a fila → passa para Uvicorn
                │
                ▼
Uvicorn entrega para Python/FastAPI (gerente)
                │
                ▼
Python processa: valida endereço, calcula total, gera código Pix
                │
                ▼
Python pede ao MySQL (caderno): "Salva esse pedido aí"
                │
                ▼
MySQL guarda → responde "Salvo com ID 123"
                │
                ▼
Python devolve para o cliente: "Pedido 123 confirmado! Aqui está o QR Code"
                │
                ▼
Cliente vê QR Code na tela → paga no Pix
```

> **Em resumo:** O clique vira uma mensagem segura, passa por porteiros, chega no gerente, que anota no caderno e responde na hora.

---

### 3. Onde tudo fica guardado — o banco de dados MySQL

O **MySQL** é como um **caderno com 15 abas**, cada aba para um assunto:

| Aba (tabela) | O que guarda | Exemplo |
|--------------|--------------|---------|
| `clientes` | Nome, telefone, endereço, coordenadas GPS | "Maria, 99 9999-9999, Rua das Flores 123, Centro" |
| `entregadores` | Nome, veículo, código de acesso, status | "Carlos, Moto Honda CG, código 1234, Disponível" |
| `produtos` | Nome, preço, estoque, foto, ativo/inativo | "Galão 20L, R$ 12,00, 50 unidades, ativo" |
| `pedidos` | Quem pediu, o quê, quando, status, código entrega | "Pedido #123, Maria, 2 galões, Recebido, código 847291" |
| `pedido_itens` | Detalhe de cada item do pedido | "Pedido #123 → Galão 20L × 2" |
| `estoque_movimentacoes` | Histórico de entrada/saída de produtos | "Saída: 2 galões no pedido #123" |
| `suporte_mensagens` | Chat entre cliente e administrador | "Cliente: 'Quando chega?' → Admin: '15 min'" |
| `cupons` | Códigos de desconto, regras, validade | "BEMVINDO10 = 10% off, válido até 31/12" |
| `configuracoes` | Nome da loja, chave Pix, loja aberta/fechada | "Água do João, pix@joao.com, aberta=sim" |
| ... e mais 6 tabelas | Entregas, localizações GPS, histórico, etc. | Rastreamento completo |

**Por que MySQL?**
- É **gratuito** (open source).
- Usado por empresas gigantes (Facebook, YouTube, Uber).
- Guarda dados **relacionados** (pedido sabe quem é o cliente, qual o entregador, quais os produtos).
- Não perde nada se a luz cair — grava no disco rígido.

> **Em resumo:** O MySQL é o **arquivo confiável** onde tudo fica salvo, organizado e fácil de achar.

---

### 4. Docker: a caixa que leva o sistema para qualquer lugar

**Problema:** "No meu computador funciona, mas no servidor não roda."  
**Solução:** **Docker** empacota o sistema inteiro — código Python, bibliotecas, configurações, variáveis de ambiente — numa **imagem** (como um arquivo .zip inteligente).

| Sem Docker | Com Docker |
|------------|------------|
| Instala Python, MySQL, bibliotecas manualmente no servidor | Baixa a imagem pronta: `docker pull aqualog/backend` |
| Versões diferentes dão erro | Mesma imagem roda no notebook, no servidor, na nuvem |
| Difícil voltar atrás se der problema | Versões antigas ficam salvas: `docker tag aqualog:v1.2` |
| Configuração de ambiente dá trabalho | Variáveis no arquivo `docker-compose.yml` |

**No ÁquaLog, usamos `docker-compose.yml` que sobe 2 containers:**

```text
┌─────────────────────────────────────┐
│         docker-compose.yml          │
├──────────────────┬──────────────────┤
│  Container 1     │  Container 2     │
│  backend         │  mysql           │
│  (Python + API)  │  (Banco de dados)│
│  Porta 8000      │  Porta 3306      │
└──────────────────┴──────────────────┘
```

> **Em resumo:** Docker garante que **o sistema roda igual em qualquer lugar** — no seu notebook, no servidor de produção, no computador do cliente piloto.

---

### 5. Quanto custa manter no ar (estimativa, novembro 2026)

| Item | O que é | Custo mensal estimado | Observação |
|------|---------|----------------------|------------|
| **VPS (servidor virtual)** | Computador alugado na nuvem (2 vCPU, 4 GB RAM, 80 GB SSD) | R$ 100–150 | Hetzner, Contabo, DigitalOcean — roda Docker + MySQL junto |
| **Domínio .com.br** | Endereço do site (ex: aguajoao.com.br) | R$ 3–5 | Registro.br cobra R$ 40/ano |
| **Certificado SSL (HTTPS)** | Cadeado verde no navegador | **Grátis** | Let's Encrypt renova sozinho a cada 3 meses |
| **Backup automático (Wasabi/S3)** | Cópia diária do banco de dados guardada fora do servidor | R$ 5–15 | Wasabi ~US$ 6 por TB/mês |
| **Monitoramento (Uptime Kuma)** | Avisa se o site cai | **Grátis** | Instalado no próprio VPS |
| **E-mail transacional** | Envia e-mail de confirmação, relatórios | R$ 0–10 | AWS SES: 62.000 e-mails grátis/mês |
| **Mapas (OSRM/Photon)** | Busca de endereço, rota, GPS | **Grátis** | Roda no próprio VPS (open source) |
| **WhatsApp Business API** | Envia mensagem automática pro cliente | R$ 0,35–0,80 por conversa | Só cobra quando manda; Meta + provedor (Zenvia/Wati) |
| **Mercado Pago (taxa Pix)** | Processa o pagamento | **1,99% + R$ 0,60** por venda | Taxa oficial (confirmar no site do MP) |
| **Total base (sem vendas)** | Infraestrutura fixa | **~R$ 110–175/mês** | Para 1 distribuidora (single-tenant) |

> **Em resumo:** O custo fixo para manter o ÁquaLog no ar é **menos de R$ 200 por mês** — mais barato que um funcionário de meio período.

---

### 5.1 Se virar SaaS (várias distribuidoras no mesmo servidor)

| Item adicional | Custo estimado para 100 clientes | Observação |
|----------------|----------------------------------|------------|
| Redis (filas, cache, rate limit) | R$ 100–300 | Evita lentidão quando muitos usam junto |
| Armazenamento de anexos (logos, PDFs) | R$ 50–200 | Wasabi ou S3 |
| SSL para domínios próprios | R$ 0–50 | Let's Encrypt grátis (tem limite de emissão) |
| E-mails em massa (relatórios) | R$ 50–200 | SendGrid ou AWS SES |
| Monitoramento avançado | R$ 100–500 | Grafana Cloud ou Datadog |
| **Total adicional (100 clientes)** | **~R$ 450–1.350/mês** | Escala sublinear: custo por cliente cai |

> **Em resumo:** Com **um servidor maior**, dá para atender **centenas de distribuidoras** pagando pouco a mais por cliente.

---

### 6. Segurança — o que protege os dados

| Proteção | Analogia | Como funciona no ÁquaLog |
|----------|----------|--------------------------|
| **HTTPS (TLS)** | Carta enviada em envelope lacrado com cadeado | Todo tráfego entre navegador e servidor é criptografado |
| **Senha com bcrypt** | Chave que não dá para copiar olhando | Senha do admin vira código embaralhado (hash) — nem o dono do sistema vê |
| **JWT (token)** | Crachá de identificação com validade | Admin loga → recebe token → usa token em cada clique → expira em 24h |
| **Rate limit** | Porteiro que barra quem tenta entrar demais | Bloqueia quem faz mais de 100 requisições por minuto |
| **Validação de entrada** | Recepcionista que confere formulário antes de passar | Impede SQL injection (comandos maliciosos no banco) e XSS (scripts no site) |
| **Backup diário offsite** | Cópia do caderno guardada no cofre do banco | `mysqldump` todo dia de madrugada → sobe para Wasabi (fora do servidor) |
| **Variáveis de ambiente** | Segredos guardados no cofre, não no código | Chave Pix, segredo JWT, senha do banco ficam em `.env`, não no GitHub |

> **Em resumo:** Dados do cliente e da distribuidora ficam **protegidos por várias camadas** — como uma casa com cadeado, alarme, cerca e seguro.

---

### 7. Se der problema — o plano de recuperação

| Problema | O que acontece | Tempo para voltar |
|----------|----------------|-------------------|
| Servidor cai (energia, rede, hardware) | Docker reinicia containers automaticamente | Segundos a minutos |
| Banco de dados corrompe | Restaura backup de ontem (offsite) | 10–30 minutos |
| Código novo quebrou algo | Volta versão anterior (Docker tag anterior) | 1–2 minutos |
| Ataque DDoS (muitos acessos falsos) | Cloudflare bloqueia automaticamente | Imediato |
| Perda total do servidor | Sobe novo VPS → `docker-compose up` → restaura backup | 30–60 minutos |

> **Em resumo:** Com **backup diário fora do servidor** e **Docker**, o pior cenário é perder **no máximo algumas horas** — e o sistema volta sozinho na maioria dos casos.

---

## Palavras que você vai ouvir (glossário)

| Termo | Definição simples | Exemplo no ÁquaLog |
|-------|-------------------|-------------------|
| **API** | Canal de comunicação entre o site (frente) e o sistema (trás) | Site manda "criar pedido" → API recebe → salva no banco |
| **Backend** | A parte do sistema que roda no servidor (o "cérebro") | Python + FastAPI + MySQL |
| **Frontend** | O que o usuário vê no navegador (a "cara") | HTML + CSS + JS do site, painel, entregador |
| **Container** | Caixa isolada com tudo que o programa precisa para rodar | Docker empacota Python + bibliotecas + config |
| **Imagem Docker** | Modelo da caixa — serve para criar quantos containers quiser | `aqualog/backend:v1.2` |
| **VPS** | Servidor Virtual Privado — computador alugado na nuvem | Onde roda os containers Docker + MySQL |
| **Cloudflare Tunnel** | Túnel seguro que esconde o IP real do servidor | Grátis, coloca HTTPS, protege contra ataques |
| **HTTPS / TLS** | Protocolo seguro (cadeado no navegador) | Dados viajam criptografados |
| **JWT** | Token (crachá digital) que prova quem você é | Admin loga → recebe JWT → usa em cada ação |
| **bcrypt** | Função que transforma senha em código irreversível | Senha "123456" vira "$2b$12$..." — não dá para voltar |
| **Rate limit** | Limite de quantas vezes pode pedir por minuto | Bloqueia robôs que tentam derrubar o site |
| **Backup offsite** | Cópia guardada em outro lugar (não no mesmo servidor) | Wasabi/S3 recebe `.sql` todo dia de madrugada |
| **Variável de ambiente** | Configuração secreta que fica fora do código | `MERCADO_PAGO_ACCESS_TOKEN=APP_USR-...` |
| **Single-tenant** | Um sistema para um cliente só | Versão atual do ÁquaLog |
| **Multi-tenant** | Um sistema para vários clientes (cada um isolado) | Futuro SaaS do ÁquaLog |

---

## Perguntas que a turma pode fazer (e como responder)

**1. "Por que não usa Firebase / Supabase / outro serviço pronto?"**  
> Porque o ÁquaLog precisa de controle total sobre os dados, custo previsível e funcionar offline-first no entregador. Serviços prontos ficam caros em escala e prendem a gente neles (vendor lock-in). Com Docker + MySQL, a gente manda no nosso sistema.

**2. "E se o MySQL travar? Perde tudo?"**  
> Não. O MySQL é muito estável. E mesmo se travar, tem backup diário automático guardado **fora do servidor** (no Wasabi). No pior caso, restaura o backup de ontem — perde no máximo algumas horas de pedidos.

**3. "O Docker é difícil de aprender?"**  
> Para usar no dia a dia, não. São 3 comandos principais: `docker-compose up` (liga), `docker-compose down` (desliga), `docker-compose logs` (vê o que aconteceu). A complexidade fica na primeira configuração — depois é só apertar o botão.

**4. "Por que não hospeda no Heroku / Railway / Vercel?"**  
> Porque eles ficam caros quando o sistema cresce (cobram por uso de CPU/RAM). Um VPS de R$ 120/mês aguenta centenas de distribuidoras no modelo SaaS. Em nuvem gerenciada, o mesmo custo seria R$ 1.000+.

**5. "Como faz para atualizar o sistema no ar?"**  
> `git pull` → `docker-compose build` → `docker-compose up -d` → pronto. O Docker sobe a nova versão e derruba a antiga sem parar o site (rolling update). Leva menos de 1 minuto.

---

## Próximos passos

- Configurar **CI/CD (GitHub Actions)**: ao fazer push na main, roda testes, builda imagem Docker e deploya automático.
- Adicionar **logs estruturados** (JSON) + **Grafana/Loki** para buscar erros rápido.
- Implementar **health check completo** (`/healthz` verifica banco, Redis, Mercado Pago).
- Migrar MySQL para **instância gerenciada (RDS/CloudSQL)** quando virar SaaS — tira a manutenção do banco das costas do time.
- Testes de carga: simular 1.000 pedidos simultâneos para ver onde engasga.

---

## Premissas usadas neste documento

- Custos baseados em preços públicos de novembro 2026 (Hetzner, Wasabi, AWS, Mercado Pago, Cloudflare).
- Servidor único (VPS) rodando Docker Compose com 2 containers: backend + MySQL.
- Versão atual é **single-tenant** (uma distribuidora por instalação).
- Pagamento principal via Mercado Pago Checkout API (Pix).
- Mapas e geocoding via OSRM/Photon self-hosted (grátis, open source).
- Backups diários via `mysqldump` + `rclone` para Wasabi (S3 compatível).
- Monitoramento básico com Uptime Kuma self-hosted no mesmo VPS.