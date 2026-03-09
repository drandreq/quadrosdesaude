# Arquitetura e Contribuição

O pacote **Quadros de Saúde** foi construído com ferramentas de alta performance em mente, objetivando ser o padrão-ouro para pesquisadores lidando com os dados públicos do DATASUS.

## O Pipeline Central
Todo o processamento acontece num fluxo atômico rigoroso:
1. **DBC (Extrato Bruto):** Baixado diretamente via FTP.
2. **DBF (Descompressão):** O arquivo DBC proprietário é expandido.
3. **Parquet (DuckLake):** O DBF é lido em lotes (para proteger a memória RAM) e convertido num formato colunar, pronto para ser consumido por Polars, DuckDB ou Pandas.

## 🛑 ATENÇÃO: Contribuidores 🛑

O passo crítico do nosso pipeline é a conversão de `DBC` para `DBF`.
Essa conversão depende majoritariamente de um motor escrito em `C` (Baseado no pacote blast). 

**Regra de Ouro do Repositório:** A pasta `c_src/` é considerada uma "Caixa Preta" de segurança e estabilidade. 
Em nenhuma hipótese modifique os arquivos descritos nesta pasta sem uma coordenação prévia extensa com a equipe principal. 
Esses arquivos foram testados à exaustão para garantir compatibilidade no **Windows e macOS**. Qualquer mudança leviana pode quebrar o pacote de forma irreversível com as *build tools* do Python nas máquinas dos usuários finais.

Se um problema vier da descompressão DBC, crie uma **Issue** relatando o problema em detalhes. Não abra um Pull Request alterando a compilação C sem o devido isolamento e testes de pipeline providos pelos mantenedores originais.
