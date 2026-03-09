
"""
Quadros de Saúde: Ferramentas para processamento de dados de saúde pública do Brasil.
"""

__version__ = "0.2.5"

try:
  from . import datasus
  from .datasus import decompress as descomprimir_dbc
  _c_extension_available = True
except ImportError as e:
  print(f"ERRO: Não foi possível importar a extensão C 'datasus': {e}")
  descomprimir_dbc = None
  _c_extension_available = False

from .conversao.orquestrador import orquestrador, dbc2parquet
from .conversao.conversor import dbc2dbf, dbf2parquet
from .extracao.ftp import FTPDownloader
from .extracao.inventario import InventarioFTP
from .logger import logger
from .utils import medir_tamanho_pasta, limpador_
import os

_ftp_downloader = FTPDownloader()

def lista_arquivos(ftp_path: str, extension: str = '.dbc', prefix: str = None):
  """
    Lista os arquivos em um diretório do servidor FTP do Datasus.

    Args:
      ftp_path (str): O caminho do diretório no servidor FTP.
      extension (str, optional): A extensão dos arquivos a serem listados. Defaults to '.dbc'.
      prefix (str, optional): O prefixo dos arquivos a serem listados. Defaults to None.

    Returns:
      list: Uma lista de nomes de arquivos.
  """
  return _ftp_downloader.lista_arquivos(ftp_path, extension, prefix)

def ftp_download_arquivo(ftp_path: str, filename: str, destination_folder: str):
  """
    Baixa um único arquivo do servidor FTP do Datasus.

    Args:
      ftp_path (str): O caminho do diretório no servidor FTP.
      filename (str): O nome do arquivo a ser baixado.
      destination_folder (str): A pasta de destino para salvar o arquivo.
  """
  return _ftp_downloader.download_arquivo(ftp_path, filename, destination_folder)

def ftp_download_pasta(ftp_path: str, destination_folder: str, extension: str = '.dbc', prefix: str = None, max_workers: int = 1):
  """
    Baixa todos os arquivos de um diretório FTP de forma concorrente.

    Args:
      ftp_path (str): O caminho do diretório no servidor FTP.
      destination_folder (str): A pasta de destino para salvar os arquivos.
      extension (str, optional): A extensão dos arquivos a serem baixados. Default '.dbc'.
      prefix (str, optional): O prefixo dos arquivos a serem baixados. Default None.
      max_workers (int, optional): O número máximo de downloads simultâneos. Default 1.
  """
  return _ftp_downloader.download_pasta(ftp_path, destination_folder, extension, prefix, max_workers)


__all__ = [
  'orquestrador',
  'dbc2dbf',
  'dbf2parquet',
  'dbc2parquet',
  'lista_arquivos',
  'ftp_download_arquivo',
  'ftp_download_pasta',
  'medir_tamanho_pasta',
  'limpador_',
  'InventarioFTP',
  'logger'
]

if _c_extension_available:
  __all__.append('descomprimir_dbc')