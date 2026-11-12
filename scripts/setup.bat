@echo off
setlocal DisableDelayedExpansion
title AquaLog - Instalador Automatico
color 0B

echo ========================================
echo   AquaLog - Instalador Automatico
echo ========================================
echo.

cd /d "%~dp0.."
if errorlevel 1 goto ERRO_DIRETORIO

set "BACKEND_DIR=%CD%\backend"
set "VENV_DIR=%BACKEND_DIR%\venv"
set "ENV_FILE=%BACKEND_DIR%\.env"
set "SCHEMA_SQL=%BACKEND_DIR%\schema.sql"

set "MYSQL_TEMP_DIR="
set "MYSQL_CNF="
set "AQUALOG_SQL_TEMP="
set "COUNT_FILE="

if not exist "%BACKEND_DIR%" goto ERRO_BACKEND

REM ==================================================
REM 1 - VERIFICAR PYTHON
REM ==================================================

echo [1/5] Verificando Python...

where python >nul 2>&1
if not errorlevel 1 goto PYTHON_FOUND

where py >nul 2>&1
if errorlevel 1 goto ERRO_PYTHON

set "PYCMD=py"
goto PYTHON_VERSION

:PYTHON_FOUND
set "PYCMD=python"

:PYTHON_VERSION
%PYCMD% --version
if errorlevel 1 goto ERRO_PYTHON

echo OK: Python encontrado.
echo.

REM ==================================================
REM 2 - CRIAR AMBIENTE VIRTUAL
REM ==================================================

echo [2/5] Preparando ambiente virtual...

if exist "%VENV_DIR%\Scripts\python.exe" goto VENV_EXISTE

if exist "%VENV_DIR%" (
    echo Ambiente virtual incompleto.
    echo Pasta: %VENV_DIR%
    goto ERRO_GERAL
)

%PYCMD% -m venv "%VENV_DIR%"
if errorlevel 1 goto ERRO_VENV

:VENV_EXISTE

if not exist "%VENV_DIR%\Scripts\python.exe" goto ERRO_VENV

echo OK: Ambiente virtual disponivel.
echo.

REM ==================================================
REM 3 - INSTALAR DEPENDENCIAS
REM ==================================================

echo [3/5] Instalando dependencias Python...

if not exist "%BACKEND_DIR%\requirements.txt" goto ERRO_REQUIREMENTS

"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto ERRO_PIP

"%VENV_DIR%\Scripts\python.exe" -m pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 goto ERRO_DEPENDENCIAS

echo OK: Dependencias instaladas.
echo.

REM ==================================================
REM 4 - LOCALIZAR MYSQL
REM ==================================================

echo [4/5] Verificando MySQL...

set "MYSQL_EXE="

where mysql >nul 2>&1
if not errorlevel 1 set "MYSQL_EXE=mysql"

if defined MYSQL_EXE goto MYSQL_FOUND

if exist "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
if exist "C:\Program Files\MySQL\MySQL Server 8.3\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.3\bin\mysql.exe"
if exist "C:\Program Files\MySQL\MySQL Server 8.2\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.2\bin\mysql.exe"
if exist "C:\Program Files\MySQL\MySQL Server 8.1\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.1\bin\mysql.exe"
if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
if exist "C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 5.7\bin\mysql.exe"

if exist "C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 8.4\bin\mysql.exe"
if exist "C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe" set "MYSQL_EXE=C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysql.exe"

if exist "C:\mysql\bin\mysql.exe" set "MYSQL_EXE=C:\mysql\bin\mysql.exe"

:MYSQL_FOUND

if not defined MYSQL_EXE goto ERRO_MYSQL

echo OK: MySQL encontrado em:
echo %MYSQL_EXE%
echo.

REM ==================================================
REM 5 - CONFIGURAR BANCO E ARQUIVO ENV
REM ==================================================

echo [5/5] Configurando arquivo .env e banco de dados...
echo.

