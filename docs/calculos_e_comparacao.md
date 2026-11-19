# Cálculos e comparação das alternativas

Mesma necessidade (reduzir a conta de luz de uma família de baixa renda de São Paulo), mesmo período de referência (1 mês e 10 anos)
e mesmos indicadores para as 3 alternativas. As fórmulas estão em `src/calculos.py` e, em planilha, em `data/planilha_premissas.xlsx`
(abas Consumo e Alternativas). Os testes automáticos conferem o código contra a planilha.

## 1. Conceitos aplicados

- **Energia (kWh)** = potência (kW) x tempo (h). O consumo de cada aparelho vem dessa fórmula.
- **Potência** é a taxa de uso de energia: um chuveiro de 5.500 W usa 5,5 kWh a cada hora ligado.
- **Eficiência energética:** gastar menos kWh para o mesmo serviço (banho mais curto, posição verão).
- **Fontes renováveis:** energia solar térmica (aquece a água) e solar fotovoltaica (gera eletricidade).
- **Custo mensal** = (kWh faturados - kWh isentos pela Tarifa Social) x tarifa com tributos.
- **Retorno do investimento (anos)** = investimento / (economia por mês x 12).
- **CO2 evitado** = kWh evitados por mês x 12 x fator de emissão da rede.

## 2. Tarifa (São Paulo, Enel SP, residencial B1)

(TUSD 0,47242 + TE 0,31696) = R$ 0,78938 por kWh sem tributos
(Resolução Homologatória ANEEL nº 3.596/2026, em vigor desde 04/07/2026). Com carga tributária efetiva de 16,3%
(consumo até 200 kWh), a tarifa usada é **R$ 0,94 por kWh**.

## 3. Consumo da família de referência (4 pessoas)

- Chuveiro: 4 pessoas x 1 banho x 5.500 W x 8 min x 30 dias = **88,0 kWh/mês**.
- Demais equipamentos (geladeira, lâmpadas, TV, outros): **90,8 kWh/mês**.
- Total: **178,8 kWh/mês**, com o chuveiro em **49%** do consumo.

*Por que o chuveiro pesa tanto?* Na literatura sobre casas de baixa renda, o chuveiro responde por 33% a 40% do consumo em medições em Florianópolis
(Silva et al., 2014) e por 60% em uma simulação no Rio de Janeiro com chuveiro de 5.400 W, 4 pessoas e banhos de 10 minutos (Silveira e Gardolinski, 2016).
A família de referência fica no meio dessa faixa. A média nacional de 24% citada pelo Procel (2005) inclui casas com muitos outros aparelhos; a nossa tem poucos
(sem ar-condicionado, sem micro-ondas, uma TV) e todos tomam banho elétrico por 8 minutos, a faixa mais comum na PPH 2019 (6 a 10 minutos). O consumo anual do
chuveiro da família (1.056 kWh) está abaixo da mediana de 1.646 kWh por ano dos nove estudos reunidos por Santos e Morais (2025). Ou seja, a participação
alta vem do consumo total baixo, e não de um chuveiro superestimado. A análise de sensibilidade abaixo mostra que as conclusões não dependem desse ponto.
No uso real, o assistente pede a conta de luz da própria família.

## 4. Alternativas comparadas

- **A) Eficiência e hábitos:** banho de 5 min e 40% dos banhos na posição verão (3.000 W). Investimento R$ 0,00.
- **B) Aquecimento solar de água (renovável):** o sol atende 60% da energia do chuveiro. Investimento de R$ 12.000,00.
- **C) Painel fotovoltaico (renovável):** 1,2 kWp x 120 kWh/kWp/mês = 144,0 kWh/mês,
  com mínimo de 30 kWh faturados e Fio B de R$ 0,10 por kWh compensado. Investimento de R$ 7.200,00.

### Cenário 1: sem Tarifa Social

| Cenário | Consumo da rede (kWh/mês) | Energia faturada (kWh/mês) | Custo mensal | Economia mensal | Investimento | Retorno | Saldo em 10 anos | CO2 evitado (kg/ano) | Viabilidade |
|---|---|---|---|---|---|---|---|---|---|
| Situação atual | 178,8 | 178,8 | R$ 168,63 | R$ 0,00 | R$ 0,00 | - | R$ 0,00 | 0 | - |
| A) Eficiência e hábitos | 135,8 | 135,8 | R$ 128,07 | R$ 40,55 | R$ 0,00 | imediato | R$ 4.866,43 | 24 | Alta |
| B) Aquecimento solar de água | 126,0 | 126,0 | R$ 118,83 | R$ 49,80 | R$ 12.000,00 | 20,1 anos | -R$ 6.024,48 | 29 | Média |
| C) Painel fotovoltaico | 178,8 | 34,8 | R$ 42,90 | R$ 125,73 | R$ 7.200,00 | 4,8 anos | R$ 7.887,28 | 80 | Baixa |

### Cenário 2: com Tarifa Social (80 kWh isentos)

