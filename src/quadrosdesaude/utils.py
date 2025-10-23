import os
import glob
import shutil
from typing import Optional

def formatar_tamanho(num_bytes: int) -> str:
  """
	Converte um número de bytes para uma string formatada legível por humanos.

	Utiliza potências de 1024 para converter bytes em Kilobytes (KB), Megabytes (MB),
	Gigabytes (GB) ou Terabytes (TB), arredondando o resultado para duas casas decimais.
	Se o valor de entrada for None, retorna "0 Bytes".

	Args:
		num_bytes: O número de bytes a ser formatado. Pode ser None.

	Returns:
		Uma string representando o tamanho formatado (ex: "1.23 MB", "500.00 KB", "2.00 GB").
		Retorna "0 Bytes" se a entrada for None.
	"""
  if num_bytes is None:
    return "0 Bytes"

  power = 1024
  n = 0
  power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}

  while num_bytes >= power and n < len(power_labels):
    num_bytes /= power
    n += 1

  return f"{num_bytes:.2f} {power_labels[n]}B"

def medir_tamanho_pasta(caminho_pasta: str) -> Optional[str]:
  """
    Calcula e retorna o tamanho total de todos os ficheiros dentro de uma pasta e suas subpastas.

    Percorre recursivamente a árvore de diretórios a partir do `caminho_pasta`,
    soma o tamanho de todos os ficheiros encontrados e retorna o tamanho total
    formatado como uma string legível (usando `formatar_tamanho`).
    Imprime mensagens informativas durante o processo e em caso de erros de acesso.

    Args:
      caminho_pasta: O caminho para o diretório cujo tamanho deve ser medido.

    Returns:
      str: Uma string com o tamanho total formatado (ex: "1.50 GB").
      None: Se a pasta não existir ou ocorrer um erro fundamental na leitura.
	"""
  print(f"🔎 Calculando o tamanho da pasta: {caminho_pasta}...")
  tamanho_total_bytes = 0
  for dirpath, dirnames, filenames in os.walk(caminho_pasta):
    for f in filenames:
      caminho_arquivo = os.path.join(dirpath, f)
      try:
        tamanho_total_bytes += os.path.getsize(caminho_arquivo)
      except OSError:
        print(f"Não foi possível acessar o arquivo: {caminho_arquivo}")
        pass
  tamanho_formatado = formatar_tamanho(tamanho_total_bytes)
  print(f'Tamanho da pasta é {tamanho_formatado}')
  return tamanho_formatado


def limpador_(caminho_pasta: str) -> None:
  """
    Apaga **PERMANENTEMENTE** todo o conteúdo (arquivos e subpastas) de um diretório específico.

    ⚠️ ATENÇÃO: Esta é uma operação DESTRUTIVA e IRREVERSÍVEL. ⚠️

    Solicita confirmação explícita do usuário antes de proceder.
    Itera sobre todos os itens no primeiro nível do `caminho_pasta` e apaga-os.
    Ficheiros são removidos com `os.remove()` e diretórios (e todo o seu conteúdo)
    são removidos recursivamente com `shutil.rmtree()`.
    Imprime o progresso e quaisquer erros que ocorram durante a exclusão.

    Args:
      caminho_pasta: O caminho completo para o diretório que será esvaziado.

    Returns:
      None. A função realiza a operação de limpeza diretamente no sistema de ficheiros.
	"""
  confirmacao = input(f"Digite 'sim' para confirmar e continuar a exclusão de tudo que está na pasta {caminho_pasta}: ")
  if confirmacao.lower() == 'sim':
    if os.path.exists(caminho_pasta):
      print(f"\nIniciando a limpeza da pasta '{caminho_pasta}'...")
      itens_para_apagar = glob.glob(os.path.join(caminho_pasta, '*'))
      if not itens_para_apagar:
        print("A pasta já está vazia. Nenhuma ação necessária.")
      else:
        for item_path in itens_para_apagar:
          try:
            if os.path.isfile(item_path):
              os.remove(item_path)
              print(f"  - Arquivo apagado: {os.path.basename(item_path)}")
            elif os.path.isdir(item_path):
              shutil.rmtree(item_path)
              print(f"  - Pasta apagada: {os.path.basename(item_path)}")
          except Exception as e:
            print(f"  - ERRO ao apagar {item_path}: {e}")
        print("\n✅ Limpeza concluída com sucesso!")
    else:
      print(f"\nERRO: A pasta '{caminho_pasta}' não foi encontrada. Verifique o caminho.")
  else:
    print("\nOperação cancelada pelo usuário.")