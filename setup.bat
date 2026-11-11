@echo off
title AquaLog - Instalador Automatico
setlocal EnableDelayedExpansion

echo ========================================
echo   AquaLog - Instalador Automatico
echo ========================================
echo   Log: %TEMP%\aqualog_setup.log
echo.

cd /d "%~dp0"

set "BACKEND_DIR=%~dp0backend"
set "VENV_DIR=%BACKEND_DIR%\venv"
set "ENV_FILE=%BACKEND_DIR%\.env"
set "ENV_EXAMPLE=%BACKEND_DIR%\.env.example"
set "SCHEMA_SQL=%BACKEND_DIR%\schema.sql"

:: --------------------------------------------------
:: 1) Verificar Python
:: --------------------------------------------------
echo [1/9] Verificando Python...
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo.
        echo  X Python nao encontrado!
        echo    Instale Python 3.11+ em: https://www.python.org/downloads/
        echo    Marque "Add Python to PATH" durante a instalacao.
        echo.
        pause
        exit /b 1
    )
    set "PYCMD=py"
) else (
    set "PYCMD=python"
)
for /f "delims=" %%v in ('%PYCMD% --version 2^>^&1') do set "PYVER=%%v"
echo  OK  %PYVER%
echo.

:: --------------------------------------------------
:: 2) Criar ambiente virtual
:: --------------------------------------------------
echo [2/9] Preparando ambiente virtual...
if not exist "%VENV_DIR%" (
    "%PYCMD%" -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo  X Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
    echo  OK  venv criado em %VENV_DIR%
) else (
    echo  OK  venv ja existe
)
echo.

:: --------------------------------------------------
:: 3) Instalar dependencias
:: --------------------------------------------------
echo [3/9] Instalando dependencias Python (pode demorar)...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo  X Falha ao instalar dependencias.
    echo    Rode manualmente:
    echo      cd backend && venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)
echo  OK  Dependencias instaladas.
echo.

:: --------------------------------------------------
:: 4) Verificar MySQL
:: --------------------------------------------------
echo [4/9] Verificando MySQL...
where mysql >nul 2>nul
if errorlevel 1 (
    echo  !  MySQL nao encontrado no PATH.
    echo     Baixe e instale: https://dev.mysql.com/downloads/mysql/
    echo     Anote a senha do root durante a instalacao.
    echo     Depois rode este script novamente.
) else (
    echo  OK  MySQL encontrado no PATH.
)
echo.

:: --------------------------------------------------
:: 5) Arquivo .env
:: --------------------------------------------------
echo [5/9] Configurando arquivo .env...
if not exist "%ENV_FILE%" (
    if exist "%ENV_EXAMPLE%" (
        copy /y "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
        echo  OK  backend\.env criado a partir do exemplo.
    ) else (
        echo # MySQL > "%ENV_FILE%"
        echo DB_HOST=localhost >> "%ENV_FILE%"
        echo DB_PORT=3306 >> "%ENV_FILE%"
        echo DB_USER=root >> "%ENV_FILE%"
        echo DB_PASSWORD= >> "%ENV_FILE%"
        echo DB_NAME=aqualog >> "%ENV_FILE%"
        echo. >> "%ENV_FILE%"
        echo # Auth >> "%ENV_FILE%"
        echo JWT_SECRET=aqualog_jwt_secret_change_in_production >> "%ENV_FILE%"
        echo ADMIN_PASSWORD=admin123 >> "%ENV_FILE%"
        echo. >> "%ENV_FILE%"
        echo # Pagamento >> "%ENV_FILE%"
        echo PIX_CHAVE= >> "%ENV_FILE%"
        echo MERCADO_PAGO_ACCESS_TOKEN= >> "%ENV_FILE%"
        echo. >> "%ENV_FILE%"
        echo # Servidor >> "%ENV_FILE%"
        echo PORT=8000 >> "%ENV_FILE%"
        echo  OK  backend\.env criado com valores padrao.
    )
    echo.
    echo  ** IMPORTANTE: edite backend\.env e preencha: **
    echo     - DB_PASSWORD  (senha do root do MySQL)
    echo     - ADMIN_PASSWORD
    echo     - JWT_SECRET
    echo     - PIX_CHAVE
) else (
    echo  OK  backend\.env ja existe (mantido).
    echo %ENV_FILE% | findstr /c:"DB_NAME=" >nul
    if errorlevel 1 (
        echo DB_NAME=aqualog >> "%ENV_FILE%"
    )
)
echo.

