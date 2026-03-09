import streamlit as st
import sys
import os

# Ajuste de path para que o utils seja resolvido a partir do diretorio ui_quadrosdesaude ou raiz
try:
    from ui_utils import render_footer
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ui_utils import render_footer

st.set_page_config(
    page_title="Quadros de Saúde",
    page_icon="🦆",
    layout="centered",
)

st.title("Quadros de Saúde v0.2.5 🦆")
st.markdown("Bem-vindo ao orquestrador de ETL para arquivos do DATASUS.")
st.markdown("---")
st.markdown("### Selecione um fluxo no menu lateral:")
st.markdown(
    """
    1. **Extração FTP:** Navegue pelos servidores do DATASUS e baixe arquivos de forma estruturada.
    2. **Descompressão:** Conveta grandes lotes de arquivos DBC (Data Base Cube) num formato legível padrão (DBF).
    3. **Domínio Parquet:** Transforme rapidamente DBF estruturado no mais poderoso padrão colunar (DuckLake).
    """
)


st.info("Para dúvidas arquiteturais, por favor leia as documentações ou sinta-se livre para usar o repósitorio OSS.")

render_footer()
