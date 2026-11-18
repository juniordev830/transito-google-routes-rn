'Consulte durações de carro com e sem influência do trânsito e compare as estimativas.'


def texto(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Use texto não vazio.")
    return value.strip()


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
    pontos = [texto(parada) for parada in paradas]
    if len(pontos) > 3 or any("|" in parada for parada in pontos):
        raise ValueError("Use até 3 paradas por link e evite o caractere |.")
    if modo not in MODOS:
        raise ValueError(f"Modo desconhecido: {modo}")
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
import sys
from relatorio_csv import escrever_csv
import json
from pathlib import Path


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
    parser.add_argument("entrada", type=Path, help="Arquivo JSON com os dados")
    parser.add_argument("--csv", action="store_true", help="Exportar a duração, a distância e o efeito do trânsito em CSV")
    args = parser.parse_args()

    try:
        with args.entrada.open(encoding="utf-8-sig") as source:
            data = json.load(
                source,
                object_pairs_hook=objeto_sem_campos_repetidos,
                parse_constant=rejeitar_constante_json,
            )
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    if args.csv:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        escrever_csv(result, sys.stdout)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
