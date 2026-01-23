@echo off
REM Jarvis AI Task Scheduler Setup Script
REM Configura Jarvis para ejecutarse automaticamente al iniciar Windows

echo Setting up Jarvis AI auto-start...

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges.
) else (
    echo Warning: Administrator privileges recommended for Task Scheduler setup.
    echo Please run as administrator for proper setup.
)

REM Obtener paths
set SCRIPT_DIR=%~dp0
set BAT_FILE=%SCRIPT_DIR%start_jarvis_daemon.bat
set TASK_NAME="Jarvis AI Auto-Start"

REM Verificar que existe el script batch
if not exist "%BAT_FILE%" (
    echo Error: start_jarvis_daemon.bat not found!
    pause
    exit /b 1
)

echo Creating scheduled task...

REM Crear la tarea programada
schtasks /create /tn %TASK_NAME% /tr "\"%BAT_FILE%\"" /sc onlogon /rl highest /f

if %errorLevel% == 0 (
    echo SUCCESS: Jarvis AI auto-start configured!
    echo The task will run when you log in to Windows.
    echo.
    echo To disable: schtasks /delete /tn %TASK_NAME% /f
) else (
    echo ERROR: Failed to create scheduled task.
    echo You can manually create it in Task Scheduler:
    echo   - Program: %BAT_FILE%
    echo   - Trigger: At log on
    echo   - Run with highest privileges
)

echo.
echo Press any key to continue...
pause >nul

exit