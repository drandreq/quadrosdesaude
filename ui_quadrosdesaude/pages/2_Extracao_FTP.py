import streamlit as st
import os
import sys
import logging
from quadrosdesaude import InventarioFTP, FTPDownloader

try:
    from ui_utils import StreamlitLogHandler, render_footer
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ui_utils import StreamlitLogHandler, render_footer

st.set_page_config(page_title="1. Extração FTP", page_icon="🌐", layout="wide")
st.header("Passo 1: Extração via FTP (Arquivos .dbc)")
st.info("O sistema criará/lerá um catálogo local para explorar as pastas do servidor do DATASUS de forma rápida.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Configurações do Catálogo")
    raiz_ftp = st.text_input("Pasta Raiz no FTP para Mapear", value="/dissemin/publicos")
    if st.button("Sincronizar Catálogo com DATASUS"):
        with st.expander("Logs da Sincronização (Ao Vivo)", expanded=True):
            log_placeholder = st.empty()
            
        handler = StreamlitLogHandler(log_placeholder)
        logger = logging.getLogger("quadrosdesaude")
        logger.addHandler(handler)
        
        try:
            with st.spinner("Mapeando árvore de arquivos no DATASUS. Isso pode levar alguns minutos..."):
                inv = InventarioFTP()
                inv.atualizar_inventario(diretorio_raiz=raiz_ftp)
                st.success("Catálogo sincronizado com sucesso!")
        except BaseException as e:
            inv.evento_parada.set()
            raise e
        finally:
            logger.removeHandler(handler)
    
    st.markdown("---")
    pasta_destino = st.text_input("Pasta local de destino para os downloads", value=os.path.abspath("./downloads"))

with col2:
    st.subheader("Explorador de Arquivos")
    if 'pasta_atual' not in st.session_state:
        st.session_state.pasta_atual = "/dissemin/publicos"

    pasta_alvo = st.text_input("Caminho FTP Atual:", value=st.session_state.pasta_atual)
    
    inv = InventarioFTP()
    itens = inv.listar_todos_arquivos(pasta_alvo)

    if not itens:
        st.warning("Nenhum arquivo encontrado associado a este nível de diretório no catálogo. Sincronize se necessário.")
    else:
        st.write(f"Encontrados **{len(itens)}** arquivos a partir de `{pasta_alvo}`")
        df_itens = [{
            "Baixar?": False, 
            "Nome do Arquivo": i['nome'], 
            "Pasta Origem": i['caminho_pai'],
            "Tamanho (MB)": round(i['tamanho_bytes'] / 1024 / 1024, 2), 
            "Caminho FTP": i['caminho_completo']
        } for i in itens]
        
        editado = st.data_editor(
            df_itens,
            column_config={
                "Baixar?": st.column_config.CheckboxColumn(default=False),
                "Caminho FTP": None # Opcional: oculta na interface
            },
            width='stretch', hide_index=True
        )

        selecionados = [linha for linha in editado if linha["Baixar?"]]
        
        if selecionados:
            st.write("---")
            if st.button("🚀 Iniciar Download Lote"):
                with st.expander("Logs do Download (Ao Vivo)", expanded=True):
                    log_placeholder_dl = st.empty()
                
                handler_dl = StreamlitLogHandler(log_placeholder_dl)
                logger_dl = logging.getLogger("quadrosdesaude")
                logger_dl.addHandler(handler_dl)
                
                try:
                    with st.status("Preparando downloads em lote...") as status:
                        downloader = FTPDownloader()
                        for s in selecionados:
                            st.write(f"Baixando: `{s['Pasta Origem']}/{s['Nome do Arquivo']}`...")
                            
                            # Realiza o download individual (roda na thread principal, é seguro contra zombies se abortado)
                            # flag_pasta=True desativa o TQDM que polui o log e usa o log custom da biblioteca invés
                            downloader.download_arquivo(
                                caminho_ftp=s['Pasta Origem'], 
                                nome_arquivo=s['Nome do Arquivo'], 
                                pasta_destino=pasta_destino, 
                                flag_pasta=True
                            )
                            
                        status.update(label="Fila concluída!", state="complete", expanded=False)
                        st.success(f"Arquivos salvos em: {pasta_destino}")
                except BaseException as e:
                    downloader.evento_parada.set()
                    raise e
                finally:
                    logger_dl.removeHandler(handler_dl)

render_footer()
