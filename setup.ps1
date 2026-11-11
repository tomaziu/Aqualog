# AquaLog - Setup Automatico (PowerShell)
# Instala dependencias, configura banco MySQL, cria tabelas automaticamente e prepara o projeto.
# Execute com: .\setup.ps1  (ou PowerShell -ExecutionPolicy Bypass -File setup.ps1)

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$VENV_DIR = Join-Path $BACKEND_DIR "venv"
$ENV_FILE = Join-Path $BACKEND_DIR ".env"
$ENV_EXAMPLE = Join-Path $BACKEND_DIR ".env.example"
$SCHEMA_SQL = Join-Path $BACKEND_DIR "schema.sql"
$LOG_FILE = Join-Path $env:TEMP "aqualog_setup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[$timestamp] $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $LOG_FILE -Value $line
}

function Test-PythonCmd {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $cmd) { $cmd = Get-Command py -ErrorAction SilentlyContinue }
    return $cmd
}

function Test-MySqlCmd {
    return Get-Command mysql -ErrorAction SilentlyContinue
}

function Invoke-MySql {
    param([string]$User, [securestring]$Password, [string]$SqlFile, [string]$Database = $null)
    $passText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password))
    $args = "-u $User", "-p$passText"
    if ($Database) { $args += $Database }
    $tempBat = Join-Path $env:TEMP "aqualog_mysql_$(Get-Random).bat"
    $redirect = if ($SqlFile) { "< `"$SqlFile`"" } else { "" }
    $cmdLine = "mysql $args $redirect"
    Set-Content -LiteralPath $tempBat -Value $cmdLine -Encoding UTF8
    & cmd /c "`"$tempBat`"" 2>$null
    $code = $LASTEXITCODE
    Remove-Item -LiteralPath $tempBat -Force -ErrorAction SilentlyContinue
    return $code
}

function Read-SecureHost {
    param([string]$Prompt, [string]$Default)
    if ($isInteractive) {
        $val = Read-Host $Prompt
        if ([string]::IsNullOrWhiteSpace($val)) { return $Default }
        return $val
    }
    return $Default
}

function Read-SecurePass {
    param([string]$Prompt)
    if ($isInteractive) {
        return Read-Host $Prompt -AsSecureString
    }
    return $null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AquaLog - Instalador Automatico" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Log: $LOG_FILE" -ForegroundColor Gray
Write-Host ""

Set-Location -LiteralPath $PROJECT_ROOT

# --------------------------------------------------
# 0) Modo interativo?
# --------------------------------------------------
$isInteractive = [Environment::UserInteractive]

# --------------------------------------------------
# 1) Verificar Python
# --------------------------------------------------
Write-Host "[1/9] Verificando Python..." -ForegroundColor Yellow
$pythonCmd = Test-PythonCmd
if (-not $pythonCmd) {
    Write-Host "  X Python nao encontrado!" -ForegroundColor Red
    Write-Host "    Instale Python 3.11+ em: https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "    Marque 'Add Python to PATH' durante a instalacao." -ForegroundColor Red
    exit 1
}
$pyVersion = & $pythonCmd.Source --version 2>&1
Write-Host "  OK  $pyVersion ($($pythonCmd.Source))" -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 2) Criar ambiente virtual
# --------------------------------------------------
Write-Host "[2/9] Preparando ambiente virtual..." -ForegroundColor Yellow
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
Write-Host "[3/9] Instalando dependencias Python (pode demorar)..." -ForegroundColor Yellow
$activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
& $activateScript | Out-Null

Write-Host "    Atualizando pip..." -ForegroundColor DarkGray
& $pythonCmd.Source -m pip install --upgrade pip >$null 2>$null

Write-Host "    Instalando requirements.txt..." -ForegroundColor DarkGray
$pipResult = & $pythonCmd.Source -m pip install -r (Join-Path $BACKEND_DIR "requirements.txt") 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Falha ao instalar dependencias." -ForegroundColor Red
    Write-Host "    Rode manualmente:" -ForegroundColor Yellow
    Write-Host "      cd backend && venv\Scripts\activate && pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
Write-Host "  OK  Dependencias instaladas." -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 4) Verificar MySQL
# --------------------------------------------------
Write-Host "[4/9] Verificando MySQL..." -ForegroundColor Yellow
$mysqlCmd = Test-MySqlCmd
$mysqlAvailable = $false
if (-not $mysqlCmd) {
    Write-Host "  !  MySQL nao encontrado no PATH." -ForegroundColor Yellow
    Write-Host "     Baixe e instale: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Yellow
    Write-Host "     Anote a senha do root durante a instalacao." -ForegroundColor Yellow
    Write-Host "     Depois rode este script novamente." -ForegroundColor Yellow
} else {
    $mysqlAvailable = $true
    Write-Host "  OK  MySQL encontrado ($($mysqlCmd.Source))" -ForegroundColor Green
}
Write-Host ""

# --------------------------------------------------
# 5) Arquivo .env
# --------------------------------------------------
Write-Host "[5/9] Configurando arquivo .env..." -ForegroundColor Yellow

