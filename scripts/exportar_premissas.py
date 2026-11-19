"""Exporta a aba Premissas da planilha para data/premissas.json.

Mantém o código e a planilha sincronizados: a planilha é a fonte dos dados,
o JSON é o que o assistente lê. Rode depois de alterar a planilha:

    python scripts/exportar_premissas.py
"""
import json
from pathlib import Path
from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parents[1]
planilha = RAIZ / "data" / "planilha_premissas.xlsx"
saida = RAIZ / "data" / "premissas.json"

wb = load_workbook(planilha, data_only=True)
ws = wb["Premissas"]
premissas = {}
for linha in ws.iter_rows(min_row=5, values_only=True):
    id_, rotulo, valor, unidade, tipo, fonte, obs = (list(linha) + [None] * 7)[:7]
    if not id_ or valor is None:
        continue
    premissas[id_] = {
        "rotulo": rotulo, "valor": valor, "unidade": unidade,
        "tipo": tipo, "fonte": fonte, "observacao": obs,
    }

fontes = {}
for linha in wb["Fontes"].iter_rows(min_row=4, values_only=True):
    if linha[0] and str(linha[0]).startswith("F"):
        fontes[linha[0]] = {"fonte": linha[1], "link": linha[2], "tipo": linha[3],
                            "uso": linha[4], "acao": linha[5], "verificacao": linha[6]}

saida.write_text(json.dumps({"consulta": "18/11/2026", "premissas": premissas, "fontes": fontes},
                            ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(premissas)} premissas e {len(fontes)} fontes exportadas para {saida}")
