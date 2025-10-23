import os
import shutil
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import Literal, Tuple, Union
from .conversor import dbc2dbf, dbf2parquet

def dbc2parquet(
  caminho_dbc: str, 
  destino_parquet: str, 
  pasta_temp_dbf: str = './temp_dbf',
  pasta_temp_parquet: str = './temp_parquet', 
  operacao: Literal['lote', 'unico'] = 'unico', 
  tamanho_lote: int = 100000
) -> Union[ Tuple[ str, bool, str ], bool ]:
  """
    Processa um único arquivo .dbc convertendo-o para o formato Parquet.

    Executa um pipeline completo de forma atomica para um unico arquivo:
    1. Descomprime o arquivo .dbc para um arquivo .dbf temporário.
    2. Converte o arquivo .dbf temporário para um arquivo .parquet temporário,
      processando em lotes e verificando a contagem de linhas no final.
    3. Se a conversão e verificação forem bem-sucedidas, move o arquivo 
      .parquet temporário para a pasta de destino final.
    4. Limpa todos os arquivos temporários (.dbf e .parquet) criados durante o processo.

    Args:
      caminho_dbc: O caminho completo para o arquivo .dbc de entrada.
      destino_parquet: O caminho para a pasta onde o arquivo .parquet final 
        (convertido com sucesso) deve ser guardado.
      pasta_temp_dbf: Diretório para armazenar o arquivo .dbf temporário 
        durante o processamento. O valor padrão é './temp_dbf'.
      pasta_temp_parquet: Diretório para armazenar o arquivo .parquet 
        temporário antes da verificação e movimentação final. 
        O valor padrão é './temp_parquet'.
      operacao: Define o formato do valor de retorno.
        'lote': Retorna uma tupla detalhada (nome_base, sucesso, mensagem).
        'unico': Retorna apenas um booleano (True para sucesso, False para falha).
      O valor padrão é 'unico'.
      tamanho_lote: Número de registos a processar de cada vez durante a 
        conversão DBF -> Parquet para otimizar o uso de memória. 
        O valor padrão é 100000.

    Returns:
      - Se operacao='lote': Uma tupla contendo:
        - nome_base (str): O nome do arquivo .dbc original.
        - sucesso (bool): True se todo o processo foi bem-sucedido, False caso contrário.
        - mensagem (str): Uma mensagem descrevendo o resultado ou o erro.
      - Se operacao='unico': 
        - True se todo o processo foi bem-sucedido.
        - False se ocorreu alguma falha em qualquer etapa.

    Raises:
      FileNotFoundError: Se o arquivo `caminho_dbc` não for encontrado (lançado por `dbc2dbf` ou `dbf2parquet`).
      Exception: Captura e relança outras exceções que podem ocorrer durante a 
        descompressão, conversão ou movimentação de arquivos (ex: erros de permissão,
        disco cheio, arquivo corrompido). A mensagem de erro original é incluída.
  """
  os.makedirs(pasta_temp_dbf, exist_ok=True)
  os.makedirs(pasta_temp_parquet, exist_ok=True)

  nome_base = os.path.basename(caminho_dbc)
  nome_sem_ext = Path(caminho_dbc).stem

  caminho_dbf_temp = os.path.join(pasta_temp_dbf, f"{nome_sem_ext}.dbf")
  caminho_parquet_temp = os.path.join(pasta_temp_parquet, f"{nome_sem_ext}.parquet")
  caminho_parquet_final = os.path.join(destino_parquet, f"{nome_sem_ext}.parquet")

  try:
    dbc2dbf(caminho_dbc, caminho_dbf_temp)

    if dbf2parquet(caminho_dbf_temp, caminho_parquet_temp, tamanho_lote=tamanho_lote):
      try:
        shutil.move(caminho_parquet_temp, caminho_parquet_final)
      except Exception as e:
        raise Exception(f'ERRO ao mover o arquivo {os.path.basename(caminho_parquet_temp)}: {e}') from e
      
      if operacao == 'lote':
        return (nome_base, True, f"Sucesso com o arquivo {caminho_parquet_final}.")
      elif operacao == 'unico':
        return True
      
    else:
      if operacao == 'lote':
        return (nome_base, False, f"Falha: Dados incompletos com o arquivo {caminho_dbf_temp}.")
      elif operacao == 'unico':
        return False

  except Exception as e:
    if operacao == 'lote':
      return (nome_base, False, f"Falha com o arquivo {caminho_dbf_temp}.")
    elif operacao == 'unico':
      return False
  finally:
    if os.path.exists(caminho_dbf_temp):
      os.remove(caminho_dbf_temp)
    if os.path.exists(caminho_parquet_temp):
      os.remove(caminho_parquet_temp)


