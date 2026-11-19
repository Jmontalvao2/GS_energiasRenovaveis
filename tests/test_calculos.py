import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
import calculos as c  # noqa: E402


class TestCalculos(unittest.TestCase):
    def setUp(self):
        self.dados = c.carregar_dados()
        self.p = c.valores(self.dados)
        self.ref = c.perfil_referencia(self.p)

    def res(self, perfil):
        return {r.id: r for r in c.avaliar(perfil, self.p)}

    def test_tarifa_com_tributos(self):
        self.assertAlmostEqual(c.tarifa_com_tributos(self.p), 0.9431, places=4)

    def test_chuveiro_formula(self):
        # 5.500 W por 8 min = 0,7333 kWh por banho; 4 pessoas x 30 dias = 88 kWh
        self.assertAlmostEqual(c.kwh_chuveiro(self.p, 1, 8) / 30, 0.7333, places=4)
        self.assertAlmostEqual(c.kwh_chuveiro(self.p, 4, 8), 88.0, places=6)

    def test_consumo_familia_referencia(self):
        self.assertAlmostEqual(self.ref.consumo_kwh, 178.8, places=6)

    def test_alternativas_sem_tarifa_social(self):
        r = self.res(self.ref)
        self.assertAlmostEqual(r["base"].custo_mensal, 168.63, places=2)
        self.assertAlmostEqual(r["A"].economia_mensal, 40.55, places=2)
        self.assertAlmostEqual(r["B"].economia_mensal, 49.80, places=2)
        self.assertAlmostEqual(r["C"].economia_mensal, 125.73, places=2)
        self.assertAlmostEqual(r["B"].retorno_anos, 20.08, places=2)
        self.assertAlmostEqual(r["C"].retorno_anos, 4.77, places=2)
        self.assertEqual(r["A"].retorno_anos, 0.0)

    def test_alternativas_com_tarifa_social(self):
        self.ref.tem_tarifa_social = True
        r = self.res(self.ref)
        self.assertAlmostEqual(r["base"].custo_mensal, 93.18, places=2)
        self.assertAlmostEqual(r["C"].economia_mensal, 83.10, places=2)
        self.assertAlmostEqual(r["C"].retorno_anos, 7.22, places=2)

    def test_co2_e_baixo(self):
        r = self.res(self.ref)
        self.assertAlmostEqual(r["C"].co2_kg_ano, 79.66, places=2)
        self.assertLess(r["A"].co2_kg_ano, 25)

    def test_sem_chuveiro_nao_aplica_a_e_b(self):
        self.ref.chuveiro_eletrico = False
        r = self.res(self.ref)
        self.assertFalse(r["A"].aplicavel)
        self.assertFalse(r["B"].aplicavel)

    def test_consumo_muito_baixo_nao_aplica_fotovoltaico(self):
        perfil = c.Perfil(30, 1, False, 0, False, True)
        self.assertFalse(self.res(perfil)["C"].aplicavel)

    def test_imovel_alugado_reduz_viabilidade_de_b(self):
        self.ref.imovel_proprio = False
        self.assertEqual(self.res(self.ref)["B"].viabilidade, "Baixa")
        self.ref.imovel_proprio = True
        self.assertEqual(self.res(self.ref)["B"].viabilidade, "Média")

    def test_alternativa_a_nunca_piora(self):
        perfil = c.Perfil(120, 2, True, 4, False, True)  # banho já curto
        self.assertGreaterEqual(self.res(perfil)["A"].economia_mensal, 0)

    def test_converter_reais_em_kwh(self):
        self.assertAlmostEqual(c.converter_reais_em_kwh(100, False, self.p), 100 / 0.9431, places=1)
        self.assertAlmostEqual(c.converter_reais_em_kwh(100, True, self.p), 100 / 0.9431 + 80, places=1)

    def test_formatacao_pt_br(self):
        self.assertEqual(c.brl(12000), "R$ 12.000,00")
        self.assertEqual(c.numero(1234.5), "1.234,5")

    def test_igual_a_planilha(self):
        """Confere os resultados do Python com os valores calculados na planilha."""
        try:
            from openpyxl import load_workbook
        except ImportError:
            self.skipTest("openpyxl não instalado")
        wb = load_workbook(RAIZ / "data" / "planilha_premissas.xlsx", data_only=True)
        wa = wb["Alternativas"]
        blocos = {False: 8, True: 16}  # primeira linha da alternativa A em cada cenário
        for ts, linha_a in blocos.items():
            self.ref.tem_tarifa_social = ts
            r = self.res(self.ref)
            for i, id_ in enumerate(("A", "B", "C")):
                self.assertAlmostEqual(wa.cell(linha_a + i, 4).value, r[id_].custo_mensal, places=6)
                self.assertAlmostEqual(wa.cell(linha_a + i, 5).value, r[id_].economia_mensal, places=6)


if __name__ == "__main__":
    unittest.main()
