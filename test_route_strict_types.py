"""Regressões para parâmetros inválidos nos links de direção."""
import unittest
from urllib.parse import parse_qs, urlparse
from app import rota


class TestRouteStrictTypes(unittest.TestCase):
    def test_modos_nao_textuais_retorna_erro_de_validacao(self):
        for modo in ([], {}, None, 10, True):
            with self.subTest(modo=modo), self.assertRaises(ValueError):
                rota("Natal, RN", "Parnamirim, RN", modo=modo)

    def test_evitar_pedagios_exige_booleano_real(self):
        for value in ("false", "true", 1, 0, None, []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                rota("Natal, RN", "Parnamirim, RN", evitar_pedagios=value)

    def test_parametro_tolls_usa_booleano_valido(self):
        with_tolls = parse_qs(urlparse(rota("Natal", "Mossoró", evitar_pedagios=True)).query)
        without_tolls = parse_qs(urlparse(rota("Natal", "Mossoró", evitar_pedagios=False)).query)
        self.assertEqual(with_tolls["avoid"], ["tolls"])
        self.assertNotIn("avoid", without_tolls)


if __name__ == "__main__":
    unittest.main()
