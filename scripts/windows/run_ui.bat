@echo off
cd %~dp0\..\..
echo ===================================================
echo   Iniciando Quadros de Saude Dashboard
echo ===================================================

if not exist ".venv\Scripts\activate.bat" (
    echo [AVISO] Ambiente virtual nao encontrado. Execute setup_env.bat primeiro!
    pause
    exit /b
)

call .venv\Scripts\activate.bat
python iniciar_ui.py
pause
