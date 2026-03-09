import pytest
import os
from unittest.mock import patch, MagicMock
from quadrosdesaude.extracao.ftp import FTPDownloader

@pytest.fixture
def mock_ftp():
    with patch('quadrosdesaude.extracao.ftp.FTP') as mock_ftp_class:
        yield mock_ftp_class

def test_ftp_lista_arquivos_sucesso(mock_ftp):
    mock_instancia = MagicMock()
    mock_ftp.return_value.__enter__.return_value = mock_instancia
    mock_instancia.nlst.return_value = ['arquivo1.dbc', 'arquivo2.dbf', 'exemplo.dbc']
    
    downloader = FTPDownloader()
    arquivos = downloader.lista_arquivos('/caminho/teste', extensao='.dbc')
    
    assert len(arquivos) == 2
    assert 'arquivo1.dbc' in arquivos
    assert 'exemplo.dbc' in arquivos
    mock_instancia.cwd.assert_called_with('/caminho/teste')

def test_ftp_download_arquivo_sucesso(mock_ftp, tmp_path):
    mock_instancia = MagicMock()
    mock_ftp.return_value.__enter__.return_value = mock_instancia
    mock_instancia.size.return_value = 100
    
    # Simular o callback do FTP para escrever dados no arquivo temporário
    def retrbinary_side_effect(cmd, callback):
        callback(b"dados de teste")
        
    mock_instancia.retrbinary.side_effect = retrbinary_side_effect
    
    pasta_destino = str(tmp_path / "destino")
    pasta_temp = str(tmp_path / "temp")
    
    downloader = FTPDownloader()
    resultado = downloader.download_arquivo('/caminho', 'teste.dbc', pasta_destino, pasta_temp=pasta_temp)
    
    assert "BAIXADO" in resultado
    arquivo_final = os.path.join(pasta_destino, 'teste.dbc')
    assert os.path.exists(arquivo_final)
    
    with open(arquivo_final, 'rb') as f:
        assert f.read() == b"dados de teste"
