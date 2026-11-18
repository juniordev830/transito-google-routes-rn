import csv


def celula(valor):
    """Mantém texto com aparência de fórmula como texto em planilhas."""
    if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + valor
    return valor


def linhas(relatorio):
    yield (relatorio["fonte"], relatorio["duracao_segundos"], relatorio["base_segundos"],
           relatorio["diferenca_segundos"], relatorio["distancia_metros"], relatorio["google_maps"])


def escrever_csv(relatorio, destino):
    escritor = csv.writer(destino, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\n")
    escritor.writerow(('fonte', 'duracao_segundos', 'base_segundos', 'diferenca_segundos', 'distancia_metros', 'google_maps'))
    for linha in linhas(relatorio):
        escritor.writerow([celula(valor) for valor in linha])
