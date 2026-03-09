import logging

def configurar_logger():
    """
    Configura o logger principal da biblioteca quadrosdesaude.
    As mensagens são formatadas de maneira limpa para o terminal,
    mas podem ser facilmente interceptadas por outras aplicações (como Streamlit).
    """
    logger = logging.getLogger("quadrosdesaude")
    
    # Se o logger já tem handlers, não adicionamos de novo para evitar duplicação.
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Formato limpo, parecido com os prints originais, mas com nível embutido
        formatter = logging.Formatter('%(message)s')
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    return logger

logger = configurar_logger()
