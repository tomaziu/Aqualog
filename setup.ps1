# AquaLog - Setup Automatico (PowerShell)
# Instala dependencias, configura .env e prepara o ambiente para rodar o projeto.
# Execute com: .\setup.ps1  (ou PowerShell -ExecutionPolicy Bypass -File setup.ps1)

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$VENV_DIR = Join-Path $BACKEND_DIR "venv"
$ENV_FILE = Join-Path $BACKEND_DIR ".env"
$ENV_EXAMPLE = Join-Path $BACKEND_DIR ".env.example"
$SCHEMA_SQL = Join-Path $BACKEND_DIR "schema.sql"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AquaLog - Instalador Automatico" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -LiteralPath $PROJECT_ROOT

# --------------------------------------------------
# 1) Verificar Python
# --------------------------------------------------
Write-Host "[1/7] Verificando Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
    Write-Host "  X Python nao encontrado!" -ForegroundColor Red
    Write-Host "    Instale Python 3.11 em: https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "    Marque 'Add Python to PATH' durante a instalacao." -ForegroundColor Red
    exit 1
}
$pyVersion = & $pythonCmd.Source --version 2>&1
Write-Host "  OK  $pyVersion" -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 2) Criar ambiente virtual
# --------------------------------------------------
Write-Host "[2/7] Preparando ambiente virtual..." -ForegroundColor Yellow
if (-not (Test-Path -LiteralPath $VENV_DIR)) {
    & $pythonCmd.Source -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  X Falha ao criar o ambiente virtual." -ForegroundColor Red
        exit 1
    }
    Write-Host "  OK  venv criado em $VENV_DIR" -ForegroundColor Green
} else {
    Write-Host "  OK  venv ja existe" -ForegroundColor Green
}
Write-Host ""

# --------------------------------------------------
# 3) Instalar dependencias
# --------------------------------------------------
Write-Host "[3/7] Instalando dependencias Python (pode demorar)..." -ForegroundColor Yellow
$activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
& $activateScript | Out-Null

Write-Host "    Atualizando pip..." -ForegroundColor DarkGray
& $pythonCmd.Source -m pip install --upgrade pip >$null 2>$null

Write-Host "    Instalando requirements.txt..." -ForegroundColor DarkGray
$pipResult = & $pythonCmd.Source -m pip install -r (Join-Path $BACKEND_DIR "requirements.txt") 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Falha ao instalar dependencias." -ForegroundColor Red
    exit 1
}
Write-Host "  OK  Dependencias instaladas." -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 4) Arquivo .env
# --------------------------------------------------
Write-Host "[4/7] Configurando arquivo .env..." -ForegroundColor Yellow
if (-not (Test-Path -LiteralPath $ENV_FILE)) {
    if (Test-Path -LiteralPath $ENV_EXAMPLE) {
        Copy-Item -LiteralPath $ENV_EXAMPLE -Destination $ENV_FILE
        Write-Host "  OK  backend\.env criado a partir do exemplo." -ForegroundColor Green
    } else {
        Write-Host "  !  backend\.env.example nao encontrado. Criando .env vazio." -ForegroundColor Yellow
        Set-Content -LiteralPath $ENV_FILE -Value ""
    }
    Write-Host ""
    Write-Host "  ** IMPORTANTE: edite backend\.env e preencha: **" -ForegroundColor Yellow
    Write-Host "     - DB_PASSWORD  (senha do MySQL)" -ForegroundColor Yellow
    Write-Host "     - ADMIN_PASSWORD" -ForegroundColor Yellow
    Write-Host "     - JWT_SECRET" -ForegroundColor Yellow
    Write-Host "     - PIX_CHAVE" -ForegroundColor Yellow
} else {
    Write-Host "  OK  backend\.env ja existe (mantido)." -ForegroundColor Green
}
Write-Host ""

# --------------------------------------------------
# 5) Verificar MySQL (aviso)
# --------------------------------------------------
Write-Host "[5/7] Verificando MySQL..." -ForegroundColor Yellow
$mysqlCmd = Get-Command mysql -ErrorAction SilentlyContinue
if (-not $mysqlCmd) {
    Write-Host "  !  MySQL nao encontrado no PATH." -ForegroundColor Yellow
    Write-Host "     Instale: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Yellow
    Write-Host "     Certifique-se de que o MySQL esteja rodando antes de iniciar o servidor." -ForegroundColor Yellow
} else {
    Write-Host "  OK  MySQL encontrado no PATH." -ForegroundColor Green
}
Write-Host ""

# --------------------------------------------------
# 6) Aplicar schema.sql (opcional)
# --------------------------------------------------
Write-Host "[6/7] Schema do banco de dados." -ForegroundColor Yellow
Write-Host ""

$schemaOpt = "1"
try {
    $schemaOpt = Read-Host "  Voce ja tem o banco 'aqualog' com as tabelas? [1] Sim, pular / [2] Nao, aplicar schema.sql agora"
} catch {
    $schemaOpt = "1"
}

if ($schemaOpt -eq "2") {
    Write-Host ""
    Write-Host "  Vamos aplicar backend\schema.sql" -ForegroundColor Yellow
    Write-Host "  Voce precisara do usuario e senha do MySQL." -ForegroundColor Yellow
    Write-Host ""
    $mysqlUser = Read-Host "  Usuario MySQL [root]"
    if ([string]::IsNullOrWhiteSpace($mysqlUser)) { $mysqlUser = "root" }
    $mysqlPass = Read-Host "  Senha MySQL" -AsSecureString
    $mysqlPassText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPass))
    $mysqlArgs = "-u $mysqlUser", "-p$mysqlPassText"

    Get-Content -LiteralPath $SCHEMA_SQL | & cmd /c "mysql $mysqlArgs" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  !  Nao foi possivel aplicar o schema agora." -ForegroundColor Yellow
        Write-Host "     Aplique manualmente depois: mysql -u root -p < backend\schema.sql" -ForegroundColor Yellow
    } else {
        Write-Host "  OK  Tabelas criadas." -ForegroundColor Green
    }
} else {
    Write-Host "  OK  Pulando schema." -ForegroundColor Green
}
Write-Host ""

# --------------------------------------------------
# 7) Final
# --------------------------------------------------
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Instalacao concluida!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Proximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Edite o arquivo backend\.env (senha MySQL, JWT, Pix)"
Write-Host "  2. Rode o servidor:"
Write-Host "       cd backend"
Write-Host "       venv\Scripts\activate"
Write-Host "       uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
Write-Host ""
Write-Host "  Ou use o atalho: iniciar_tudo.bat"
Write-Host ""
Write-Host "  Telas apos iniciar:" -ForegroundColor Yellow
Write-Host "    Admin:      http://127.0.0.1:8000"
Write-Host "    Cliente:    http://127.0.0.1:8000/cliente.html"
Write-Host "    Entregador: http://127.0.0.1:8000/entregador.html"
Write-Host ""
Write-Host "  Testes:"
Write-Host "    cd backend && pytest tests/ -v"
Write-Host ""

try {
    pause
} catch {}