def orquestrador(
  pasta_origem_dbc: str,
  pasta_destino_parquet: str,
  pasta_temp_dbf: str = './temp_dbf',
  pasta_temp_parquet: str = './temp_parquet',
  max_workers: int = 1,
  tamanho_lote: int = 100000
) -> None:
  """
    Orquestra o processamento completo de uma pasta de arquivos .DBC.

    Esta função gerencia o pipeline DBC -> DBF Temporário -> Parquet Final -> Mover ao destino,
    utilizando multithreading para processar cada ficheiro de forma 
    atomica e paralela. TODO: Incluir verificação de arquivos existentes

    Args:
        pasta_origem_dbc: Caminho para a pasta contendo os arquivos .dbc (origem).
        pasta_destino_parquet: Caminho para a pasta onde os ficheiros .parquet 
          convertidos com sucesso serão guardados.
        pasta_temp_dbf: Caminho para pasta temporária onde os arquivos .dbc 
          descomprimidos para .dbf com sucesso devem aguardar
        pasta_temp_parquet: Caminho para pasta temporária onde os arquivos .parquet 
          são escritos e verificados antes de seguirem pra pasta_detino_parquet.
        max_workers: O número máximo de threads a serem usadas para o processamento 
          paralelo. O valor padrão é 1.
        tamanho_lote: O número de registos a serem processados de cada vez durante 
          a conversão DBF -> Parquet. O valor padrão é 100000.
    Returns:
      None. A função executa o processo e move o resultado (arquivo .parquet) para pasta destino.

    Raises:
      FileNotFoundError: Se a pasta de origem não for encontrada.
  """

  for pasta in [pasta_temp_dbf, pasta_temp_parquet]:
    if os.path.exists(pasta):
      shutil.rmtree(pasta)
    os.makedirs(pasta, exist_ok=True)
  
  arquivos_dbc = list( Path( pasta_origem_dbc ).glob( '*.[dD][bB][cC]' ) )
  if not arquivos_dbc:
    print("Nenhum ficheiro .dbc encontrado na pasta de origem.")
    return

  sucessos, falhas = 0, 0
  start_time_total = time.perf_counter()

  with ThreadPoolExecutor(max_workers=max_workers) as executor:
    progress_bar = tqdm( total = len(arquivos_dbc), desc = "Processando Ficheiros" )
    operacao = 'lote'
    futuros = []
    for caminho_dbc in arquivos_dbc:
      futuro.append(
        executor.submit(dbc2parquet, str(caminho_dbc), pasta_destino_parquet, pasta_temp_dbf, pasta_temp_parquet, operacao, tamanho_lote)
      )
    try:
      for futuro in as_completed(futuros):
        nome_base, sucesso, mensagem = futuro.result()
        if sucesso:
          sucessos += 1
        else:
          print(f"'{nome_base}': {mensagem}")
          falhas += 1
        progress_bar.update(1)
      progress_bar.close()
    except KeyboardInterrupt:
      print(f"\n\n🛑 INTERRUPÇÃO DETECTADA PELO USUÁRIO.")
      print("Encerrando o executor e cancelando tarefas pendentes... Por favor, aguarde.")
      executor.shutdown(wait = False, cancel_futures = True)
      return

    except Exception as e:
      print(f"\n\nERRO CRÍTICO: Interrompendo processamento...")
      print(f"Detalhes: {e}")
      executor.shutdown(wait = False, cancel_futures = True)
      return

  duration_total = time.perf_counter() - start_time_total
  print(f"Processamento concluído em {duration_total:.2f} segundos.")
  print(f"Sucessos: {sucessos}")
  print(f"Falhas: {falhas}")
