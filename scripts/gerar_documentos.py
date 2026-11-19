"""Gera os documentos do repositório a partir dos dados e do código de cálculo.

Assim os números do README, das justificativas e do roteiro do vídeo são SEMPRE os mesmos
que o assistente mostra. Rode depois de mudar a planilha ou os cálculos:

    python scripts/exportar_premissas.py
    python scripts/gerar_documentos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
import calculos as c  # noqa: E402
import assistente as a  # noqa: E402

brl, num = c.brl, c.numero


def _retorno(r) -> str:
    if not r.aplicavel:
        return "não se aplica"
    if r.retorno_anos is None:
        return "não se paga"
    if r.retorno_anos == 0:
        return "imediato"
    return f"{num(r.retorno_anos)} anos"


def avaliar_ref(p: dict, tem_ts: bool):
    pf = c.perfil_referencia(p)
    pf.tem_tarifa_social = tem_ts
    return pf, {r.id: r for r in c.avaliar(pf, p)}


# ------------------------------------------------------------------ sensibilidade
CASOS = [
    ("Caso base (planilha)", {}, None),
    ("Chuveiro de 4.000 W", {"C01": 4000}, None),
    ("Chuveiro de 5.000 W", {"C01": 5000}, None),
    ("Banho de 6 minutos", {"C02": 6}, None),
    ("Banho de 10 minutos", {"C02": 10}, None),
    ("3 pessoas na casa", {}, 3),
    ("5 pessoas na casa", {}, 5),
    ("Tarifa 10% maior", {"T03": 0.10}, None),
    ("Aquecedor solar a R$ 8 mil", {"B02": 8000}, None),
    ("Aquecedor solar a R$ 16 mil", {"B02": 16000}, None),
    ("Fração solar de 50%", {"B01": 0.5}, None),
    ("Fração solar de 70%", {"B01": 0.7}, None),
    ("Geração de 105 kWh/kWp (litoral do Sudeste)", {"F03": 105}, None),
    ("Fotovoltaico a R$ 4.500/kWp", {"F02": 4500}, None),
    ("Fotovoltaico a R$ 7.000/kWp", {"F02": 7000}, None),
]


def tabela_sensibilidade(P: dict) -> tuple[str, dict]:
    linhas = ["| Caso | Consumo (kWh/mês) | Chuveiro no consumo | Economia A (R$/mês) | Economia B (R$/mês) | Retorno B (anos) | "
              "Economia C (R$/mês) | Retorno C sem Tarifa Social | Retorno C com Tarifa Social |",
              "|---|---|---|---|---|---|---|---|---|"]
    resumo = {"B": [], "C": [], "A_min": 1e9}
    for nome, over, pessoas in CASOS:
        p = dict(P); p.update(over)
        if pessoas:
            p["P01"] = pessoas
        pf, r0 = avaliar_ref(p, False)
        _, r1 = avaliar_ref(p, True)
        chuv = c.kwh_chuveiro(p, int(p["P01"]), p["C02"])
        linhas.append(f"| {nome} | {num(pf.consumo_kwh)} | {num(100 * chuv / pf.consumo_kwh, 0)}% | {brl(r0['A'].economia_mensal)} | "
                      f"{brl(r0['B'].economia_mensal)} | {_retorno(r0['B'])} | {brl(r0['C'].economia_mensal)} | "
                      f"{_retorno(r0['C'])} | {_retorno(r1['C'])} |")
        for k in ("B", "C"):
            for rr in (r0[k], r1[k]):
                if rr.retorno_anos:
                    resumo[k].append(rr.retorno_anos)
        resumo["A_min"] = min(resumo["A_min"], r0["A"].economia_mensal, r1["A"].economia_mensal)
    return "\n".join(linhas), resumo


# ------------------------------------------------------------------ documentos
def doc_dados(D: dict) -> str:
    linhas = ["# Dados utilizados, origem e premissas", "",
              f"Fonte de verdade: `data/planilha_premissas.xlsx` (aba Premissas), exportada para `data/premissas.json`. "
              f"Consulta às fontes em {D['consulta']}.", "",
              "**Tipos de dado:** *Oficial* (órgão público ou distribuidora), *Secundária (verificar)* (imprensa, blog ou site comercial que "
              "reproduz dado oficial), *ESTIMADO* (premissa da equipe, justificada) e *Calculado*.", "",
              "| ID | Parâmetro | Valor | Unidade | Tipo | Fonte | Observação |", "|---|---|---|---|---|---|---|"]
    for id_, v in D["premissas"].items():
        valor = v["valor"]
        valor = f"{valor:g}" if isinstance(valor, (int, float)) else str(valor)
        linhas.append(f"| {id_} | {v['rotulo']} | {valor} | {v['unidade']} | {v['tipo']} | {v['fonte']} | {v['observacao'] or ''} |")
    linhas += ["", "## Período e unidades", "",
               "- Consumo em kWh por mês; custos em R$ por mês; investimento em R$; retorno em anos.",
               f"- Período de referência comum às 3 alternativas: 1 mês (custos) e {int(D['premissas']['P02']['valor'])} anos (saldo acumulado), "
               "com tarifa constante, sem manutenção e sem juros.",
               "- A conta calculada considera só a energia faturada. Não inclui bandeira tarifária (assumida verde) nem taxa de iluminação pública (COSIP).",
               "", "## Dados estimados (claramente identificados)", "",
               "Todo valor com tipo *ESTIMADO* é premissa do grupo: tamanho da família, duração do banho, aparelhos, fração solar do aquecedor, "
               "custos de instalação e autoconsumo do painel. A análise de sensibilidade (`docs/calculos_e_comparacao.md`) mostra quanto as "
               "conclusões mudam quando essas premissas variam."]
    return "\n".join(linhas) + "\n"


def doc_calculos(D: dict, P: dict) -> str:
    t = c.tarifa_com_tributos(P)
    pf0, r0 = avaliar_ref(P, False)
    pf1, r1 = avaliar_ref(P, True)
    chuv = c.kwh_chuveiro(P, int(P["P01"]), P["C02"])
    demais = pf0.consumo_kwh - chuv
    sens, resumo = tabela_sensibilidade(P)

    def tab(r):
        linhas = ["| Cenário | Consumo da rede (kWh/mês) | Energia faturada (kWh/mês) | Custo mensal | Economia mensal | Investimento | Retorno | Saldo em "
                  f"{int(P['P02'])} anos | CO2 evitado (kg/ano) | Viabilidade |", "|---|---|---|---|---|---|---|---|---|---|"]
        for k in ("base", "A", "B", "C"):
            x = r[k]
            linhas.append(f"| {x.nome} | {num(x.consumo_kwh)} | {num(x.energia_faturada_kwh)} | {brl(x.custo_mensal)} | {brl(x.economia_mensal)} | "
                          f"{brl(x.investimento)} | {_retorno(x) if k != 'base' else '-'} | {brl(x.saldo_horizonte)} | {num(x.co2_kg_ano, 0)} | {x.viabilidade} |")
        return "\n".join(linhas)

    return f"""# Cálculos e comparação das alternativas

