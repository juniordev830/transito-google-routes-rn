import json
from pathlib import Path
import subprocess
import sys
import unittest

from app import run

ROOT = Path(__file__).resolve().parent


class ProjetoTest(unittest.TestCase):
    def test_exemplo_documentado(self):
        data = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        result = run(data)
        self.assertEqual(result['diferenca_segundos'], 540)

    def test_cli_com_exemplo(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), str(ROOT / "exemplo.json")],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertEqual(json.loads(result.stdout)['diferenca_segundos'], 540)

    def test_rejeita_dados_incompletos(self):
        with self.assertRaises((KeyError, ValueError, TypeError)):
            run({})

    def test_requisicao_traffic_aware(self):
        from io import BytesIO
        from unittest.mock import patch
        from app import ENDPOINT, consulta_google

        def abrir(request, timeout):
            self.assertEqual(request.full_url, ENDPOINT)
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(timeout, 15)
            self.assertEqual(request.get_header("X-goog-api-key"), "teste")
            body = json.loads(request.data)
            self.assertEqual(body["routingPreference"], "TRAFFIC_AWARE")
            self.assertEqual(body["origin"]["address"], "Natal, RN")
            return BytesIO(b'{"routes": []}')

        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "teste"}):
            self.assertEqual(consulta_google("Natal, RN", "Macau, RN", abrir=abrir), {"routes": []})

    def test_sem_chave_nao_faz_chamada(self):
        from app import consulta_google
        from unittest.mock import patch, Mock
        abrir = Mock()
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(ValueError):
            consulta_google("Natal", "Recife", abrir=abrir)
        abrir.assert_not_called()

    def test_sem_rotas(self):
        with self.assertRaises(ValueError):
            run(dict(origem="A", destino="B", fonte="demonstracao", resposta_exemplo={"routes": []}))

    def test_duracao_fracionaria_e_invalida(self):
        from app import segundos
        self.assertAlmostEqual(segundos("1.125s"), 1.125)
        for value in ("NaNs", "-1s", "12", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                segundos(value)
