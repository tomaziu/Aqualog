# ÁquaLog - Sistema de Controle de Entregas

Sistema completo para uma distribuidora de água, com controle de clientes, entregadores, produtos, pedidos, status de entrega, roteirização simples por bairro e relatório de tempo médio.

## Tecnologias
- Backend: Python + FastAPI
- Banco de dados: MySQL
- Frontend: HTML, CSS e JavaScript

## Como rodar

### 1. Criar banco MySQL
Abra o MySQL Workbench ou terminal e execute o arquivo:

```
backend/schema.sql
```

Isso cria o banco `aqualog`, as tabelas e já insere dados de exemplo (15 clientes, 3 entregadores, 5 produtos, 15 pedidos de Caxias-MA).

### 2. Configurar backend
Entre na pasta `backend`:

```bash
cd backend
```

Crie o ambiente virtual:

```bash
py -m venv venv
```

Ative:

```bash
venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure o arquivo `.env` com seu usuário e senha do MySQL.

### 3. Rodar API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

A API abre em:

```text
http://127.0.0.1:8000
```

Documentação automática:

```text
http://127.0.0.1:8000/docs
```

### 4. Abrir o frontend
Use o `iniciar_server.bat` (recomendado) ou abra manualmente:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/entregador.html
```

> O `iniciar_server.bat` inicia o servidor com `--host 0.0.0.0` (acessível de outros dispositivos na rede), aguarda 3 segundos e abre o frontend automaticamente.

## Páginas

### Admin (`/`)
- Dashboard com total de pedidos, tempo médio, status e roteirização por bairro
- CRUD de Clientes (com bairros reais de Caxias-MA)
- CRUD de Entregadores (com código de acesso para login)
- CRUD de Produtos
- Gerenciamento de Pedidos (criação, filtro por status, alteração de status)
- Edição inline nas tabelas

### Entregador (`/entregador.html`)
- Login com código de acesso
- Visualiza apenas os pedidos atribuídos a ele
- Vê endereço, bairro, referência, telefone do cliente e produto
- Botões: "Saiu p/ entrega" e "Entregue"
- Filtros: Todos / Em rota / Preparando / Entregues

## Fluxo do pedido
Recebido → Em preparo → Saiu para entrega → Entregue

## Entregadores (dados de exemplo)
| Nome | Código de acesso | Veículo |
|------|-----------------|---------|
| Lucas Mendes | lucas123 | Fiorino |
| Rafael Santos | rafael123 | Moto |
| Diego Costa | diego123 | Kombi |

## Acessar do celular
1. Descubra o IP do computador na rede (ex: 10.0.0.129)
2. No celular (mesma rede Wi-Fi), abra:
   - `http://SEU_IP:8000` para o admin
   - `http://SEU_IP:8000/entregador.html` para o entregador
3. Se não conectar, libere a porta 8000 no firewall do Windows

> ⚠️ **Importante:** Não abra o `index.html` ou `entregador.html` direto pelo Explorador de Arquivos (duplo clique). O frontend precisa ser servido pelo backend para conseguir carregar os dados do banco. Sempre use `http://127.0.0.1:8000` ou o `iniciar_server.bat`.