Mesma necessidade (reduzir a conta de luz de uma família de baixa renda de São Paulo), mesmo período de referência (1 mês e {int(P['P02'])} anos)
e mesmos indicadores para as 3 alternativas. As fórmulas estão em `src/calculos.py` e, em planilha, em `data/planilha_premissas.xlsx`
(abas Consumo e Alternativas). Os testes automáticos conferem o código contra a planilha.

## 1. Conceitos aplicados

- **Energia (kWh)** = potência (kW) x tempo (h). O consumo de cada aparelho vem dessa fórmula.
- **Potência** é a taxa de uso de energia: um chuveiro de {num(P['C01'], 0)} W usa {num(P['C01'] / 1000, 1)} kWh a cada hora ligado.
- **Eficiência energética:** gastar menos kWh para o mesmo serviço (banho mais curto, posição verão).
- **Fontes renováveis:** energia solar térmica (aquece a água) e solar fotovoltaica (gera eletricidade).
- **Custo mensal** = (kWh faturados - kWh isentos pela Tarifa Social) x tarifa com tributos.
- **Retorno do investimento (anos)** = investimento / (economia por mês x 12).
- **CO2 evitado** = kWh evitados por mês x 12 x fator de emissão da rede.

## 2. Tarifa (São Paulo, Enel SP, residencial B1)

