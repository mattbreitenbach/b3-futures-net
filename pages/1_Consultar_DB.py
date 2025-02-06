import streamlit as st

import src.db_connector as db_connector


st.set_page_config(page_title="Consultar DB",
                   layout="wide")

st.title("Consultar Banco de Dados")

st.markdown('''
            Consulta abaixo os dados disponíveis sobre contratos futuros registrados na B3.
            ''')

st.write(" ")


col_consulta_1, col_consulta_2 = st.columns([5, 5])

with col_consulta_1:
    coluna_consulta = st.selectbox(
        "Itens Disponíveis nas Tabelas do Banco de Dados", ("", "data_pregao", "mercadoria"))

    if coluna_consulta != "":
        itens = db_connector.query_unique_in_column(coluna_consulta)
        st.dataframe(itens, width=350, height=300)

with col_consulta_2:
    data_consulta = st.date_input(
        "Consultar Mercadorias Disponíveis na Data", min_value="1990-01-01", format="DD/MM/YYYY", key="query_mercadorias_datas")
    data_consulta = data_consulta.strftime("%d/%m/%Y")
    mercadorias = db_connector.query_mercadorias_na_data(data_consulta)
    if len(mercadorias) > 0:
        st.dataframe(mercadorias, width=350, height=300)

st.text(" ")
st.divider()
st.subheader("Consulta Livre")
col_query_1, col_query_2, col_query_3 = st.columns(3)

with col_query_1:
    query_data_pregao = st.date_input(
        "Data do Pregão", min_value="1990-01-01", format="DD/MM/YYYY", key="query_dp")
    query_data_pregao = query_data_pregao.strftime("%d/%m/%Y")
with col_query_2:
    query_mercadoria = st.text_input("Mercadoria")
with col_query_3:
    query_vencimento = st.text_input("Vencimento:  <M><YY>", value="F25")

if query_data_pregao or query_mercadoria or query_vencimento:
    df_query = db_connector.query_db(data_pregao=query_data_pregao,
                                     mercadoria=query_mercadoria, vencimento=query_vencimento)
    st.dataframe(df_query, width=1200)

st.divider()
st.markdown('''
            Este sistema foi desenvolvido para fins educacionais e informativos, não devendo ser utilizado como base para decisões de investimento. Embora tenha sido feito um esforço para garantir a precisão dos cálculos, pode haver erros nas fórmulas e nas estimativas apresentadas.<br>
            Recomenda-se que os usuários validem todas as informações de forma independente e consultem profissionais qualificados antes de tomar qualquer decisão financeira. O desenvolvedor não se responsabiliza por quaisquer perdas ou danos decorrentes do uso deste sistema.
            ''',
            unsafe_allow_html=True)
