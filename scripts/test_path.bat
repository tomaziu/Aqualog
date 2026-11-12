@echo off
echo SCRIPT_DIR: %~dp0
set "BACKEND_DIR=%~dp0..\backend"
for %%I in ("%BACKEND_DIR%") do set "BACKEND_DIR=%%~fI"
echo BACKEND_DIR: %BACKEND_DIR%
