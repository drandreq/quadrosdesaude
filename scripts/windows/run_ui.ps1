Set-Location -Path $PSScriptRoot\..\..
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Quadros de Saude Dashboard" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[AVISO] Ambiente virtual nao encontrado. Execute setup_env.ps1 primeiro!" -ForegroundColor Red
    Pause
    exit
}

. .\.venv\Scripts\Activate.ps1
python iniciar_ui.py
Pause
