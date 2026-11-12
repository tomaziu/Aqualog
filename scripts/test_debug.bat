@echo off
echo TESTANDO...
echo SCRIPT_DIR: %~dp0
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
echo PROJECT_ROOT: %PROJECT_ROOT%
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
echo BACKEND_DIR: %BACKEND_DIR%
pause
