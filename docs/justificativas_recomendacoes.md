# Justificativas das recomendações

Custo, viabilidade e impacto ambiental de cada alternativa, para a família de referência (4 pessoas, 178,8 kWh/mês, São Paulo).
Os números abaixo são os mesmos que o assistente mostra (gerados por `src/calculos.py`).

## Recomendação principal do assistente

**Começar pela alternativa A (hábitos).** Economiza cerca de R$ 40,55 por mês sem comprar nada, vale para casa alugada ou própria e
é a única com retorno imediato. B e C só entram na decisão de quem é dono do imóvel, tem como investir e comparou orçamentos.

## A) Eficiência e hábitos

- **Custo:** investimento de R$ 0,00. Economia de R$ 40,55 por mês (43,0 kWh), igual com ou sem Tarifa Social
  enquanto o consumo ficar acima de 80 kWh. Saldo em 10 anos: R$ 4.866,43.
- **Viabilidade: Alta.** Sem custo de compra; vale para casa alugada ou própria; depende de mudar o hábito de banho.
- **Impacto ambiental:** evita cerca de 24 kg de CO2 por ano.
- **Por que recomendar:** é a opção sem risco financeiro e a mais rápida. A condição é a mudança de hábito, que o assistente apresenta de forma concreta
  (banho de 5 minutos e posição verão).

## B) Aquecimento solar de água (fonte renovável)

- **Custo:** investimento de R$ 12.000,00 (faixa citada: R$ 8 mil a R$ 16 mil). Economia de R$ 49,80 por mês. Retorno de
  20,1 anos, e o saldo em 10 anos é -R$ 6.024,48 (negativo: o sistema só se paga depois do horizonte). A literatura traz retornos de 11 a 13,5 anos: 137 meses (11 anos e 5 meses) para uma família de baixa renda com
  Tarifa Social no Rio de Janeiro (Silveira e Gardolinski, 2016, citado em artigo da ANTAC) e 13 anos e 5 meses para uma casa em Minas Gerais com sistema de R$ 5.840 em 2020
  (Geá et al., 2020), com vida útil de 20 a 25 anos. Nosso retorno no caso base é maior porque usamos o ponto médio da faixa de R$ 8 mil a R$ 16 mil e esta família economiza
  R$ 49,80 por mês; com R$ 8 mil o retorno cai para 13,4 anos, na faixa da literatura.
- **Viabilidade: Média.** Viável para quem tem casa própria e telhado, com possível financiamento; custo inicial alto para a renda e instalação especializada.
- **Impacto ambiental:** evita cerca de 29 kg de CO2 por ano, um pouco mais que a alternativa A.
- **Por que não é a primeira recomendação:** o investimento é alto para a renda e o retorno passa do horizonte. Faz sentido para quem tem casa própria e
  acesso a financiamento ou programa de apoio.

## C) Painel solar fotovoltaico (fonte renovável)

- **Custo:** investimento de R$ 7.200,00 para 1,2 kWp. Economia de R$ 125,73 por mês sem Tarifa Social
  (retorno de 4,8 anos) e de R$ 83,10 por mês com Tarifa Social (retorno de 7,2 anos), porque a Tarifa Social já zera os primeiros
  80 kWh. Saldo em 10 anos: R$ 7.887,28 e R$ 2.771,87.
- **Viabilidade: Baixa.** Investimento alto para a renda; precisa de telhado adequado e homologação na distribuidora; Fio B crescente; Tarifa Social com geração própria não confirmada. A conta nunca zera: há o mínimo de 30 kWh e o Fio B. O retorno em anos é o menor dos três; o que pesa é o investimento e a exigência de imóvel próprio.
- **Impacto ambiental:** evita cerca de 80 kg de CO2 por ano, o maior dos três, e ainda assim pequeno porque a rede brasileira emite pouco.
- **Por que não é a primeira recomendação:** o menor retorno em anos não elimina o obstáculo do investimento inicial de R$ 7.200,00, a exigência de imóvel próprio e telhado adequado e a
  incerteza sobre manter a Tarifa Social com geração própria.

## Comparação final

| Critério | A) Hábitos | B) Aquecimento solar | C) Fotovoltaico |
|---|---|---|---|
| Economia por mês (sem Tarifa Social) | R$ 40,55 | R$ 49,80 | R$ 125,73 |
| Investimento | R$ 0,00 | R$ 12.000,00 | R$ 7.200,00 |
| Retorno | imediato | 20,1 anos | 4,8 anos |
| CO2 evitado (kg/ano) | 24 | 29 | 80 |
| Viabilidade | Alta | Média | Baixa |

Coerência com a literatura: estudos de casas de baixa renda em Pelotas (RS) e Itajubá (MG) também acharam o painel fotovoltaico mais atrativo que o aquecimento solar, e
o segundo trabalho aponta que as adaptações da casa encarecem o aquecimento solar (Santos e Morais, 2025).

## Sobre o impacto ambiental

O CO2 evitado é pequeno nas três alternativas porque a eletricidade do Brasil é, em grande parte, de fonte renovável: o fator médio da rede foi
de 46,1 g de CO2 por kWh em 2025. O assistente diz isso à família em vez de exagerar o ganho ambiental. O argumento mais forte para a
família é financeiro. Não medimos impactos de fabricação e descarte de equipamentos (limitação registrada).

## Condições e limitações das recomendações

Estimativas, não garantias. Dependem da tarifa e da bandeira do mês, do consumo real da família, de orçamentos reais e das regras da distribuidora.
A família com Tarifa Social deve confirmar com a distribuidora se mantém o benefício ao instalar painel solar.
