@echo off
cd /d "%~dp0backend"

echo Iniciando processos no Prompt de Comando padrao...

:: Aplica migrações e abre o servidor em uma nova janela do CMD
start "AquaLog Server" cmd /k "cd /d %~dp0backend && venv\Scripts\python migrate_site_features.py && venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Abrindo frontend...
start "" http://127.0.0.1:8000
start "" http://127.0.0.1:8000/cliente.html
start "" http://127.0.0.1:8000/entregador.html
