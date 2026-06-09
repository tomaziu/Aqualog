@echo off
title AquaLog

echo ========================================
echo   Iniciando AquaLog
echo ========================================

set "CLOUDFLARED=cloudflared"
where cloudflared >nul 2>nul
if errorlevel 1 (
  set "CLOUDFLARED=C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"
)

cd /d "%~dp0aqualog\backend"
echo Aplicando migracoes...
"venv\Scripts\python" migrate_site_features.py
if errorlevel 1 (
  echo Falha ao aplicar migracoes.
  pause
  exit /b 1
)

start "AquaLog Server" "venv\Scripts\python" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
timeout /t 3 /nobreak >nul

echo Abrindo tunel Cloudflare...
if exist "%CLOUDFLARED%" (
  start "AquaLog Tunnel" cmd /k ""%CLOUDFLARED%" tunnel --url http://127.0.0.1:8000"
) else (
  start "AquaLog Tunnel" cmd /k "cloudflared tunnel --url http://127.0.0.1:8000"
)

echo Abrindo frontend...
start "" http://127.0.0.1:8000
start "" http://127.0.0.1:8000/cliente.html
start "" http://127.0.0.1:8000/entregador.html

echo.
echo Servidor iniciado!
echo Admin: http://127.0.0.1:8000
echo Cliente: http://127.0.0.1:8000/cliente.html
echo Entregador: http://127.0.0.1:8000/entregador.html
echo.
echo O link publico vai aparecer na janela "AquaLog Tunnel".
echo Use no Mercado Pago:
echo https://SEU-LINK.trycloudflare.com/api/v1/site/mercado-pago/webhook
echo Nao feche a janela do servidor.
