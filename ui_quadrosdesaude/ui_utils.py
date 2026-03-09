import logging
import streamlit as st
import os

class StreamlitLogHandler(logging.Handler):
    """
    Um handler customizado para o módulo logging do Python que redireciona 
    os logs do backend (quadrosdesaude) para um arquivo persistente e 
    para um placeholder dinâmico do Streamlit (apenas os ultimos N itens).
    """
    def __init__(self, placeholder, log_file="quadrosdesaude.log", max_lines_ui=30):
        super().__init__()
        self.placeholder = placeholder
        self.log_file = log_file
        self.max_lines_ui = max_lines_ui
        self.log_lines = []
        self.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))

    def emit(self, record):
        try:
            msg = self.format(record)
            
            # 1. Escreve no arquivo de disco de forma persistente (Append)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
            
            # 2. Mantém cache em mémória apenas dos ultimos `max_lines_ui` para a Interface
            self.log_lines.append(msg)
            if len(self.log_lines) > self.max_lines_ui:
                self.log_lines.pop(0)
            
            # Atualiza a UI em tempo real dentro do bloco vazio
            texto_ui = "\n".join(self.log_lines)
            self.placeholder.code(texto_ui, language="log")
        except Exception:
            self.handleError(record)

def render_footer():
    """Renderiza a assinatura de autoria em um padrão consistente para todas as páginas do Streamlit"""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: gray; font-size: small;">
            <b>Quadros de Saúde</b> - Ferramentas para Dados do SUS<br>
            Desenvolvido por <a href="https://instagram.com/dr.andreq" target="_blank" style="text-decoration: none; color: #1e88e5;"><b>Dr. André Quadros</b></a>
        </div>
        """,
        unsafe_allow_html=True
    )
