# Dados utilizados, origem e premissas

Fonte de verdade: `data/planilha_premissas.xlsx` (aba Premissas), exportada para `data/premissas.json`. Consulta às fontes em 18/11/2026.

**Tipos de dado:** *Oficial* (órgão público ou distribuidora), *Secundária (verificar)* (imprensa, blog ou site comercial que reproduz dado oficial), *ESTIMADO* (premissa da equipe, justificada) e *Calculado*.

| ID | Parâmetro | Valor | Unidade | Tipo | Fonte | Observação |
|---|---|---|---|---|---|---|
| P01 | Pessoas na família de referência | 4 | pessoas | ESTIMADO | Decisão do grupo; F3 | Procel PPH-SP: média de 3,04 moradores por domicílio. O grupo adotou 4 pessoas. |
| P02 | Horizonte de comparação | 10 | anos | ESTIMADO | Decisão do grupo | Período comum às 3 alternativas. Tarifa constante, sem manutenção e sem juros. |
| T01 | TUSD sem tributos | 0.47242 | R$/kWh | Oficial | F1 | B1 residencial convencional, vigente de 04/07/2026 a 03/07/2027 (Resolução Homologatória ANEEL nº 3.596/2026): 472,42 R$/MWh, conforme quadro de tarifas da Enel SP. |
| T02 | TE (energia) sem tributos | 0.31696 | R$/kWh | Oficial | F1 | Mesma resolução: 316,96 R$/MWh. Soma TUSD + TE = R$ 0,78938/kWh sem tributos. |
| T03 | Reajuste adicional sobre T01 e T02 | 0 | fração | Oficial | F1 | Zero: T01 e T02 já são as tarifas vigentes depois do reajuste de 04/07/2026 (+8,9% no B1 residencial; a média de todas as classes foi 10,18%). |
| T04 | Carga tributária efetiva (ICMS + PIS/COFINS), consumo até 200 kWh | 0.163 | fração | Calculado | F2 | Derivada de fatura B1 de jan/2026 (167 kWh, ICMS 12%): 1 - 0,43244/0,51659. Acima de 200 kWh a alíquota observada foi 18%. Confirmar a alíquota vigente na SEFAZ-SP. |
| T05 | Adicional de bandeira tarifária | 0 | R$/kWh | ESTIMADO | Decisão do grupo | Assume bandeira verde. A bandeira muda todo mês. Taxa de iluminação pública (COSIP) não incluída. |
| T06 | Tarifa com tributos (resultado) | 0.943106 | R$/kWh | Calculado | T01 a T05 | Valor usado em todos os cálculos de custo. |
| S01 | Consumo mensal isento para quem tem direito | 80 | kWh/mês | Oficial | F4 | Gratuidade de 100% até 80 kWh por mês para famílias do CadÚnico com renda de até meio salário mínimo por pessoa; o que passar disso é pago normalmente (página do MME, lida em 18/11/2026). BPC e o valor de R$ 810,50 (meio salário mínimo de 2026) vêm de fontes secundárias. Simplificação: não detalha tributos nem COSIP. |
| C01 | Potência do chuveiro elétrico | 5500 | W | Secundária (verificar) | F5; F6; F16 | Valor típico usado em simulações de Procel/Idec e Cemig. Outras fontes trazem valores menores (média de cerca de 4.989 W em tabela da PPH 2019; cerca de 4.000 W típicos no Sudeste, segundo a Unicamp). Ver análise de sensibilidade. Conferir a etiqueta do chuveiro da família. |
| C02 | Duração de cada banho (situação atual) | 8 | min | ESTIMADO | F5; F6; F15 | A PPH 2019 do Procel mostra 6 a 10 minutos como a duração mais comum (45,59% das residências); 8 minutos é o valor usado em estudos acadêmicos e simulações. Mudar conforme o relato da família. |
| C03 | Banhos por pessoa por dia | 1 | banhos/dia | ESTIMADO | Decisão do grupo |  |
| C04 | Dias por mês | 30 | dias | Oficial | Convenção |  |
| C05 | Geladeira (consumo mensal) | 40 | kWh/mês | ESTIMADO | F7 | Valor típico de geladeira frost free pela etiqueta Inmetro. Procel PPH-SP: 99,6% dos domicílios têm geladeira. |
| C06 | Lâmpadas: quantidade | 6 | unid. | ESTIMADO | F3 | Procel PPH-SP: média de 6,44 lâmpadas por domicílio. |
| C07 | Lâmpadas: potência média | 12 | W | ESTIMADO | F3 | Mistura de LED e fluorescente compacta (PPH-SP). |
| C08 | Lâmpadas: horas de uso por dia | 5 | h/dia | ESTIMADO | F3 | A PPH-SP mostra pico de lâmpadas acesas entre 19h e 22h. |
| C09 | TV: quantidade | 1 | unid. | ESTIMADO | F3 | PPH-SP: média de 1,35 TV por domicílio. |
| C10 | TV: potência | 100 | W | ESTIMADO | Decisão do grupo |  |
| C11 | TV: horas por dia | 5 | h/dia | ESTIMADO | F3 |  |
| C12 | Outros equipamentos (máquina de lavar, ferro, liquidificador, ventilador, carregadores, roteador) | 25 | kWh/mês | ESTIMADO | Decisão do grupo | Soma agregada. A conferir com uma conta de luz real da família no teste com usuários. |
| A01 | Duração do banho após ajuste | 5 | min | ESTIMADO | F6 | Redução de 8 para 5 minutos, exemplo usado em orientações de Procel. |
| A02 | Potência do chuveiro na posição verão | 3000 | W | Secundária (verificar) | F7; F8 | Exemplo de redução de 5.500 W para cerca de 3.000 W. A posição verão pode economizar até 30%. |
| A03 | Parcela dos banhos na posição verão | 0.4 | fração | ESTIMADO | Decisão do grupo | Depende da estação e do conforto da família. |
| A04 | Investimento | 0 | R$ | ESTIMADO | Decisão do grupo | Mudança de hábito, sem compra. |
| B01 | Fração solar (parcela da energia do chuveiro atendida pelo sol) | 0.6 | fração | ESTIMADO | F11; F13 | Escolhida para dar economia de cerca de 30% na conta total, valor citado em trabalhos da UFMG e na literatura de mercado. |
| B02 | Investimento (sistema instalado) | 12000 | R$ | ESTIMADO | F12 | Ponto médio da faixa de R$ 8 mil a R$ 16 mil citada para 3 a 4 pessoas. Obter orçamentos reais. A aba Alternativas traz a sensibilidade. |
| F01 | Potência do sistema | 1.2 | kWp | ESTIMADO | F13 | Dimensionado para cobrir cerca de 80% do consumo da família de referência. |
| F02 | Custo instalado por kWp | 6000 | R$/kWp | ESTIMADO | F13 | Faixa citada para 2 a 5 kWp: R$ 5.500 a R$ 7.000. Sistemas maiores saem mais baratos por kWp. |
| F03 | Geração por kWp | 120 | kWh/kWp/mês | ESTIMADO | F13 | Faixa citada: 110 a 134 kWh por kWp por mês, com perdas de cerca de 20%. Conferir em CRESESB para São Paulo. |
| F04 | Autoconsumo instantâneo (energia usada na hora em que é gerada) | 0.3 | fração | ESTIMADO | Decisão do grupo | Família usa mais energia à noite. O restante vai para a rede e vira crédito. |
| F05 | Custo do Fio B sobre energia compensada (2026, 60%) | 0.1 | R$/kWh | ESTIMADO | F13 | Lei 14.300: em 2026 paga-se 60% do Fio B. Faixa citada: R$ 0,07 a R$ 0,12 por kWh. Sobe nos anos seguintes. |
| F06 | Custo de disponibilidade (ligação monofásica) | 30 | kWh/mês | Oficial | F1; F13 | Mínimo faturado mesmo com geração: 30 kWh (monofásico), 50 (bifásico) ou 100 (trifásico), conforme quadro da Enel SP (REH 3.596/2026). |
| E01 | Fator de emissão médio do SIN (2025) | 0.0461 | kg CO2/kWh | Secundária (verificar) | F9 | Média anual de 2025 publicada pelo MCTI (0,0461 tCO2/MWh), citada via planilha do MCTI. Anos anteriores: 2022 0,0426; 2023 0,0385; 2024 0,0545. Em 2025 o fator mensal variou de 0,0215 a 0,0778. Confirmar na planilha do SIRENE. É fator médio; o fator marginal, usado em metodologias de projeto, tende a ser maior. |

## Período e unidades

- Consumo em kWh por mês; custos em R$ por mês; investimento em R$; retorno em anos.
- Período de referência comum às 3 alternativas: 1 mês (custos) e 10 anos (saldo acumulado), com tarifa constante, sem manutenção e sem juros.
- A conta calculada considera só a energia faturada. Não inclui bandeira tarifária (assumida verde) nem taxa de iluminação pública (COSIP).

## Dados estimados (claramente identificados)

Todo valor com tipo *ESTIMADO* é premissa do grupo: tamanho da família, duração do banho, aparelhos, fração solar do aquecedor, custos de instalação e autoconsumo do painel. A análise de sensibilidade (`docs/calculos_e_comparacao.md`) mostra quanto as conclusões mudam quando essas premissas variam.
