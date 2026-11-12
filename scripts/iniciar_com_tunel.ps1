# AquaLog - Iniciar Tudo (PowerShell)
# Equivalente ao iniciar_com_tunel.bat
# Execute com: .\iniciar_com_tunel.ps1  (ou PowerShell -ExecutionPolicy Bypass -File iniciar_com_tunel.ps1)

$ErrorActionPreference = "Continue"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROJECT_ROOT = Resolve-Path (Join-Path $SCRIPT_DIR "..")
Set-Location -LiteralPath (Join-Path $PROJECT_ROOT "backend")

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando AquaLog" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Aplicando migracoes
Write-Host "Aplicando migracoes..." -ForegroundColor Yellow
$mig = & "venv\Scripts\python" migrate_site_features.py 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha ao aplicar migracoes." -ForegroundColor Red
    exit 1
}

# Iniciar servidor uvicorn
Write-Host "Iniciando servidor AquaLog..." -ForegroundColor Yellow
Start-Process -FilePath "venv\Scripts\python" -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
Start-Sleep -Seconds 3

# Tunnel Cloudflare
$CLOUDFLARED = "cloudflared"
$cloudflaredPath = Get-Command $CLOUDFLARED -ErrorAction SilentlyContinue
if (-not $cloudflaredPath) {
    $candidate = "C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"
    if (Test-Path -LiteralPath $candidate) { $cloudflaredPath = $candidate }
}

Write-Host "Abrindo tunel Cloudflare..." -ForegroundColor Yellow
if ($cloudflaredPath) {
    Start-Process -FilePath "cmd" -ArgumentList "/k `"& '$cloudflaredPath' tunnel --url http://127.0.0.1:8000`"" -WindowStyle Normal
} else {
    Start-Process -FilePath "cmd" -ArgumentList "/k cloudflared tunnel --url http://127.0.0.1:8000" -WindowStyle Normal
}

# Abrir frontend
Write-Host "Abrindo frontend..." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:8000"
Start-Process "http://127.0.0.1:8000/cliente.html"
Start-Process "http://127.0.0.1:8000/entregador.html"

Write-Host ""
Write-Host "Servidor iniciado!" -ForegroundColor Green
Write-Host "Admin:      http://127.0.0.1:8000"
Write-Host "Cliente:    http://127.0.0.1:8000/cliente.html"
Write-Host "Entregador: http://127.0.0.1:8000/entregador.html"
Write-Host ""
Write-Host "O link publico vai aparecer na janela 'AquaLog Tunnel'."
Write-Host "Use no Mercado Pago:"
Write-Host "  https://SEU-LINK.trycloudflare.com/api/v1/site/mercado-pago/webhook"
Write-Host "Nao feche a janela do servidor."
Write-Host ""

try { pause } catch {}