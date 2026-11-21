"""Testes de regressão sem chamadas à API externa."""
import unittest

from app import rota, run, segundos


class RoutesRegressionTests(unittest.TestCase):
    def test_duration_accepts_fractional_seconds(self):
        self.assertEqual(segundos("12.125s"), 12.125)

    def test_duration_rejects_invalid_values(self):
        for value in ("", "12", "-1s", "NaNs", "1.1234567890s", "9" * 400 + "s", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    segundos(value)

    def test_adjacent_route_url_encodes_addresses(self):
        url = rota("Natal, RN", "São Gonçalo do Amarante, RN")
        self.assertIn("travelmode=driving", url)
        self.assertIn("origin=Natal%2C+RN", url)
        self.assertIn("destination=S%C3%A3o+Gon%C3%A7alo", url)

    def test_route_rejects_more_than_three_stops(self):
        with self.assertRaises(ValueError):
            rota("Natal", "Recife", paradas=("A", "B", "C", "D"))

    def test_demonstration_computes_traffic_difference(self):
        result = run({
            "origem": "Natal", "destino": "Parnamirim",
            "fonte": "demonstracao",
            "resposta_exemplo": {"routes": [{
                "duration": "900s", "staticDuration": "720s",
                "distanceMeters": 10000
            }]}
        })
        self.assertEqual(result["diferenca_segundos"], 180)
        self.assertEqual(result["fonte"], "demonstracao")
        self.assertEqual(result["distancia_metros"], 10000)

    def test_empty_routes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Nenhuma rota"):
            run({"origem": "Natal", "destino": "Recife",
                 "fonte": "demonstracao", "resposta_exemplo": {"routes": []}})

    def test_malformed_response_shapes_are_rejected(self):
        for response in (None, [], {"routes": "invalid"}, {"routes": [None]}):
            with self.subTest(response=response), self.assertRaises(ValueError):
                run({"origem": "Natal", "destino": "Recife",
                     "fonte": "demonstracao", "resposta_exemplo": response})

    def test_missing_duration_is_rejected(self):
        with self.assertRaises(KeyError):
            run({"origem": "Natal", "destino": "Recife",
                 "fonte": "demonstracao",
                 "resposta_exemplo": {"routes": [{"staticDuration": "12s"}]}})




    def test_route_rejects_oversized_and_control_character_addresses(self):
        for origin in ("N" * 301, "Natal\nRecife", "Natal\x00Centro"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                rota(origin, "Recife")

    def test_google_route_validates_address_before_network_call(self):
        from unittest.mock import Mock, patch
        from app import consulta_google

        opener = Mock()
        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "test-key"}):
            with self.assertRaises(ValueError):
                consulta_google("N" * 301, "Natal", abrir=opener)
        opener.assert_not_called()

    def test_run_requires_a_json_object(self):
        for value in (None, [], "texto", 123):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "objeto JSON"):
                run(value)


if __name__ == "__main__":
    unittest.main()
