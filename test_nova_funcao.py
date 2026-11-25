import unittest
from app import run
class VariacaoRota(unittest.TestCase):
    def test_variacao(self):
        data={"origem":"Natal","destino":"Macaíba","fonte":"demonstracao","diagnostico":True,"resposta_exemplo":{"routes":[{"duration":"90s","staticDuration":"60s","distanceMeters":1000}]}}
        result=run(data)
        self.assertEqual(result["variacao_percentual"],50)
        self.assertEqual(result["duracao_minutos"],1.5)
        data["resposta_exemplo"]["routes"][0]["staticDuration"]="0s"
        self.assertIsNone(run(data)["variacao_percentual"])
        data["diagnostico"]=False
        self.assertNotIn("variacao_percentual",run(data))