(TUSD {num(P['T01'], 5)} + TE {num(P['T02'], 5)}) = R$ {num(P['T01'] + P['T02'], 5)} por kWh sem tributos
(Resolução Homologatória ANEEL nº 3.596/2026, em vigor desde 04/07/2026). Com carga tributária efetiva de {num(P['T04'] * 100)}%
(consumo até 200 kWh), a tarifa usada é **{brl(t)} por kWh**.

## 3. Consumo da família de referência (4 pessoas)

- Chuveiro: {int(P['P01'])} pessoas x 1 banho x {num(P['C01'], 0)} W x {num(P['C02'], 0)} min x {num(P['C04'], 0)} dias = **{num(chuv)} kWh/mês**.
- Demais equipamentos (geladeira, lâmpadas, TV, outros): **{num(demais)} kWh/mês**.
- Total: **{num(pf0.consumo_kwh)} kWh/mês**, com o chuveiro em **{num(100 * chuv / pf0.consumo_kwh, 0)}%** do consumo.

*Por que o chuveiro pesa tanto?* Na literatura sobre casas de baixa renda, o chuveiro responde por 33% a 40% do consumo em medições em Florianópolis
(Silva et al., 2014) e por 60% em uma simulação no Rio de Janeiro com chuveiro de 5.400 W, 4 pessoas e banhos de 10 minutos (Silveira e Gardolinski, 2016).
A família de referência fica no meio dessa faixa. A média nacional de 24% citada pelo Procel (2005) inclui casas com muitos outros aparelhos; a nossa tem poucos
(sem ar-condicionado, sem micro-ondas, uma TV) e todos tomam banho elétrico por 8 minutos, a faixa mais comum na PPH 2019 (6 a 10 minutos). O consumo anual do
chuveiro da família ({num(chuv * 12, 0)} kWh) está abaixo da mediana de 1.646 kWh por ano dos nove estudos reunidos por Santos e Morais (2025). Ou seja, a participação
alta vem do consumo total baixo, e não de um chuveiro superestimado. A análise de sensibilidade abaixo mostra que as conclusões não dependem desse ponto.
No uso real, o assistente pede a conta de luz da própria família.

## 4. Alternativas comparadas

- **A) Eficiência e hábitos:** banho de {num(P['A01'], 0)} min e {num(P['A03'] * 100, 0)}% dos banhos na posição verão ({num(P['A02'], 0)} W). Investimento {brl(P['A04'])}.
- **B) Aquecimento solar de água (renovável):** o sol atende {num(P['B01'] * 100, 0)}% da energia do chuveiro. Investimento de {brl(P['B02'])}.
- **C) Painel fotovoltaico (renovável):** {num(r0['C'].potencia_kwp)} kWp x {num(P['F03'], 0)} kWh/kWp/mês = {num(r0['C'].potencia_kwp * P['F03'])} kWh/mês,
  com mínimo de {num(P['F06'], 0)} kWh faturados e Fio B de {brl(P['F05'])} por kWh compensado. Investimento de {brl(r0['C'].investimento)}.

### Cenário 1: sem Tarifa Social

{tab(r0)}

### Cenário 2: com Tarifa Social (80 kWh isentos)