:: --------------------------------------------------
:: 6) Criar banco e tabelas via schema.sql
:: --------------------------------------------------
echo [6/9] Criando banco de dados e tabelas...
where mysql >nul 2>nul
if errorlevel 1 (
    echo  !  Pulando (MySQL nao disponível).
    echo     Instale MySQL e rode manualmente:
    echo       mysql -u root -p < backend\schema.sql
) else (
    echo.
    set /p APLY_SCHEMA=  Aplicar backend\schema.sql agora? (cria banco + tabelas) [1=Nao / 2=Sim]:
    if "!APLY_SCHEMA!"=="2" (
        echo.
        set /p MYSQL_USER=  Usuario MySQL [root]:
        if "!MYSQL_USER!"=="" set "MYSQL_USER=root"
        set /p MYSQL_PASS=  Senha MySQL para !MYSQL_USER!:

        echo.
        echo  Aplicando backend\schema.sql...
        mysql -u !MYSQL_USER! -p!MYSQL_PASS! < "%SCHEMA_SQL%"
        if errorlevel 1 (
            echo  !  Falha ao aplicar schema.sql.
            echo     Verifique se o MySQL esta rodando e a senha esta correta.
            echo     Rode manualmente: mysql -u !MYSQL_USER! -p < backend\schema.sql
        ) else (
            echo  OK  Banco 'aqualog' e tabelas criados com sucesso.
        )
    ) else (
        echo  OK  Pulando aplicacao do schema.
    )
)
echo.

:: --------------------------------------------------
:: 7) Testar conectividade com banco
:: --------------------------------------------------
echo [7/9] Testando conectividade com MySQL...
where mysql >nul 2>nul
if errorlevel 1 (
    echo  !  MySQL nao disponível. Pulando teste.
) else (
    set "ENV_USER=root"
    set "ENV_PASS="
    if exist "%ENV_FILE%" (
        for /f "usebackq tokens=1* delims==" %%a in ("%ENV_FILE%") do (
            if "%%a"=="DB_USER" set "ENV_USER=%%b"
            if "%%a"=="DB_PASSWORD" set "ENV_PASS=%%b"
        )
    )
    if defined ENV_PASS (
        mysql -u %ENV_USER% -p%ENV_PASS% -e "SELECT 1" aqualog >nul 2>nul
        if errorlevel 1 (
            echo  !  Nao conseguiu conectar ao banco 'aqualog'.
            echo     Verifique DB_USER e DB_PASSWORD no backend\.env
        ) else (
            echo  OK  Conectou ao banco 'aqualog' com sucesso.
        )
    ) else (
        echo  !  Senha do MySQL nao preenchida no .env. Pulando teste.
    )
)
echo.

:: --------------------------------------------------
:: 8) Resumo / Final
:: --------------------------------------------------
echo ========================================
echo   Instalacao concluida!
echo ========================================
echo.
echo   Proximos passos:
echo.
echo   1. Edite o arquivo backend\.env (confirme DB_PASSWORD, JWT_SECRET, ADMIN_PASSWORD)
echo   2. Rode o servidor:
echo        cd backend
echo        venv\Scripts\activate
echo        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo   Ou use: iniciar_tudo.bat
echo.
echo   Telas:
echo     Admin:      http://127.0.0.1:8000
echo     Cliente:    http://127.0.0.1:8000/cliente.html
echo     Entregador: http://127.0.0.1:8000/entregador.html
echo.
echo   Testes:
echo     cd backend && pytest tests/ -v
echo.
echo   Log salvo em: %TEMP%\aqualog_setup.log
echo.

pause
endlocal
