"""Lógica do assistente de energia do Citizen Assist AI.

Princípios (ver README):
1. Os NÚMEROS vêm sempre de calculos.py e das premissas verificadas.
2. A IA generativa, se ligada, só reescreve o texto em linguagem simples
   e uma trava descarta a reescrita se qualquer número mudar.
3. Toda resposta traz fonte, data de verificação e limitações (selo de confiança).
4. Se não há informação verificada, o assistente diz que não sabe e registra a lacuna.
"""
from __future__ import annotations

import csv
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

from calculos import (Resultado, Perfil, brl, kwh_chuveiro, numero, tarifa_com_tributos, valores)

RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_LACUNAS = RAIZ / "data" / "lacunas.csv"

AVISO_ESTIMATIVA = ("Estas são estimativas, não garantias de economia, geração ou custo. "
                    "Tarifa, bandeira, impostos e regras da distribuidora podem mudar.")


# ---------------------------------------------------------------- selo de confiança
def listar_fontes(dados: dict, ids: Optional[list[str]] = None) -> str:
    """Todas as referências usadas, com link e tipo (oficial, secundária, acadêmica)."""
    linhas = []
    for id_, f in dados["fontes"].items():
        if ids and id_ not in ids:
            continue
        linhas.append(f"- **{id_}** {f['fonte']} ({f['tipo']}). {f['link']}")
    return "\n".join(linhas)


def selo_confianca(dados: dict, ids_fontes: Optional[list[str]] = None) -> str:
    """Texto com fontes, data de verificação e limitações."""
    fontes = dados["fontes"]
    ids = ids_fontes or ["F1", "F2", "F4", "F9", "F13"]
    linhas = [f"**Selo de confiança** (dados consultados em {dados['consulta']})"]
    for i in ids:
        f = fontes.get(i)
        if f:
            linhas.append(f"- {f['fonte']} ({f['tipo']}). Uso: {f['uso']}.")
    linhas.append("- Limitações: " + AVISO_ESTIMATIVA)
    linhas.append("- Valores marcados como ESTIMADO na planilha são premissas do grupo, "
                  "não dados oficiais. A conta não inclui taxa de iluminação pública nem bandeira tarifária.")
    return "\n".join(linhas)


# ---------------------------------------------------------------- explicação dos resultados
def _retorno_txt(r: Resultado, horizonte: float) -> str:
    if r.retorno_anos is None:
        return "nessa conta, o investimento não se paga"
    if r.retorno_anos == 0:
        return "retorno imediato, pois não há compra"
    txt = f"o retorno leva cerca de {numero(r.retorno_anos)} anos"
    if r.retorno_anos > horizonte:
        txt += f", mais que os {numero(horizonte, 0)} anos usados na comparação"
    return txt