{tab(r1)}

Na alternativa C, o cenário 2 é uma hipótese: não encontramos fonte oficial dizendo se quem tem Tarifa Social mantém o benefício com geração própria.
O assistente pede para confirmar com a distribuidora.

## 5. Análise de sensibilidade

Cada linha muda uma premissa e recalcula tudo com o mesmo código do assistente.

{sens}

**Leitura dos resultados**

- A economia da alternativa A é positiva em todos os casos (mínimo de {brl(resumo['A_min'])} por mês) e não exige compra.
- O retorno do aquecimento solar (B) fica entre {num(min(resumo['B']))} e {num(max(resumo['B']))} anos nos casos testados, {"acima dos " + str(int(P['P02'])) + " anos de referência em todos eles" if min(resumo['B']) > P['P02'] else "acima dos " + str(int(P['P02'])) + " anos de referência em parte deles"}.
- O retorno do painel fotovoltaico (C) fica entre {num(min(resumo['C']))} e {num(max(resumo['C']))} anos, o menor de todos, mas exige imóvel próprio e um investimento alto.
- A ordem de recomendação (A primeiro; B e C só com imóvel próprio e orçamentos reais) não muda nos casos testados.

## 6. Limitações dos cálculos

- Tarifa, bandeira, impostos e regras mudam; usamos tarifa constante, sem manutenção e sem juros.
- Custos de instalação vêm de fontes comerciais e precisam de orçamentos reais. A faixa de R$ 5.500 a R$ 7.000 por kWp vale para sistemas de 2 a 5 kWp; nosso sistema de {num(r0['C'].potencia_kwp)} kWp é menor, e sistemas pequenos tendem a custar mais por kWp.
- O fator de emissão usado é a média da rede de 2025; fatores marginais, usados em metodologias de projeto, tendem a ser maiores.
- Não quantificamos impactos de fabricação e descarte de painéis e coletores.
- Valores são estimativas, não garantias de economia, geração ou custo.
"""


def doc_justificativas(D: dict, P: dict) -> str:
    pf0, r0 = avaliar_ref(P, False)
    pf1, r1 = avaliar_ref(P, True)
    A0, B0, C0 = r0["A"], r0["B"], r0["C"]
    A1, B1, C1 = r1["A"], r1["B"], r1["C"]
    return f"""# Justificativas das recomendações

Custo, viabilidade e impacto ambiental de cada alternativa, para a família de referência (4 pessoas, {num(pf0.consumo_kwh)} kWh/mês, São Paulo).
Os números abaixo são os mesmos que o assistente mostra (gerados por `src/calculos.py`).

## Recomendação principal do assistente

**Começar pela alternativa A (hábitos).** Economiza cerca de {brl(A0.economia_mensal)} por mês sem comprar nada, vale para casa alugada ou própria e
é a única com retorno imediato. B e C só entram na decisão de quem é dono do imóvel, tem como investir e comparou orçamentos.

## A) Eficiência e hábitos

- **Custo:** investimento de {brl(A0.investimento)}. Economia de {brl(A0.economia_mensal)} por mês ({num(A0.kwh_evitados)} kWh), igual com ou sem Tarifa Social
  enquanto o consumo ficar acima de {num(P['S01'], 0)} kWh. Saldo em {int(P['P02'])} anos: {brl(A0.saldo_horizonte)}.
- **Viabilidade: {A0.viabilidade}.** {A0.justificativa}
- **Impacto ambiental:** evita cerca de {num(A0.co2_kg_ano, 0)} kg de CO2 por ano.
- **Por que recomendar:** é a opção sem risco financeiro e a mais rápida. A condição é a mudança de hábito, que o assistente apresenta de forma concreta
  (banho de {num(P['A01'], 0)} minutos e posição verão).

## B) Aquecimento solar de água (fonte renovável)

