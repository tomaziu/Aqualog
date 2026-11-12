@echo off
title AquaLog - Iniciar Servidor Local

echo ========================================
echo   Iniciando AquaLog - Servidor Local
echo ========================================
echo.

:: Obtem o diretorio deste script de forma confiavel
set "SCRIPT_DIR=%~dp0"
:: Remove a barra final se houver
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Sobe um nivel para a raiz do projeto, depois entra em backend
:: SCRIPT_DIR = ...\aqualog_projeto\scripts
:: PROJECT_ROOT = ...\aqualog_projeto
:: BACKEND_DIR = ...\aqualog_projeto\backend
for %%I in ("%SCRIPT_DIR%\..") do set "PROJECT_ROOT=%%~fI"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"

echo Procurando backend em: %BACKEND_DIR%
if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    echo.
    echo ERRO: Nao encontrou o backend em "%BACKEND_DIR%"
    echo.
    echo Verificando caminhos alternativos...
    
    :: Tenta caminhos alternativos
    if exist "..\backend\venv\Scripts\python.exe" (
        set "BACKEND_DIR=..\backend"
        for %%I in ("%BACKEND_DIR%") do set "BACKEND_DIR=%%~fI"
        echo Encontrou backend em caminho relativo: %BACKEND_DIR%
    ) else if exist "backend\venv\Scripts\python.exe" (
        set "BACKEND_DIR=backend"
        for %%I in ("%BACKEND_DIR%") do set "BACKEND_DIR=%%~fI"
        echo Encontrou backend em: %BACKEND_DIR%
    ) else (
        echo.
        echo ERRO: Nao foi possível localizar a pasta backend\venv
        echo.
        echo Dica: Execute este arquivo a partir da pasta do projeto ou certifique-se
        echo de que a estrutura de pastas esta correta:
        echo   aqualog_projeto/
        echo   ├── backend/
        echo   │   └── venv/
        echo   └── scripts/
        echo       └── iniciar_local.bat
        echo.
        pause
        exit /b 1
    )
)

echo BACKEND_DIR: %BACKEND_DIR%
if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    echo ERRO: Python do venv nao encontrado em %BACKEND_DIR%\venv\Scripts\python.exe
    pause
    exit /b 1
)
echo BACKEND_DIR OK: %BACKEND_DIR%
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