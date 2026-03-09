# QUADROS DE SAÚDE - DATASUS

[![PyPI version](https://badge.fury.io/py/quadrosdesaude.svg)](https://badge.fury.io/py/quadrosdesaude)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`quadrosdesaude` é um pacote Python desenhado para automatizar o processo de ETL (Extração, Transformação e Carga) de dados de saúde pública do Brasil, com foco inicial nos arquivos do DATASUS.

## O Problema que Resolvemos

Os dados brutos do DATASUS são disponibilizados publicamente, mas em um formato `.dbc`. Este é um formato compactado proprietário e de difícil leitura pela maioria dos pesquisadores e das ferramentas modernas de análise de dados, como Pandas, Polars ou DuckDB.

O fluxo de trabalho manual para usar esses dados é tedioso e facil de errar:
1.  Encontrar o arquivo correto no FTP.
2.  Baixar o arquivo `.dbc`.
3.  Usar um descompressor (como o `blast-dbf` em C) para convertê-lo para `.dbf`.
4.  Converter o `.dbf` para um formato analítico moderno (como Parquet ou CSV).

## A Solução

O pacote `quadrosdesaude` automatiza e otimiza todo esse pipeline para você com apenas Duas funções: um orquestrador de __extração__ e um orquestrador de __tratamento__

-   **Extrai:** Baixa os arquivos `.dbc` diretamente do `ftp.datasus.gov.br`.
-   **Tratamento:**:
    -   **Descomprime:** Converte os arquivos `.dbc` em `.dbf` usando a dependência C interna (da pasta `c_src`).
    -   **Transforma:** Converte os arquivos `.dbf` em `.parquet`, um formato colunar otimizado para performance em ferramentas de *data analysis*.

O objetivo final é criar um "Data Lake" (ou "DuckLake" 🦆) de arquivos Parquet prontos para análise imediata.

## Instalação

Você pode instalar o pacote diretamente a partir do PyPI:

```bash
pip install quadrosdesaude
```


## Colaborando
Para contribuir com este projeto você precisará fazer um fork do repositório, clone local e instalar via Poetry para ambiente de desenvolvimento isolado:

```bash
# Instala o projeto com as dependências de desenvolvimento
poetry install --with dev
```

Para garantir a construção correta dos Módulos C nativos durante o testes:
```bash
poetry build
```

E finalmente, para habilitar o ambiente onde você poderá executar a UI local do Streamlit:
```bash 
poetry shell
python iniciar_ui.py
```


## Autor

**Dr. André Quadros**
- [LinkedIn](https://www.linkedin.com/in/andrequadros/)

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE.md` para detalhes.