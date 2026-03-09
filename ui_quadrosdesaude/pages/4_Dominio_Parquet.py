import streamlit as st
import os
import sys
import glob
import logging
from quadrosdesaude import dbf2parquet

try:
    from ui_utils import StreamlitLogHandler, render_footer
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ui_utils import StreamlitLogHandler, render_footer

st.set_page_config(page_title="3. DuckLake Parquet", page_icon="🦆", layout="wide")
st.header("Passo 3: Construção do DuckLake (Parquet)")
st.info("Transforme arquivos DBF num belíssimo cofre analítico usando conversão colunar em batch (Apache Arrow).")

pasta_dbf_fonte = st.text_input("Pasta contendo arquivos .dbf (Origem):", value=os.path.abspath("./temp_dbf"))

if os.path.exists(pasta_dbf_fonte) and os.path.isdir(pasta_dbf_fonte):
    arquivos_dbf = glob.glob(os.path.join(pasta_dbf_fonte, "*.[dD][bB][fF]"))
    if not arquivos_dbf:
        st.warning("Nenhum arquivo .dbf encontrado.")
    else:
        st.write(f"Encontrados **{len(arquivos_dbf)}** arquivos .dbf.")
        
        df_dbf = [{"Converter?": False, "Nome": os.path.basename(f), "Caminho": f} for f in arquivos_dbf]
        editado_dbf = st.data_editor(
            df_dbf,
            column_config={"Converter?": st.column_config.CheckboxColumn(default=False), "Caminho": None},
            width='stretch', hide_index=True
        )
        
        selecionados_dbf = [linha for linha in editado_dbf if linha["Converter?"]]
        
        if selecionados_dbf:
            st.markdown("---")
            pasta_parquet = st.text_input("Pasta de destino final (O seu DuckLake):", value=os.path.abspath("./ducklake"))
            
            if st.button("🚀 Iniciar Construção Parquet (DBF -> PARQUET)"):
                with st.expander("Logs do Processamento Pular (Ao Vivo)", expanded=True):
                    log_placeholder = st.empty()
                    
                handler = StreamlitLogHandler(log_placeholder)
                logger = logging.getLogger("quadrosdesaude")
                logger.addHandler(handler)
                
                try:
                    os.makedirs(pasta_parquet, exist_ok=True)
                    barra = st.progress(0, text="Preparando transformação...")
                    
                    sucessos = 0
                    for i, s in enumerate(selecionados_dbf):
                        nome_arquivo = s["Nome"]
                        caminho_entrada = s["Caminho"]
                        caminho_saida = os.path.join(pasta_parquet, nome_arquivo.replace(".dbf", ".parquet").replace(".DBF", ".parquet"))
                        
                        barra.progress(int((i / len(selecionados_dbf)) * 100), text=f"Lendo em Bateadas: {nome_arquivo}...")
                        
                        if dbf2parquet(caminho_entrada, caminho_saida, tamanho_lote=200000):
                            sucessos += 1
                        
                    barra.progress(100, text="O DuckLake foi populado!")
                    st.success(f"{sucessos} de {len(selecionados_dbf)} arquivos transformados com sucesso na pasta `{pasta_parquet}`!")
                finally:
                    logger.removeHandler(handler)

render_footer()
