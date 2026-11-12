# ÁquaLog - Sistema de Controle de Entregas

Sistema para distribuidora de água com pedido online, painel administrativo, tela do entregador, controle de estoque, status de entrega e relatórios.

## Tecnologias

- **Backend:** Python + FastAPI
- **Banco de dados:** MySQL
- **Frontend:** HTML, CSS e JavaScript vanilla

## Telas

| Tela | URL | Usuário |
|------|-----|---------|
| Admin | `http://127.0.0.1:8000` | senha: `admin123` |
| Cliente | `http://127.0.0.1:8000/cliente.html` | sem login (identifica por telefone) |
| Entregador | `http://127.0.0.1:8000/entregador.html` | código de acesso do entregador |

## Como instalar e rodar (qualquer PC Windows)

### 1. Baixe o projeto
Descompacte ou clone o repositório em qualquer pasta.

### 2. Instale os pré-requisitos
O AquaLog precisa de:
- **Python 3.11+** (https://www.python.org/downloads/) — marque "Add Python to PATH"
- **MySQL** (https://dev.mysql.com/downloads/mysql/) — anote a senha do `root`

### 3. Rode o instalador
Abra o PowerShell na pasta do projeto e execute:

```powershell
.\scripts\setup.ps1
```

Ou use o `.bat`:

```cmd
scripts\setup.bat
```

O instalador vai:
- Criar o ambiente virtual Python
- Instalar todas as dependências
- Criar o arquivo `backend\.env` com valores padrão
- Criar o banco de dados e as tabelas no MySQL

### 4. Inicie o servidor
Após a instalação, rode:

```powershell
.\scripts\iniciar_local.ps1
```

Ou:

```cmd
scripts\iniciar_local.bat
```

Isso inicia o servidor e abre automaticamente as três telas no navegador.

### 5. Acesse
- **Admin:** http://127.0.0.1:8000 (senha: `admin123`)
- **Cliente:** http://127.0.0.1:8000/cliente.html
- **Entregador:** http://127.0.0.1:8000/entregador.html

---

## Estrutura rápida

```
scripts/          <- scripts de instalacao e inicio (.bat e .ps1)
backend/          <- API FastAPI + banco
frontend/         <- HTML/CSS/JS (admin, cliente, entregador)
docs/             <- documentacao tecnica
```

## Precise de ajuda?

- Se o MySQL não estiver instalado, o `setup.ps1` avisa e para com instruções.
- Se esquecer a senha do MySQL, edite `backend\.env` com a senha correta e rode o setup novamente.
- Para expor o sistema na internet (ex: webhook do Mercado Pago), use `.\scripts\iniciar_com_tunel.ps1`.