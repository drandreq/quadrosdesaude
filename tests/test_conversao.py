import pytest
from unittest.mock import patch, MagicMock
from quadrosdesaude.conversao.conversor import dbc2dbf, harmonizar_registos_em_fluxo
from quadrosdesaude.conversao.orquestrador import dbc2parquet
import os

def test_dbc2dbf_arquivo_inexistente():
    """Testa se a função retorna falso e lida com erro ao não encontrar o arquivo C."""
    resultado = dbc2dbf("caminho_inexistente.dbc", "saida_falsa.dbf")
    # Dependendo de como a extensão C lida, pode retornar falso
    assert resultado is False

@patch('quadrosdesaude.conversao.conversor.descomprimir_dbc')
def test_dbc2dbf_chamada_sucesso(mock_descomprimir):
    """Testa se a função wrapper chama a extensão C corretamente."""
    mock_descomprimir.return_value = None
    resultado = dbc2dbf("entrada.dbc", "saida.dbf")
    assert resultado is True
    mock_descomprimir.assert_called_once_with("entrada.dbc", "saida.dbf")

def test_harmonizar_registos():
    """Testa o gerador de harmonização de schemas."""
    schema = ['A', 'B', 'C']
    lote_incompleto = [
        {'A': '1', 'B': '2'},
        {'B': '3', 'C': '4'},
        {'A': '5', 'C': '6', 'D': 'Ignorado'}
    ]
    
    resultado = list(harmonizar_registos_em_fluxo(iter(lote_incompleto), schema))
    
    assert len(resultado) == 3
    assert resultado[0] == {'A': '1', 'B': '2', 'C': ''}
    assert resultado[1] == {'A': '', 'B': '3', 'C': '4'}
    assert resultado[2] == {'A': '5', 'B': '', 'C': '6', 'D': 'Ignorado'} # Ele atualiza, mas D fica pois estava no dict original

@patch('quadrosdesaude.conversao.orquestrador.dbc2dbf')
@patch('quadrosdesaude.conversao.orquestrador.dbf2parquet')
def test_dbc2parquet_fluxo(mock_dbf2parquet, mock_dbc2dbf, tmp_path):
    """Testa o orquestrador individual de arquivo."""
    mock_dbc2dbf.return_value = True
    mock_dbf2parquet.return_value = True
    
    pasta_destino = str(tmp_path / "destino")
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Mocar também o shutil.move para fingir que o temporário existia
    with patch('shutil.move') as mock_move:
        resultado = dbc2parquet("teste.dbc", pasta_destino, operacao='unico')
        assert resultado is True
        mock_dbc2dbf.assert_called_once()
        mock_dbf2parquet.assert_called_once()
