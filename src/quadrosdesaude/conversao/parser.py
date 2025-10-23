from dbfread import FieldParser

class StringFieldParser(FieldParser):
  """
    Parser personalizado para dbfread que tenta decodificar todos os campos como strings latin1.

    Esta classe sobrescreve o método `parse` padrão. Para cada campo lido do
    ficheiro DBF, ela tenta remover espaços extras e decodificar os bytes
    usando a codificação 'latin1'. Se a decodificação falhar (por exemplo,
    porque o dado não é bytes ou contém caracteres inválidos), o dado original
    é retornado sem modificação.

    Isto é útil para ler ficheiros DBF com dados potencialmente "sujos" ou
    tipos inconsistentes, garantindo que a leitura prossiga e que os dados
    sejam tratados como texto sempre que possível.

    Uso:
      tabela = DBF('meu_arquivo.dbf', parserclass=StringFieldParser)
  """
  def parse(self, field, data):
    """
      Tenta decodificar o dado como uma string latin1 após remover espaços.

      Args:
        field: O objeto Field do dbfread (não usado diretamente aqui).
        data: O valor bruto do campo lido do ficheiro DBF.

      Returns:
        str or object: A string decodificada (se bem-sucedido) ou o dado original.
    """
    try:
      # Tenta decodificar os bytes para uma string latin1
      return data.strip().decode('latin1')
    except (ValueError, AttributeError):
      # Se falhar ou se o dado já não for bytes, retorna como está
      return data