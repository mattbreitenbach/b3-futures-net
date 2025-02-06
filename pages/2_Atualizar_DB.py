import streamlit as st

import src.db_connector as db_connector
import src.db_formatter as db_formatter
import src.scrapper as scrapper

st.set_page_config(page_title="Atualizar DB",
                   layout="wide")

st.title("Atualizar Banco de Dados")

st.markdown('''
            Selecione abaixo os dias que você deseja para extender o banco de dados.
            ''')

st.write(" ")


datas_ja_adicionadas = db_connector.query_unique_in_column("data_pregao")
datas_ja_adicionadas = [f"{data[-2:]}/{data[-5:-3]
                                       }/{data[:4]}" for data in datas_ja_adicionadas]

data_column_1, data_column_2 = st.columns([3, 3])

with data_column_1:
    st.write("Apenas um dia")
    data_download = st.date_input("Data Inicial", min_value="1990-01-01",
                                  max_value="2070-01-01", format="DD/MM/YYYY", key="data_download1")

    if st.button("Adicionar dia ao banco de dados", key="botao1"):
        if data_download.strftime("%d/%m/%Y") in datas_ja_adicionadas:
            st.write("ERRO: Data já adicionada.")
        else:
            placeholder_1 = st.empty()
            placeholder_1.write("Adicionando dados...")
            data_download_str = data_download.strftime("%d/%m/%Y")
            try:
                dados = scrapper.baixar_ajuste_bmf(data_download_str)
                dados = db_formatter.scrapper_format_to_db(dados)
                resultado = db_connector.add_ajustes_from_df(dados)
                if resultado == 1:
                    placeholder_1.write("Concluido!")
                else:
                    placeholder_1.write("ERRO: tente novamente")
            except:
                placeholder_1.write("ERRO: tente novamente")

with data_column_2:
    st.write("Multiplos dias")
    data_inicio_download = st.date_input(
        "Data Inicial", min_value="1990-01-01", max_value="2070-01-01", format="DD/MM/YYYY", key="data_download2")
    data_fim_download = st.date_input("Data Final", min_value="1990-01-01",
                                      max_value="2070-01-01", format="DD/MM/YYYY", key="data_download3")

    if st.button("Adicionar dia ao banco de dados", key="botao2"):
        placeholder_2 = st.empty()
        if ((data_fim_download-data_inicio_download).days) < 0:
            placeholder_2.write(
                "ERRO: Data final não pode ser anterior à data inicial.")
        elif ((data_fim_download-data_inicio_download).days) > 252:
            placeholder_2.write(
                "ERRO: Período muito grande, máximo de 252 dias.")
        else:
            placeholder_2.write(
                "Adicionando dados... Isso pode levar alguns minutos.")
            data_inicial_download_str = data_inicio_download.strftime(
                "%d/%m/%Y")
            data_final_download_str = data_fim_download.strftime("%d/%m/%Y")
            try:
                dados = scrapper.baixar_ajuste_bmf_multiplos_dias(
                    data_inicial_download_str, data_final_download_str, datas_ja_adicionadas)
                dados = db_formatter.scrapper_format_to_db(dados)
                resultado = db_connector.add_ajustes_from_df(dados)
                if resultado == 1:
                    placeholder_2.write("Concluido!")
                else:
                    placeholder_2.write("ERRO: tente novamente")
            except:
                placeholder_2.write("ERRO: tente novamente")

st.divider()
st.markdown('''
            Este sistema foi desenvolvido para fins educacionais e informativos, não devendo ser utilizado como base para decisões de investimento. Embora tenha sido feito um esforço para garantir a precisão dos cálculos, pode haver erros nas fórmulas e nas estimativas apresentadas.<br>
            Recomenda-se que os usuários validem todas as informações de forma independente e consultem profissionais qualificados antes de tomar qualquer decisão financeira. O desenvolvedor não se responsabiliza por quaisquer perdas ou danos decorrentes do uso deste sistema.
            ''',
            unsafe_allow_html=True)
