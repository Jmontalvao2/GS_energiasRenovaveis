# Roteiro dos testes com usuários

**Objetivo:** verificar se as orientações de energia são compreendidas e úteis para o público (famílias de baixa renda) e ajustar o assistente.

## Como fazer

- **Formato:** teste presencial rápido, de cerca de 10 minutos, com **3 a 5 pessoas**. A pessoa usa o assistente e comenta em voz alta. Quem testa só observa e anota.
- **Quem convidar:** adultos que pagam ou ajudam a pagar a conta de luz, de preferência com perfil próximo do público (renda baixa, pouca prática com aplicativos, idosos).
- **Privacidade:** explique o objetivo e peça concordância verbal. Registre cada pessoa só por código (P1, P2...). Não anote nome, CPF, telefone, endereço nem número da conta.
  Peça que a pessoa não digite dados pessoais no app (o app também apaga números longos dos comentários e das dúvidas).

## Situações a testar (cada pessoa faz 2 ou 3)

| Código | Situação | O que observar |
|---|---|---|
| S1 | Família com Tarifa Social que informa o valor da conta em R$ | Entendeu a pergunta da Tarifa Social? Soube onde digitar a conta? |
| S2 | Família sem Tarifa Social que informa o consumo em kWh | Soube achar os kWh na conta? |
| S3 | Pessoa que não sabe o consumo e usa a família de referência | Entendeu que o resultado é um exemplo? |
| S4 | Casa alugada | Entendeu por que B e C aparecem como pouco viáveis? |
| S5 | Pergunta fora do escopo (ex.: "como tiro meu RG?") | Entendeu a resposta "não sei" e o que fazer depois? |

## Perguntas de compreensão (depois do resultado)

1. Quanto o assistente diz que você pode economizar com a alternativa A?
2. O que significa "retorno de 20 anos"?
3. Qual seria a primeira coisa que você faria?
4. O assistente garantiu que você vai economizar esse valor? (verifica se entendeu a limitação)
5. De onde vêm as informações? (verifica o selo de confiança)
6. Algum termo ou frase ficou difícil?

## Como registrar

1. Preencha uma linha por situação em `registro_testes.md`.
2. A própria pessoa pode responder "Essa orientação ajudou?" no fim do app. As respostas ficam em `data/feedback_testes.csv`, sem dados pessoais.
3. Para cada problema encontrado, descreva o ajuste feito em `ajustes_realizados.md`.

## Regra para decidir ajustes

Se 2 ou mais pessoas não entenderem o mesmo termo, número ou botão, o texto é reescrito e o ponto é testado de novo com outra pessoa.
