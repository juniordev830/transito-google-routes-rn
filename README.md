# Estimativas de trânsito com Google Routes

Consulte durações de carro com e sem influência do trânsito e compare as estimativas.

## Rodar

Python 3.10 ou mais recente. Cada execução lê um JSON local e imprime outro JSON no terminal.

```bash
python app.py exemplo.json
python -m unittest -v
```

## Uso

O exemplo roda com dados fictícios no modo `demonstracao`. Para dados do Google, altere `fonte` para `google`, habilite [Routes API](https://developers.google.com/maps/documentation/routes/reference/rest/v2/TopLevel/computeRoutes) com faturamento e configure a variável de ambiente `GOOGLE_MAPS_API_KEY`. Uma consulta é enviada por execução no modo Google. O relatório usa a diferença entre `duration` e `staticDuration` e indica quando o serviço devolve uma alternativa de cálculo em `fallbackInfo`.

O arquivo de exemplo demonstra o formato da resposta. A integração usa a rede apenas no modo `google`.

## Google Maps

Os links seguem a documentação de [Maps URLs](https://developers.google.com/maps/documentation/urls/get-started) e abrem o app ou site sem chave. Confira no Maps a rota oferecida, a cobertura de transporte e as condições do momento. Os valores numéricos no arquivo de exemplo são demonstrações.

## Estado do projeto

Versão inicial funcional por linha de comando, sem interface web. Usa apenas a biblioteca padrão do Python. Os testes executam os exemplos e verificam as regras do projeto.
