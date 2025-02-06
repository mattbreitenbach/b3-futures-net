import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import src.db_connector as db_connector
import src.futures_calc as futures_calc
import src.contador_dias as contador_dias
import src.intepolator_nss as interpolator_nss

st.set_page_config(page_title="Atualizar DB",
                   layout="wide")

st.title("Comparar Curvas")

st.markdown('''
            Compare abaixo as curvas disponiveis.
            ''')

st.write(" ")


datas_disponiveis = db_connector.query_unique_in_column("data_pregao")
datas_disponiveis = [f"{data[-2:]}/{data[-5:-3]
                                    }/{data[:4]}" for data in datas_disponiveis]

opcoes_curvas = ["DI1 - DI de 1 dia", "DAP - Cupom de DI x IPCA",
                 "DDI - Cupom cambial", "DCO - Cupom Cambial em OC1"]
curva_selecionada = st.selectbox("Curva de Juros Desejada", opcoes_curvas)

column_data_1, column_data_2 = st.columns([3, 3])
data_pregao_1 = column_data_1.date_input("Data Pregao 1", min_value="1990-01-01",
                                         max_value="2070-01-01", format="DD/MM/YYYY", key="data_pregao_1")
data_pregao_1 = data_pregao_1.strftime("%d/%m/%Y")

data_pregao_2 = column_data_2.date_input("Data Pregao 2", min_value="1990-01-01",
                                         max_value="2070-01-01", format="DD/MM/YYYY", key="data_pregao_2")
data_pregao_2 = data_pregao_2.strftime("%d/%m/%Y")


if data_pregao_1 not in datas_disponiveis:
    st.write("ERRO: Data pregão 1 não disponivel.")
    st.stop()
if data_pregao_2 not in datas_disponiveis:
    st.write("ERRO: Data pregão 2 não disponivel.")
    st.stop()


if st.button("Comparar Curvas", key="botao_consultar_curva"):
    query_1 = db_connector.query_db(
        data_pregao=data_pregao_1, mercadoria=curva_selecionada)
    query_2 = db_connector.query_db(
        data_pregao=data_pregao_2, mercadoria=curva_selecionada)

    if curva_selecionada in ["DDI - Cupom cambial", "DCO - Cupom Cambial em OC1"]:
        query_1 = contador_dias.add_dia_vencimento_df(query_1, "prim_du")
        query_2 = contador_dias.add_dia_vencimento_df(query_2, "prim_du")

        query_1 = contador_dias.calc_du_df(query_1)
        query_1 = contador_dias.calc_dc_df(query_1)
        query_1 = futures_calc.calc_taxa_externa_df(query_1)
        query_2 = contador_dias.calc_du_df(query_2)
        query_2 = contador_dias.calc_dc_df(query_2)
        query_2 = futures_calc.calc_taxa_externa_df(query_2)

        query_1_formated = query_1.copy()
        query_1_formated["taxa"] = query_1_formated["taxa"].multiply(
            100).round(4)
        query_2_formated = query_2.copy()
        query_2_formated["taxa"] = query_2_formated["taxa"].multiply(
            100).round(4)

        eixo_x_coluna = "dc"
        eixo_y_coluna = "taxa"

    if curva_selecionada in ["DI1 - DI de 1 dia", "DAP - Cupom de DI x IPCA"]:
        if curva_selecionada == "DI1 - DI de 1 dia":
            query_1 = contador_dias.add_dia_vencimento_df(query_1, "prim_du")
            query_2 = contador_dias.add_dia_vencimento_df(query_2, "prim_du")
        elif curva_selecionada == "DAP - Cupom de DI x IPCA":
            query_1 = contador_dias.add_dia_vencimento_df(query_1, "dia_15")
            query_2 = contador_dias.add_dia_vencimento_df(query_2, "dia_15")

        query_1 = contador_dias.calc_du_df(query_1)
        query_1 = contador_dias.calc_dc_df(query_1)
        query_1 = futures_calc.calc_taxa_local_df(query_1)
        query_2 = contador_dias.calc_du_df(query_2)
        query_2 = contador_dias.calc_dc_df(query_2)
        query_2 = futures_calc.calc_taxa_local_df(query_2)

        query_1_formated = query_1.copy()
        query_1_formated["taxa"] = query_1_formated["taxa"].multiply(
            100).round(4)
        query_2_formated = query_2.copy()
        query_2_formated["taxa"] = query_2_formated["taxa"].multiply(
            100).round(4)

        eixo_x_coluna = "du"
        eixo_y_coluna = "taxa"

    beta_0_1, beta_1_1, beta_2_1, beta_3_1, lambda_1_1, lambda_2_1 = interpolator_nss.calc_params_nss(
        query_1)
    curva_interpolada_1 = interpolator_nss.generate_curve(
        beta_0_1, beta_1_1, beta_2_1, beta_3_1, lambda_1_1, lambda_2_1)
    curva_interpolada_1["taxa"] = curva_interpolada_1["taxa"].multiply(
        100).round(4)

    beta_0_2, beta_1_2, beta_2_2, beta_3_2, lambda_1_2, lambda_2_2 = interpolator_nss.calc_params_nss(
        query_2)
    curva_interpolada_2 = interpolator_nss.generate_curve(
        beta_0_2, beta_1_2, beta_2_2, beta_3_2, lambda_1_2, lambda_2_2)
    curva_interpolada_2["taxa"] = curva_interpolada_2["taxa"].multiply(
        100).round(4)

    query_1["taxa"] = query_1["taxa"].multiply(100).round(4)
    query_2["taxa"] = query_2["taxa"].multiply(100).round(4)

    fig = px.scatter(query_1,
                     x=eixo_x_coluna,
                     y=eixo_y_coluna,
                     color_continuous_scale="red")
    fig.update_traces(marker=dict(color="red"))

    fig.add_trace(go.Scatter(
        x=curva_interpolada_1["vertices"],
        y=curva_interpolada_1["taxa"],
        mode="lines",
        name=f"1 - {data_pregao_1}",
        line=dict(color="red", width=2)
    ))

    fig.add_trace(go.Scatter(
        x=query_2[eixo_x_coluna],
        y=query_2[eixo_y_coluna],
        mode="markers",
        line=dict(color="blue", width=2),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=curva_interpolada_2["vertices"],
        y=curva_interpolada_2["taxa"],
        mode="lines",
        name=f"2 - {data_pregao_2}",
        line=dict(color="blue", width=2)
    ))

    fig.update_layout(title=f"Comparação Curvas de Juros - {curva_selecionada}",
                      xaxis_title="Dias até Vencimento",
                      yaxis_title="Taxa de Juros",
                      legend=dict(orientation="h", yanchor="bottom", y=1))

    fig.update_traces(marker={"size": 15, "opacity": 0.9})
    st.plotly_chart(fig, width=1300, height=600, use_container_width=True)


st.divider()
st.markdown('''
            Este sistema foi desenvolvido para fins educacionais e informativos, não devendo ser utilizado como base para decisões de investimento. Embora tenha sido feito um esforço para garantir a precisão dos cálculos, pode haver erros nas fórmulas e nas estimativas apresentadas.<br>
            Recomenda-se que os usuários validem todas as informações de forma independente e consultem profissionais qualificados antes de tomar qualquer decisão financeira. O desenvolvedor não se responsabiliza por quaisquer perdas ou danos decorrentes do uso deste sistema.
            ''',
            unsafe_allow_html=True)