set "BANCO_PADRAO=aqualog"
set "BANCO_NOME="

set /p "BANCO_NOME=Digite o nome do banco (Enter para aqualog): "

if not defined BANCO_NOME set "BANCO_NOME=%BANCO_PADRAO%"

set "AQUALOG_DB_NAME=%BANCO_NOME%"

REM Validar nome do banco

powershell -NoProfile -ExecutionPolicy Bypass -Command "$db=$env:AQUALOG_DB_NAME; if ($db -notmatch '^[a-zA-Z0-9_]+$') { Write-Host 'Nome de banco invalido. Use somente letras, numeros e underline.'; exit 1 }"

if errorlevel 1 goto ERRO_NOME_BANCO

echo.
echo Banco selecionado: %BANCO_NOME%
echo.

REM ==================================================
REM SENHA DO MYSQL (UMA UNICA VEZ, USADA NO .env E NA CONEXAO)
REM ==================================================

set "AQUALOG_DB_PASSWORD="
set "AQUALOG_ENV_FILE=%ENV_FILE%"

echo ========================================
echo   AUTENTICACAO DO MYSQL
echo ========================================
echo.
echo Informe a senha do usuario root.
echo Se o root nao possuir senha, pressione Enter.
echo.

set /p "AQUALOG_DB_PASSWORD=Senha do MySQL root: "

REM ==================================================
REM CRIAR OU ATUALIZAR .env (valor sempre entre aspas)
REM ==================================================

echo.
echo Configurando arquivo .env...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=$env:AQUALOG_ENV_FILE; $db=$env:AQUALOG_DB_NAME.Trim(); $pw=[string]$env:AQUALOG_DB_PASSWORD; $q=[string][char]34; $bs=[string][char]92; $ev=$q+$pw.Replace($bs,$bs+$bs).Replace($q,$bs+$q)+$q; $u=New-Object System.Text.UTF8Encoding($false); if(-not (Test-Path -LiteralPath $p)){ $l=@('# MySQL','DB_HOST=localhost','DB_PORT=3306','DB_USER=root',('DB_PASSWORD='+$ev),('DB_NAME='+$db),'','# Auth','JWT_SECRET=aqualog_jwt_secret_change_in_production','ADMIN_PASSWORD=admin123','','# Pagamento','PIX_CHAVE=','MERCADO_PAGO_ACCESS_TOKEN=','','# Servidor','PORT=8000'); [IO.File]::WriteAllLines($p,$l,$u) } else { $o=New-Object System.Collections.Generic.List[string]; $tdb=$false; $tpw=$false; foreach($x in [IO.File]::ReadAllLines($p)){ if($x -match '^\s*DB_NAME\s*='){ $o.Add('DB_NAME='+$db); $tdb=$true } elseif($x -match '^\s*DB_PASSWORD\s*='){ $o.Add('DB_PASSWORD='+$ev); $tpw=$true } else { $o.Add($x) } }; if(-not $tdb){ $o.Add('DB_NAME='+$db) }; if(-not $tpw){ $o.Add('DB_PASSWORD='+$ev) }; [IO.File]::WriteAllLines($p,$o,$u) }; Write-Host 'Arquivo .env configurado.'"

if errorlevel 1 goto ERRO_ENV

echo OK: Arquivo .env configurado.
echo.

if not exist "%SCHEMA_SQL%" goto ERRO_SCHEMA

REM ==================================================
REM PREPARAR mysql.cnf TEMPORARIO (usa a mesma senha)
REM ==================================================

set "MYSQL_TEMP_DIR=%TEMP%\AquaLog_MySQL_%RANDOM%_%RANDOM%"
set "MYSQL_CNF=%MYSQL_TEMP_DIR%\mysql.cnf"

md "%MYSQL_TEMP_DIR%" >nul 2>&1
if errorlevel 1 goto ERRO_AUTH

