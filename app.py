"""Interface em Streamlit do módulo Energia do Citizen Assist AI.

Rodar:  streamlit run app.py
Fluxo principal com botões (Tarifa Social -> dados da família -> opções) e campo livre para dúvidas.
"""
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
import assistente as ast_  # noqa: E402
import calculos as calc  # noqa: E402

st.set_page_config(page_title="Energia | Citizen Assist AI", page_icon="💡", layout="centered")


@st.cache_data
def carregar():
    return calc.carregar_dados()


DADOS = carregar()
P = calc.valores(DADOS)

# ------------------------------------------------------------------ estado
st.session_state.setdefault("etapa", 0)
st.session_state.setdefault("ts", None)          # 'sim' | 'nao' | 'nao_sei'
st.session_state.setdefault("ia_ligada", False)


def ir(etapa: int):
    st.session_state["etapa"] = etapa


def escolher_ts(valor: str):
    st.session_state["ts"] = valor
    st.session_state["etapa"] = 2


# ------------------------------------------------------------------ barra lateral
with st.sidebar:
    st.header("Sobre este assistente")
    st.write("Orientações sobre uso de energia em casa, com cálculos e fontes. "
             "Os números vêm de contas feitas em código, não de uma IA.")
    if os.environ.get("ANTHROPIC_API_KEY"):
        st.session_state["ia_ligada"] = st.checkbox(
            "Usar IA para simplificar o texto (os números são conferidos pelo código)",
            value=st.session_state["ia_ligada"])
    else:
        st.caption("IA para simplificar o texto: desligada (sem chave de API). O assistente funciona sem ela.")
    with st.expander("Feedback dos testes (equipe)"):
        fb = ast_.ler_feedback()
        if fb:
            st.write(f"{len(fb)} avaliação(ões) registrada(s).")
            st.dataframe(pd.DataFrame(fb), use_container_width=True)
        else:
            st.write("Nenhuma avaliação ainda.")
    with st.expander("Painel de Lacunas (equipe)"):
        lac = ast_.ler_lacunas()
        if lac:
            st.write(f"{len(lac)} dúvida(s) sem resposta verificada:")
            st.dataframe(pd.DataFrame(lac), use_container_width=True)
        else:
            st.write("Nenhuma dúvida sem resposta ainda.")

st.title("💡 Menos conta de luz, com contas claras")

# ------------------------------------------------------------------ etapa 0: boas-vindas
if st.session_state["etapa"] == 0:
    st.write("Vou te ajudar a entender quanto sua família gasta de energia e comparar 3 jeitos de gastar menos: "
             "mudar hábitos, usar aquecimento solar de água e usar painel solar.")
    st.info("Tudo aqui é **estimativa**, não garantia. Eu mostro de onde veio cada informação.")
    st.button("Começar", type="primary", use_container_width=True, on_click=ir, args=(1,))

# ------------------------------------------------------------------ etapa 1: tarifa social
elif st.session_state["etapa"] == 1:
    st.subheader("Passo 1 de 2: Tarifa Social")
    st.write("A sua família está no CadÚnico com renda de até meio salário mínimo por pessoa, "
             "ou recebe o BPC?")
    st.button("Sim", use_container_width=True, on_click=escolher_ts, args=("sim",))
    st.button("Não", use_container_width=True, on_click=escolher_ts, args=("nao",))
    st.button("Não sei", use_container_width=True, on_click=escolher_ts, args=("nao_sei",))

# ------------------------------------------------------------------ etapa 2: dados da família
elif st.session_state["etapa"] == 2:
    st.subheader("Passo 2 de 2: sua família")
    st.info(ast_.mensagem_tarifa_social(st.session_state["ts"], DADOS))

    modo = st.radio("Como você quer informar o gasto de energia?",
                    ["Valor da conta de luz (R$)", "Consumo em kWh (aparece na conta)",
                     "Não sei: usar uma família de referência"], key="modo")
    valor = 0.0
    if modo.startswith("Valor"):
        valor = st.number_input("Quanto veio na última conta, em R$?", min_value=0.0, step=10.0, key="valor")
    elif modo.startswith("Consumo"):
        valor = st.number_input("Quantos kWh aparecem na conta?", min_value=0.0, step=10.0, key="kwh")

    if modo.startswith("Não sei"):
        pessoas, chuveiro, minutos = int(P["P01"]), True, float(P["C02"])
        st.caption(f"Vou usar uma família de {pessoas} pessoas, com chuveiro elétrico e banho de {int(minutos)} minutos.")
    else:
        pessoas = st.number_input("Quantas pessoas moram na casa?", min_value=1, max_value=12, value=4, step=1, key="pessoas")
        chuveiro = st.radio("A casa tem chuveiro elétrico?", ["Sim", "Não"], horizontal=True, key="chuv") == "Sim"
        minutos = st.slider("Quantos minutos dura um banho, em média?", 3, 20, int(P["C02"]), key="min") if chuveiro else 0
    proprio = st.radio("A casa é...", ["Própria", "Alugada"], horizontal=True, key="imovel") == "Própria"

    c1, c2 = st.columns(2)
    c1.button("Voltar", use_container_width=True, on_click=ir, args=(1,))
    ver = c2.button("Ver minhas opções", type="primary", use_container_width=True)
    if ver:
        tem_ts = st.session_state["ts"] == "sim"
        if modo.startswith("Não sei"):
            perfil = calc.perfil_referencia(P)
            perfil.tem_tarifa_social, perfil.imovel_proprio = tem_ts, proprio
        elif valor <= 0:
            st.warning("Digite um valor maior que zero, ou escolha usar a família de referência.")
            st.stop()
        else:
            kwh = valor if modo.startswith("Consumo") else calc.converter_reais_em_kwh(valor, tem_ts, P)
            perfil = calc.Perfil(consumo_kwh=kwh, pessoas=int(pessoas), chuveiro_eletrico=chuveiro,
                                 minutos_banho=float(minutos), tem_tarifa_social=tem_ts, imovel_proprio=proprio,
                                 origem_consumo="kwh" if modo.startswith("Consumo") else "reais")
        st.session_state["perfil"] = perfil
        st.session_state["etapa"] = 3
        st.rerun()

