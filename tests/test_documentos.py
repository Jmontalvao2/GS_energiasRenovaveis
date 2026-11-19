import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))


def carregar_gerador():
    spec = importlib.util.spec_from_file_location("gerar_documentos", RAIZ / "scripts" / "gerar_documentos.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDocumentos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.destino = Path(tempfile.mkdtemp())
        cls.arquivos = carregar_gerador().gerar(cls.destino)

    def texto(self, nome):
        return (self.destino / nome).read_text(encoding="utf-8")

    def test_arquivos_exigidos_pelo_enunciado_existem(self):
        for nome in ("README.md", "docs/dados_e_premissas.md", "docs/calculos_e_comparacao.md",
                     "docs/justificativas_recomendacoes.md", "docs/referencias.md", "docs/roteiro_video.md"):
            self.assertTrue((self.destino / nome).exists(), nome)

    def test_numeros_dos_documentos_sao_os_do_assistente(self):
        for nome in ("README.md", "docs/calculos_e_comparacao.md", "docs/justificativas_recomendacoes.md"):
            self.assertIn("R$ 40,55", self.texto(nome), nome)
        self.assertIn("0,9431", self.texto("README.md"))

    def test_readme_tem_secoes_obrigatorias(self):
        readme = self.texto("README.md")
        for trecho in ("## Integrantes", "## Público e problema", "## Funcionalidades de energia", "## Como executar", "## Como testar"):
            self.assertIn(trecho, readme)

    def test_toda_fonte_do_json_aparece_nas_referencias(self):
        import calculos as c
        refs = self.texto("docs/referencias.md")
        for id_ in c.carregar_dados()["fontes"]:
            self.assertIn(f"**{id_}.**", refs)

    def test_roteiro_do_video_cabe_em_3_minutos(self):
        falas = re.findall(r"\*\*Fala:\*\* (.+)", self.texto("docs/roteiro_video.md"))
        palavras = sum(len(f.split()) for f in falas)
        self.assertLessEqual(palavras / 150, 3.0)
        self.assertGreater(palavras, 150)

    def test_sensibilidade_tem_todos_os_casos(self):
        txt = self.texto("docs/calculos_e_comparacao.md")
        for caso in ("Caso base", "Chuveiro de 4.000 W", "Banho de 6 minutos", "5 pessoas na casa", "Fotovoltaico a R$ 7.000/kWp"):
            self.assertIn(caso, txt)

    def test_atribuicao_correta_do_estudo_de_retorno(self):
        just = self.texto("docs/justificativas_recomendacoes.md")
        self.assertNotIn("Um estudo da ENTAC achou", just)
        self.assertIn("Silveira e Gardolinski", just)
        self.assertIn("Geá et al.", just)

    def test_referencias_trazem_verificacao_de_cada_fonte(self):
        refs = self.texto("docs/referencias.md")
        self.assertEqual(refs.count("Verificação em 18/11/2026:"), 17)


if __name__ == "__main__":
    unittest.main()
