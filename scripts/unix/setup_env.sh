#!/bin/bash
cd "$(dirname "$0")/../.."

echo "==================================================="
echo "  Iniciando Setup do Ambiente Quadros de Saude"
echo "==================================================="

echo "[1/3] Verificando Python..."
if ! command -v python3 &> /dev/null
then
    echo "[ERRO] Python3 não encontrado! Por favor instale dependências base."
    exit 1
fi

echo ""
echo "[2/3] Criando ambiente virtual (.venv)..."
python3 -m venv .venv

echo ""
echo "[3/3] Instalando dependencias do projeto via pip..."
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .

echo ""
echo "==================================================="
echo "  Setup Concluido! Pode usar run_ui.sh agora."
echo "==================================================="
