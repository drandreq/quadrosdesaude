Set-Location -Path $PSScriptRoot\..\..
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Setup do Ambiente Quadros de Saude" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Python nao encontrado! Instale a partir de python.org" -ForegroundColor Red
    Pause
    exit
}

Write-Host "`n[2/3] Criando ambiente virtual (.venv)..." -ForegroundColor Yellow
python -m venv .venv

Write-Host "`n[3/3] Instalando dependencias do projeto via pip..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .

Write-Host "`n===================================================" -ForegroundColor Green
Write-Host "  Setup Concluido! Pode usar run_ui.ps1 agora." -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Pause