def explicar_resultados(resultados: list[Resultado], perfil: Perfil, dados: dict) -> str:
    """Texto principal: reais primeiro, kWh só como detalhe."""
    p = valores(dados)
    base = resultados[0]
    por_id = {r.id: r for r in resultados}
    linhas = []
    origem = {"referencia": "em uma família de referência de " + str(perfil.pessoas) + " pessoas",
              "kwh": "no consumo que você informou", "reais": "no valor de conta que você informou"}[perfil.origem_consumo]
    linhas.append(f"Pelas contas deste cálculo, com base {origem}, a energia custa cerca de "
                  f"{brl(base.custo_mensal)} por mês ({numero(base.consumo_kwh)} kWh).")
    if perfil.tem_tarifa_social:
        linhas.append(f"Já considerei a Tarifa Social: até {numero(p['S01'], 0)} kWh por mês sem cobrança de energia.")

    a, b, c = por_id["A"], por_id["B"], por_id["C"]
    if a.aplicavel:
        linhas.append(f"**A) Banho mais curto e chuveiro na posição verão (viabilidade {a.viabilidade.lower()}).** "
                      f"Você pode economizar cerca de {brl(a.economia_mensal)} por mês "
                      f"({numero(a.kwh_evitados)} kWh), sem comprar nada.")
    if b.aplicavel:
        linhas.append(f"**B) Aquecimento solar de água (viabilidade {b.viabilidade.lower()}).** "
                      f"Pode economizar cerca de {brl(b.economia_mensal)} por mês, mas o sistema custa cerca de "
                      f"{brl(b.investimento)}; {_retorno_txt(b, p['P02'])}.")
    if c.aplicavel:
        linhas.append(f"**C) Painel solar fotovoltaico de {numero(c.potencia_kwp)} kWp (viabilidade {c.viabilidade.lower()}).** "
                      f"Pode economizar cerca de {brl(c.economia_mensal)} por mês, mas o sistema custa cerca de "
                      f"{brl(c.investimento)}; {_retorno_txt(c, p['P02'])}."
                      + (" Confirme com a distribuidora se você mantém a Tarifa Social com painel solar." if perfil.tem_tarifa_social else ""))

    if a.aplicavel:
        linhas.append("**Por onde começar:** pela alternativa A, que não custa nada e vale para casa alugada ou própria.")
    if (b.aplicavel or c.aplicavel):
        if perfil.imovel_proprio:
            linhas.append("B e C só valem a pena se você for dono do imóvel, tiver como investir e comparar "
                          "pelo menos 3 orçamentos antes de decidir.")
        else:
            linhas.append("Como o imóvel é alugado, B e C dependem de autorização do proprietário e talvez não se paguem "
                          "antes de uma mudança.")
    co = [x for x in (a, b, c) if x.aplicavel]
    if co:
        partes = ", ".join(f"{numero(x.co2_kg_ano, 0)} kg ({x.id})" for x in co)
        linhas.append(f"**Impacto ambiental:** o CO2 evitado é pequeno, cerca de {partes} por ano, porque a energia "
                      "elétrica do Brasil já é em grande parte renovável. O ganho maior para a sua família é no bolso.")
    linhas.append(AVISO_ESTIMATIVA)
    return "\n\n".join(linhas)


def explicar_calculo(resultados: list[Resultado], perfil: Perfil, dados: dict) -> str:
    """Passo a passo dos números, para a pessoa (e a banca) verem como saiu cada valor."""
    p = valores(dados)
    t = tarifa_com_tributos(p)
    chuv = kwh_chuveiro(p, perfil.pessoas, perfil.minutos_banho) if perfil.chuveiro_eletrico else 0.0
    base, a, b, c = resultados
    linhas = [
        "**Como calculamos**",
        f"1. Tarifa: ({numero(p['T01'], 5)} + {numero(p['T02'], 5)}) R$/kWh sem impostos, mais impostos de "
        f"{numero(p['T04'] * 100)}%, dá {numero(t, 4)} R$/kWh.",
        f"2. Consumo usado: {numero(perfil.consumo_kwh)} kWh por mês.",
    ]
    if perfil.chuveiro_eletrico:
        linhas.append(f"3. Chuveiro: {perfil.pessoas} pessoas x 1 banho x {numero(p['C01'], 0)} W x "
                      f"{numero(perfil.minutos_banho, 0)} min x {numero(p['C04'], 0)} dias = {numero(chuv)} kWh por mês.")
    isencao = p["S01"] if perfil.tem_tarifa_social else 0
    linhas.append(f"4. Custo mensal = (kWh faturados - {numero(isencao, 0)} kWh isentos) x tarifa. "
                  f"Hoje: {brl(base.custo_mensal)}.")
    linhas.append("5. Economia = custo de hoje menos o custo com a alternativa. "
                  "Retorno (anos) = investimento / (economia por mês x 12).")
    linhas.append(f"6. CO2 evitado = kWh evitados por mês x 12 x {numero(p['E01'], 4)} kg CO2/kWh (média da rede em 2025).")
    if c.aplicavel:
        ger = c.potencia_kwp * p["F03"]
        linhas.append(f"7. Painel solar: {numero(c.potencia_kwp)} kWp x {numero(p['F03'], 0)} kWh/kWp = {numero(ger)} kWh por mês. "
                      f"Sempre se paga o mínimo de {numero(p['F06'], 0)} kWh e uma parte do Fio B ({brl(p['F05'])} por kWh compensado).")
    linhas.append("Fórmulas, fontes e premissas completas: planilha em data/planilha_premissas.xlsx.")
    return "\n\n".join(linhas)


