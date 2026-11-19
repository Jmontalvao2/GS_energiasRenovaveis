# Citizen Assist AI | Módulo Energia e Sustentabilidade

Contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis** (Ciência da Computação, turma 1CC) ao desafio Global Solution
Citizen Assist AI. O módulo orienta famílias de baixa renda de São Paulo a gastar menos energia, com cálculos, fontes verificáveis e limites claros.

## Integrantes

| Nome completo | RM |
|---|---|
| [Gabriel Carlos Barbosa] | [RM: 574074] |
| [Gustavo Pola Simões] | [RM: 570114] |
| [João Victor Montalvão Correia] | [RM: 571630] |

Vídeo técnico: [https://youtu.be/K4h2NK7o6Os?si=mfb4tPmRAxLm7Ter]

## Público e problema

- **Público:** famílias de baixa renda de São Paulo (capital e região atendida pela Enel SP) com conta de luz alta. Muitas estão no CadÚnico,
  o mesmo público do assistente Caminho Certo, que leva o cidadão do "não sei por onde começar" ao serviço público resolvido.
- **Necessidade energética:** reduzir o gasto com eletricidade, em que o chuveiro elétrico costuma pesar muito, e saber se aquecimento solar ou painel
  fotovoltaico valem a pena. Na família de referência (4 pessoas) o chuveiro responde por cerca de 49% de 178,8 kWh/mês.
- **Como as orientações contribuem:** a família informa a conta (em R$ ou kWh) e recebe, em linguagem simples e com reais primeiro, quanto pode economizar
  com cada alternativa, quanto custa e em quanto tempo se paga, com fonte e limitações.

## Funcionalidades de energia

1. **Tarifa Social primeiro:** orienta sobre a gratuidade de até 80 kWh por mês para famílias do CadÚnico com renda de até meio salário mínimo por pessoa.
2. **Análise a partir da conta:** a pessoa informa R$ ou kWh; se não souber, o assistente usa a família de referência.
3. **Comparação de 3 alternativas** para a mesma necessidade: hábitos, aquecimento solar de água e painel fotovoltaico (duas renováveis).
4. **Indicadores:** economia mensal em R$, investimento, retorno em anos, saldo em 10 anos, CO2 evitado e viabilidade (alta, média ou baixa).
5. **Selo de confiança** em toda resposta: fonte, data de consulta e limitações; passo a passo "Como calculamos"; lista completa de fontes.
6. **Campo livre para dúvidas**, respondido só com informação verificada. Sem fonte, o assistente diz que não sabe e registra a lacuna (Painel de Lacunas).
7. **Feedback** de quem testa (clareza e utilidade), guardado sem dados pessoais.
8. **IA generativa opcional:** só reescreve o texto em linguagem simples; uma trava descarta a reescrita se qualquer número mudar.

## Resultados para a família de referência

Tarifa: R$ 0,9431 por kWh (Enel SP, B1, com tributos, bandeira verde). Sem Tarifa Social, a energia custa R$ 168,63 por mês.

| Alternativa | Economia por mês | Investimento | Retorno | CO2 evitado (kg/ano) | Viabilidade |
|---|---|---|---|---|---|
| A) Hábitos (banho de 5 min + posição verão) | R$ 40,55 | R$ 0,00 | imediato | 24 | Alta |
| B) Aquecimento solar de água | R$ 49,80 | R$ 12.000,00 | 20,1 anos | 29 | Média |
| C) Painel fotovoltaico (1,2 kWp) | R$ 125,73 | R$ 7.200,00 | 4,8 anos | 80 | Baixa |

**Recomendação:** começar pela alternativa A. B e C só para quem tem imóvel próprio, pode investir e comparou orçamentos. Detalhes, cenário com Tarifa Social e
análise de sensibilidade em [`docs/calculos_e_comparacao.md`](docs/calculos_e_comparacao.md) e [`docs/justificativas_recomendacoes.md`](docs/justificativas_recomendacoes.md).

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opcional (IA para simplificar o texto): defina `ANTHROPIC_API_KEY` antes de rodar. Sem chave, tudo funciona normalmente.

## Como testar

```bash
python -m unittest discover -s tests -v
```

Os testes conferem fórmulas, regras do assistente, a trava de números da IA e a igualdade entre o código e a planilha.

## Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `app.py` | interface Streamlit (botões para o fluxo principal e campo livre) |
| `src/calculos.py` | cálculos de energia, custo, retorno e CO2 |
| `src/assistente.py` | respostas, selo de confiança, "não sei" honesto, feedback e trava de números |
| `data/planilha_premissas.xlsx` | dados, premissas, fontes e comparação (fonte de verdade) |
| `data/premissas.json` | exportado da planilha por `scripts/exportar_premissas.py` |
| `scripts/` | exportação de premissas e geração dos documentos |
| `tests/` | testes automáticos |
| `docs/dados_e_premissas.md` | dados usados, origem, unidades, período e o que é estimativa |
| `docs/calculos_e_comparacao.md` | fórmulas, comparação das alternativas e sensibilidade |
| `docs/justificativas_recomendacoes.md` | custo, viabilidade e impacto ambiental de cada recomendação |
| `docs/integracao_assistente.md` | como a análise sustenta cada resposta do assistente |
| `docs/referencias.md` | fontes verificáveis, com a verificação feita em 18/11/2026 |
| `docs/verificacao_das_fontes.md` | o que foi conferido página a página e o que ainda falta |
| `docs/testes_usuarios/` | roteiro, registro dos testes e ajustes realizados |
| `docs/uso_de_ia_generativa.md` | uso de IA no projeto e verificação pela equipe |
| `docs/decisoes_do_grupo.md` | decisões do grupo e justificativas |
| `docs/roteiro_video.md` | roteiro do vídeo de 3 minutos |

## Limitações

Estimativas, não garantias. Os cálculos assumem bandeira verde, tarifa constante, sem manutenção e sem juros, e não incluem a taxa de iluminação pública.
Custos de instalação precisam de orçamentos reais. Não sabemos se a Tarifa Social se mantém com geração própria: o assistente pede para confirmar com a distribuidora.
O CO2 evitado usa o fator médio da rede de 2025. Lista completa em [`docs/calculos_e_comparacao.md`](docs/calculos_e_comparacao.md).

## Testes com usuários

Roteiro, registro e ajustes em [`docs/testes_usuarios/`](docs/testes_usuarios/). Status: ver `docs/testes_usuarios/registro_testes.md`.

## Uso de IA generativa

Declarado em [`docs/uso_de_ia_generativa.md`](docs/uso_de_ia_generativa.md). A equipe é responsável por verificar dados, cálculos, referências e recomendações.
