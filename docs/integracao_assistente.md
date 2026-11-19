# Como a análise sustenta as respostas do assistente

Cada resposta do assistente tem origem rastreável: premissa (planilha) -> cálculo (código) -> texto -> teste automático.

| O que o assistente diz | Onde nasce | Premissas e fórmulas | Fonte | Teste |
|---|---|---|---|---|
| "Você pode ter direito à Tarifa Social: 80 kWh sem cobrança de energia" | `assistente.mensagem_tarifa_social` | S01 | F4 (MME/ANEEL) | `test_duvida_com_resposta_verificada` |
| "A energia custa cerca de R$ X por mês" | `calculos.avaliar` | T01 a T05, tarifa com tributos; custo = (kWh - isenção) x tarifa | F1, F2 | `test_alternativas_sem_tarifa_social` |
| "O banho gasta R$ X por mês" | `calculos.kwh_chuveiro` | C01 a C04; kWh = banhos x kW x h x dias | F5, F6, F15 | `test_chuveiro_formula` |
| "Alternativa A: economiza R$ X" | `calculos.avaliar` (A) | A01 a A04 | F6, F7, F8 | `test_alternativas_sem_tarifa_social`, `test_alternativa_a_nunca_piora` |
| "Alternativa B: custa R$ X, retorno de Y anos" | `calculos.avaliar` (B) | B01, B02 | F10, F11, F12 | `test_alternativas_sem_tarifa_social` |
| "Alternativa C: painel de X kWp" | `calculos.avaliar` (C) | F01 a F06 | F13, F17 | `test_alternativas_com_tarifa_social`, `test_consumo_muito_baixo_nao_aplica_fotovoltaico` |
| "O CO2 evitado é pequeno" | `calculos.avaliar` | E01 | F9 (MCTI) | `test_co2_e_baixo` |
| "Viabilidade alta, média ou baixa" | `calculos._viabilidade` | decisão do grupo | docs/justificativas_recomendacoes.md | `test_imovel_alugado_reduz_viabilidade_de_b` |
| Valor da conta (R$) vira kWh | `calculos.converter_reais_em_kwh` | tarifa e isenção | F1 | `test_converter_reais_em_kwh` |
| Selo de confiança com fonte, data e limitações | `assistente.selo_confianca` | `consulta` e fontes do JSON | todas | `test_selo_de_confianca_tem_data_fonte_e_limitacao` |
| "Não tenho essa informação" e registro da lacuna | `assistente.responder_duvida` | sem intenção reconhecida | - | `test_duvida_sem_resposta_registra_lacuna_sem_dados_pessoais` |
| Passo a passo "Como calculamos" | `assistente.explicar_calculo` | todas as usadas | planilha | `test_explicar_calculo_mostra_formulas_e_fontes` |

## Garantias do projeto

1. **Os números nunca vêm da IA.** Vêm de `calculos.py`. A IA, se ligada, só reescreve o texto em linguagem simples.
2. **Trava de números.** `assistente.validar_reescrita` descarta a reescrita se qualquer número mudar ou aparecer promessa nova
   (`test_trava_rejeita_numero_alterado_ou_promessa`).
3. **Código e planilha batem.** `test_igual_a_planilha` compara os resultados do Python com os valores calculados na planilha.
4. **"Não sei" honesto.** Sem fonte verificada, o assistente não responde e registra a dúvida no Painel de Lacunas, sem dados pessoais.
5. **Condições e limitações em toda resposta.** Texto de estimativa, selo de confiança e lista completa de fontes no app.

## Ligação com o Caminho Certo

O módulo Energia entra no menu do assistente. O primeiro passo é a Tarifa Social, que depende do CadÚnico, serviço já tratado no Caminho Certo.
O Painel de Lacunas segue a ideia do Caminho Certo: cada dúvida sem resposta verificada vira registro para a equipe corrigir.
