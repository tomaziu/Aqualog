# AquaLog - Iniciar Tudo (PowerShell)
# Execute com: .\iniciar_com_tunel.ps1
# Ou: PowerShell -ExecutionPolicy Bypass -File .\iniciar_com_tunel.ps1

$SCRIPT_DIR   = $PSScriptRoot
$PROJECT_ROOT = (Resolve-Path (Join-Path $SCRIPT_DIR "..")).Path
$BACKEND_DIR  = Join-Path $PROJECT_ROOT "backend"
$PY           = Join-Path $BACKEND_DIR "venv\Scripts\python.exe"

function Find-Cloudflared {
    $cmd = Get-Command cloudflared -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $locais = @(
        (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"),
        "$env:ProgramFiles\cloudflared",
        "$env:ProgramFiles\Cloudflare"
    )
    foreach ($pasta in $locais) {
        if (Test-Path -LiteralPath $pasta) {
            $achado = Get-ChildItem -LiteralPath $pasta -Filter "cloudflared.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($achado) { return $achado.FullName }
        }
    }
    return $null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando AquaLog" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path -LiteralPath $PY)) {
    Write-Host "ERRO: Python do venv nao encontrado em:" -ForegroundColor Red
    Write-Host "  $PY"
    Read-Host "Pressione Enter para sair"
    exit 1
}

Set-Location -LiteralPath $BACKEND_DIR

# Migracoes
Write-Host "Aplicando migracoes..." -ForegroundColor Yellow
& $PY migrate_site_features.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha ao aplicar migracoes." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "OK - Migracoes aplicadas." -ForegroundColor Green
Write-Host ""

# Servidor uvicorn em janela propria
Write-Host "Iniciando servidor AquaLog..." -ForegroundColor Yellow
Start-Process -FilePath $PY `
    -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" `
    -WorkingDirectory $BACKEND_DIR
Start-Sleep -Seconds 3

# Tunel Cloudflare (direto, sem cmd)
Write-Host "Abrindo tunel Cloudflare..." -ForegroundColor Yellow
$cf = Find-Cloudflared
if ($cf) {
    Start-Process -FilePath $cf `
        -ArgumentList "tunnel", "--url", "http://127.0.0.1:8000" `
        -WorkingDirectory $BACKEND_DIR
    Write-Host "Tunel iniciado: $cf" -ForegroundColor Green
} else {
    Write-Host "AVISO: cloudflared nao encontrado. Instale com: winget install Cloudflare.cloudflared" -ForegroundColor Red
}

# Frontend
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
Write-Host "O link publico aparece na janela do cloudflared (linha 'https://...trycloudflare.com')."
Write-Host "Use no Mercado Pago:"
Write-Host "  https://SEU-LINK.trycloudflare.com/api/v1/site/mercado-pago/webhook"
Write-Host "Nao feche as janelas do servidor e do tunel."
Write-Host ""

Read-Host "Pressione Enter para fechar este terminal"