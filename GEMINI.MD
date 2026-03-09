# Memória do Projeto: QUADROS DE SAÚDE (v0.2.5)

Este documento serve como a "Cápsula de Contexto" para IAs e desenvolvedores que retomarem este projeto. Ele resume a inteligência acumulada na Sprint de Produção.

## 1. Identidade e Propósito
Pacote criado por **Dr. André Quadros** para automatizar o ETL do DATASUS: `DBC -> DBF -> Parquet (DuckLake)`.
- **Regra de Ouro:** A pasta `c_src` é intocável. Módulos C nativos são compilados via `build.py` e Poetry.

## 2. Arquitetura Atual (v0.2.5)
O projeto evoluiu de scripts isolados para um pacote de software robusto:

### Backend (`src/quadrosdesaude`)
- **`InventarioFTP`**: Usa DuckDB local (`inventario_datasus.db`) para catalogar o FTP do Datasus, permitindo exploração ultra-rápida sem timeouts.
- **`FTPDownloader`**: Implementa `threading.Event()` para permitir o cancelamento instantâneo de processos (Stop) sem criar threads zumbis.
- **`logger.py`**: Centraliza logs em PT-BR para terminal e interface.

### Frontend (`ui_quadrosdesaude`)
- **Multi-page Streamlit**: Interface profissional dividida por etapas do pipeline.
- **`ui_utils.py`**: Contém o `StreamlitLogHandler` (logs em tempo real no expander) e `render_footer()` (marca d'água de autoria com Instagram).

### Distribuição (`scripts/`)
- **Windows**: `.bat` para setup e execução automática.
- **Unix/Linux (Manylinux)**: `build_manylinux.sh` via Docker utiliza a imagem oficial PyPA para gerar binários universais (.whl) compatíveis com qualquer distruição Linux.

## 3. Estado da Conversão
- **0.2.5 Publicada:** Versão está operacional no PyPI e GitHub.
- **Logs de UI:** Injetados diretamente no orquestrador do Streamlit para feedback ao vivo.
- **Dependências:** `streamlit` e `duckdb` são instaladas automaticamente pelo `pip install`.

## 4. Próximos Passos Sugeridos
- Implementar suporte a outros protocolos ou bases além do SINAN se necessário.
- Ampliar a suíte de testes em `tests/` para cobertura de 90%+.

---
*Assinado: Antigravity AI (Pair Programming com Dr. André Quadros)*