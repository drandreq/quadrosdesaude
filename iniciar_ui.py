import socket
from contextlib import closing

def encontrar_porta_livre(porta_inicial: int = 8501) -> int:
    """Procura iterativamente por uma porta TCP local disponível."""
    porta = porta_inicial
    while porta < 9000:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(('localhost', porta))
                return porta
            except OSError:
                porta += 1
    raise RuntimeError("Não foi possível encontrar uma porta livre para o Streamlit.")

if __name__ == "__main__":
    import sys
    import subprocess
    
    try:
        porta = encontrar_porta_livre()
        print(f"Iniciando Quadros de Saude UI na porta {porta}...")
        
        # O subprocess.run roda o streamlit bloqueando este script ate o fim
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "ui_quadrosdesaude/1_Home.py", 
            "--server.port", str(porta), 
            "--server.headless", "true"
        ], check=True)
    except Exception as e:
        print(f"Erro crítico ao tentar iniciar a interface: {e}")