icacls "%MYSQL_TEMP_DIR%" /inheritance:r /grant:r "%USERDOMAIN%\%USERNAME%:(OI)(CI)F" >nul 2>&1
if errorlevel 1 goto ERRO_AUTH

set "AQUALOG_MYSQL_CNF=%MYSQL_CNF%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$f=$env:AQUALOG_MYSQL_CNF; $pw=[string]$env:AQUALOG_DB_PASSWORD; $q=[char]34; $bs=[char]92; $nl=[Environment]::NewLine; $content='[client]'+$nl+'user=root'+$nl+'host=localhost'+$nl+'port=3306'+$nl+'protocol=tcp'+$nl; if($pw.Length -gt 0) { $escaped=$pw.Replace([string]$bs,[string]$bs+[string]$bs).Replace([string]$q,[string]$bs+[string]$q); $content+='password='+$q+$escaped+$q+$nl }; [IO.File]::WriteAllText($f,$content,[Text.Encoding]::ASCII); Write-Host 'Autenticacao preparada.'"

if errorlevel 1 goto ERRO_AUTH

echo OK: Autenticacao configurada.
echo.

REM ==================================================
REM TESTAR CONEXAO MYSQL
REM ==================================================

echo Testando conexao com MySQL...

"%MYSQL_EXE%" --defaults-extra-file="%MYSQL_CNF%" -e "SELECT 1;"

if errorlevel 1 goto ERRO_CONEXAO

echo.
echo OK: Conexao estabelecida.
echo.

REM ==================================================
REM VERIFICAR BANCO E TABELAS
REM ==================================================

echo Verificando banco %BANCO_NOME%...

set "TABLE_COUNT=0"
set "COUNT_FILE=%MYSQL_TEMP_DIR%\table_count.txt"

"%MYSQL_EXE%" --defaults-extra-file="%MYSQL_CNF%" -N -B -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='%BANCO_NOME%';" > "%COUNT_FILE%"

if errorlevel 1 goto ERRO_CONEXAO

for /f "usebackq delims=" %%A in ("%COUNT_FILE%") do set "TABLE_COUNT=%%A"

if not defined TABLE_COUNT goto ERRO_CONEXAO

echo Tabelas encontradas: %TABLE_COUNT%
echo.

if not "%TABLE_COUNT%"=="0" goto BANCO_EXISTENTE

REM ==================================================
REM CRIAR BANCO
REM ==================================================

echo Criando banco de dados %BANCO_NOME%...

"%MYSQL_EXE%" --defaults-extra-file="%MYSQL_CNF%" -e "CREATE DATABASE IF NOT EXISTS %BANCO_NOME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if errorlevel 1 goto ERRO_CRIAR_BANCO

echo OK: Banco criado.
echo.

REM ==================================================
REM PREPARAR SCHEMA SQL
REM ==================================================

echo Preparando schema.sql...

set "AQUALOG_SCHEMA=%SCHEMA_SQL%"
set "AQUALOG_SQL_TEMP=%MYSQL_TEMP_DIR%\schema_final.sql"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=$env:AQUALOG_SCHEMA; $o=$env:AQUALOG_SQL_TEMP; $db=$env:AQUALOG_DB_NAME; $sql=[IO.File]::ReadAllText($s); $sql=[regex]::Replace($sql,'(?i)\baqualog\b',$db); [IO.File]::WriteAllText($o,$sql,[Text.UTF8Encoding]::new($false)); Write-Host 'Schema preparado.'"

if errorlevel 1 goto ERRO_SCHEMA

REM ==================================================
REM APLICAR SCHEMA
REM ==================================================

echo.
echo Aplicando schema.sql no banco %BANCO_NOME%...

"%MYSQL_EXE%" --defaults-extra-file="%MYSQL_CNF%" %BANCO_NOME% < "%AQUALOG_SQL_TEMP%"

if errorlevel 1 goto ERRO_APLICAR_SCHEMA

echo.
echo OK: Schema aplicado com sucesso.
goto INSTALACAO_CONCLUIDA

