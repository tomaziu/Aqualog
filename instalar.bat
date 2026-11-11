@echo off
title AquaLog - Instalador
setlocal EnableDelayedExpansion

echo ========================================
echo   AquaLog - Instalador Automatico
echo ========================================
echo.

cd /d "%~dp0"

:: --------------------------------------------------
:: 1) Verificar Python
:: --------------------------------------------------
echo [1/6] Verificando Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  X Python nao encontrado!
    echo    Instale Python 3.11 em: https://www.python.org/downloads/
    echo    Marque "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo  OK  !PYVER!
echo.

:: --------------------------------------------------
:: 2) Criar ambiente virtual
:: --------------------------------------------------
echo [2/6] Preparando ambiente virtual...
if not exist "backend\venv" (
    py -m venv backend\venv 2>nul || python -m venv backend\venv
    if errorlevel 1 (
        echo  X Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
    echo  OK  venv criado em backend\venv
) else (
    echo  OK  venv ja existe
)
echo.

:: --------------------------------------------------
:: 3) Instalar dependencias
:: --------------------------------------------------
echo [3/6] Instalando dependencias Python (pode demorar)...
call "backend\venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo  X Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo  OK  Dependencias instaladas.
echo.

:: --------------------------------------------------
:: 4) Arquivo .env
:: --------------------------------------------------
echo [4/6] Configurando arquivo .env...
if not exist "backend\.env" (
    copy /y "backend\.env.example" "backend\.env" >nul
    echo  OK  backend\.env criado a partir do exemplo.
    echo.
    echo  ** IMPORTANTE: edite backend\.env e preencha: **
    echo     - DB_PASSWORD  (senha do MySQL)
    echo     - ADMIN_PASSWORD
    echo     - JWT_SECRET
    echo     - PIX_CHAVE
    echo.
) else (
    echo  OK  backend\.env ja existe (mantido).
)
echo.

:: --------------------------------------------------
:: 5) Verificar MySQL (aviso)
:: --------------------------------------------------
echo [5/6] Verificando MySQL...
where mysql >nul 2>nul
if errorlevel 1 (
    echo  !  MySQL nao encontrado no PATH.
    echo     Instale: https://dev.mysql.com/downloads/mysql/
) else (
    echo  OK  MySQL encontrado no PATH.
)
echo.

:: --------------------------------------------------
:: 6) Criar tabelas (opcional)
:: --------------------------------------------------
echo [6/6] Schema do banco de dados.
echo.
echo  Voce ja tem o banco "aqualog" com as tabelas?
echo    [1] Sim, pular
echo    [2] Nao, tentar aplicar schema.sql agora
echo.
set "SCHEMA_OPT=0"
set /p SCHEMA_OPT=Escolha (1 ou 2): 

if "!SCHEMA_OPT!"=="2" (
    echo.
    echo  Vamos aplicar backend\schema.sql
    echo  Voce precisara do usuario e senha do MySQL.
    echo.
    set /p MYSQL_USER=Usuario MySQL [root]: 
    if "!MYSQL_USER!"=="" set "MYSQL_USER=root"
    set /p MYSQL_PASS=Senha MySQL: 
    mysql -u !MYSQL_USER! -p!MYSQL_PASS! < backend\schema.sql
    if errorlevel 1 (
        echo  !  Nao foi possivel aplicar o schema agora.
        echo     Aplique manualmente depois:
        echo     mysql -u root -p ^< backend\schema.sql
    ) else (
        echo  OK  Tabelas criadas.
    )
) else (
    echo  OK  Pulando schema.
)
echo.

:: --------------------------------------------------
:: Final
:: --------------------------------------------------
echo ========================================
echo   Instalacao concluida!
echo ========================================
echo.
echo  Proximos passos:
echo.
echo  1. Edite o arquivo backend\.env (senha MySQL, JWT, Pix)
echo  2. Rode o servidor:
echo       cd backend
echo       venv\Scripts\activate
echo       uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo  Ou use o atalho: iniciar_tudo.bat
echo.
echo  Telas apos iniciar:
echo    Admin:      http://127.0.0.1:8000
echo    Cliente:    http://127.0.0.1:8000/cliente.html
echo    Entregador: http://127.0.0.1:8000/entregador.html
echo.
echo  Testes:
echo    cd backend ^&^& pytest tests/ -v
echo.

pause
endlocal
