@echo off
title Lanzador de Simulacion Webots - Pista Montana Rusa
cls
echo ===================================================================
echo     LABORATORIO DE FISICA: SIMULACION EN WEBOTS (PISTA DE FISICA)
echo ===================================================================
echo.

set "WEBOTS_HOME=C:\Program Files\Webots"

for %%I in ("%~dp0worlds\pista_montana_rusa.wbt") do set "SHORT_WORLD=%%~fsI"
for %%I in ("%~dp0worlds\pista_montana_rusa.wbt") do set "FULL_WORLD=%%~fI"

if not exist "%WEBOTS_HOME%\msys64\mingw64\bin\webotsw.exe" (
    echo [ERROR] No se encontro Webots en %WEBOTS_HOME%
    echo Por favor verifica la instalacion de Webots.
    echo.
    pause
    exit /b 1
)

if not exist "%SHORT_WORLD%" (
    echo [ERROR] No se encontro el archivo del mundo:
    echo %FULL_WORLD%
    echo.
    pause
    exit /b 1
)

echo [1/2] Configurando entorno de Webots...
set "PATH=%WEBOTS_HOME%\msys64\mingw64\bin;%WEBOTS_HOME%\lib\controller;%PATH%"

echo [2/2] Abriendo pista en Webots (Ruta sin espacios: %SHORT_WORLD%)...
cd /d "%WEBOTS_HOME%"
start "" /d "%WEBOTS_HOME%" "%WEBOTS_HOME%\msys64\mingw64\bin\webotsw.exe" "%SHORT_WORLD%"

echo.
echo ===================================================================
echo   [OK] Webots ha sido lanzado con la pista de laboratorio.
echo ===================================================================
echo.
echo Instrucciones:
echo 1. Observa como Webots abre directamente 'pista_montana_rusa.wbt'.
echo 2. Presiona el boton Play en la barra superior para iniciar el recorrido.
echo 3. Observaras la telemetria y HUD de fisica en vivo.
echo.
echo Presiona cualquier tecla para cerrar esta ventana auxiliar.
pause >nul