REM ==================================================
REM BANCO EXISTENTE
REM ==================================================

:BANCO_EXISTENTE

echo O banco ja possui tabelas.
echo Para preservar os dados, a aplicacao do schema foi ignorada.
echo.

REM ==================================================
REM FINALIZACAO
REM ==================================================

:INSTALACAO_CONCLUIDA

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo O que foi feito:
echo   - Ambiente virtual Python verificado
echo   - Dependencias instaladas
echo   - MySQL localizado e conectado
echo   - Arquivo .env configurado
echo   - Banco de dados verificado
echo   - Schema aplicado quando necessario
echo.
echo Banco configurado: %BANCO_NOME%
echo.
echo Para iniciar o servidor:
echo   scripts\iniciar_local.bat
echo.
echo Telas:
echo   Admin:      http://127.0.0.1:8000
echo   Cliente:    http://127.0.0.1:8000/cliente.html
echo   Entregador: http://127.0.0.1:8000/entregador.html
echo.
echo Login admin: senha definida no arquivo .env
echo.

call :LIMPAR_TEMP
pause
exit /b 0

REM ==================================================
REM TRATAMENTO DE ERROS
REM ==================================================

:ERRO_DIRETORIO
echo ERRO: Nao foi possivel acessar a raiz do projeto.
goto ERRO_GERAL

:ERRO_BACKEND
echo ERRO: Pasta backend nao encontrada.
goto ERRO_GERAL

:ERRO_PYTHON
echo ERRO: Python nao encontrado ou nao funcional.
echo Instale em https://www.python.org/downloads/
goto ERRO_GERAL

:ERRO_VENV
echo ERRO: Falha ao criar ou localizar o ambiente virtual.
goto ERRO_GERAL

:ERRO_REQUIREMENTS
echo ERRO: requirements.txt nao encontrado.
goto ERRO_GERAL

:ERRO_PIP
echo ERRO: Falha ao atualizar pip.
goto ERRO_GERAL

:ERRO_DEPENDENCIAS
echo ERRO: Falha ao instalar dependencias Python.
goto ERRO_GERAL

:ERRO_MYSQL
echo ERRO: MySQL nao encontrado.
goto ERRO_GERAL

:ERRO_NOME_BANCO
echo ERRO: Nome do banco invalido.
goto ERRO_GERAL

:ERRO_ENV
echo ERRO: Falha ao criar ou atualizar o .env.
goto ERRO_GERAL

:ERRO_SCHEMA
echo ERRO: Arquivo schema.sql nao encontrado ou invalido.
goto ERRO_GERAL

:ERRO_AUTH
echo ERRO: Falha ao preparar a autenticacao do MySQL.
goto ERRO_GERAL

:ERRO_CONEXAO
echo ERRO: Nao foi possivel conectar ao MySQL.
echo Verifique a senha, o usuario e o servico MySQL.
goto ERRO_GERAL

:ERRO_CRIAR_BANCO
echo ERRO: Falha ao criar o banco de dados.
goto ERRO_GERAL

:ERRO_APLICAR_SCHEMA
echo ERRO: Falha ao aplicar schema.sql.
goto ERRO_GERAL

:ERRO_GERAL

echo.
echo ========================================
echo   INSTALACAO INTERROMPIDA
echo ========================================
echo.
echo Ocorreu um erro durante a instalacao.
echo Os arquivos temporarios serao removidos.
echo.

call :LIMPAR_TEMP

pause
exit /b 1

REM ==================================================
REM LIMPEZA DE ARQUIVOS TEMPORARIOS
REM ==================================================

:LIMPAR_TEMP

if defined MYSQL_TEMP_DIR (
    if exist "%MYSQL_TEMP_DIR%" (
        attrib -R -H -S "%MYSQL_TEMP_DIR%\*" /S /D >nul 2>&1
        rmdir /S /Q "%MYSQL_TEMP_DIR%" >nul 2>&1
    )
)

exit /b 0