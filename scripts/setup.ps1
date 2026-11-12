# AquaLog - Instalador Automatico (PowerShell)
# Instala tudo o que e necessario para rodar o AquaLog em qualquer PC Windows.
# Execute com: .\scripts\setup.ps1  (ou PowerShell -ExecutionPolicy Bypass -File scripts\setup.ps1)

$ErrorActionPreference = "Continue"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROJECT_ROOT = Resolve-Path (Join-Path $SCRIPT_DIR "..")
Set-Location -LiteralPath $PROJECT_ROOT

$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$VENV_DIR = Join-Path $BACKEND_DIR "venv"
$ENV_FILE = Join-Path $BACKEND_DIR ".env"
$SCHEMA_SQL = Join-Path $BACKEND_DIR "schema.sql"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AquaLog - Instalador Automatico" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --------------------------------------------------
# 1) Verificar Python
# --------------------------------------------------
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) { $pythonCmd = Get-Command py -ErrorAction SilentlyContinue }
if (-not $pythonCmd) {
    Write-Host "  X Python nao encontrado!" -ForegroundColor Red
    Write-Host "    Baixe e instale: https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "    IMPORTANTE: marque 'Add Python to PATH' durante a instalacao." -ForegroundColor Red
    exit 1
}
$pyVersion = & $pythonCmd.Source --version 2>&1
Write-Host "  OK  $pyVersion ($($pythonCmd.Source))" -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 2) Criar ambiente virtual
# --------------------------------------------------
Write-Host "[2/5] Preparando ambiente virtual..." -ForegroundColor Yellow
if (-not (Test-Path -LiteralPath $VENV_DIR)) {
    & $pythonCmd.Source -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  X Falha ao criar o ambiente virtual." -ForegroundColor Red
        exit 1
    }
    Write-Host "  OK  venv criado em backend\venv" -ForegroundColor Green
} else {
    Write-Host "  OK  venv ja existe" -ForegroundColor Green
}
Write-Host ""

# --------------------------------------------------
# 3) Instalar dependencias
# --------------------------------------------------
Write-Host "[3/5] Instalando dependencias Python (pode demorar alguns minutos)..." -ForegroundColor Yellow
$activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
& $activateScript | Out-Null

Write-Host "    Atualizando pip..." -ForegroundColor DarkGray
& $pythonCmd.Source -m pip install --upgrade pip >$null 2>$null

Write-Host "    Instalando requirements.txt..." -ForegroundColor DarkGray
$pipResult = & $pythonCmd.Source -m pip install -r (Join-Path $BACKEND_DIR "requirements.txt") 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Falha ao instalar dependencias." -ForegroundColor Red
    Write-Host "    Tente rodar manualmente:" -ForegroundColor Yellow
    Write-Host "      cd backend && venv\Scripts\activate && pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
Write-Host "  OK  Dependencias instaladas." -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 4) Verificar MySQL
# --------------------------------------------------
Write-Host "[4/5] Verificando MySQL..." -ForegroundColor Yellow
$mysqlExecutable = Get-Command mysql -ErrorAction SilentlyContinue
if ($mysqlExecutable) {
    $mysqlExecutable = $mysqlExecutable.Source
}

if (-not $mysqlExecutable) {
    $versoes = @("8.4", "8.3", "8.2", "8.1", "8.0", "5.7")
    $caminhosComuns = @()
    foreach ($v in $versoes) {
        $caminhosComuns += "C:\Program Files\MySQL\MySQL Server $v\bin\mysql.exe"
        $caminhosComuns += "C:\Program Files (x86)\MySQL\MySQL Server $v\bin\mysql.exe"
    }
    $caminhosComuns += "C:\mysql\bin\mysql.exe"
    foreach ($caminho in $caminhosComuns) {
        if (Test-Path -LiteralPath $caminho) {
            $mysqlExecutable = $caminho
            break
        }
    }
}

if (-not $mysqlExecutable) {
    Write-Host "  X MySQL nao encontrado!" -ForegroundColor Red
    Write-Host "    O AquaLog precisa do MySQL para funcionar." -ForegroundColor Red
    Write-Host "    1. Baixe e instale: https://www.mysql.com/downloads/" -ForegroundColor Red
    Write-Host "    2. Durante a instalacao, anote a senha do usuario root." -ForegroundColor Red
    Write-Host "    3. Adicione o MySQL ao PATH do Windows ou instale na pasta padrao." -ForegroundColor Red
    Write-Host "    4. Depois rode este script novamente." -ForegroundColor Red
    exit 1
}
Write-Host "  OK  MySQL encontrado ($mysqlExecutable)" -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 5) Configurar .env e banco de dados
# --------------------------------------------------
Write-Host "[5/5] Configurando arquivo .env e banco de dados..." -ForegroundColor Yellow