$defaultEnv = @"
# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=aqualog

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
    if (Test-Path -LiteralPath $ENV_EXAMPLE) {
        Copy-Item -LiteralPath $ENV_EXAMPLE -Destination $ENV_FILE
        Write-Host "  OK  backend\.env criado a partir do exemplo." -ForegroundColor Green
    } else {
        Set-Content -LiteralPath $ENV_FILE -Value $defaultEnv -Encoding UTF8
        Write-Host "  OK  backend\.env criado com valores padrao." -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "  ** IMPORTANTE: edite backend\.env e preencha: **" -ForegroundColor Yellow
    Write-Host "     - DB_PASSWORD  (senha do root do MySQL)" -ForegroundColor Yellow
    Write-Host "     - ADMIN_PASSWORD" -ForegroundColor Yellow
    Write-Host "     - JWT_SECRET" -ForegroundColor Yellow
    Write-Host "     - PIX_CHAVE" -ForegroundColor Yellow
} else {
    Write-Host "  OK  backend\.env ja existe (mantido)." -ForegroundColor Green
    $envContent = Get-Content -LiteralPath $ENV_FILE -Raw
    if ($envContent -notmatch 'DB_NAME=') {
        Add-Content -LiteralPath $ENV_FILE -Value "`nDB_NAME=aqualog"
    }
}
Write-Host ""

# --------------------------------------------------
# 6) Criar banco e tabelas via schema.sql
# --------------------------------------------------
Write-Host "[6/9] Criando banco de dados e tabelas..." -ForegroundColor Yellow

if (-not $mysqlAvailable) {
    Write-Host "  !  Pulando (MySQL nao disponível)." -ForegroundColor Yellow
    Write-Host "     Instale MySQL e rode manualmente:" -ForegroundColor Yellow
    Write-Host "       mysql -u root -p < backend\schema.sql" -ForegroundColor Yellow
} else {
    $shouldApply = $false
    if ($isInteractive) {
        try { $choice = Read-Host "  Aplicar backend\schema.sql agora? (cria banco + tabelas) [1] Nao / [2] Sim" } catch { $choice = "2" }
        if ($choice -eq "2") { $shouldApply = $true }
    } else {
        $shouldApply = $true
    }

    if ($shouldApply) {
        $mysqlUser = Read-SecureHost -Prompt "  Usuario MySQL [root]" -Default "root"
        $mysqlPass = Read-SecurePass -Prompt "  Senha MySQL para '$mysqlUser'"

        if (-not $mysqlPass) {
            Write-Host "  !  Senha vazia, pulando aplicacao do schema." -ForegroundColor Yellow
        } else {
            Write-Host "  Aplicando backend\schema.sql..." -ForegroundColor Yellow
            $code = Invoke-MySql -User $mysqlUser -Password $mysqlPass -SqlFile $SCHEMA_SQL
            if ($code -ne 0) {
                Write-Host "  !  Falha ao aplicar schema.sql (codigo $code)." -ForegroundColor Yellow
                Write-Host "     Verifique se o MySQL esta rodando e a senha esta correta." -ForegroundColor Yellow
                Write-Host "     Rode manualmente: mysql -u $mysqlUser -p < backend\schema.sql" -ForegroundColor Yellow
            } else {
                Write-Host "  OK  Banco 'aqualog' e tabelas criados com sucesso." -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  OK  Pulando aplicacao do schema." -ForegroundColor Green
    }
}
Write-Host ""

# --------------------------------------------------
# 7) Testar conectividade com banco
# --------------------------------------------------
Write-Host "[7/9] Testando conectividade com MySQL..." -ForegroundColor Yellow
if ($mysqlAvailable) {
    $envText = ""
    if (Test-Path -LiteralPath $ENV_FILE) {
        $envText = Get-Content -LiteralPath $ENV_FILE -Raw
    }
    $envUser = "root"
    $envPass = ""
    if ($envText -match 'DB_USER=(.+)') { $envUser = $Matches[1].Trim() }
    if ($envText -match 'DB_PASSWORD=(.+)') { $envPass = $Matches[1].Trim() }

    if (-not [string]::IsNullOrWhiteSpace($envPass)) {
        $secPass = $envPass | ConvertTo-SecureString -AsPlainText -Force
        $code = Invoke-MySql -User $envUser -Password $secPass -SqlFile $null -Database "aqualog"
        if ($code -eq 0) {
            Write-Host "  OK  Conectou ao banco 'aqualog' com sucesso." -ForegroundColor Green
        } else {
            Write-Host "  !  Nao conseguiu conectar ao banco 'aqualog'." -ForegroundColor Yellow
            Write-Host "     Verifique DB_USER e DB_PASSWORD no backend\.env" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  !  Senha do MySQL nao preenchida no .env. Pulando teste." -ForegroundColor Yellow
    }
} else {
    Write-Host "  !  MySQL nao disponível. Pulando teste." -ForegroundColor Yellow
}
Write-Host ""

# --------------------------------------------------
# 8) Resumo
# --------------------------------------------------
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Instalacao concluida!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Proximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Edite backend\.env (confirme DB_PASSWORD, JWT_SECRET, ADMIN_PASSWORD)"
Write-Host "  2. Rode o servidor:"
Write-Host "       cd backend"
Write-Host "       venv\Scripts\activate"
Write-Host "       uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
Write-Host ""
Write-Host "  Ou use: iniciar_tudo.bat"
Write-Host ""
Write-Host "  Telas:" -ForegroundColor Yellow
Write-Host "    Admin:      http://127.0.0.1:8000"
Write-Host "    Cliente:    http://127.0.0.1:8000/cliente.html"
Write-Host "    Entregador: http://127.0.0.1:8000/entregador.html"
Write-Host ""
Write-Host "  Testes:"
Write-Host "    cd backend && pytest tests/ -v"
Write-Host ""
Write-Host "  Log completo: $LOG_FILE" -ForegroundColor Gray
Write-Host ""

try { pause } catch {}