- **Custo:** investimento de {brl(B0.investimento)} (faixa citada: R$ 8 mil a R$ 16 mil). Economia de {brl(B0.economia_mensal)} por mês. Retorno de
  {_retorno(B0)}, e o saldo em {int(P['P02'])} anos é {brl(B0.saldo_horizonte)} (negativo: o sistema só se paga depois do horizonte). A literatura traz retornos de 11 a 13,5 anos: 137 meses (11 anos e 5 meses) para uma família de baixa renda com
  Tarifa Social no Rio de Janeiro (Silveira e Gardolinski, 2016, citado em artigo da ANTAC) e 13 anos e 5 meses para uma casa em Minas Gerais com sistema de R$ 5.840 em 2020
  (Geá et al., 2020), com vida útil de 20 a 25 anos. Nosso retorno no caso base é maior porque usamos o ponto médio da faixa de R$ 8 mil a R$ 16 mil e esta família economiza
  {brl(B0.economia_mensal)} por mês; com R$ 8 mil o retorno cai para {_retorno(avaliar_ref(dict(P, B02=8000), False)[1]['B'])}, na faixa da literatura.
- **Viabilidade: {B0.viabilidade}.** {B0.justificativa}
- **Impacto ambiental:** evita cerca de {num(B0.co2_kg_ano, 0)} kg de CO2 por ano, um pouco mais que a alternativa A.
- **Por que não é a primeira recomendação:** o investimento é alto para a renda e o retorno passa do horizonte. Faz sentido para quem tem casa própria e
  acesso a financiamento ou programa de apoio.

## C) Painel solar fotovoltaico (fonte renovável)

- **Custo:** investimento de {brl(C0.investimento)} para {num(C0.potencia_kwp)} kWp. Economia de {brl(C0.economia_mensal)} por mês sem Tarifa Social
  (retorno de {_retorno(C0)}) e de {brl(C1.economia_mensal)} por mês com Tarifa Social (retorno de {_retorno(C1)}), porque a Tarifa Social já zera os primeiros
  {num(P['S01'], 0)} kWh. Saldo em {int(P['P02'])} anos: {brl(C0.saldo_horizonte)} e {brl(C1.saldo_horizonte)}.
- **Viabilidade: {C0.viabilidade}.** {C0.justificativa} A conta nunca zera: há o mínimo de {num(P['F06'], 0)} kWh e o Fio B. O retorno em anos é o menor dos três; o que pesa é o investimento e a exigência de imóvel próprio.
- **Impacto ambiental:** evita cerca de {num(C0.co2_kg_ano, 0)} kg de CO2 por ano, o maior dos três, e ainda assim pequeno porque a rede brasileira emite pouco.
- **Por que não é a primeira recomendação:** o menor retorno em anos não elimina o obstáculo do investimento inicial de {brl(C0.investimento)}, a exigência de imóvel próprio e telhado adequado e a
  incerteza sobre manter a Tarifa Social com geração própria.

## Comparação final

| Critério | A) Hábitos | B) Aquecimento solar | C) Fotovoltaico |
|---|---|---|---|
| Economia por mês (sem Tarifa Social) | {brl(A0.economia_mensal)} | {brl(B0.economia_mensal)} | {brl(C0.economia_mensal)} |
| Investimento | {brl(A0.investimento)} | {brl(B0.investimento)} | {brl(C0.investimento)} |
| Retorno | {_retorno(A0)} | {_retorno(B0)} | {_retorno(C0)} |
| CO2 evitado (kg/ano) | {num(A0.co2_kg_ano, 0)} | {num(B0.co2_kg_ano, 0)} | {num(C0.co2_kg_ano, 0)} |
| Viabilidade | {A0.viabilidade} | {B0.viabilidade} | {C0.viabilidade} |

Coerência com a literatura: estudos de casas de baixa renda em Pelotas (RS) e Itajubá (MG) também acharam o painel fotovoltaico mais atrativo que o aquecimento solar, e
o segundo trabalho aponta que as adaptações da casa encarecem o aquecimento solar (Santos e Morais, 2025).

