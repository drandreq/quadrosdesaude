#!/bin/bash
cd "$(dirname "$0")/../.."

echo "==================================================="
echo "  Iniciando Quadros de Saude Dashboard"
echo "==================================================="

if [ ! -f ".venv/bin/activate" ]; then
    echo "[AVISO] Ambiente virtual não encontrado. Execute setup_env.sh primeiro!"
    exit 1
fi

source .venv/bin/activate
python iniciar_ui.py
