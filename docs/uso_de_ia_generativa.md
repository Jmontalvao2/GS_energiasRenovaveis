# Uso de IA generativa

Esta página declara onde a IA foi usada e como a equipe verifica.

## Onde a IA foi usada

1. **No desenvolvimento do projeto:** o assistente de IA (Claude, da Anthropic) apoiou a estrutura da planilha, o código Python e os testes.
   As decisões de escopo (público, alternativas, indicadores, região, linguagem, testes) foram do grupo, conforme `decisoes_do_grupo.md`.
2. **No produto (opcional):** a IA só reescreve em linguagem simples o texto que o código já calculou. Os números não vêm da IA e uma trava descarta a reescrita
   se qualquer número mudar (`src/assistente.py`, função `validar_reescrita`). Sem chave de API, o assistente funciona sem IA.

## Exemplo de cálculo à mão (chuveiro da família de referência)

- Energia de um banho = 5,5 kW x 8/60 h = 0,733 kWh.
- Por mês = 0,733 kWh x 4 pessoas x 30 dias = 88,0 kWh.
- Custo = 88,0 kWh x R$ 0,9431 por kWh = cerca de R$ 83,00 por mês.
- Com banho de 5 minutos e 40% dos banhos na posição verão (3.000 W): potência média de 4.500 W, então 4,5 kW x 5/60 h x 4 x 30 = 45,0 kWh por mês, uma economia de 43,0 kWh,
  ou cerca de R$ 40,55 por mês.

## Limites conhecidos do uso de IA

A IA pode errar dados e interpretar mal uma regra. Por isso: cada número tem fonte e tipo (oficial, secundária ou estimado), os testes comparam o código com a planilha,
e as fontes secundárias estão marcadas para conferência.
