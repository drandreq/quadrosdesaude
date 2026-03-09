# src/quadrosdesaude/conversion/converter.py

import os
import time
import itertools
import gc
import polars as pl
import pyarrow.parquet as pq
from dbfread import DBF
from quadrosdesaude import descomprimir_dbc
from .parser import StringFieldParser
from quadrosdesaude.logger import logger

def harmonizar_registos_em_fluxo(iterator_dbf, schema_mestre):
  """
    Processa um iterador de registos DBF garantindo que cada registo tenha todas as colunas.

    Este é um gerador que recebe registros-dicionários de um arquivo DBF, que podem ter 
    colunas em falta devido a peculiaridades dos dados do DATASUS. Para cada registo, ele cria um 
    novo dicionário contendo todas as colunas definidas no `schema_mestre`, preenchendo as colunas 
    em falta com uma string vazia e mantendo os valores existentes.

    Args:
      iterator_dbf: Um iterador que produz dicionários, onde cada dicionário
        representa um registo do arquivo DBF.
      schema_mestre (list): Uma lista de strings contendo os nomes de todas as
        colunas que deveriam existir em cada registo (normalmente obtida de `DBF(...).field_names`).

    Yields:
      dict: Um dicionário representando um registo harmonizado, garantindo que
        todas as chaves presentes em `schema_mestre` existem no registro-dicionário.
	"""
  valor_vazio = ''
  for registo in iterator_dbf:
    registo_completo = {coluna: valor_vazio for coluna in schema_mestre}
    registo_completo.update(registo)
    yield registo_completo

def dbc2dbf(caminho_dbc: str, caminho_dbf: str) -> bool:
  """
    Descomprime um único arquivo .dbc do PKWare (DATASUS) para o formato padrão .dbf.

    Utiliza a função `descomprimir_dbc` para realizar a extração binária. Registra o tempo 
    de execução e retorna um booleano de sucesso.
    
    Atenção: A biblioteca de extração foi fornecida e otimizada por `@danicat` na extensão C original.

    Args:
      caminho_dbc: Caminho completo para o arquivo .dbc de entrada.
      caminho_dbf: Caminho completo onde o arquivo .dbf descomprimido será guardado.

    Returns:
      bool: True se a descompressão foi bem-sucedida, False caso contrário.

    Raises:
      FileNotFoundError: Se o `caminho_dbc` não for encontrado (lançado por `fopen` em C).
      Exception: Outras exceções relacionadas a erros de I/O ou falhas na descompressão (originadas na extensão C).
	"""
  start_time = time.perf_counter()
  try:
    descomprimir_dbc(caminho_dbc, caminho_dbf)
    duration = time.perf_counter() - start_time
    return True
  except Exception as e:
    duration = time.perf_counter() - start_time
    return False


def dbf2parquet(caminho_dbf: str, destino_parquet: str = None, tamanho_lote: int = 100000) -> bool:
  """
    Converte um arquivo .dbf para o formato Parquet de forma eficiente em memória.

    Lê o arquivo .dbf em lotes (chunks), harmoniza os registos para garantir
    um schema consistente e protegido contra colunas faltantes, converte cada lote 
    para um DataFrame Polars e escreve/anexa a um arquivo Parquet final usando PyArrow.
    Por segurança, valida se as linhas escritas correspondem ao cabeçalho original.

    Args:
      caminho_dbf: Caminho completo para o arquivo .dbf de entrada.
      destino_parquet: Caminho completo onde o arquivo .parquet final
        será guardado. Se None, o nome será derivado do
        arquivo de entrada e salvo no diretório atual.
        Valor padrão é None.
      tamanho_lote: Número de registos DBF a serem lidos e processados
        em memória de cada vez. Ajustar este valor pode
        impactar o uso de RAM e a velocidade. Valor padrão é 100000.

    Returns:
      bool: True se a conversão e a verificação de contagem de linhas
        foram bem-sucedidas, False caso contrário.

    Raises:
      FileNotFoundError: Se o `caminho_dbf` não for encontrado.
      dbfread.exceptions.DBFNotFound: Se o arquivo DBF não for válido ou estiver corrompido.
      Exception: Outras exceções relacionadas a erros de I/O, falhas na
        escrita do Parquet, ou problemas de memória.
	"""
  if not destino_parquet:
    nome_base = os.path.basename(caminho_dbf)
    destino_parquet = f'{nome_base}.parquet'

  start_time = time.perf_counter()
  writer = None
  total_linhas_processadas = 0

  try:
    tabela_dbf = DBF(caminho_dbf, parserclass = StringFieldParser)
    schema_mestre = tabela_dbf.field_names
    total_linhas_cabecalho = len(tabela_dbf)

    gerador_harmonizado = harmonizar_registos_em_fluxo( iter( tabela_dbf ), schema_mestre )

    for lote_de_registros in iter( lambda: list( itertools.islice( gerador_harmonizado, tamanho_lote ) ), [] ):
      df_lote = pl.DataFrame( lote_de_registros, schema_overrides={col: pl.Utf8 for col in schema_mestre} )
      tabela_arrow = df_lote.to_arrow()
      if writer is None:
        writer = pq.ParquetWriter(destino_parquet, tabela_arrow.schema)
      writer.write_table(tabela_arrow)
      total_linhas_processadas += len(df_lote)
      del lote_de_registros, df_lote, tabela_arrow
      gc.collect()

    if writer:
      writer.close()

    linhas_no_parquet = pq.ParquetFile(destino_parquet).metadata.num_rows
    duration = time.perf_counter() - start_time

    if total_linhas_cabecalho == linhas_no_parquet:
      return True
    else:
      logger.error(f'Falha no dbf2parquet do arquivo {caminho_dbf}')
      return False
  except Exception as e:
    logger.error(f'Falha crítica ao processar dbf2parquet do arquivo {caminho_dbf}')
    del lote_de_registros, df_lote, tabela_arrow
    gc.collect()
    if writer:
      writer.close()
    return False
