@echo off
title AquaLog - Instalador Automatico

echo ========================================
echo   AquaLog - Instalador Automatico
echo ========================================
echo.

:: Vai para a raiz do projeto (pasta onde o scripts/ esta)
cd /d "%~dp0.."

set "BACKEND_DIR=%CD%\backend"
set "VENV_DIR=%BACKEND_DIR%\venv"
set "ENV_FILE=%BACKEND_DIR%\.env"
set "SCHEMA_SQL=%BACKEND_DIR%\schema.sql"

:: --------------------------------------------------
:: 1) Verificar Python
:: --------------------------------------------------
echo [1/5] Verificando Python...
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo.
        echo  X Python nao encontrado!
        echo    Baixe e instale: https://www.python.org/downloads/
        echo    IMPORTANTE: marque "Add Python to PATH" durante a instalacao.
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
echo [2/5] Preparando ambiente virtual...
if not exist "%VENV_DIR%" (
    "%PYCMD%" -m venv "%VENV_DIR%"
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
echo [3/5] Instalando dependencias Python (pode demorar alguns minutos)...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo  X Falha ao instalar dependencias.
    echo    Tente rodar manualmente:
    echo      cd backend && venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)
echo  OK  Dependencias instaladas.
echo.

:: --------------------------------------------------
:: 4) Verificar MySQL
:: --------------------------------------------------
echo [4/5] Verificando MySQL...
where mysql >nul 2>nul
if errorlevel 1 (
    echo    MySQL nao esta no PATH. Procurando em instalacoes comuns...
    set "MYSQL_EXE="
    if exist "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
    if exist "C:\Program Files\MySQL\MySQL Server 8.3\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.3\bin\mysql.exe"
    if exist "C:\Program Files\MySQL\MySQL Server 8.2\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.2\bin\mysql.exe"
    if exist "C:\Program Files\MySQL\MySQL Server 8.1\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.1\bin\mysql.exe"
    if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
    if exist "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe"
    if exist "C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe"
    if exist "C:\Program Files (x86)\MySQL\MySQL Server 8.3\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 8.3\bin\mysql.exe"
    if exist "C:\Program Files (x86)\MySQL\MySQL Server 8.2\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 8.2\bin\mysql.exe"
    if exist "C:\Program Files (x86)\MySQL\MySQL Server 8.1\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 8.1\bin\mysql.exe"
    if exist "C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe"
    if exist "C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 5.7\bin\mysql.exe"
    if exist "C:\mysql\bin\mysql.exe" set "MYSQL_EXE=C:\mysql\bin\mysql.exe"

    if not defined MYSQL_EXE (
        echo  X MySQL nao encontrado!
        echo    O AquaLog precisa do MySQL para funcionar.
        echo    1. Baixe e instale: https://dev.mysql.com/downloads/mysql/
        echo    2. Durante a instalacao, anote a senha do usuario 'root'.
        echo    3. Adicione o MySQL ao PATH do Windows ou instale na pasta padrao.
        echo    4. Depois rode este script novamente.
        echo.
        pause
        exit /b 1
    )
    echo  OK  MySQL encontrado em: %MYSQL_EXE%
) else (
    echo  OK  MySQL encontrado no PATH.
    set "MYSQL_EXE=mysql"
)
echo.

:: --------------------------------------------------
:: 5) Configurar .env e banco de dados
:: --------------------------------------------------
echo [5/5] Configurando arquivo .env e banco de dados...

:: Perguntar nome do banco de dados
set "BANCO_PADRAO=aqualog"
echo  Nome do banco de dados (padrao: %BANCO_PADRAO%):
set /p BANCO_NOME=  Digite o nome ou pressione Enter para usar '%BANCO_PADRAO%':
if "%BANCO_NOME%"=="" set "BANCO_NOME=%BANCO_PADRAO%"
echo  Usando banco: %BANCO_NOME%
echo.

:: --- Criar .env com valores padrao ---
if not exist "%ENV_FILE%" (
    echo # MySQL > "%ENV_FILE%"
    echo DB_HOST=localhost >> "%ENV_FILE%"
    echo DB_PORT=3306 >> "%ENV_FILE%"
    echo DB_USER=root >> "%ENV_FILE%"
    echo DB_PASSWORD= >> "%ENV_FILE%"
    echo DB_NAME=%BANCO_NOME% >> "%ENV_FILE%"
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
) else (
    :: Atualiza apenas o DB_NAME se ja existir
    for /f "usebackq tokens=1* delims==" %%a in ("%ENV_FILE%") do (
        if "%%a"=="DB_NAME" (
            echo DB_NAME=%BANCO_NOME% >> "%ENV_FILE%.tmp"
        ) else (
            echo %%a=%%b >> "%ENV_FILE%.tmp"
        )
    )
    move /y "%ENV_FILE%.tmp" "%ENV_FILE%" >nul
    echo  OK  backend\.env ja existe (atualizado DB_NAME=%BANCO_NOME%).
)
echo.

