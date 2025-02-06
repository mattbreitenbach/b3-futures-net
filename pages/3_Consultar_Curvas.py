import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import src.db_connector as db_connector
import src.futures_calc as futures_calc
import src.contador_dias as contador_dias
import src.intepolator_nss as interpolator_nss


st.set_page_config(page_title="Atualizar DB",
                   layout="wide")

st.title("Consultar Curvas")

st.markdown('''
            Consulte abaixo as curvas disponiveis, tanto observadas quanto com dados de interpolação.
            ''')

st.write(" ")

datas_disponiveis = db_connector.query_unique_in_column("data_pregao")
datas_disponiveis = [f"{data[-2:]}/{data[-5:-3]
                                    }/{data[:4]}" for data in datas_disponiveis]

data_pregao = st.date_input("Data Pregao", min_value="1990-01-01",
                            max_value="2070-01-01", format="DD/MM/YYYY", key="data_pregao")
data_pregao = data_pregao.strftime("%d/%m/%Y")
modo_consulta = st.selectbox("Modo de Consulta", ["Juros", "Preços"])
mercadorias = db_connector.query_unique_in_column("mercadoria")

opcoes_juros = ["DI1 - DI de 1 dia", "DAP - Cupom de DI x IPCA",
                "DDI - Cupom cambial", "DCO - Cupom Cambial em OC1"]
opcoes_precos = mercadorias

if modo_consulta == "Juros":
    curva_selecionada = st.selectbox("Curva de Juros Desejada", opcoes_juros)
elif modo_consulta == "Preços":
    curva_selecionada = st.selectbox("Curva Preços Desejada", opcoes_precos)
    metodo_vencimento = st.selectbox("Qual o modo de vencimento do contrato?", [
                                     "prim_du", "ult_du", "terceira_sexta", "quarta_prox_quinze", "dia_15"])


if data_pregao not in datas_disponiveis:
    st.write("ERRO: Data não disponivel.")
    st.stop()

if st.button("Consultar Curva", key="botao_consultar_curva"):
    query = db_connector.query_db(
        data_pregao=data_pregao, mercadoria=curva_selecionada)

    if modo_consulta == "Juros":
        if curva_selecionada in ["DDI - Cupom cambial", "DCO - Cupom Cambial em OC1"]:
            if curva_selecionada == "DDI - Cupom cambial":
                query = contador_dias.add_dia_vencimento_df(query, "prim_du")
            elif curva_selecionada == "DCO - Cupom Cambial em OC1":
                query = contador_dias.add_dia_vencimento_df(query, "prim_du")
            query = contador_dias.calc_du_df(query)
            query = contador_dias.calc_dc_df(query)
            query = futures_calc.calc_taxa_externa_df(query)
            query_formated = query.copy()
            query_formated["taxa"] = query_formated["taxa"].multiply(
                100).round(4)
            eixo_x_coluna = "dc"
            eixo_y_coluna = "taxa"

        if curva_selecionada in ["DI1 - DI de 1 dia", "DAP - Cupom de DI x IPCA"]:
            if curva_selecionada == "DI1 - DI de 1 dia":
                query = contador_dias.add_dia_vencimento_df(query, "prim_du")
            elif curva_selecionada == "DAP - Cupom de DI x IPCA":
                query = contador_dias.add_dia_vencimento_df(query, "dia_15")
            query = contador_dias.calc_du_df(query)
            query = contador_dias.calc_dc_df(query)
            query = futures_calc.calc_taxa_local_df(query)
            query_formated = query.copy()
            query_formated["taxa"] = query_formated["taxa"].multiply(
                100).round(4)
            eixo_x_coluna = "du"
            eixo_y_coluna = "taxa"

        beta_0, beta_1, beta_2, beta_3, lambda_1, lambda_2 = interpolator_nss.calc_params_nss(
            query)
        curva_interpolada = interpolator_nss.generate_curve(
            beta_0, beta_1, beta_2, beta_3, lambda_1, lambda_2)
        curva_interpolada["taxa"] = curva_interpolada["taxa"].multiply(
            100).round(4)

        fig = px.scatter(query_formated,
                         x=eixo_x_coluna,
                         y=eixo_y_coluna)

        fig.add_trace(go.Scatter(
            x=curva_interpolada["vertices"],
            y=curva_interpolada["taxa"],
            mode="lines",
            name="Curva Interpolada",
            line=dict(color="red", width=2)
        ))

        fig.update_layout(title=f"Curva de Juros Futuros - {curva_selecionada}",
                          xaxis_title="Dias até Vencimento",
                          yaxis_title="Taxa de Juros")

        fig.update_traces(marker={"size": 15, "opacity": 0.9})
        st.plotly_chart(fig, width=1300, height=600, use_container_width=True)

    elif modo_consulta == "Preços":
        query = db_connector.query_db(
            data_pregao=data_pregao, mercadoria=curva_selecionada)
        query = contador_dias.add_dia_vencimento_df(query, metodo_vencimento)
        query = contador_dias.calc_du_df(query)
        eixo_x_coluna = "du"

        fig = px.scatter(query,
                         x=eixo_x_coluna,
                         y="preco_ajuste")

        fig.update_layout(title=f"Curva de Preços Futuros - {curva_selecionada}",
                          xaxis_title="Dias até Vencimento",
                          yaxis_title="Preço de Ajuste")

        fig.update_traces(marker={"size": 15, "opacity": 0.9})
        st.plotly_chart(fig, width=1300, height=600)

st.divider()
st.markdown('''
            Este sistema foi desenvolvido para fins educacionais e informativos, não devendo ser utilizado como base para decisões de investimento. Embora tenha sido feito um esforço para garantir a precisão dos cálculos, pode haver erros nas fórmulas e nas estimativas apresentadas.<br>
            Recomenda-se que os usuários validem todas as informações de forma independente e consultem profissionais qualificados antes de tomar qualquer decisão financeira. O desenvolvedor não se responsabiliza por quaisquer perdas ou danos decorrentes do uso deste sistema.
            ''',
            unsafe_allow_html=True)
