"""Cálculos de energia do Citizen Assist AI.

Reproduz, em Python, as mesmas fórmulas da planilha data/planilha_premissas.xlsx
(abas Consumo e Alternativas). Nenhum número daqui vem de IA generativa: tudo
sai de fórmulas simples sobre as premissas de data/premissas.json.

Conceitos usados:
- Energia (kWh) = potência (kW) x tempo (h).
- Custo = kWh faturados x tarifa com tributos (R$/kWh).
- Retorno do investimento (anos) = investimento / economia anual.
- CO2 evitado = kWh evitados x fator de emissão do sistema elétrico.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_PREMISSAS = RAIZ / "data" / "premissas.json"


# ---------------------------------------------------------------- premissas
def carregar_dados(caminho: Path = CAMINHO_PREMISSAS) -> dict:
    """Lê o JSON exportado da planilha (premissas + fontes)."""
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def valores(dados: dict) -> dict:
    """Atalho: id da premissa -> valor numérico."""
    return {k: v["valor"] for k, v in dados["premissas"].items()}


# ---------------------------------------------------------------- tarifa
def tarifa_com_tributos(p: dict) -> float:
    """R$/kWh com tributos: ((TUSD + TE) x (1 + reajuste) + bandeira) / (1 - tributos)."""
    base = (p["T01"] + p["T02"]) * (1 + p["T03"]) + p["T05"]
    return base / (1 - p["T04"])


# ---------------------------------------------------------------- perfil
@dataclass
class Perfil:
    """Situação da família que será avaliada."""
    consumo_kwh: float            # consumo mensal total (kWh)
    pessoas: int
    chuveiro_eletrico: bool
    minutos_banho: float
    tem_tarifa_social: bool
    imovel_proprio: bool
    origem_consumo: str = "referencia"   # 'referencia' | 'kwh' | 'reais'


def kwh_chuveiro(p: dict, pessoas: int, minutos: float, potencia_w: Optional[float] = None) -> float:
    """kWh/mês do chuveiro: banhos/dia x potência (kW) x horas por banho x dias."""
    pot = p["C01"] if potencia_w is None else potencia_w
    return pessoas * p["C03"] * (pot / 1000) * (minutos / 60) * p["C04"]


def consumo_demais_referencia(p: dict) -> float:
    """Geladeira + lâmpadas + TV + outros da família de referência (kWh/mês)."""
    lampadas = p["C06"] * p["C07"] / 1000 * p["C08"] * p["C04"]
    tv = p["C09"] * p["C10"] / 1000 * p["C11"] * p["C04"]
    return p["C05"] + lampadas + tv + p["C12"]


def perfil_referencia(p: dict) -> Perfil:
    """Família de referência da planilha: 4 pessoas, banho de 8 min, ~178,8 kWh/mês."""
    pessoas = int(p["P01"])
    total = kwh_chuveiro(p, pessoas, p["C02"]) + consumo_demais_referencia(p)
    return Perfil(consumo_kwh=total, pessoas=pessoas, chuveiro_eletrico=True,
                  minutos_banho=p["C02"], tem_tarifa_social=False,
                  imovel_proprio=True, origem_consumo="referencia")


def converter_reais_em_kwh(valor_reais: float, tem_tarifa_social: bool, p: dict) -> float:
    """Estima kWh a partir do valor da conta (R$).

    Simplificação: a conta tem também taxa de iluminação, bandeira e outros itens,
    então o resultado é aproximado e tende a superestimar o consumo.
    Com Tarifa Social, os primeiros kWh isentos não aparecem no valor pago.
    """
    t = tarifa_com_tributos(p)
    kwh = valor_reais / t
    if tem_tarifa_social and valor_reais > 0:
        kwh += p["S01"]
    return kwh


# ---------------------------------------------------------------- resultado
@dataclass
class Resultado:
    id: str                       # 'base' | 'A' | 'B' | 'C'
    nome: str
    aplicavel: bool
    consumo_kwh: float
    energia_faturada_kwh: float
    custo_mensal: float
    economia_mensal: float
    investimento: float
    retorno_anos: Optional[float]  # None = sem retorno; 0.0 = imediato
    saldo_horizonte: float
    kwh_evitados: float
    co2_kg_ano: float
    viabilidade: str
    justificativa: str
    potencia_kwp: Optional[float] = None
    nota: str = ""


NOMES = {
    "base": "Situação atual",
    "A": "A) Eficiência e hábitos",
    "B": "B) Aquecimento solar de água",
    "C": "C) Painel fotovoltaico",
}


def _viabilidade(id_: str, imovel_proprio: bool) -> tuple[str, str]:
    if id_ == "A":
        return "Alta", ("Sem custo de compra; vale para casa alugada ou própria; "
                        "depende de mudar o hábito de banho.")
    if id_ == "B":
        if imovel_proprio:
            return "Média", ("Viável para quem tem casa própria e telhado, com possível financiamento; "
                             "custo inicial alto para a renda e instalação especializada.")
        return "Baixa", ("Imóvel alugado: depende de autorização do proprietário e o investimento "
                         "pode não se pagar antes de a família se mudar.")
    if id_ == "C":
        if imovel_proprio:
            return "Baixa", ("Investimento alto para a renda; precisa de telhado adequado e homologação na "
                             "distribuidora; Fio B crescente; Tarifa Social com geração própria não confirmada.")
        return "Baixa", ("Imóvel alugado: precisa de autorização do proprietário, de telhado adequado "
                         "e de homologação na distribuidora.")
    return "-", "Situação de referência."


def avaliar(perfil: Perfil, p: dict) -> list[Resultado]:
    """Compara situação atual e alternativas A, B e C para um mesmo perfil."""
    tarifa = tarifa_com_tributos(p)
    isencao = p["S01"] if perfil.tem_tarifa_social else 0.0
    anos = p["P02"]
    fe = p["E01"]
    disp = p["F06"]

    # separa o consumo em chuveiro e demais equipamentos
    if perfil.chuveiro_eletrico:
        chuv = min(kwh_chuveiro(p, perfil.pessoas, perfil.minutos_banho), perfil.consumo_kwh)
    else:
        chuv = 0.0
    demais = perfil.consumo_kwh - chuv

    def custo_simples(consumo: float) -> float:
        return max(0.0, consumo - isencao) * tarifa

    custo_base = custo_simples(perfil.consumo_kwh)
    resultados = [Resultado(
        "base", NOMES["base"], True, perfil.consumo_kwh, perfil.consumo_kwh, custo_base,
        0.0, 0.0, None, 0.0, 0.0, 0.0, "-", "Situação de referência.")]

    def montar(id_, consumo, faturada, custo, invest, aplicavel=True, kwp=None, nota=""):
        eco = custo_base - custo
        if invest == 0:
            retorno = 0.0 if eco > 0 else None
        else:
            retorno = invest / (eco * 12) if eco > 0 else None
        evit = perfil.consumo_kwh - faturada
        v, j = _viabilidade(id_, perfil.imovel_proprio)
        return Resultado(id_, NOMES[id_], aplicavel, consumo, faturada, custo, eco, invest,
                         retorno, eco * 12 * anos - invest, evit, evit * 12 * fe, v, j, kwp, nota)

    # A) eficiência e hábitos
    if perfil.chuveiro_eletrico:
        min_a = min(p["A01"], perfil.minutos_banho)
        pot_a = p["A03"] * p["A02"] + (1 - p["A03"]) * p["C01"]
        chuv_a = kwh_chuveiro(p, perfil.pessoas, min_a, potencia_w=pot_a)
        chuv_a = min(chuv_a, chuv)  # nunca piora
        cons_a = demais + chuv_a
        resultados.append(montar("A", cons_a, cons_a, custo_simples(cons_a), p["A04"]))
    else:
        resultados.append(montar("A", perfil.consumo_kwh, perfil.consumo_kwh, custo_base, 0.0, False,
                                 nota="Sem chuveiro elétrico, esta alternativa não se aplica."))

    # B) aquecimento solar de água
    if perfil.chuveiro_eletrico:
        cons_b = demais + chuv * (1 - p["B01"])
        resultados.append(montar("B", cons_b, cons_b, custo_simples(cons_b), p["B02"]))
    else:
        resultados.append(montar("B", perfil.consumo_kwh, perfil.consumo_kwh, custo_base, p["B02"], False,
                                 nota="Sem chuveiro elétrico, esta alternativa não se aplica."))

    # C) painel fotovoltaico: dimensiona para cobrir ~80% do consumo
    kwp = round(0.8 * perfil.consumo_kwh / p["F03"], 1)
    if kwp < 0.6:
        resultados.append(montar("C", perfil.consumo_kwh, perfil.consumo_kwh, custo_base,
                                 0.0, False, nota="Consumo baixo demais para compensar um sistema solar."))
    else:
        ger = kwp * p["F03"]
        faturada = max(perfil.consumo_kwh - ger, disp)
        injetada_compensada = max(0.0, min(ger * (1 - p["F04"]), perfil.consumo_kwh - ger * p["F04"]))
        custo_c = max(0.0, faturada - isencao) * tarifa + p["F05"] * injetada_compensada
        resultados.append(montar("C", perfil.consumo_kwh, faturada, custo_c, kwp * p["F02"], True, kwp=kwp))
    return resultados


# ---------------------------------------------------------------- formatação pt-BR
def brl(valor: float) -> str:
    s = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{'-' if valor < 0 else ''}R$ {s}"


def numero(valor: float, casas: int = 1) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
