@echo off
REM Jarvis AI Auto-Start Script
REM Ejecuta Jarvis en modo daemon al inicio de Windows

echo Starting Jarvis AI in daemon mode...

REM Obtener el directorio del script
set SCRIPT_DIR=%~dp0
set JARVIS_DIR=%SCRIPT_DIR%jarvis

REM Verificar que existe el directorio
if not exist "%JARVIS_DIR%" (
    echo Error: Jarvis directory not found at %JARVIS_DIR%
    pause
    exit /b 1
)

REM Cambiar al directorio de Jarvis
cd /d "%JARVIS_DIR%"

REM Ejecutar con pythonw.exe (sin consola) en modo daemon
start "" pythonw.exe main.py --daemon

echo Jarvis AI started in background.
echo Check logs at Desktop\JarvisData\logs\ for status.

REM Pequeña pausa para que el usuario vea el mensaje
timeout /t 2 /nobreak > nul

exit