## Sobre o impacto ambiental

O CO2 evitado é pequeno nas três alternativas porque a eletricidade do Brasil é, em grande parte, de fonte renovável: o fator médio da rede foi
de {num(P['E01'] * 1000, 1)} g de CO2 por kWh em 2025. O assistente diz isso à família em vez de exagerar o ganho ambiental. O argumento mais forte para a
família é financeiro. Não medimos impactos de fabricação e descarte de equipamentos (limitação registrada).

## Condições e limitações das recomendações

Estimativas, não garantias. Dependem da tarifa e da bandeira do mês, do consumo real da família, de orçamentos reais e das regras da distribuidora.
A família com Tarifa Social deve confirmar com a distribuidora se mantém o benefício ao instalar painel solar.
"""


def doc_integracao(D: dict) -> str:
    return """# Como a análise sustenta as respostas do assistente

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
"""


def doc_referencias(D: dict) -> str:
    linhas = ["# Referências utilizadas", "",
              f"Consultadas em {D['consulta']}. O tipo indica o grau de confiança; fontes *secundárias* devem ser conferidas na fonte oficial antes de uma decisão real.", ""]
    for id_, f in D["fontes"].items():
        linhas.append(f"**{id_}.** {f['fonte']}. {f['link']}. Tipo: {f['tipo']}. Uso no projeto: {f['uso']}. Verificação em 18/11/2026: {f.get('verificacao') or 'não registrada'}." + (f" Ação: {f['acao']}" if f.get("acao") else ""))
        linhas.append("")
    return "\n".join(linhas)


def roteiro_video(D: dict, P: dict) -> str:
    pf0, r0 = avaliar_ref(P, False)
    pf1, r1 = avaliar_ref(P, True)
    chuv = c.kwh_chuveiro(P, int(P["P01"]), P["C02"])
    A, B, C = r0["A"], r0["B"], r0["C"]
    cena = [
        ("0:00 a 0:20", "Público e necessidade", "app, passo 1 (Tarifa Social).",
         f"Este é o módulo de Energia do Citizen Assist AI. O público são famílias de baixa renda de São Paulo, com conta de luz alta. "
         f"A necessidade: gastar menos energia, sobretudo no banho, e saber se vale instalar energia solar."),
        ("0:20 a 0:55", "Análise de consumo", "planilha, aba Consumo.",
         f"Analisamos uma família de referência de {int(P['P01'])} pessoas. O chuveiro de {num(P['C01'], 0)} watts, usado {num(P['C02'], 0)} minutos por pessoa por dia, "
         f"gasta cerca de {num(chuv, 0)} quilowatts-hora por mês, de um total estimado de {num(pf0.consumo_kwh, 0)}. A tarifa da Enel SP é R$ {num(P['T01'] + P['T02'], 2)} por quilowatt-hora sem impostos, "
         f"R$ {num(c.tarifa_com_tributos(P), 2)} com impostos. Os dados são estimativas e vêm de fontes como Procel, ANEEL e MCTI."),
        ("0:55 a 1:35", "Comparação das alternativas", "planilha, aba Alternativas (tabela).",
         f"Comparamos três alternativas. A, hábitos: banho de {num(P['A01'], 0)} minutos e posição verão, economiza cerca de {brl(A.economia_mensal)} por mês e não custa nada. "
         f"B, aquecimento solar, fonte renovável: economiza {brl(B.economia_mensal)} por mês, mas custa cerca de {brl(B.investimento)}, com retorno perto de {num(B.retorno_anos, 0)} anos. "
         f"C, painel fotovoltaico, também renovável: economiza {brl(C.economia_mensal)} por mês, custa cerca de {brl(C.investimento)}, retorno de {num(C.retorno_anos, 0)} anos, mas exige casa própria."),
        ("1:35 a 2:25", "Demonstração do assistente", "app. Responder 'Sim' na Tarifa Social, informar a conta em reais, clicar em 'Ver minhas opções', abrir o selo de confiança, perguntar sobre o chuveiro e depois uma pergunta fora do escopo.",
         "No assistente, a família responde se tem Tarifa Social, informa o valor da conta e recebe as opções, em reais primeiro. Cada resposta traz o selo de confiança, com fonte, data e limitações, "
         "e o passo a passo do cálculo. Se a pergunta não tem informação verificada, o assistente diz que não sabe e registra a lacuna."),
        ("2:25 a 2:55", "Recomendações e limitações", "texto 'Por onde começar' e aviso de estimativa.",
         f"A recomendação é começar pelos hábitos. Aquecimento solar e painel só valem para quem é dono do imóvel e comparou orçamentos. O CO2 evitado é pequeno, cerca de {num(A.co2_kg_ano, 0)} a {num(C.co2_kg_ano, 0)} quilos por ano, "
         "porque a energia do Brasil já é muito renovável. São estimativas, não garantias, e dependem de tarifa, bandeira e regras da distribuidora."),
        ("2:55 a 3:00", "Encerramento", "repositório no GitHub.", "Código, dados, cálculos e testes estão no repositório. Obrigado."),
    ]
    palavras = sum(len(x[3].split()) for x in cena)
    linhas = ["# Roteiro do vídeo técnico (máximo de 3 minutos)", "",
              f"Vídeo **não listado** no YouTube, com **no máximo 3 minutos**. O texto abaixo tem cerca de {palavras} palavras de fala, "
              f"o que dá uns {palavras / 150:.1f} minutos falando em ritmo calmo (150 palavras por minuto), e o resto do tempo é para a demonstração na tela. "
              "Os números são os do assistente (gerados por `scripts/gerar_documentos.py`).", "",
              "Checklist do enunciado: público e necessidade | análise de consumo e comparação com a fonte renovável | demonstração das funcionalidades de energia | "
              "principais recomendações e limitações.", ""]
    for t, titulo, tela, fala in cena:
        linhas += [f"## {t}: {titulo}", f"**Na tela:** {tela}", "", f"**Fala:** {fala}", ""]
    linhas += ["## Dicas de gravação", "",
               "- Grave a tela do app já rodando (`streamlit run app.py`) e use a mesma entrada do roteiro para os números baterem.",
               "- Confira no cronômetro: o vídeo não pode passar de 3 minutos.",
               "- Publique como **não listado** e teste o link em janela anônima antes de enviar.",
               "- Não mostre CPF, telefone, nome de terceiros nem conta de luz real com dados pessoais."]
    return "\n".join(linhas) + "\n"


def readme(D: dict, P: dict) -> str:
    pf0, r0 = avaliar_ref(P, False)
    pf1, r1 = avaliar_ref(P, True)
    A, B, C = r0["A"], r0["B"], r0["C"]
    return f"""# Citizen Assist AI | Módulo Energia e Sustentabilidade

