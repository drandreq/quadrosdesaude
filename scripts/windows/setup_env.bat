@echo off
cd %~dp0\..\..
echo ===================================================
echo   Iniciando Setup do Ambiente Quadros de Saude
echo ===================================================

echo [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale a partir de python.org
    pause
    exit /b
)

echo.
echo [2/3] Criando ambiente virtual (.venv)...
python -m venv .venv

echo.
echo [3/3] Instalando todas as dependencias do projeto via pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .

echo.
echo ===================================================
echo   Setup Concluido! Pode usar run_ui.bat agora.
echo ===================================================
pause