def mensagem_tarifa_social(resposta: str, dados: dict) -> str:
    """Primeiro passo do fluxo: orientação sobre a Tarifa Social."""
    p = valores(dados)
    base = (f"A Tarifa Social zera a cobrança de energia dos primeiros {numero(p['S01'], 0)} kWh por mês "
            "para famílias do CadÚnico com renda de até meio salário mínimo por pessoa (R$ 810,50 em 2026) "
            "ou que recebem BPC. Se a família gastar mais que isso, paga só a diferença. "
            "Mantenha o cadastro atualizado, pois cadastro com divergência pode fazer a família perder o benefício. "
            "Confirme no CRAS da sua cidade ou na sua distribuidora.")
    if resposta == "sim":
        return "Ótimo, vou considerar a Tarifa Social nos cálculos. " + base
    if resposta == "nao_sei":
        return "Vale conferir se você tem direito. " + base
    return ("Sem a Tarifa Social, os cálculos usam a tarifa cheia. Se a renda da família mudar ou se você "
            "ainda não está no CadÚnico, vale perguntar no CRAS. Quem tem renda entre meio e um salário mínimo "
            "por pessoa pode ter o Desconto Social, um benefício menor (informação de fontes secundárias; "
            "confirme na distribuidora). " + base)


# ---------------------------------------------------------------- perguntas livres
def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(ch for ch in t if unicodedata.category(ch) != "Mn")


def redigir_dados_pessoais(texto: str) -> str:
    """Remove sequências longas de números (CPF, telefone, NIS) e limita o tamanho."""
    t = re.sub(r"\d[\d.\-\s]{3,}\d", "[número removido]", texto)
    return t.strip()[:200]


def registrar_lacuna(pergunta: str, caminho: Path = CAMINHO_LACUNAS) -> None:
    """Guarda perguntas sem resposta verificada (Painel de Lacunas), sem dados pessoais."""
    caminho = Path(caminho)
    novo = not caminho.exists()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["data_hora", "pergunta"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), redigir_dados_pessoais(pergunta)])


def ler_lacunas(caminho: Path = CAMINHO_LACUNAS) -> list[dict]:
    caminho = Path(caminho)
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _tem(t: str, *palavras: str) -> bool:
    return any(p in t for p in palavras)


