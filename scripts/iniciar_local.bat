@echo off
title AquaLog - Iniciar Servidor Local

echo ========================================
echo   Iniciando AquaLog - Servidor Local
echo ========================================
echo.

:: Encontra o diretorio do backend procurando a pasta venv
set "BACKEND_DIR="
if exist "..\backend\venv" set "BACKEND_DIR=..\backend"
if exist "backend\venv" set "BACKEND_DIR=backend"
if exist "%~dp0..\backend\venv" set "BACKEND_DIR=%~dp0..\backend"

:: Normaliza o caminho
for %%I in ("%BACKEND_DIR%") do set "BACKEND_DIR=%%~fI"

echo BACKEND_DIR: %BACKEND_DIR%
if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    echo ERRO: Backend nao encontrado em %BACKEND_DIR%
    pause
    exit /b 1
)
echo BACKEND_DIR: %BACKEND_DIR%
echo.

:: Aplica migrações
echo Aplicando migracoes...
cd /d "%BACKEND_DIR%"
call "%BACKEND_DIR%\venv\Scripts\activate.bat"
python migrate_site_features.py
if errorlevel 1 (
    echo ERRO: Falha nas migracoes (errorlevel=%errorlevel%)
    pause
    exit /b 1
)
echo OK - Migracoes aplicadas.
echo.

:: Inicia servidor em nova janela
echo Iniciando servidor...
set "SERVER_BAT=%TEMP%\aqualog_server_%RANDOM%.bat"
echo @echo off > "%SERVER_BAT%"
echo title AquaLog Server >> "%SERVER_BAT%"
echo cd /d "%BACKEND_DIR%" >> "%SERVER_BAT%"
echo call "%BACKEND_DIR%\venv\Scripts\activate.bat" >> "%SERVER_BAT%"
echo python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload >> "%SERVER_BAT%"
echo pause >> "%SERVER_BAT%"

start "AquaLog Server" cmd /k "%SERVER_BAT%"

timeout /t 3 /nobreak >nul

echo Abrindo frontend...
start "" http://127.0.0.1:8000
start "" http://127.0.0.1:8000/cliente.html
start "" http://127.0.0.1:8000/entregador.html

echo.
echo Servidor em http://127.0.0.1:8000
pause