# Perguntar nome do banco de dados
$bancoPadrao = "aqualog"
Write-Host "  Nome do banco de dados (padrao: $bancoPadrao):" -ForegroundColor DarkGray
$bancoNome = Read-Host "  Digite o nome ou pressione Enter para usar '$bancoPadrao'"
if ([string]::IsNullOrWhiteSpace($bancoNome)) {
    $bancoNome = $bancoPadrao
}
Write-Host "  Usando banco: $bancoNome" -ForegroundColor Green
Write-Host ""

# .env com valores padrao
$defaultEnv = @"
# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=$bancoNome

# Auth
JWT_SECRET=aqualog_jwt_secret_change_in_production
ADMIN_PASSWORD=admin123

# Pagamento
PIX_CHAVE=
MERCADO_PAGO_ACCESS_TOKEN=

# Servidor
PORT=8000
"@

if (-not (Test-Path -LiteralPath $ENV_FILE)) {
    Set-Content -LiteralPath $ENV_FILE -Value $defaultEnv -Encoding UTF8
    Write-Host "  OK  backend.env criado com valores padrao." -ForegroundColor Green
} else {
    :: Atualiza apenas o DB_NAME se ja existir, preservando o restante
    $conteudoEnv = Get-Content -LiteralPath $ENV_FILE -Raw
    $linhas = @()
    $encontrouDB_NAME = $false
    foreach ($linha in $conteudoEnv -split "`n") {
        if ($linha -match '^DB_NAME=') {
            $linhas += "DB_NAME=$bancoNome"
            $encontrouDB_NAME = $true
        } else {
            $linhas += $linha
        }
    }
    if (-not $encontrouDB_NAME) {
        $linhas += "DB_NAME=$bancoNome"
    }
    $conteudoEnv = $linhas -join "`n"
    Set-Content -LiteralPath $ENV_FILE -Value $conteudoEnv -Encoding UTF8
    Write-Host "  OK  backend.env ja existe (atualizado DB_NAME=$bancoNome)." -ForegroundColor Green
}
Write-Host ""

# Funcao para executar query no MySQL
function Executar-MySqlQuery {
    param([string]$Query, [securestring]$Senha = $null)
    if ($Senha) {
        $senhaTexto = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Senha))
        $cmdLine = """$mysqlExecutable"" -u root -p$senhaTexto -e ""$Query"""
    } else {
        $cmdLine = """$mysqlExecutable"" -u root -e ""$Query"""
    }
    & cmd /c $cmdLine 2>$null
    return $LASTEXITCODE
}

# Verificar se o banco ja tem tabelas criadas
Write-Host "  Verificando se o banco '$bancoNome' ja esta configurado..." -ForegroundColor Yellow

$tabelasExistem = $false
$queryTeste = "USE $bancoNome; SHOW TABLES LIKE 'pedidos';"
$cmdLineTeste = """$mysqlExecutable"" -u root -e ""$queryTeste"""
$testeTabelas = & cmd /c $cmdLineTeste 2>$null
if ($LASTEXITCODE -eq 0 -and $testeTabelas -match 'pedidos') {
    $tabelasExistem = $true
}

