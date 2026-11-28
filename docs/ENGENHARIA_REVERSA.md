# Engenharia reversa e estudo — Estimativas de trânsito com Google Routes

## Objetivo e fluxo

Comparação de durações com e sem influência do trânsito. Em app.py, consulta_google faz a chamada ao serviço, segundos interpreta a duração e run calcula a comparação. A chave é configuração de ambiente.

**Tecnologias identificadas** · Python.

**Revisão de referência** · `e42f6f182824`.

```mermaid
flowchart TD
    In["Entrada do cenário"] --> Core["app.py · run"]
    Core --> Google["Consulta Google Routes"]
    Google --> Parse["Interpretação das durações"]
    Parse --> Results["Resultado de comparação"]
    Results --> CSV["relatorio_csv.py"]
```

## Mapa do código

| Caminho | Papel de leitura | Símbolos selecionados |
| --- | --- | --- |
| [app.py](../app.py) | Ponto de leitura para entrada ou composição | `texto`, `inteiro`, `_url`, `rota`, `consulta_google`, `segundos`, `run`, `objeto_sem_campos_repetidos`, `rejeitar_constante_json` |
| [relatorio_csv.py](../relatorio_csv.py) | Implementação | `celula`, `linhas`, `escrever_csv` |

## Roteiro de estudo e desenvolvimento

1. Comece pelo fluxo descrito acima e localize seus pontos de entrada no mapa. Acompanhe uma entrada válida até a transformação ou a resposta.
2. Abra um teste relacionado ao fluxo e descreva qual regra ele protege. Compare o tratamento esperado para entradas válidas, inválidas e nos limites.
3. Ao adicionar uma regra, determine qual módulo controla o dado e cubra o caso nesse nível. Em seguida, confira o efeito no comando, na API ou na interface de entrada.

**Pergunta de entrevista**

Como testar a interpretação das respostas sem depender da API externa ou de uma credencial?

## Testes versionados

Arquivos para começar a leitura dos cenários de teste: [test_app.py](../test_app.py), [test_regressoes.py](../test_regressoes.py), [test_saida_csv.py](../test_saida_csv.py), [test_stdin.py](../test_stdin.py).

Os comandos e versões de runtime usados no CI ficam em [.github/workflows/python-tests.yml](../.github/workflows/python-tests.yml), [.github/workflows/tests.yml](../.github/workflows/tests.yml).

[Voltar ao README](../README.md).