:: --- Verificar se o banco ja tem tabelas criadas ---
echo  Verificando se o banco '%BANCO_NOME%' ja esta configurado...
"%MYSQL_EXE%" -u root -e "USE %BANCO_NOME%; SHOW TABLES LIKE 'pedidos';" >nul 2>nul
if not errorlevel 1 (
    echo  OK  Banco '%BANCO_NOME%' ja existe com tabelas criadas. Pulando aplicacao do schema.
    goto FINAL
) else (
    echo    Banco vazio ou nao existe. Criando banco e aplicando schema.sql...

    :: Tentativa 1: root sem senha - criar banco
    "%MYSQL_EXE%" -u root -e "CREATE DATABASE IF NOT EXISTS `%BANCO_NOME%` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" >nul 2>nul
    if not errorlevel 1 (
        echo  OK  Banco '%BANCO_NOME%' criado (root sem senha).
    ) else (
        echo    Nao conseguiu (sem senha).
        echo.
        set /p MYSQL_PASS=  Informe a senha do MySQL (root) para criar o banco:
        if "%MYSQL_PASS%"=="" (
            echo  !  Senha nao informada. Pulando criacao de tabelas.
            echo     Aplique manualmente depois:
            echo       "%MYSQL_EXE%" -u root -p
            echo       mysql> CREATE DATABASE %BANCO_NOME%;
            echo       mysql> USE %BANCO_NOME%;
            echo       mysql> source backend\schema.sql
            goto FINAL
        ) else (
            "%MYSQL_EXE%" -u root -p%MYSQL_PASS% -e "CREATE DATABASE IF NOT EXISTS `%BANCO_NOME%` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" >nul 2>nul
            if not errorlevel 1 (
                echo  OK  Banco '%BANCO_NOME%' criado com sucesso.
            ) else (
                echo  !  Falha ao criar banco. Verifique a senha e se o MySQL esta rodando.
                goto FINAL
            )
        )
    )

    :: Aplicar schema.sql se o banco foi criado
    echo  Aplicando schema.sql...

    :: Faz replace do nome do banco no schema.sql (aqualog -> nome escolhido)
    findstr /v /c:"^$" "%SCHEMA_SQL%" > "%TEMP%\aqualog_schema_temp.sql"

    setlocal EnableDelayedExpansion
    (for /f "usebackq delims=" %%a in ("%TEMP%\aqualog_schema_temp.sql") do (
        set "linha=%%a"
        set "linha=!linha:aqualog=%BANCO_NOME%!"
        echo !linha!
    )) > "%TEMP%\aqualog_schema_final.sql"
    endlocal

    :: Tentativa sem senha
    "%MYSQL_EXE%" -u root < "%TEMP%\aqualog_schema_final.sql" >nul 2>nul
    if not errorlevel 1 (
        echo  OK  Tabelas criadas com sucesso.
    ) else (
        if not "%MYSQL_PASS%"=="" (
            "%MYSQL_EXE%" -u root -p%MYSQL_PASS% < "%TEMP%\aqualog_schema_final.sql" >nul 2>nul
            if not errorlevel 1 (
                echo  OK  Tabelas criadas com sucesso.
            ) else (
                echo  !  Falha ao aplicar schema.sql.
            )
        ) else (
            echo  !  Falha ao aplicar schema.sql.
        )
    )

    del "%TEMP%\aqualog_schema_temp.sql" 2>nul
    del "%TEMP%\aqualog_schema_final.sql" 2>nul
)

:FINAL
echo.

:: --------------------------------------------------
:: Final
:: --------------------------------------------------
echo ========================================
echo   Instalacao concluida!
echo ========================================
echo.
echo   O que foi feito:
echo     - Ambiente virtual Python criado (backend\venv)
echo     - Dependencias instaladas
echo     - Arquivo backend\.env configurado (DB_NAME=%BANCO_NOME%)
echo     - Banco de dados e tabelas criados (se o MySQL estiver rodando)
echo.
echo   Para iniciar o servidor:
echo       .\scripts\iniciar_local.bat
echo.
echo   Telas apos iniciar:
echo     Admin:      http://127.0.0.1:8000
echo     Cliente:    http://127.0.0.1:8000/cliente.html
echo     Entregador: http://127.0.0.1:8000/entregador.html
echo.
echo   Login admin: senha 'admin123'
echo.

pause