def responder_duvida(pergunta: str, dados: dict, perfil: Optional[Perfil] = None,
                     caminho_lacunas: Path = CAMINHO_LACUNAS) -> tuple[str, list[str], bool]:
    """Responde dúvidas de energia só quando há informação verificada.

    Retorna (texto, ids_das_fontes, encontrou_resposta).
    """
    p = valores(dados)
    t = _norm(pergunta)
    tarifa = tarifa_com_tributos(p)
    pessoas = perfil.pessoas if perfil else int(p["P01"])
    minutos = perfil.minutos_banho if perfil else p["C02"]

    if _tem(t, "tarifa social", "cadunico", "cadastro unico", "bpc", "desconto na conta", "conta zerada"):
        return (f"A Tarifa Social zera a cobrança de energia dos primeiros {numero(p['S01'], 0)} kWh por mês "
                "para famílias do CadÚnico com renda de até meio salário mínimo por pessoa, ou com BPC. "
                "O que passar disso é cobrado normalmente, e taxa de iluminação e impostos seguem regra própria. "
                "Confirme seu direito no CRAS ou na sua distribuidora. " + AVISO_ESTIMATIVA, ["F4"], True)

    if _tem(t, "valor do kwh", "preco do kwh", "quanto custa o kwh", "reajuste", "tarifa da enel", "tarifa de energia", "quanto custa a energia"):
        sem_trib = (p["T01"] + p["T02"]) * (1 + p["T03"])
        return (f"Em São Paulo (Enel SP), o kWh residencial custa {brl(sem_trib)} sem impostos desde 4 de julho de 2026. "
                f"Com impostos, fica perto de {brl(tarifa)} por kWh para quem consome até 200 kWh; acima disso o ICMS é maior. "
                "A bandeira tarifária do mês e a taxa de iluminação pública entram à parte. " + AVISO_ESTIMATIVA, ["F1", "F2"], True)

    if _tem(t, "chuveiro", "banho", "posicao verao", "verao"):
        kwh_banho = (p["C01"] / 1000) * (minutos / 60)
        mensal = kwh_chuveiro(p, pessoas, minutos)
        return (f"Um chuveiro de {numero(p['C01'], 0)} W ligado por {numero(minutos, 0)} minutos gasta cerca de "
                f"{brl(kwh_banho * tarifa)} por banho ({numero(kwh_banho, 2)} kWh). Com {pessoas} pessoas tomando um banho por dia, "
                f"são cerca de {brl(mensal * tarifa)} por mês ({numero(mensal)} kWh). "
                f"Reduzir o banho para {numero(p['A01'], 0)} minutos e usar a posição verão em parte dos banhos diminui esse gasto. "
                + AVISO_ESTIMATIVA, ["F5", "F6", "F7"], True)

    if _tem(t, "aquecedor solar", "aquecimento solar", "coletor"):
        return (f"O aquecimento solar usa o sol para esquentar a água do banho. Neste cálculo, o sistema custa cerca de "
                f"{brl(p['B02'])} e atende {numero(p['B01'] * 100, 0)}% da energia do chuveiro. Para famílias de baixa renda, "
                "o retorno tende a ser longo: estudos acadêmicos acharam entre 11 e 13 anos, mesmo com Tarifa Social. "
                "Compare pelo menos 3 orçamentos. " + AVISO_ESTIMATIVA, ["F10", "F11", "F12"], True)

    if _tem(t, "fio b", "taxa minima", "disponibilidade"):
        return (f"Mesmo com painel solar, a conta não zera: existe um mínimo de {numero(p['F06'], 0)} kWh (ligação monofásica) "
                "mais a taxa de iluminação pública. Além disso, quem instala hoje paga parte do Fio B sobre a energia que "
                "injeta na rede (60% em 2026, e sobe nos anos seguintes). " + AVISO_ESTIMATIVA, ["F13"], True)

    if _tem(t, "painel", "placa solar", "fotovoltaic", "energia solar", "solar"):
        return (f"Um painel solar fotovoltaico gera energia a partir do sol e abate da sua conta. Neste cálculo, um sistema de "
                f"cerca de {numero(p['F01'])} kWp custa perto de {brl(p['F01'] * p['F02'])}. Ele exige imóvel próprio, telhado "
                "adequado e aprovação da distribuidora, e a conta não zera. " + AVISO_ESTIMATIVA, ["F13"], True)

    if _tem(t, "bandeira"):
        return ("A bandeira tarifária (verde, amarela ou vermelha) acrescenta valor por kWh e muda todo mês. "
                "Os cálculos deste assistente assumem bandeira verde, então a conta real pode ser maior. "
                "Veja a bandeira do mês na sua conta ou no site da distribuidora.", ["F2"], True)

    if _tem(t, "co2", "carbono", "ambiental", "meio ambiente", "poluic"):
        return (f"A energia elétrica do Brasil emite pouco CO2: cerca de {numero(p['E01'] * 1000, 1)} gramas por kWh em 2025, em média. "
                "Por isso, economizar energia evita pouco CO2 em números absolutos, mas ajuda o meio ambiente e o seu bolso. "
                + AVISO_ESTIMATIVA, ["F9"], True)

    if _tem(t, "geladeira", "lampada", "led", "televisao", "tv"):
        lamp = p["C06"] * p["C07"] / 1000 * p["C08"] * p["C04"]
        tv = p["C09"] * p["C10"] / 1000 * p["C11"] * p["C04"]
        return (f"Para uma família de referência, estimamos: geladeira cerca de {brl(p['C05'] * tarifa)} por mês, "
                f"lâmpadas cerca de {brl(lamp * tarifa)} e TV cerca de {brl(tv * tarifa)}. São estimativas; "
                "o chuveiro elétrico costuma pesar mais que todos esses juntos. " + AVISO_ESTIMATIVA, ["F3", "F7"], True)

    registrar_lacuna(pergunta, caminho_lacunas)
    return ("Não tenho essa informação com fonte verificada, então prefiro não arriscar uma resposta. "
            "Anotei a sua dúvida para a equipe melhorar o assistente. "
            "Procure o CRAS, a sua distribuidora de energia ou o atendimento oficial.", [], False)


