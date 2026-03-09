import streamlit as st
import os
import sys
import glob
import logging
from quadrosdesaude import dbc2dbf

try:
    from ui_utils import StreamlitLogHandler, render_footer
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ui_utils import StreamlitLogHandler, render_footer

st.set_page_config(page_title="2. Descompressão", page_icon="🗜️", layout="wide")
st.header("Passo 2: Descompressão (DBC -> DBF)")
st.info("Mapeie a pasta local de arquivos .dbc salvos e converta para leitura analítica (.dbf).")

pasta_dbc = st.text_input("Pasta contendo arquivos .dbc (Origem):", value=os.path.abspath("./downloads"))

if os.path.exists(pasta_dbc) and os.path.isdir(pasta_dbc):
    arquivos_dbc = glob.glob(os.path.join(pasta_dbc, "*.[dD][bB][cC]"))
    if not arquivos_dbc:
        st.warning("Nenhum arquivo .dbc encontrado nesta pasta.")
    else:
        st.write(f"Encontrados **{len(arquivos_dbc)}** arquivos .dbc.")
        
        df_dbc = [{"Converter?": False, "Nome": os.path.basename(f), "Caminho": f} for f in arquivos_dbc]
        editado_dbc = st.data_editor(
            df_dbc,
            column_config={"Converter?": st.column_config.CheckboxColumn(default=False), "Caminho": None},
            width='stretch', hide_index=True
        )
        
        selecionados_dbc = [linha for linha in editado_dbc if linha["Converter?"]]
        
        if selecionados_dbc:
            st.markdown("---")
            pasta_dbf = st.text_input("Pasta destino (Temporários DBF):", value=os.path.abspath("./temp_dbf"))
            
            if st.button("🚀 Iniciar Descompressão Lote (DBC -> DBF)"):
                with st.expander("Logs da Conversão C (Ao Vivo)", expanded=True):
                    log_placeholder = st.empty()
                    
                handler = StreamlitLogHandler(log_placeholder)
                logger = logging.getLogger("quadrosdesaude")
                logger.addHandler(handler)
                
                try:
                    os.makedirs(pasta_dbf, exist_ok=True)
                    barra = st.progress(0, text="Preparando conversão...")
                    
                    sucessos = 0
                    for i, s in enumerate(selecionados_dbc):
                        nome_arquivo = s["Nome"]
                        caminho_entrada = s["Caminho"]
                        caminho_saida = os.path.join(pasta_dbf, nome_arquivo.replace(".dbc", ".dbf").replace(".DBC", ".dbf"))
                        
                        barra.progress(int((i / len(selecionados_dbc)) * 100), text=f"Convertendo: {nome_arquivo}...")
                        
                        if dbc2dbf(caminho_entrada, caminho_saida):
                            sucessos += 1
                        
                    barra.progress(100, text="Processamento concluído!")
                    st.success(f"{sucessos} de {len(selecionados_dbc)} convertidos com sucesso na pasta `{pasta_dbf}`!")
                finally:
                    logger.removeHandler(handler)

render_footer()
