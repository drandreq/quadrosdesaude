import ftplib
import time
import threading
import duckdb
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from typing import Optional
from quadrosdesaude.logger import logger

class InventarioFTP:
    """
    Constrói um catálogo local em DuckDB mapeando a árvore de diretórios do FTP.
    Baseado no projeto EntropyZero V8. Processa strings ASCII/Latin-1 nativamente, 
    formatando os resultados para dicionários padronizados e lidando silenciosamente 
    com negativas de acesso no FTP.
    """

    def __init__(self, db_path: str = "inventario_datasus.db", max_workers: int = 8):
        self.db_path = db_path
        self.servidor_ftp = "ftp.datasus.gov.br"
        self.max_workers = max_workers
        self.evento_parada = threading.Event()
        self.trava_db = threading.Lock()
        self.fila_diretorios = Queue()

    def inicializar_banco(self):
        """Cria o banco de dados e a tabela de inventário caso não existam."""
        conexao = duckdb.connect(self.db_path)
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                caminho_completo TEXT PRIMARY KEY,
                nome TEXT,
                tipo TEXT,
                tamanho_bytes BIGINT,
                caminho_pai TEXT,
                segundos_mapeamento FLOAT,
                capturado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conexao.execute("PRAGMA force_checkpoint")
        conexao.close()
        logger.info(f"Banco de Dados inicializado: {self.db_path}")

    def _extrair_dados_msdos(self, linha_bruta: str, caminho_pai: str) -> Optional[dict]:
        """Faz o parsing da linha retornada pelo comando LIST/DIR do servidor FTP."""
        try:
            partes = linha_bruta.split()
            if len(partes) < 4:
                return None

            indicador_tipo = partes[2]
            eh_diretorio = indicador_tipo == "<DIR>"
            nome_do_item = " ".join(partes[3:])
            tamanho = int(indicador_tipo) if not eh_diretorio else 0

            nome_do_item = nome_do_item.encode("latin-1", errors="replace").decode("latin-1")
            caminho_limpo = caminho_pai if caminho_pai.endswith("/") else f"{caminho_pai}/"

            return {
                "caminho_completo": f"{caminho_limpo}{nome_do_item}",
                "nome": nome_do_item,
                "tipo": "diretorio" if eh_diretorio else "arquivo",
                "tamanho_bytes": tamanho,
                "caminho_pai": caminho_pai
            }
        except Exception as e:
            logger.debug(f"Aviso no parsing da linha: {linha_bruta} | {e}")
            return None

    def _worker_mapeamento(self):
        """Thread worker que se conecta ao FTP e consome a fila de diretórios."""
        conexao_db = None
        conexao_ftp = None

        try:
            conexao_db = duckdb.connect(self.db_path)
            conexao_ftp = ftplib.FTP(self.servidor_ftp)
            conexao_ftp.login()
            conexao_ftp.encoding = "latin-1"
            conexao_ftp.voidcmd("TYPE I")
        except Exception as e:
            logger.error(f"Falha de conexão na thread: {e}")
            return

        while not self.evento_parada.is_set():
            try:
                caminho_alvo = self.fila_diretorios.get(timeout=2)
            except Empty:
                break

            logger.info(f"Lendo diretório: {caminho_alvo}")
            tempo_inicio = time.time()
            sucesso = False

            while not sucesso:
                if self.evento_parada.is_set(): break

                try:
                    conexao_ftp.cwd(caminho_alvo)
                    listagem_bruta = []
                    conexao_ftp.dir(listagem_bruta.append)
                    tempo_total = time.time() - tempo_inicio

                    for linha in listagem_bruta:
                        fatos = self._extrair_dados_msdos(linha, caminho_alvo)
                        if fatos:
                            with self.trava_db:
                                conexao_db.execute("""
                                    INSERT OR IGNORE INTO inventory
                                    (caminho_completo, nome, tipo, tamanho_bytes, caminho_pai, segundos_mapeamento)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, [
                                    fatos["caminho_completo"], fatos["nome"], fatos["tipo"],
                                    fatos["tamanho_bytes"], fatos["caminho_pai"], tempo_total
                                ])

                            if fatos["tipo"] == "diretorio":
                                self.fila_diretorios.put(fatos["caminho_completo"])
                    
                    sucesso = True

                except Exception as e:
                    if "550" in str(e):
                        logger.warning(f"Acesso Negado ou caminho vazio: {caminho_alvo}")
                        sucesso = True
                    else:
                        logger.error(f"Erro em {caminho_alvo}: {e}. Reconectando...")
                        try:
                            conexao_ftp.quit()
                            time.sleep(1)
                            conexao_ftp = ftplib.FTP(self.servidor_ftp)
                            conexao_ftp.login()
                            conexao_ftp.encoding = "latin-1"
                            conexao_ftp.voidcmd("TYPE I")
                        except: pass

            self.fila_diretorios.task_done()

            # Checkpoint
            if self.fila_diretorios.qsize() % 50 == 0:
                with self.trava_db:
                    conexao_db.execute("PRAGMA force_checkpoint")

        if conexao_db:
            conexao_db.execute("PRAGMA force_checkpoint")
            conexao_db.close()
        if conexao_ftp:
            try: conexao_ftp.quit()
            except: pass

    def atualizar_inventario(self, diretorio_raiz: str = "/dissemin/publicos"):
        """
        Gera/Atualiza o inventário percorrendo recursivamente a partir da raiz dada via conexões FTP em lote.
        """
        logger.info(f"Iniciando Mapeamento a partir de: {diretorio_raiz}")
        self.inicializar_banco()
        self.fila_diretorios.put(diretorio_raiz)
        self.evento_parada.clear()

        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for _ in range(self.max_workers):
                    executor.submit(self._worker_mapeamento)

                # Mantem a thread principal viva para poder capturar KeyboardInterrupt
                while not self.fila_diretorios.empty():
                    time.sleep(2)
                    if self.evento_parada.is_set(): break
                    
        except KeyboardInterrupt:
            logger.warning("\nInterrupção detectada. Finalizando mapeamento de forma segura...")
            self.evento_parada.set()
        finally:
            self.evento_parada.set()
            time.sleep(2) # Aguarda as threads se despedirem

        # Sumário do inventário gerado
        try:
            con_resumo = duckdb.connect(self.db_path)
            resumo = con_resumo.execute("""
                SELECT COUNT(*), COALESCE(SUM(tamanho_bytes), 0) / 1024 / 1024 / 1024
                FROM inventory
            """).fetchone()
            logger.info(f"RESUMO DO INVENTÁRIO: {resumo[0]} registros mapeados.")
            logger.info(f"VOLUME MAPEADO: {resumo[1]:.4f} GB")
            con_resumo.close()
        except Exception as e:
            logger.error(f"Erro ao consolidar resumo do banco: {e}")

    def listar_todos_arquivos(self, pasta_raiz: str):
        """Retorna todos os ARQUIVOS a partir de uma pasta raiz, ordenados por caminho_pai e nome."""
        try:
            con = duckdb.connect(self.db_path)
            # Busca recursiva usando LIKE para pegar tudo que está "abaixo" da pasta raiz
            padrao = f"{pasta_raiz}%"
            resultado = con.execute("""
                SELECT caminho_completo, nome, tamanho_bytes, caminho_pai 
                FROM inventory
                WHERE tipo = 'arquivo' AND caminho_completo LIKE ?
                ORDER BY caminho_pai ASC, nome ASC
            """, [padrao]).fetchall()
            con.close()
            
            return [
                {
                    "caminho_completo": row[0],
                    "nome": row[1],
                    "tamanho_bytes": row[2],
                    "caminho_pai": row[3]
                }
                for row in resultado
            ]
        except Exception as e:
            logger.error(f"Erro ao consultar arquivos em {pasta_raiz}: {e}")
            return []
