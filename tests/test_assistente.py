import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
import assistente as a  # noqa: E402
import calculos as c  # noqa: E402


class ClienteFalso:
    """Imita o cliente da API para testar a trava de números sem internet."""
    def __init__(self, resposta):
        self.messages = SimpleNamespace(create=lambda **kw: SimpleNamespace(
            content=[SimpleNamespace(type="text", text=resposta)]))


class TestAssistente(unittest.TestCase):
    def setUp(self):
        self.dados = c.carregar_dados()
        self.p = c.valores(self.dados)
        self.perfil = c.perfil_referencia(self.p)
        self.lacunas = Path(tempfile.mkdtemp()) / "lacunas.csv"

    def test_texto_principal_traz_reais_e_aviso(self):
        texto = a.explicar_resultados(c.avaliar(self.perfil, self.p), self.perfil, self.dados)
        self.assertIn("R$ 40,55", texto)
        self.assertIn("não garantias", texto)
        self.assertIn("alternativa A", texto)

    def test_selo_de_confianca_tem_data_fonte_e_limitacao(self):
        selo = a.selo_confianca(self.dados)
        self.assertIn("18/11/2026", selo)
        self.assertIn("Limitações", selo)
        self.assertIn("ANEEL", selo)

    def test_duvida_com_resposta_verificada(self):
        texto, fontes, achou = a.responder_duvida("Como funciona a tarifa social?", self.dados, self.perfil, self.lacunas)
        self.assertTrue(achou)
        self.assertIn("80", texto)
        self.assertEqual(fontes, ["F4"])
        self.assertFalse(self.lacunas.exists())

    def test_duvida_sem_resposta_registra_lacuna_sem_dados_pessoais(self):
        texto, fontes, achou = a.responder_duvida("Como tiro meu RG? CPF 123.456.789-00", self.dados, self.perfil, self.lacunas)
        self.assertFalse(achou)
        self.assertIn("Não tenho essa informação", texto)
        registros = a.ler_lacunas(self.lacunas)
        self.assertEqual(len(registros), 1)
        self.assertNotIn("123.456", registros[0]["pergunta"])

    def test_trava_aceita_mesmos_numeros(self):
        self.assertTrue(a.validar_reescrita("Você economiza R$ 41,05 por mês (43,0 kWh).",
                                            "Dá para economizar R$ 41,05 todo mês, ou 43,0 kWh."))

    def test_trava_rejeita_numero_alterado_ou_promessa(self):
        original = "Você economiza R$ 41,05 por mês."
        self.assertFalse(a.validar_reescrita(original, "Você economiza R$ 45,00 por mês."))
        self.assertFalse(a.validar_reescrita(original, "Você economiza R$ 41,05 por mês, garantimos."))
        self.assertFalse(a.validar_reescrita(original, "   "))

    def test_ia_sem_chave_devolve_texto_original(self):
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        self.assertEqual(a.reescrever_em_linguagem_simples("Economia de R$ 41,05."), ("Economia de R$ 41,05.", False))

    def test_ia_fiel_e_aceita_e_ia_infiel_e_descartada(self):
        original = "Economia de R$ 41,05 por mês."
        novo, usou = a.reescrever_em_linguagem_simples(original, ClienteFalso("Você guarda R$ 41,05 por mês."))
        self.assertTrue(usou)
        self.assertEqual(novo, "Você guarda R$ 41,05 por mês.")
        novo, usou = a.reescrever_em_linguagem_simples(original, ClienteFalso("Você guarda R$ 51,05 por mês."))
        self.assertFalse(usou)
        self.assertEqual(novo, original)

    def test_frase_de_origem_em_portugues_correto(self):
        for origem, esperado in (("reais", "com base no valor de conta"), ("kwh", "com base no consumo"),
                                 ("referencia", "com base em uma família")):
            self.perfil.origem_consumo = origem
            texto = a.explicar_resultados(c.avaliar(self.perfil, self.p), self.perfil, self.dados)
            self.assertIn(esperado, texto)
            self.assertNotIn("em o ", texto)

    def test_explicar_calculo_mostra_formulas_e_fontes(self):
        res = c.avaliar(self.perfil, self.p)
        texto = a.explicar_calculo(res, self.perfil, self.dados)
        self.assertIn("Como calculamos", texto)
        self.assertIn("0,9431", texto)
        self.assertIn("88,0 kWh", texto)
        self.assertIn("planilha", texto)

    def test_lista_de_fontes_traz_links(self):
        texto = a.listar_fontes(self.dados)
        self.assertIn("https://www.enel.com.br", texto)
        self.assertIn("https://www.gov.br/mme", texto)

    def test_feedback_registra_sem_dados_pessoais(self):
        caminho = Path(tempfile.mkdtemp()) / "fb.csv"
        a.registrar_feedback("Sim", "Mais ou menos", "Meu telefone é 11 98765-4321", "reais", caminho)
        reg = a.ler_feedback(caminho)
        self.assertEqual(len(reg), 1)
        self.assertEqual(reg[0]["clareza"], "Sim")
        self.assertNotIn("98765", reg[0]["comentario"])

    def test_resposta_sobre_preco_do_kwh(self):
        texto, fontes, achou = a.responder_duvida("Quanto custa o kWh da Enel?", self.dados, self.perfil, self.lacunas)
        self.assertTrue(achou)
        self.assertIn("0,79", texto)
        self.assertEqual(fontes, ["F1", "F2"])

    def test_painel_com_tarifa_social_pede_confirmacao_na_distribuidora(self):
        self.perfil.tem_tarifa_social = True
        texto = a.explicar_resultados(c.avaliar(self.perfil, self.p), self.perfil, self.dados)
        self.assertIn("Confirme com a distribuidora", texto)


if __name__ == "__main__":
    unittest.main()
