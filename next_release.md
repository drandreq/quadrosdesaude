# Próximo release — quadrosdesaude

Alterações preparadas no submódulo `.quadrosdesaude` para o pipeline EntropyZero (Colab).

## `conversao/conversor.py` — `dbf2parquet`

### O quê
- Validação de **colunas** além de linhas: compara `schema_mestre` do DBF com o schema do Parquet gerado.
- Tratamento explícito de `MemoryError` e `FileNotFoundError` (logs distintos antes do retorno `False`).
- Remoção do `del` de variáveis no loop que causava `UnboundLocalError` no `except` (correção anterior mantida).
- Arquivo DBF vazio: retorno `True` sem exigir Parquet materializado.

### Por quê
- O orquestrador precisa distinguir corrupção estrutural de falha genérica (`erro_integridade` vs `erro_conversao`).
- DATASUS pode divergir em colunas; detectar cedo evita Gold inválido.
- Colab OOM deve aparecer claramente nos logs para ajuste de `tamanho_lote` / workers.

## Compatibilidade
- Assinatura pública de `dbf2parquet` inalterada (`bool`).
- Consumidores que só checam `True`/`False` continuam funcionando.

## Após publicar
1. `pip install -e .quadrosdesaude` no Colab.
2. Rodar conciliação (5.5) e pré-voo (6.5) antes do flow de conversão.
