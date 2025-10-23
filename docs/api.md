# Referência da API

Esta secção contém a documentação gerada automaticamente a partir do código fonte do pacote `quadrosdesaude`.

## Orquestração

::: quadrosdesaude.conversao.orquestrador.orquestrador 
  options:
    show_source: true

## Processamento Atomico

::: quadrosdesaude.conversao.orquestrador.dbc2parquet 
  options:
    show_source: true

## Funções de Conversão

::: quadrosdesaude.conversao.conversor.dbc2dbf
::: quadrosdesaude.conversao.conversor.dbf2parquet
::: quadrosdesaude.conversao.conversor.harmonizar_registos_em_fluxo

## Extração FTP

::: quadrosdesaude.extracao.ftp.FTPDownloader
  options:
    members: # Lista os métodos que quer documentar explicitamente
      - __init__
      - lista_arquivos
      - download_arquivo
      - download_pasta
    show_root_toc_entry: false

## Utilitários

::: quadrosdesaude.utils.formatar_tamanho
::: quadrosdesaude.utils.medir_tamanho_pasta
::: quadrosdesaude.utils.limpador_

## Parsers Internos

::: quadrosdesaude.conversao.parser.StringFieldParser

## Função de Descompressão C (`descomprimir_dbc`)

Esta função, implementada em C para máxima performance, descomprime um ficheiro `.dbc` do DATASUS para o formato `.dbf`.

**Assinatura (como exposta em Python):**

```python
quadrosdesaude.descomprimir_dbc(caminho_dbc: str, caminho_dbf: str) -> int
```