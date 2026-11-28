# Estimativas de trânsito com Google Routes

**Navegação** · [Rodar](#rodar) · [Uso](#uso) · [Google Maps](#google-maps) · [Código e estudo](docs/ENGENHARIA_REVERSA.md)

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

## Exportação para planilha

Use `python app.py exemplo.json --csv > relatorio.csv` para exportar a duração, a distância e o efeito do trânsito. O CSV usa ponto e vírgula, conserva a ordem do relatório e inclui o cabeçalho mesmo quando a seleção está vazia. O JSON continua sendo a saída padrão.

Também é possível encadear a ferramenta com outro comando usando `-` como entrada. Exemplo em um terminal Bash:

```bash
cat exemplo.json | python app.py -
```

Arquivos e entrada padrão JSON são limitados a 1 MB (1.000.000 bytes). Conteúdos maiores são rejeitados antes de consultar o Google Routes ou processar dados de demonstração.

## Código e roteiro de estudo

Como testar a interpretação das respostas sem depender da API externa ou de uma credencial? O [guia de engenharia reversa](docs/ENGENHARIA_REVERSA.md) reúne o mapa dos módulos e uma pergunta técnica baseada no projeto.

Mantido por [João Junior](https://github.com/juniordev830).
