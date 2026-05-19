import os
import shutil
from ftplib import FTP, error_perm
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from quadrosdesaude.logger import logger

class FTPDownloader:
  """
    Facilita o download de arquivos de servidores FTP, com foco no DATASUS.

    Esta classe encapsula a lógica para listar arquivos, baixar arquivos individuais
    e baixar múltiplos arquivos de um diretório FTP de forma concorrente,
    incluindo barras de progresso e tratamento básico de erros.

    Attributes:
      ftp_host (str): O endereço do servidor FTP a ser utilizado.
        O padrão é "ftp.datasus.gov.br".
	"""
  def __init__(self, ftp_host="ftp.datasus.gov.br"):
    """
      Inicializa o FTPDownloader.

      Args:
        ftp_host (str, optional): O endereço do servidor FTP.
          Valor padrão é "ftp.datasus.gov.br".
		"""
    self.ftp_host = ftp_host
    self.evento_parada = threading.Event()

  def lista_arquivos(self, caminho_ftp: str, extensao: str = '.dbc', prefixo: str = None, usuario: str = None, senha: str = None):
    """
      Lista arquivos num diretório específico do servidor FTP.

      Conecta-se ao servidor FTP, mapeia o `caminho_ftp` especificado e
      retorna os arquivos de acordo com filtros opcionais de extensão e prefixo.

      Args:
        caminho_ftp: O caminho completo do diretório no servidor FTP a ser listado
          (ex: "/dissemin/publicos/SINAN/DADOS/FINAIS").
        extensao: A extensão dos arquivos a serem listados (case-insensitive).
          Se None, não filtra por extensão. Valor padrão é '.dbc'.
        prefixo: O prefixo dos nomes dos arquivos a serem listados (case-insensitive).
          Se None, não filtra por prefixo. Valor padrão é None.
        usuario: Nome de usuário para autenticação no FTP. Se None, usa login anônimo.
          Valor padrão é None.
        senha: Senha para autenticação no FTP. Usado apenas se `usuario` for fornecido.
          Valor padrão é None.

      Returns:
        Uma lista de strings contendo os nomes dos arquivos que correspondem
        aos filtros no diretório especificado. Retorna uma lista vazia se
        nenhum arquivo for encontrado ou em caso de erro de conexão/permissão.

      Raises:
        (Imprime erros no console, mas retorna lista vazia em caso de falha)
        ftplib.error_perm: Se houver problemas de permissão ou o caminho não existir.
        Exception: Para outros erros inesperados de conexão ou listagem.
		"""

    try:
      with FTP(self.ftp_host, timeout=180) as ftp:
        
        if usuario:
          ftp.login(user=usuario, passwd=senha)
        else:
          ftp.login()
        ftp.cwd(caminho_ftp)
        arquivos_e_pastas = ftp.nlst()

        if not prefixo and not extensao:
          return arquivos_e_pastas

        if extensao:
          files = [item for item in arquivos_e_pastas if item.upper().endswith(extensao.upper())]
        if prefixo:
          files = [item for item in files if item.upper().startswith(prefixo.upper())]
        
        if not files:
          logger.info("Nenhum arquivo encontrado que corresponda aos filtros.")
          return []
        
        return files
      
    except error_perm as e:
      logger.error(f"❌ Erro ao acessar o caminho: {e}. Verifique se o caminho está correto.")
      return []
    except Exception as e:
      logger.error(f"❌ Ocorreu um erro inesperado: {e}")
      return []

  def download_arquivo(self, caminho_ftp: str, nome_arquivo: str, pasta_destino: str, pasta_temp: str = './temp_download', usuario: str = None, senha: str = None, flag_pasta: bool = False):
    """
    Baixa um único arquivo do servidor remoto para um destino local usando buffer temporário.

    Gere o download através de uma pasta temporária para evitar corrupção, e move 
    ao destino final após sucesso (inclui barra de progresso TQDM). Ignora se o arquivo
    já existir salvo no disco.

      Args:
        caminho_ftp: O caminho do diretório no servidor FTP onde o arquivo reside.
        nome_arquivo: O nome exato do arquivo a ser baixado.
        pasta_destino: A pasta local onde o arquivo será salvo permanentemente.
        pasta_temp: A pasta local temporária usada durante o download.
          Valor padrão é './temp_download'.
        usuario: Nome de usuário para login no FTP. Valor padrão é None (anônimo).
        senha: Senha para login no FTP. Valor padrão é None.
        flag_pasta: Se True, omite a barra de progresso TQDM (útil para
          downloads em lote onde o TQDM principal controla o progresso).
          Valor padrão é False.

      Returns:
        str: Uma mensagem indicando o status ("BAIXADO: nome_arquivo" ou
          "Arquivo já baixado: nome_arquivo").
        None: Retorna None se ocorrer um erro durante o download.

      Raises:
        (Imprime erros no console, mas retorna None em caso de falha)
        Exception: Erro ao mover o arquivo da pasta temporária para a final.
        ftplib.error_perm: Erro de permissão no FTP ou arquivo não encontrado.
        Exception: Outros erros inesperados de conexão ou download.
    """
    os.makedirs(pasta_destino, exist_ok=True)
    os.makedirs(pasta_temp, exist_ok=True)

    caminho_destino = os.path.join(pasta_destino, nome_arquivo)
    caminho_temp = os.path.join(pasta_temp, nome_arquivo)

    if os.path.exists(caminho_destino):
      return f"Arquivo já baixado: {nome_arquivo}"

    try:
      with FTP(self.ftp_host, timeout=180) as ftp:
        if usuario:
          ftp.login(user=usuario, passwd=senha)
        else:
          ftp.login()
        ftp.cwd(caminho_ftp)

        if not flag_pasta:
          total_size = ftp.size(nome_arquivo)
          with open(caminho_temp, 'wb') as f_local, tqdm(
            total = total_size,
            unit = 'B', unit_scale = True, unit_divisor = 1024, desc = nome_arquivo
          ) as pbar:
            def callback(data):
              if self.evento_parada.is_set():
                  raise Exception("Download cancelado pelo usuário.")
              f_local.write(data)
              pbar.update(len(data))
            ftp.retrbinary(f"RETR {nome_arquivo}", callback)
        
        else:
          with open(caminho_temp, 'wb') as f_local:
            def callback(data):
              if self.evento_parada.is_set():
                  raise Exception("Download cancelado pelo usuário.")
              f_local.write(data)
            ftp.retrbinary(f"RETR {nome_arquivo}", callback)
      try:
        shutil.move(caminho_temp, caminho_destino)
      except Exception as e:
        raise Exception(f'ERRO ao mover o arquivo {os.path.basename(caminho_temp)}: {e}') from e
      return f"BAIXADO: {nome_arquivo}"

    except error_perm as e:
      logger.error(f"❌ Erro de permissão ou arquivo não encontrado: {e}")
    except Exception as e:
      logger.error(f"❌ Ocorreu um erro inesperado durante o download: {e}")
      if os.path.exists(caminho_temp):
        os.remove(caminho_temp)
    finally:
      if os.path.exists(caminho_temp):
        os.remove(caminho_temp)


  def download_pasta(self, caminho_ftp: str, pasta_destino: str, pasta_temp: str = './temp_download', extensao: str = '.dbc', prefix: str = None, max_workers: int = 1):
    """
    Baixa múltiplos arquivos de um diretório remoto em lotes de forma concorrente.

    Lista todos os conteúdos viáveis e faz o mapeamento `ThreadPoolExecutor` para o 
    download em paralelo com a exibição do progresso TQDM.

      Args:
        caminho_ftp: O caminho do diretório no servidor FTP a partir do qual baixar.
        pasta_destino: A pasta local onde os arquivos serão salvos permanentemente.
        pasta_temp: A pasta local temporária usada durante os downloads.
          Valor padrão é './temp_download'.
        extensao: Filtro de extensão para os arquivos a baixar (case-insensitive).
          Valor padrão é '.dbc'.
        prefixo: Filtro de prefixo para os nomes dos arquivos (case-insensitive).
          Valor padrão é None.
        max_workers: O número máximo de downloads simultâneos (threads).
          Valor padrão é 1.
        usuario: Nome de usuário para login no FTP. Valor padrão é None (anônimo).
        senha: Senha para login no FTP. Valor padrão é None.

      Returns:
        None. A função executa o processo de download e imprime o progresso
        e eventuais erros no console.
		"""
    logger.info("--- Iniciando o processo de download em lote ---")

    arquivos_para_download = self.lista_arquivos(caminho_ftp, extensao, prefix)

    if not arquivos_para_download:
      logger.warning("Nenhum arquivo encontrado. Verifique o caminho ou as permissões.")
      return

    total_arquivos = len(arquivos_para_download)
    logger.info(f"Encontrados {total_arquivos} arquivos. Começando downloads com {max_workers} conexões simultâneas.")
    self.evento_parada.clear()

    try:
      with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = []
        for nome_arquivo in arquivos_para_download:
          futuros.append(
            executor.submit(self.download_arquivo, caminho_ftp, nome_arquivo, pasta_destino, pasta_temp, usuario, senha, True)
          )

        with tqdm(total = total_arquivos, desc = "Progresso Geral", position = 0) as pbar:
            for future in as_completed(futuros):
              # Check event
              if self.evento_parada.is_set():
                 logger.warning("Cancelamento solicitado. Interrompendo fila de downloads.")
                 executor.shutdown(wait=False, cancel_futures=True)
                 break
              try:
                result = future.result()
                pbar.update(1)
              except Exception as e:
                logger.error(f"Erro no download individual: {e}")

    except KeyboardInterrupt:
        logger.warning(f"\n\n🛑 INTERRUPÇÃO DETECTADA PELO TÉRMINO NA CLI.")
        self.evento_parada.set()
    except BaseException as e: # Catch all exceptions like Streamlit StopException
        logger.error(f"Forçando o desligamento das threads devido a interrupção da plataforma.")
        self.evento_parada.set()
        raise e
    finally:
       self.evento_parada.set()
    
    logger.info("\n--- Processo de download concluído ou finalizado! ---")
