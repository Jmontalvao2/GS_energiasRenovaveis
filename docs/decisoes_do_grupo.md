# Decisões do grupo e justificativas

Ajuda a explicar, com as palavras do grupo, por que cada escolha foi feita.

| Decisão | Escolha do grupo | Por quê |
|---|---|---|
| Público e necessidade | Famílias de baixa renda com conta de luz alta, em São Paulo | É o público do assistente Caminho Certo (CadÚnico) e o chuveiro elétrico pesa muito na conta dessas famílias. |
| Alternativas comparadas | Hábitos, aquecimento solar de água e painel fotovoltaico | O enunciado exige pelo menos duas, com uma renovável; incluímos duas renováveis e uma sem custo. |
| Região e tarifa | São Paulo, tarifa ANEEL da distribuidora local (Enel SP) | Dados oficiais e verificáveis para uma região só. |
| Dados de consumo | Família de referência estimada com fontes públicas (Procel, EPE), marcada como estimativa | O enunciado aceita dados estimados com justificativa. A pessoa pode informar a conta real. |
| Família de referência | 4 pessoas, banho de 8 minutos | A PPH 2019 mostra 6 a 10 minutos como o mais comum. O chuveiro pesa 49%, dentro da faixa de 33% a 60% da literatura de baixa renda; a sensibilidade mostra que a conclusão se mantém. |
| Indicadores | Custo (R$ por mês, investimento e retorno), CO2 evitado e viabilidade | O enunciado pede custos, viabilidade e impactos ambientais. |
| Viabilidade | Nota alta, média ou baixa com justificativa curta; aquecimento solar em "média" | Fácil de entender; B é média porque pode ser financiado por quem tem casa própria. |
| Imóvel alugado | Rebaixa B e C para viabilidade baixa | Regra proposta durante o desenvolvimento, por depender de autorização do proprietário. **Confirmar se o grupo concorda.** |
| Integração com o assistente | Módulo Energia no menu, com a Tarifa Social como primeiro passo | A Tarifa Social depende do CadÚnico, serviço já tratado no Caminho Certo. |
| Linguagem | Bem simples, em reais primeiro e kWh como detalhe | A família entende melhor o valor em reais. |
| Forma do assistente | Python com Streamlit; botões para o fluxo e campo livre para dúvidas | Fácil de executar e testar; botões ajudam quem tem pouca prática digital. |
| IA generativa | Só para reescrever o texto, com os números fixos vindos do cálculo | Evita número errado e atende ao uso criterioso pedido no enunciado. |
| Dado informado pela família | R$ ou kWh; se não souber, usa a família de referência | Ninguém fica sem resposta. |
| Testes com usuários | Presenciais e rápidos, com 3 a 5 pessoas | Permite observar a compreensão e ajustar. |
| Repositório | Só desta disciplina, com o Caminho Certo citado como contexto | Deixa clara a contribuição de energia. |

## Perguntas que a banca pode fazer

1. **Por que o aquecimento solar demora tanto para se pagar?** Porque a economia é de cerca de R$ 50 por mês e o sistema custa cerca de R$ 12 mil. Com R$ 8 mil o retorno cai para
   13 anos, na faixa da literatura: 11 anos e 5 meses para baixa renda com Tarifa Social (Silveira e Gardolinski, 2016) e 13 anos e 5 meses em Minas Gerais (Geá et al., 2020).
2. **Por que o CO2 evitado é tão pequeno?** Porque a rede elétrica brasileira emite pouco (46 g por kWh em 2025). O ganho forte é financeiro.
3. **Os números podem estar errados?** São estimativas marcadas como tal. Tarifa, Tarifa Social e CO2 têm fonte oficial; custos de instalação precisam de orçamentos reais.
4. **A IA calcula alguma coisa?** Não. O cálculo é feito em Python. A IA, se ligada, só reescreve o texto, e o código descarta a reescrita se um número mudar.
5. **O que acontece se a pessoa perguntar algo que o assistente não sabe?** Ele diz que não sabe, indica o CRAS ou a distribuidora e registra a dúvida no Painel de Lacunas.