# ---------------------------------------------------------------- feedback dos testes com usuários
CAMINHO_FEEDBACK = RAIZ / "data" / "feedback_testes.csv"


def registrar_feedback(clareza: str, util: str, comentario: str = "", situacao: str = "",
                       caminho: Path = CAMINHO_FEEDBACK) -> None:
    """Guarda a avaliação da orientação, sem dados pessoais (números longos são removidos)."""
    caminho = Path(caminho)
    novo = not caminho.exists()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["data_hora", "situacao", "clareza", "utilidade", "comentario"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), situacao, clareza, util,
                    redigir_dados_pessoais(comentario)])


def ler_feedback(caminho: Path = CAMINHO_FEEDBACK) -> list[dict]:
    caminho = Path(caminho)
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- IA (opcional) com trava de números
_RE_NUM = re.compile(r"\d+(?:[.,]\d+)*")

PROMPT_SISTEMA = (
    "Você reescreve textos curtos de orientação sobre energia elétrica para famílias de baixa renda do Brasil. "
    "Regras obrigatórias: (1) use português simples, frases curtas e palavras do dia a dia; "
    "(2) NÃO altere, arredonde, remova ou acrescente nenhum número, valor em reais ou unidade; "
    "(3) NÃO prometa economia garantida e mantenha os avisos de que são estimativas; "
    "(4) mantenha todos os fatos e a ordem das recomendações; (5) responda só com o texto reescrito."
)


def numeros_em(texto: str) -> set[str]:
    return set(_RE_NUM.findall(texto))


def validar_reescrita(original: str, reescrito: str) -> bool:
    """Aceita a reescrita só se os números forem exatamente os mesmos e sem promessas novas."""
    if not reescrito.strip():
        return False
    if numeros_em(original) != numeros_em(reescrito):
        return False
    o, r = _norm(original), _norm(reescrito)
    for palavra in ("garantimos", "garantido", "com certeza", "sem duvida"):
        if palavra in r and palavra not in o:
            return False
    return True


def reescrever_em_linguagem_simples(texto: str, cliente=None, modelo: Optional[str] = None) -> tuple[str, bool]:
    """Pede à IA para simplificar o texto; devolve (texto_final, usou_ia).

    Sem chave de API, sem biblioteca ou se a trava de números falhar, devolve o texto original.
    """
    if cliente is None:
        chave = os.environ.get("ANTHROPIC_API_KEY")
        if not chave:
            return texto, False
        try:
            import anthropic  # importação tardia: opcional
            cliente = anthropic.Anthropic(api_key=chave)
        except Exception:
            return texto, False
    modelo = modelo or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    try:
        resp = cliente.messages.create(model=modelo, max_tokens=1200, system=PROMPT_SISTEMA,
                                       messages=[{"role": "user", "content": texto}])
        novo = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    except Exception:
        return texto, False
    if validar_reescrita(texto, novo):
        return novo.strip(), True
    return texto, False