| Cenário | Consumo da rede (kWh/mês) | Energia faturada (kWh/mês) | Custo mensal | Economia mensal | Investimento | Retorno | Saldo em 10 anos | CO2 evitado (kg/ano) | Viabilidade |
|---|---|---|---|---|---|---|---|---|---|
| Situação atual | 178,8 | 178,8 | R$ 93,18 | R$ 0,00 | R$ 0,00 | - | R$ 0,00 | 0 | - |
| A) Eficiência e hábitos | 135,8 | 135,8 | R$ 52,63 | R$ 40,55 | R$ 0,00 | imediato | R$ 4.866,43 | 24 | Alta |
| B) Aquecimento solar de água | 126,0 | 126,0 | R$ 43,38 | R$ 49,80 | R$ 12.000,00 | 20,1 anos | -R$ 6.024,48 | 29 | Média |
| C) Painel fotovoltaico | 178,8 | 34,8 | R$ 10,08 | R$ 83,10 | R$ 7.200,00 | 7,2 anos | R$ 2.771,87 | 80 | Baixa |

Na alternativa C, o cenário 2 é uma hipótese: não encontramos fonte oficial dizendo se quem tem Tarifa Social mantém o benefício com geração própria.
O assistente pede para confirmar com a distribuidora.

## 5. Análise de sensibilidade

Cada linha muda uma premissa e recalcula tudo com o mesmo código do assistente.

| Caso | Consumo (kWh/mês) | Chuveiro no consumo | Economia A (R$/mês) | Economia B (R$/mês) | Retorno B (anos) | Economia C (R$/mês) | Retorno C sem Tarifa Social | Retorno C com Tarifa Social |
|---|---|---|---|---|---|---|---|---|
| Caso base (planilha) | 178,8 | 49% | R$ 40,55 | R$ 49,80 | 20,1 anos | R$ 125,73 | 4,8 anos | 7,2 anos |
| Chuveiro de 4.000 W | 154,8 | 41% | R$ 26,41 | R$ 36,22 | 27,6 anos | R$ 104,77 | 4,8 anos | 8,0 anos |
| Chuveiro de 5.000 W | 170,8 | 47% | R$ 35,84 | R$ 45,27 | 22,1 anos | R$ 115,25 | 4,8 anos | 7,2 anos |
| Banho de 6 minutos | 156,8 | 42% | R$ 19,81 | R$ 37,35 | 26,8 anos | R$ 104,77 | 4,8 anos | 7,8 anos |
| Banho de 10 minutos | 200,8 | 55% | R$ 61,30 | R$ 62,25 | 16,1 anos | R$ 136,20 | 4,8 anos | 6,3 anos |
| 3 pessoas na casa | 156,8 | 42% | R$ 30,42 | R$ 37,35 | 26,8 anos | R$ 104,77 | 4,8 anos | 7,8 anos |
| 5 pessoas na casa | 200,8 | 55% | R$ 50,69 | R$ 62,25 | 16,1 anos | R$ 136,20 | 4,8 anos | 6,3 anos |
| Tarifa 10% maior | 178,8 | 49% | R$ 44,61 | R$ 54,78 | 18,3 anos | R$ 139,31 | 4,3 anos | 6,5 anos |
| Aquecedor solar a R$ 8 mil | 178,8 | 49% | R$ 40,55 | R$ 49,80 | 13,4 anos | R$ 125,73 | 4,8 anos | 7,2 anos |
| Aquecedor solar a R$ 16 mil | 178,8 | 49% | R$ 40,55 | R$ 49,80 | 26,8 anos | R$ 125,73 | 4,8 anos | 7,2 anos |
| Fração solar de 50% | 178,8 | 49% | R$ 40,55 | R$ 41,50 | 24,1 anos | R$ 125,73 | 4,8 anos | 7,2 anos |
| Fração solar de 70% | 178,8 | 49% | R$ 40,55 | R$ 58,10 | 17,2 anos | R$ 125,73 | 4,8 anos | 7,2 anos |
| Geração de 105 kWh/kWp (litoral do Sudeste) | 178,8 | 49% | R$ 40,55 | R$ 49,80 | 20,1 anos | R$ 128,35 | 5,5 anos | 8,4 anos |
| Fotovoltaico a R$ 4.500/kWp | 178,8 | 49% | R$ 40,55 | R$ 49,80 | 20,1 anos | R$ 125,73 | 3,6 anos | 5,4 anos |
| Fotovoltaico a R$ 7.000/kWp | 178,8 | 49% | R$ 40,55 | R$ 49,80 | 20,1 anos | R$ 125,73 | 5,6 anos | 8,4 anos |

**Leitura dos resultados**

- A economia da alternativa A é positiva em todos os casos (mínimo de R$ 19,81 por mês) e não exige compra.
- O retorno do aquecimento solar (B) fica entre 13,4 e 27,6 anos nos casos testados, acima dos 10 anos de referência em todos eles.
- O retorno do painel fotovoltaico (C) fica entre 3,6 e 8,4 anos, o menor de todos, mas exige imóvel próprio e um investimento alto.
- A ordem de recomendação (A primeiro; B e C só com imóvel próprio e orçamentos reais) não muda nos casos testados.

## 6. Limitações dos cálculos

- Tarifa, bandeira, impostos e regras mudam; usamos tarifa constante, sem manutenção e sem juros.
- Custos de instalação vêm de fontes comerciais e precisam de orçamentos reais. A faixa de R$ 5.500 a R$ 7.000 por kWp vale para sistemas de 2 a 5 kWp; nosso sistema de 1,2 kWp é menor, e sistemas pequenos tendem a custar mais por kWp.
- O fator de emissão usado é a média da rede de 2025; fatores marginais, usados em metodologias de projeto, tendem a ser maiores.
- Não quantificamos impactos de fabricação e descarte de painéis e coletores.
- Valores são estimativas, não garantias de economia, geração ou custo.
