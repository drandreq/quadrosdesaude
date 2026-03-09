# scripts/windows/publish_pypi.ps1

$CaminhoDoArquivoDeConfiguracaoLocal = ".pypirc.local"
$DiretorioDeDistribuicaoDosPacotes = "dist/"
$ListaDeArquivosParaUpload = Get-ChildItem -Path "$DiretorioDeDistribuicaoDosPacotes*"

# Verificação de existência do arquivo de config
if (-not (Test-Path $CaminhoDoArquivoDeConfiguracaoLocal)) {
    Write-Host ">>> Erro: Arquivo $CaminhoDoArquivoDeConfiguracaoLocal nao encontrado." -ForegroundColor Red
    exit
}

Write-Host ">>> Iniciando validacao de integridade dos pacotes..." -ForegroundColor Cyan
# Verifique se há erros no README.MD aqui
twine check $ListaDeArquivosParaUpload

if ($LASTEXITCODE -ne 0) {
    Write-Host ">>> Erro na validacao dos metadados. Verifique seu README.md." -ForegroundColor Red
    exit
}

# --- ETAPA 1: TEST PYPI (Ambiente de Staging) ---
Write-Host ">>> Enviando para TEST PYPI..." -ForegroundColor Yellow

# Adicionamos --skip-existing para ignorar os arquivos que ja subiram com sucesso
twine upload --config-file $CaminhoDoArquivoDeConfiguracaoLocal --repository testpypi --skip-existing $ListaDeArquivosParaUpload

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n>>> Sucesso no Test PyPI!" -ForegroundColor Green
    Write-Host "Verifique em: https://test.pypi.org/project/quadrosdesaude/" -ForegroundColor Gray
    
    # --- ETAPA 2: CONFIRMAÇÃO PARA PRODUÇÃO ---
    $DesejaProsseguirParaProducao = Read-Host "`nDeseja prosseguir com o upload para PRODUCAO (PyPI Oficial)? [S/N]"
    
    if ($DesejaProsseguirParaProducao -eq "S" -or $DesejaProsseguirParaProducao -eq "s") {
        Write-Host ">>> Iniciando upload para PRODUCAO..." -ForegroundColor Cyan
        
        # CORREÇÃO: Apontando para o repositório 'pypi' e mantendo a segurança do skip-existing
        twine upload --config-file $CaminhoDoArquivoDeConfiguracaoLocal --repository pypi --skip-existing $ListaDeArquivosParaUpload
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ">>> Publicacao em PRODUCAO concluida com sucesso!" -ForegroundColor Green
        }
    } else {
        Write-Host ">>> Upload para producao cancelado pelo usuario." -ForegroundColor Yellow
    }
} else {
    Write-Host ">>> Falha no upload para o Test PyPI. Tente rodar com a flag --verbose se o erro persistir." -ForegroundColor Red
}