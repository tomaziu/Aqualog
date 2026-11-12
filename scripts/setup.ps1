# AquaLog - Instalador Automatico (PowerShell)
# Instala tudo o que e necessario para rodar o AquaLog em qualquer PC Windows.
# Execute com: .\scripts\setup.ps1  (ou PowerShell -ExecutionPolicy Bypass -File scripts\setup.ps1)

$ErrorActionPreference = "Continue"
$SCRIPT_DIR   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROJECT_ROOT = Resolve-Path (Join-Path $SCRIPT_DIR "..")
Set-Location -LiteralPath $PROJECT_ROOT

$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$VENV_DIR    = Join-Path $BACKEND_DIR "venv"
$ENV_FILE    = Join-Path $BACKEND_DIR ".env"
$SCHEMA_SQL  = Join-Path $BACKEND_DIR "schema.sql"

$UTF8_SEM_BOM = New-Object System.Text.UTF8Encoding($false)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AquaLog - Instalador Automatico" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --------------------------------------------------
# Funcoes auxiliares
# --------------------------------------------------

# Escreve valor de .env entre aspas, escapando \ e "
function Format-EnvValue {
    param([AllowNull()][AllowEmptyString()][string]$Valor)
    if ($null -eq $Valor) { $Valor = "" }
    $escaped = $Valor.Replace('\', '\\').Replace('"', '\"')
    return '"' + $escaped + '"'
}

# Le o .env como linhas, sem \r
function Read-EnvLinhas {
    param([string]$Caminho)
    if (-not (Test-Path -LiteralPath $Caminho)) { return @() }
    return [string[]]([IO.File]::ReadAllText($Caminho) -split "`r?`n")
}

# Grava o .env sem BOM e com \n
function Write-EnvLinhas {
    param([string]$Caminho, [string[]]$Linhas)
    [IO.File]::WriteAllText($Caminho, (($Linhas -join "`n") + "`n"), $UTF8_SEM_BOM)
}

# Define ou troca uma chave no .env, preservando o resto
function Set-EnvChave {
    param([string[]]$Linhas, [string]$Chave, [string]$Valor)
    $achou = $false
    $saida = New-Object System.Collections.Generic.List[string]
    foreach ($l in $Linhas) {
        if ($l -match "^\s*$([regex]::Escape($Chave))\s*=") {
            $saida.Add("$Chave=$Valor")
            $achou = $true
        } else {
            $saida.Add($l)
        }
    }
    if (-not $achou) { $saida.Add("$Chave=$Valor") }
    return ,$saida.ToArray()
}

# Executa mysql sem passar a senha pela linha de comando
function Invoke-MySql {
    param([string]$Exe, [string]$Senha, [string]$Sql, [string]$ArquivoSql = $null, [string]$Banco = $null)

    $cnf = Join-Path $env:TEMP ("aqualog_" + [guid]::NewGuid().ToString("N") + ".cnf")
    try {
        $linhasCnf = @("[client]", "user=root", "host=localhost", "port=3306", "protocol=tcp")
        if (-not [string]::IsNullOrEmpty($Senha)) {
            $linhasCnf += "password=" + $Senha.Replace('\', '\\').Replace('"', '\"').Insert(0, '"').Insert(0, 'password=').Substring(9) + '"'
        }
        [IO.File]::WriteAllText($cnf, (($linhasCnf -join "`n") + "`n"), $UTF8_SEM_BOM)

        $args = @("--defaults-extra-file=$cnf")
        if ($Banco) { $args += $Banco }

        if ($ArquivoSql) {
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = $Exe
            $psi.Arguments = ($args | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
            $psi.RedirectStandardInput = $true
            $psi.RedirectStandardOutput = $true
            $psi.RedirectStandardError = $true
            $psi.UseShellExecute = $false
            $psi.CreateNoWindow = $true
            $p = [System.Diagnostics.Process]::Start($psi)
            $p.StandardInput.Write([IO.File]::ReadAllText($ArquivoSql, [Text.Encoding]::UTF8))
            $p.StandardInput.Close()
            $p.StandardOutput.ReadToEnd() | Out-Null
            $p.StandardError.ReadToEnd() | Out-Null
            $p.WaitForExit()
            return $p.ExitCode
        } else {
            $args += @("-N", "-B", "-e", $Sql)
            $saida = & $Exe @args 2>$null
            if ($LASTEXITCODE -ne 0) { return @{ Codigo = $LASTEXITCODE; Saida = $saida } }
            return @{ Codigo = 0; Saida = $saida }
        }
    } finally {
        Remove-Item -LiteralPath $cnf -Force -ErrorAction SilentlyContinue
    }
}

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
$venvPython = Join-Path $VENV_DIR "Scripts\python.exe"

Write-Host "    Atualizando pip..." -ForegroundColor DarkGray
& $venvPython -m pip install --upgrade pip *> $null

Write-Host "    Instalando requirements.txt..." -ForegroundColor DarkGray
& $venvPython -m pip install -r (Join-Path $BACKEND_DIR "requirements.txt")
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
$mysqlExecutable = $null
$mysqlCmd = Get-Command mysql -ErrorAction SilentlyContinue
if ($mysqlCmd) { $mysqlExecutable = $mysqlCmd.Source }

if (-not $mysqlExecutable) {
    $versoes = @("8.4", "8.3", "8.2", "8.1", "8.0", "5.7")
    $caminhosComuns = @()
    foreach ($v in $versoes) {
        $caminhosComuns += "C:\Program Files\MySQL\MySQL Server $v\bin\mysql.exe"
        $caminhosComuns += "C:\Program Files (x86)\MySQL\MySQL Server $v\bin\mysql.exe"
    }
    $caminhosComuns += "C:\mysql\bin\mysql.exe"
    foreach ($caminho in $caminhosComuns) {
        if (Test-Path -LiteralPath $caminho) { $mysqlExecutable = $caminho; break }
    }
}

if (-not $mysqlExecutable) {
    Write-Host "  X MySQL nao encontrado!" -ForegroundColor Red
    Write-Host "    1. Baixe e instale: https://www.mysql.com/downloads/" -ForegroundColor Red
    Write-Host "    2. Anote a senha do usuario root durante a instalacao." -ForegroundColor Red
    Write-Host "    3. Adicione o MySQL ao PATH ou instale na pasta padrao." -ForegroundColor Red
    Write-Host "    4. Rode este script novamente." -ForegroundColor Red
    exit 1
}
Write-Host "  OK  MySQL encontrado ($mysqlExecutable)" -ForegroundColor Green
Write-Host ""

# --------------------------------------------------
# 5) Configurar .env e banco de dados
# --------------------------------------------------
Write-Host "[5/5] Configurando arquivo .env e banco de dados..." -ForegroundColor Yellow

$bancoPadrao = "aqualog"
$bancoNome = Read-Host "  Nome do banco (Enter para '$bancoPadrao')"
if ([string]::IsNullOrWhiteSpace($bancoNome)) { $bancoNome = $bancoPadrao }
$bancoNome = $bancoNome.Trim()
if ($bancoNome -notmatch '^[a-zA-Z0-9_]+$') {
    Write-Host "  X Nome de banco invalido. Use somente letras, numeros e underline." -ForegroundColor Red
    exit 1
}
Write-Host "  Usando banco: $bancoNome" -ForegroundColor Green
Write-Host ""

# Senha pedida uma unica vez (Enter = root sem senha)
$senhaSegura = Read-Host "  Senha do MySQL root (Enter se nao houver)" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($senhaSegura)
try { $senhaMysql = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
if ($null -eq $senhaMysql) { $senhaMysql = "" }

# Monta o .env
$padraoEnv = @(
    "# MySQL",
    "DB_HOST=localhost",
    "DB_PORT=3306",
    "DB_USER=root",
    "DB_PASSWORD=",
    "DB_NAME=",
    "",
    "# Auth",
    "JWT_SECRET=aqualog_jwt_secret_change_in_production",
    "ADMIN_PASSWORD=admin123",
    "",
    "# Pagamento",
    "PIX_CHAVE=",
    "MERCADO_PAGO_ACCESS_TOKEN=",
    "",
    "# Servidor",
    "PORT=8000"
)

$linhasEnv = if (Test-Path -LiteralPath $ENV_FILE) { Read-EnvLinhas $ENV_FILE } else { $padraoEnv }
$linhasEnv = Set-EnvChave -Linhas $linhasEnv -Chave "DB_USER" -Valor "root"
$linhasEnv = Set-EnvChave -Linhas $linhasEnv -Chave "DB_PASSWORD" -Valor (Format-EnvValue $senhaMysql)
$linhasEnv = Set-EnvChave -Linhas $linhasEnv -Chave "DB_NAME" -Valor $bancoNome
Write-EnvLinhas -Caminho $ENV_FILE -Linhas $linhasEnv
Write-Host "  OK  backend\.env configurado (DB_NAME=$bancoNome)." -ForegroundColor Green
Write-Host ""

# Verifica conexao
Write-Host "  Testando conexao com MySQL..." -ForegroundColor Yellow
$teste = Invoke-MySql -Exe $mysqlExecutable -Senha $senhaMysql -Sql "SELECT 1;"
if ($teste.Codigo -ne 0) {
    Write-Host "  X Nao foi possivel conectar ao MySQL. Verifique a senha e se o servico esta rodando." -ForegroundColor Red
    exit 1
}
Write-Host "  OK  Conexao estabelecida." -ForegroundColor Green

# Cria banco se nao existir
$criar = Invoke-MySql -Exe $mysqlExecutable -Senha $senhaMysql -Sql "CREATE DATABASE IF NOT EXISTS ``$bancoNome`` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if ($criar.Codigo -ne 0) {
    Write-Host "  X Falha ao criar o banco '$bancoNome'." -ForegroundColor Red
    exit 1
}

# Verifica se ja tem tabelas
$contagem = Invoke-MySql -Exe $mysqlExecutable -Senha $senhaMysql -Sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$bancoNome';"
$totalTabelas = 0
if ($contagem.Codigo -eq 0 -and $contagem.Saida) {
    [int]::TryParse(([string]($contagem.Saida | Select-Object -Last 1)).Trim(), [ref]$totalTabelas) | Out-Null
}

if ($totalTabelas -gt 0) {
    Write-Host "  OK  Banco '$bancoNome' ja possui $totalTabelas tabela(s). Schema nao foi reaplicado." -ForegroundColor Green
} else {
    Write-Host "  Aplicando schema.sql no banco '$bancoNome'..." -ForegroundColor Yellow
    $schemaConteudo = [IO.File]::ReadAllText($SCHEMA_SQL)
    $schemaConteudo = [regex]::Replace($schemaConteudo, '(?i)\baqualog\b', $bancoNome)
    $schemaTemp = Join-Path $env:TEMP ("aqualog_schema_" + [guid]::NewGuid().ToString("N") + ".sql")
    [IO.File]::WriteAllText($schemaTemp, $schemaConteudo, $UTF8_SEM_BOM)
    try {
        $aplicar = Invoke-MySql -Exe $mysqlExecutable -Senha $senhaMysql -ArquivoSql $schemaTemp -Banco $bancoNome
        if ($aplicar -ne 0) {
            Write-Host "  X Falha ao aplicar schema.sql." -ForegroundColor Red
            exit 1
        }
        Write-Host "  OK  Tabelas criadas com sucesso." -ForegroundColor Green
    } finally {
        Remove-Item -LiteralPath $schemaTemp -Force -ErrorAction SilentlyContinue
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
Write-Host "    - Arquivo backend\.env configurado (DB_NAME=$bancoNome)"
Write-Host "    - Banco de dados e tabelas verificados"
Write-Host ""
Write-Host "  Para iniciar o servidor:" -ForegroundColor Yellow
Write-Host "    .\scripts\iniciar_local.ps1"
Write-Host ""
Write-Host "  Telas apos iniciar:" -ForegroundColor Yellow
Write-Host "    Admin:      http://127.0.0.1:8000"
Write-Host "    Cliente:    http://127.0.0.1:8000/cliente.html"
Write-Host "    Entregador: http://127.0.0.1:8000/entregador.html"
Write-Host ""
Write-Host "  Login admin: senha definida no arquivo .env (ADMIN_PASSWORD)" -ForegroundColor Yellow
Write-Host ""

try { pause } catch {}