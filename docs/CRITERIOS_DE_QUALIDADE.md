# Contrato de confiabilidade da integração Routes

## Objetivo

Garantir que estimativas de deslocamento sejam apresentadas com origem, horário e fonte identificáveis. O modo demonstração não representa trânsito em tempo real.

## Cenários de validação

| Cenário | Resultado esperado |
| --- | --- |
| Arquivo JSON inválido | Mensagem de erro e código de saída não zero |
| Origem ou destino ausente | Rejeitar antes da requisição |
| Chave de API ausente no modo Google | Falhar sem revelar segredos |
| HTTP 429 | Informar limite de uso; não apresentar valor fictício |
| HTTP 5xx ou timeout | Informar indisponibilidade e permitir nova tentativa manual |
| Resposta sem duração | Rejeitar cálculo e sinalizar resposta incompleta |
| Diferença de duração negativa | Preservar dados brutos e sinalizar resultado atípico |
| fallbackInfo presente | Exibir aviso de cálculo alternativo |
| Modo demonstração | Rotular todas as estimativas como fictícias |

## Segurança e custo

- Nunca versionar GOOGLE_MAPS_API_KEY nem registrá-la em logs.
- Configurar restrições de chave e cotas no Google Cloud.
- Evitar consultas automáticas repetitivas sem controle de custo.
- Não prometer tempos de chegada exatos; condições de trânsito variam.

## Comandos de verificação

```bash
python app.py exemplo.json
python -m unittest -v
```

Este arquivo é uma especificação de aceitação; os cenários ainda precisam ser confrontados com a implementação e testes automatizados.
