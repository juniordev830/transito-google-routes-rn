'Consulte durações de carro com e sem influência do trânsito e compare as estimativas.'


def texto(value, max_chars=300):
    if not isinstance(value, str):
        raise ValueError("Use texto não vazio.")
    normalized = value.strip()
    if not normalized:
        raise ValueError("Use texto não vazio.")
    if len(normalized) > max_chars:
        raise ValueError(f"Use texto com até {max_chars} caracteres.")
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise ValueError("O texto não pode conter caracteres de controle.")
    return normalized


def inteiro(value, minimo=0):
    if type(value) is not int or value < minimo:
        raise ValueError(f"Use um número inteiro a partir de {minimo}.")
    return value


from urllib.parse import urlencode


MODOS = {"carro": "driving", "a-pe": "walking", "bicicleta": "bicycling", "onibus": "transit"}


def _url(acao, parametros):
    url = "https://www.google.com/maps/" + acao + "?" + urlencode({"api": 1, **parametros})
    if len(url) > 2048:
        raise ValueError("O endereço gerado ultrapassa o limite do Google Maps.")
    return url


def rota(origem, destino, modo="carro", paradas=(), evitar_pedagios=False):
    if isinstance(paradas, (str, bytes)) or paradas is None:
        raise ValueError("As paradas devem ser uma sequência de endereços.")
    try:
        from itertools import islice
        pontos = [texto(parada) for parada in islice(paradas, 4)]
    except TypeError as exc:
        raise ValueError("As paradas devem ser uma sequência de endereços.") from exc
    if len(pontos) > 3 or any("|" in parada for parada in pontos):
        raise ValueError("Use até 3 paradas por link e evite o caractere |.")
    if not isinstance(modo, str) or modo not in MODOS:
        raise ValueError(f"Modo desconhecido: {modo}")
    if type(evitar_pedagios) is not bool:
        raise ValueError("evitar_pedagios deve ser verdadeiro ou falso.")
    params = {"origin": texto(origem), "destination": texto(destino), "travelmode": MODOS[modo]}
    if pontos:
        params["waypoints"] = "|".join(pontos)
    if evitar_pedagios:
        params["avoid"] = "tolls"
    return _url("dir/", params)


import os
import re
from math import isfinite
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://routes.googleapis.com/directions/v2:computeRoutes"


def consulta_google(origem, destino, *, abrir=None):
    origem, destino = texto(origem), texto(destino)
    chave_api = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not chave_api:
        raise ValueError("Defina a variável GOOGLE_MAPS_API_KEY antes de consultar.")
    payload = {"origin": {"address": origem}, "destination": {"address": destino},
               "travelMode": "DRIVE", "routingPreference": "TRAFFIC_AWARE",
               "languageCode": "pt-BR", "regionCode": "BR"}
    request = Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), method="POST",
                      headers={"Content-Type": "application/json",
                               "X-Goog-Api-Key": chave_api,
                               "X-Goog-FieldMask": "routes.duration,routes.staticDuration,routes.distanceMeters,fallbackInfo"})
    try:
        with (abrir or urlopen)(request, timeout=15) as resposta:
            return json.load(resposta)
    except HTTPError as exc:
        raise ValueError(f"Google Routes respondeu HTTP {exc.code}.") from None
    except (URLError, TimeoutError):
        raise ValueError("Falha de conexão com Google Routes.") from None


def segundos(duration):
    if not isinstance(duration, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,9})?s", duration):
        raise ValueError("Duração ausente ou inválida na resposta.")
    value = float(duration[:-1])
    if not isfinite(value):
        raise ValueError("Duração ausente ou inválida na resposta.")
    return value


def run(data):
    if not isinstance(data, dict):
        raise ValueError("A entrada deve ser um objeto JSON.")
    origem, destino = texto(data["origem"]), texto(data["destino"])
    fonte = texto(data["fonte"])
    if fonte == "google":
        resposta = consulta_google(origem, destino)
    elif fonte == "demonstracao":
        resposta = data["resposta_exemplo"]
    else:
        raise ValueError("Escolha google ou demonstracao.")
    if not isinstance(resposta, dict):
        raise ValueError("A resposta de rotas deve ser um objeto JSON.")
    rotas = resposta.get("routes", [])
    if not isinstance(rotas, list):
        raise ValueError("A resposta deve conter uma lista de rotas.")
    if not rotas:
        raise ValueError("Nenhuma rota disponível para os endereços informados.")
    primeira = rotas[0]
    if not isinstance(primeira, dict):
        raise ValueError("A primeira rota deve ser um objeto JSON.")
    duracao, estatico = segundos(primeira["duration"]), segundos(primeira["staticDuration"])
    return {"fonte": fonte, "duracao_segundos": duracao, "base_segundos": estatico,
            "diferenca_segundos": round(duracao - estatico, 9),
            "distancia_metros": inteiro(primeira.get("distanceMeters", 0)),
            "calculo_alternativo": resposta.get("fallbackInfo"),
            "google_maps": rota(origem, destino)}


import argparse
from contextlib import nullcontext
import sys
from relatorio_csv import escrever_csv
import json
from pathlib import Path

MAX_JSON_BYTES = 1_000_000


def objeto_sem_campos_repetidos(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Campo JSON repetido: {chave!r}.")
        objeto[chave] = valor
    return objeto


def rejeitar_constante_json(constante):
    raise ValueError(f"Constante numérica inválida em JSON: {constante}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="Arquivo JSON com os dados ou - para a entrada padrão")
    parser.add_argument("--csv", action="store_true", help="Exportar a duração, a distância e o efeito do trânsito em CSV")
    args = parser.parse_args()

    try:
        entrada = nullcontext(sys.stdin.buffer) if args.entrada == "-" else Path(args.entrada).open("rb")
        with entrada as source:
            raw = source.read(MAX_JSON_BYTES + 1)
        if len(raw) > MAX_JSON_BYTES:
            raise ValueError("JSON excede o limite de 1 MB.")
        data = json.loads(
            raw,
            object_pairs_hook=objeto_sem_campos_repetidos,
            parse_constant=rejeitar_constante_json,
        )
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data)
    except RecursionError:
        parser.exit(2, "O JSON tem níveis de aninhamento demais.\n")
    except (KeyError, TypeError, ValueError, UnicodeError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if args.csv:
        escrever_csv(result, sys.stdout)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
