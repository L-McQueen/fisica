@echo off
title Lanzador de Simulacion Webots - Pista Montana Rusa
cls
echo ===================================================================
echo     LABORATORIO DE FISICA: SIMULACION EN WEBOTS (PISTA DE FISICA)
echo ===================================================================
echo.

set "WEBOTS_HOME=C:\Program Files\Webots"
set "WORLD_PATH=%~dp0worlds\pista_montana_rusa.wbt"

if not exist "%WEBOTS_HOME%\msys64\mingw64\bin\webotsw.exe" (
    echo [ERROR] No se encontro Webots en %WEBOTS_HOME%
    echo Por favor verifica la instalacion de Webots.
    echo.
    pause
    exit /b 1
)

if not exist "%WORLD_PATH%" (
    echo [ERROR] No se encontro el archivo del mundo:
    echo %WORLD_PATH%
    echo.
    pause
    exit /b 1
)

echo [1/2] Configurando entorno de Webots y bibliotecas Qt/MinGW...
set "PATH=%WEBOTS_HOME%\msys64\mingw64\bin;%WEBOTS_HOME%\lib\controller;%PATH%"

echo [2/2] Abriendo Webots con la pista 'pista_montana_rusa.wbt'...
cd /d "%WEBOTS_HOME%"
start "" /d "%WEBOTS_HOME%" "%WEBOTS_HOME%\msys64\mingw64\bin\webotsw.exe" "%WORLD_PATH%"

echo.
echo ===================================================================
echo   [OK] Webots ha sido lanzado.
echo ===================================================================
echo.
echo Instrucciones:
echo 1. Espera a que Webots termine de cargar el mundo 3D en pantalla.
echo 2. Presiona el boton Play en la barra superior de Webots para iniciar.
echo 3. Observaras la maleta, el carrito y el HUD de fisica en tiempo real.
echo.
echo Si prefieres abrirlo manualmente desde Webots:
echo Menu: Archivo -> Abrir Mundo -> Selecciona 'worlds\pista_montana_rusa.wbt'
echo.
echo Presiona cualquier tecla para cerrar esta ventana auxiliar.
pause >nul
