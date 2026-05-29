@echo off
cd /d "%~dp0backend"

echo Iniciando servidor...
start "AquaLog Server" "venv\Scripts\python" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

timeout /t 3 /nobreak >nul

echo Abrindo frontend...
start "" http://127.0.0.1:8000
start "" http://127.0.0.1:8000/entregador.html