if ($tabelasExistem) {
    Write-Host "  OK  Banco '$bancoNome' ja existe com tabelas criadas. Pulando aplicacao do schema." -ForegroundColor Green
} else {
    Write-Host "  Banco vazio ou nao existe. Criando banco e aplicando schema.sql..." -ForegroundColor Yellow

    $criouBanco = $false

    # Tentativa 1: root sem senha
    Write-Host "    Tentando conectar como root (sem senha)..." -ForegroundColor DarkGray
    $queryCreate = "CREATE DATABASE IF NOT EXISTS `$bancoNome` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    $code = Executar-MySqlQuery -Query $queryCreate
    if ($code -eq 0) {
        Write-Host "  OK  Banco '$bancoNome' criado (root sem senha)." -ForegroundColor Green
        $criouBanco = $true
        $conteudoEnv = Get-Content -LiteralPath $ENV_FILE -Raw
        $conteudoEnv = $conteudoEnv -replace '(?<=^DB_PASSWORD=).*$', ''
        Set-Content -LiteralPath $ENV_FILE -Value $conteudoEnv -Encoding UTF8
    } else {
        Write-Host "    Nao conseguiu (sem senha)." -ForegroundColor DarkGray
    }

    # Tentativa 2: pedir senha
    if (-not $criouBanco) {
        Write-Host ""
        $mysqlPass = Read-Host "  Informe a senha do MySQL (root) para criar o banco"
        if ([string]::IsNullOrWhiteSpace($mysqlPass)) {
            Write-Host "  !  Senha nao informada. Pulando criacao de tabelas." -ForegroundColor Yellow
            Write-Host "     Aplique manualmente depois:" -ForegroundColor Yellow
            Write-Host "       $mysqlExecutable -u root -p" -ForegroundColor Yellow
            Write-Host "       mysql> CREATE DATABASE $bancoNome;" -ForegroundColor Yellow
            Write-Host "       mysql> USE $bancoNome;" -ForegroundColor Yellow
            Write-Host "       mysql> source backend\schema.sql" -ForegroundColor Yellow
        } else {
            $secPass = $mysqlPass | ConvertTo-SecureString -AsPlainText -Force
            $queryCreate = "CREATE DATABASE IF NOT EXISTS `$bancoNome` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            $code = Executar-MySqlQuery -Query $queryCreate -Senha $secPass
            if ($code -eq 0) {
                Write-Host "  OK  Banco '$bancoNome' criado com sucesso." -ForegroundColor Green
                $criouBanco = $true
                $conteudoEnv = Get-Content -LiteralPath $ENV_FILE -Raw
                $conteudoEnv = $conteudoEnv -replace '(?<=^DB_PASSWORD=).*$', $mysqlPass
                Set-Content -LiteralPath $ENV_FILE -Value $conteudoEnv -Encoding UTF8
            } else {
                Write-Host "  !  Falha ao criar banco. Verifique a senha e se o MySQL esta rodando." -ForegroundColor Yellow
            }
        }
    }

    # Aplicar schema.sql se o banco foi criado
    if ($criouBanco) {
        Write-Host "  Aplicando schema.sql..." -ForegroundColor Yellow

        $schemaConteudo = Get-Content -LiteralPath $SCHEMA_SQL -Raw
        $schemaConteudo = $schemaConteudo -replace 'aqualog', $bancoNome
        $schemaTemp = Join-Path $env:TEMP "aqualog_schema_$bancoNome.sql"
        Set-Content -LiteralPath $schemaTemp -Value $schemaConteudo -Encoding UTF8

        # Criar arquivo bat temporario para aplicar schema com redirecionamento
        $batTemp = Join-Path $env:TEMP "aqualog_apply_$bancoNome.bat"
        $batContent = """$mysqlExecutable"" -u root < ""$schemaTemp""""
        Set-Content -LiteralPath $batTemp -Value $batContent -Encoding UTF8
        & cmd /c $batTemp 2>$null
        $code = $LASTEXITCODE

        if ($code -eq 0) {
            Write-Host "  OK  Tabelas criadas com sucesso." -ForegroundColor Green
        } else {
            if (-not [string]::IsNullOrWhiteSpace($mysqlPass)) {
                $batContent2 = """$mysqlExecutable"" -u root -p$mysqlPass < ""$schemaTemp""""
                Set-Content -LiteralPath $batTemp -Value $batContent2 -Encoding UTF8
                & cmd /c $batTemp 2>$null
                $code = $LASTEXITCODE
                if ($code -eq 0) {
                    Write-Host "  OK  Tabelas criadas com sucesso." -ForegroundColor Green
                } else {
                    Write-Host "  !  Falha ao aplicar schema.sql." -ForegroundColor Yellow
                }
            } else {
                Write-Host "  !  Falha ao aplicar schema.sql." -ForegroundColor Yellow
            }
        }

        Remove-Item -LiteralPath $schemaTemp -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $batTemp -Force -ErrorAction SilentlyContinue
    }
}
Write-Host ""

# --------------------------------------------------
# Final
# --------------------------------------------------
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Instalacao concluida!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  O que foi feito:" -ForegroundColor Yellow
Write-Host "    - Ambiente virtual Python criado (backend\venv)"
Write-Host "    - Dependencias instaladas"
Write-Host "    - Arquivo backend.env configurado (DB_NAME=$bancoNome)"
Write-Host "    - Banco de dados e tabelas criados (se o MySQL estiver rodando)"
Write-Host ""
Write-Host "  Para iniciar o servidor:" -ForegroundColor Yellow
Write-Host "    .\scripts\iniciar_local.ps1"
Write-Host ""
Write-Host "  Telas apos iniciar:" -ForegroundColor Yellow
Write-Host "    Admin:      http://127.0.0.1:8000"
Write-Host "    Cliente:    http://127.0.0.1:8000/cliente.html"
Write-Host "    Entregador: http://127.0.0.1:8000/entregador.html"
Write-Host ""
Write-Host "  Login admin: senha admin123"
Write-Host ""

try { pause } catch {}