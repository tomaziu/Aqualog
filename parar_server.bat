@echo off
title Parar AquaLog

echo.
echo Parando somente processos do AquaLog...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0parar_server.ps1"

echo.
echo Pronto.
echo.