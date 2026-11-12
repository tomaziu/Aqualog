# AquaLog - Iniciar Servidor (PowerShell)
# Equivalente ao iniciar_local.bat
# Execute com: .\iniciar_local.ps1  (ou PowerShell -ExecutionPolicy Bypass -File iniciar_local.ps1)

$ErrorActionPreference = "Continue"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROJECT_ROOT = Resolve-Path (Join-Path $SCRIPT_DIR "..")
Set-Location -LiteralPath $PROJECT_ROOT

Write-Host "Iniciando processos no PowerShell..." -ForegroundColor Yellow

# Aplica migracao e inicia o servidor em uma nova janela
$cmd = "cd /d `"$PROJECT_ROOT\backend`" && venv\Scripts\python migrate_site_features.py && venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -FilePath "cmd" -ArgumentList "/k `"$cmd`"" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "Abrindo frontend..." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:8000"
Start-Process "http://127.0.0.1:8000/cliente.html"
Start-Process "http://127.0.0.1:8000/entregador.html"

Write-Host "Servidor iniciado!" -ForegroundColor Green

try { pause } catch {}