Contribuição da disciplina **Soluções em Energias Renováveis e Sustentáveis** (Ciência da Computação, turma 1CC) ao desafio Global Solution
Citizen Assist AI. O módulo orienta famílias de baixa renda de São Paulo a gastar menos energia, com cálculos, fontes verificáveis e limites claros.

## Integrantes

| Nome completo | RM |
|---|---|
| [PREENCHER] | [PREENCHER] |
| [PREENCHER] | [PREENCHER] |

Vídeo técnico (YouTube, não listado): [PREENCHER: link]

## Público e problema

- **Público:** famílias de baixa renda de São Paulo (capital e região atendida pela Enel SP) com conta de luz alta. Muitas estão no CadÚnico,
  o mesmo público do assistente Caminho Certo, que leva o cidadão do "não sei por onde começar" ao serviço público resolvido.
- **Necessidade energética:** reduzir o gasto com eletricidade, em que o chuveiro elétrico costuma pesar muito, e saber se aquecimento solar ou painel
  fotovoltaico valem a pena. Na família de referência (4 pessoas) o chuveiro responde por cerca de {num(100 * c.kwh_chuveiro(P, int(P['P01']), P['C02']) / pf0.consumo_kwh, 0)}% de {num(pf0.consumo_kwh)} kWh/mês.
