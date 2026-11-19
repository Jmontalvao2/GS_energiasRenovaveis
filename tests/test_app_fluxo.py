"""Executa o app.py inteiro com um Streamlit simulado, tela por tela.

Não testa a aparência. Pega erros de código e de lógica no fluxo: boas-vindas, Tarifa Social,
dados da família, resultados, dúvida, 'não sei' honesto e feedback.
"""
import runpy
import sys
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
import pandas  # noqa: E402,F401  (carrega antes, para o app não importar de novo)
import assistente  # noqa: E402
import calculos as c  # noqa: E402


class EstadoSessao(dict):
    pass


def streamlit_falso(etapa, extra=None, pergunta=""):
    st = MagicMock(name="streamlit")
    st.session_state = EstadoSessao(etapa=etapa)
    st.session_state.update(extra or {})
    st.cache_data = lambda f: f
    st.radio = MagicMock(side_effect=lambda label, options, **kw: options[0])
    st.number_input = MagicMock(side_effect=lambda *a, **kw: kw.get("value", 150.0))
    st.slider = MagicMock(side_effect=lambda label, lo, hi, val, **kw: val)
    st.text_input = MagicMock(side_effect=lambda label, **kw: pergunta if "dúvida" in label else "")
    st.columns = MagicMock(side_effect=lambda n: [MagicMock() for _ in range(n)])
    st.button = MagicMock(return_value=False)
    st.checkbox = MagicMock(return_value=False)
    st.form_submit_button = MagicMock(return_value=True)
    return st


def textos(st):
    saida = []
    for nome in ("markdown", "info", "success", "warning", "write", "caption", "subheader", "title"):
        for chamada in getattr(st, nome).call_args_list:
            saida.append(" ".join(str(a) for a in chamada.args))
    return "\n".join(saida)


class TestFluxoDoApp(unittest.TestCase):
    def rodar(self, st):
        anterior = sys.modules.get("streamlit")
        sys.modules["streamlit"] = st
        try:
            with mock.patch.object(assistente, "registrar_feedback") as fb, \
                 mock.patch.object(assistente, "registrar_lacuna") as lac, \
                 mock.patch.object(assistente, "ler_lacunas", return_value=[]), \
                 mock.patch.object(assistente, "ler_feedback", return_value=[]):
                runpy.run_path(str(RAIZ / "app.py"), run_name="__main__")
        finally:
            if anterior is None:
                sys.modules.pop("streamlit", None)
            else:
                sys.modules["streamlit"] = anterior
        return fb, lac

    def test_tela_inicial(self):
        st = streamlit_falso(0)
        self.rodar(st)
        self.assertIn("estimativa", textos(st))

    def test_tela_tarifa_social(self):
        st = streamlit_falso(1)
        self.rodar(st)
        self.assertIn("Tarifa Social", textos(st))

    def test_tela_dados_calcula_e_vai_para_resultados(self):
        st = streamlit_falso(2, {"ts": "sim"})
        self.rodar(st)
        self.assertEqual(st.session_state["etapa"], 3)
        perfil = st.session_state["perfil"]
        self.assertEqual(perfil.origem_consumo, "reais")
        self.assertTrue(perfil.tem_tarifa_social)
        self.assertAlmostEqual(perfil.consumo_kwh, 150 / c.tarifa_com_tributos(c.valores(c.carregar_dados())) + 80, places=3)

    def test_tela_resultados_mostra_recomendacao_selo_e_fontes(self):
        p = c.valores(c.carregar_dados())
        perfil = c.perfil_referencia(p)
        st = streamlit_falso(3, {"perfil": perfil, "ts": "nao"}, pergunta="Quanto custa o kWh?")
        fb, lac = self.rodar(st)
        t = textos(st)
        self.assertIn("Por onde começar", t)
        self.assertIn("Selo de confiança", t)
        self.assertIn("Como calculamos", t)
        expanders = " ".join(str(c_.args) for c_ in st.expander.call_args_list)
        self.assertIn("Todas as fontes usadas", expanders)
        self.assertIn("Como calculamos", expanders)
        fb.assert_called_once()
        lac.assert_not_called()

    def test_pergunta_sem_resposta_registra_lacuna(self):
        p = c.valores(c.carregar_dados())
        st = streamlit_falso(3, {"perfil": c.perfil_referencia(p), "ts": "nao"}, pergunta="Como tiro meu RG?")
        fb, lac = self.rodar(st)
        lac.assert_called_once()
        self.assertIn("Não tenho essa informação", textos(st))


if __name__ == "__main__":
    unittest.main()