# ------------------------------------------------------------------ etapa 3: resultados
else:
    perfil = st.session_state["perfil"]
    resultados = calc.avaliar(perfil, P)
    texto = ast_.explicar_resultados(resultados, perfil, DADOS)
    mostrado, usou_ia = texto, False
    if st.session_state["ia_ligada"]:
        with st.spinner("Simplificando o texto..."):
            mostrado, usou_ia = ast_.reescrever_em_linguagem_simples(texto)

    st.subheader("Suas opções")
    if perfil.origem_consumo == "reais":
        st.caption("Convertemos o valor da conta em kWh de forma aproximada: a conta também tem taxa de iluminação "
                   "e bandeira, então o consumo pode estar um pouco superestimado.")
    st.markdown(mostrado)
    if usou_ia:
        st.caption("Texto simplificado por IA. O código conferiu que todos os números são os mesmos do cálculo.")

    linhas = []
    for r in resultados[1:]:
        linhas.append({
            "Alternativa": r.nome,
            "Economia por mês": calc.brl(r.economia_mensal) if r.aplicavel else "não se aplica",
            "Investimento": calc.brl(r.investimento) if r.aplicavel else "-",
            "Retorno": ("não se paga" if r.retorno_anos is None else "imediato" if r.retorno_anos == 0
                        else f"{calc.numero(r.retorno_anos)} anos") if r.aplicavel else "-",
            "Viabilidade": r.viabilidade if r.aplicavel else "-",
        })
    st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

    with st.expander("Selo de confiança: fontes, data e limitações"):
        st.markdown(ast_.selo_confianca(DADOS))
    with st.expander("Como calculamos (passo a passo)"):
        st.markdown(ast_.explicar_calculo(resultados, perfil, DADOS))
    with st.expander("Todas as fontes usadas"):
        st.markdown(ast_.listar_fontes(DADOS))
    for r in resultados[1:]:
        if r.nota:
            st.caption(f"{r.nome}: {r.nota}")

    st.download_button("Baixar este resumo (.txt)", data=(mostrado + "\n\n" + ast_.selo_confianca(DADOS)).replace("**", ""),
                       file_name="resumo_energia.txt", use_container_width=True)

    st.divider()
    st.subheader("Tem alguma dúvida?")
    st.caption("Não escreva CPF, telefone nem outros dados pessoais.")
    pergunta = st.text_input("Escreva sua dúvida sobre energia", key="pergunta")
    if pergunta:
        resp, fontes, achou = ast_.responder_duvida(pergunta, DADOS, perfil)
        (st.success if achou else st.warning)(resp)
        if achou:
            nomes = [DADOS["fontes"][f]["fonte"] for f in fontes if f in DADOS["fontes"]]
            st.caption("Fontes: " + "; ".join(nomes) + f". Consultadas em {DADOS['consulta']}.")

    st.divider()
    st.subheader("Essa orientação ajudou?")
    with st.form("feedback"):
        clareza = st.radio("O texto foi fácil de entender?", ["Sim", "Mais ou menos", "Não"], horizontal=True)
        util = st.radio("Ajudou a decidir o que fazer?", ["Sim", "Mais ou menos", "Não"], horizontal=True)
        comentario = st.text_input("Quer deixar um comentário? (não escreva dados pessoais)")
        enviar = st.form_submit_button("Enviar")
    if enviar:
        situacao = (f"{perfil.origem_consumo}; tarifa social: {'sim' if perfil.tem_tarifa_social else 'não'}; "
                    f"imóvel {'próprio' if perfil.imovel_proprio else 'alugado'}")
        ast_.registrar_feedback(clareza, util, comentario, situacao)
        st.success("Obrigado! Sua resposta ajuda a melhorar o assistente.")

    st.button("Refazer", use_container_width=True, on_click=ir, args=(1,))