- **Como as orientações contribuem:** a família informa a conta (em R$ ou kWh) e recebe, em linguagem simples e com reais primeiro, quanto pode economizar
  com cada alternativa, quanto custa e em quanto tempo se paga, com fonte e limitações.

## Funcionalidades de energia

1. **Tarifa Social primeiro:** orienta sobre a gratuidade de até {num(P['S01'], 0)} kWh por mês para famílias do CadÚnico com renda de até meio salário mínimo por pessoa.
2. **Análise a partir da conta:** a pessoa informa R$ ou kWh; se não souber, o assistente usa a família de referência.
3. **Comparação de 3 alternativas** para a mesma necessidade: hábitos, aquecimento solar de água e painel fotovoltaico (duas renováveis).
4. **Indicadores:** economia mensal em R$, investimento, retorno em anos, saldo em {int(P['P02'])} anos, CO2 evitado e viabilidade (alta, média ou baixa).
5. **Selo de confiança** em toda resposta: fonte, data de consulta e limitações; passo a passo "Como calculamos"; lista completa de fontes.
6. **Campo livre para dúvidas**, respondido só com informação verificada. Sem fonte, o assistente diz que não sabe e registra a lacuna (Painel de Lacunas).
7. **Feedback** de quem testa (clareza e utilidade), guardado sem dados pessoais.
8. **IA generativa opcional:** só reescreve o texto em linguagem simples; uma trava descarta a reescrita se qualquer número mudar.

## Resultados para a família de referência

Tarifa: R$ {num(c.tarifa_com_tributos(P), 4)} por kWh (Enel SP, B1, com tributos, bandeira verde). Sem Tarifa Social, a energia custa {brl(r0['base'].custo_mensal)} por mês.

| Alternativa | Economia por mês | Investimento | Retorno | CO2 evitado (kg/ano) | Viabilidade |
|---|---|---|---|---|---|
| A) Hábitos (banho de {num(P['A01'], 0)} min + posição verão) | {brl(A.economia_mensal)} | {brl(A.investimento)} | {_retorno(A)} | {num(A.co2_kg_ano, 0)} | {A.viabilidade} |
| B) Aquecimento solar de água | {brl(B.economia_mensal)} | {brl(B.investimento)} | {_retorno(B)} | {num(B.co2_kg_ano, 0)} | {B.viabilidade} |
| C) Painel fotovoltaico ({num(C.potencia_kwp)} kWp) | {brl(C.economia_mensal)} | {brl(C.investimento)} | {_retorno(C)} | {num(C.co2_kg_ano, 0)} | {C.viabilidade} |

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
"""


def gerar(destino: Path = RAIZ) -> list[Path]:
    D = c.carregar_dados()
    P = c.valores(D)
    docs = destino / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    arquivos = {
        destino / "README.md": readme(D, P),
        docs / "dados_e_premissas.md": doc_dados(D),
        docs / "calculos_e_comparacao.md": doc_calculos(D, P),
        docs / "justificativas_recomendacoes.md": doc_justificativas(D, P),
        docs / "integracao_assistente.md": doc_integracao(D),
        docs / "referencias.md": doc_referencias(D),
        docs / "roteiro_video.md": roteiro_video(D, P),
    }
    for caminho, texto in arquivos.items():
        caminho.write_text(texto, encoding="utf-8")
    return list(arquivos)


if __name__ == "__main__":
    for arq in gerar():
        print("gerado:", arq.relative_to(RAIZ))
