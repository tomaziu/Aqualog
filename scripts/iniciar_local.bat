@echo off
title AquaLog - Iniciar Servidor Local

echo ========================================
echo   Iniciando AquaLog - Servidor Local
echo ========================================
echo.

rem Raiz do projeto = pasta acima de scripts
pushd "%~dp0.."
set "PROJECT_ROOT=%CD%"
popd

set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "PY=%BACKEND_DIR%\venv\Scripts\python.exe"

echo Projeto: %PROJECT_ROOT%
echo Backend: %BACKEND_DIR%
echo.

if not exist "%PY%" goto erro_venv

echo Aplicando migracoes...
cd /d "%BACKEND_DIR%"
"%PY%" migrate_site_features.py
if errorlevel 1 goto erro_migracao
echo OK - Migracoes aplicadas.
echo.

echo Iniciando servidor em nova janela...
start "AquaLog Server" /D "%BACKEND_DIR%" cmd /k ""%PY%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Abrindo frontend...
start "" http://127.0.0.1:8000
start "" http://127.0.0.1:8000/cliente.html
start "" http://127.0.0.1:8000/entregador.html

echo.
echo Servidor em http://127.0.0.1:8000
pause
exit /b 0

:erro_venv
echo ERRO: Python do venv nao encontrado em:
echo   %PY%
echo.
echo Confira se a estrutura e:
echo   aqualog_projeto\backend\venv\Scripts\python.exe
echo.
pause
exit /b 1

:erro_migracao
echo ERRO: Falha nas migracoes (errorlevel=%errorlevel%)
pause
exit /b 1