# Uso de IA generativa

O enunciado pede uso criterioso e responsabilidade da equipe por dados, cálculos, referências e recomendações. Esta página declara onde a IA foi usada e como a equipe verifica.

## Onde a IA foi usada

1. **No desenvolvimento do projeto:** um assistente de IA (Claude, da Anthropic) apoiou a pesquisa de fontes, a estrutura da planilha, o código Python, os testes e a redação dos documentos.
   As decisões de escopo (público, alternativas, indicadores, região, linguagem, testes) foram do grupo, conforme `decisoes_do_grupo.md`.
2. **No produto (opcional):** a IA só reescreve em linguagem simples o texto que o código já calculou. Os números não vêm da IA e uma trava descarta a reescrita
   se qualquer número mudar (`src/assistente.py`, função `validar_reescrita`). Sem chave de API, o assistente funciona sem IA.

## O que a equipe deve verificar antes de entregar

Marque cada item depois de conferir pessoalmente.

- [ ] **Tarifa:** abrir o quadro da Enel SP e confirmar TUSD 472,42 e TE 316,96 R$/MWh para o B1 residencial (F1).
- [ ] **Tarifa Social:** ler a notícia do Ministério de Minas e Energia (80 kWh, renda de até meio salário mínimo por pessoa) e confirmar em fonte oficial o BPC e o valor de R$ 810,50, que essa página não traz (F4).
- [ ] **Fontes ainda não abertas:** conferir as fontes marcadas como "Só trecho de busca" em `docs/verificacao_das_fontes.md`.
- [ ] **Fator de CO2:** abrir a planilha do MCTI (SIRENE) e confirmar o valor médio de 2025 (F9).
- [ ] **Referências:** abrir cada link de `docs/referencias.md` e conferir se diz o que o projeto afirma.
- [ ] **Custos de instalação:** pedir orçamentos reais de aquecedor solar e de painel fotovoltaico pequeno e atualizar B02 e F02 na planilha.
- [ ] **Cálculos:** rodar `python -m unittest discover -s tests -v` e refazer um cálculo à mão (exemplo abaixo).
- [ ] **Recomendações:** ler `docs/justificativas_recomendacoes.md` e concordar com cada nota de viabilidade.
- [ ] **Compreensão:** ler `docs/decisoes_do_grupo.md` e saber explicar cada decisão com suas palavras.

## Exemplo de cálculo à mão (chuveiro da família de referência)

- Energia de um banho = 5,5 kW x 8/60 h = 0,733 kWh.
- Por mês = 0,733 kWh x 4 pessoas x 30 dias = 88,0 kWh.
- Custo = 88,0 kWh x R$ 0,9431 por kWh = cerca de R$ 83,00 por mês.
- Com banho de 5 minutos e 40% dos banhos na posição verão (3.000 W): potência média de 4.500 W, então 4,5 kW x 5/60 h x 4 x 30 = 45,0 kWh por mês, uma economia de 43,0 kWh,
  ou cerca de R$ 40,55 por mês.

## Limites conhecidos do uso de IA

A IA pode errar dados e interpretar mal uma regra. Por isso: cada número tem fonte e tipo (oficial, secundária ou estimado), os testes comparam o código com a planilha,
e as fontes secundárias estão marcadas para conferência. A IA do desenvolvimento não acessou fontes protegidas nem dados pessoais de usuários.
