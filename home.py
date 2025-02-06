import streamlit as st


def main():

    st.set_page_config(page_title="B3 FUTURES NET")

    st.title("Bem-vindo!")

    st.markdown('''
                Este é um sistema proprietário de consulta de dados sobre contratos futuros registrados na B3.<br>
                Temos algumas páginas disponíveis, abaixo uma breve descrição de cada uma delas:
                ''',
                unsafe_allow_html=True)
    st.divider()
    st.markdown('''
                ATENÇÃO: Este sistema foi desenvolvido para fins educacionais e informativos, não devendo ser utilizado como base para decisões de investimento. Embora tenha sido feito um esforço para garantir a precisão dos cálculos, pode haver erros nas fórmulas e nas estimativas apresentadas.<br>
                Recomenda-se que os usuários validem todas as informações de forma independente e consultem profissionais qualificados antes de tomar qualquer decisão financeira. O desenvolvedor não se responsabiliza por quaisquer perdas ou danos decorrentes do uso deste sistema.
                ''',
                unsafe_allow_html=True)
    st.divider()

    with st.popover("Consultar DB"):
        st.write('''
            Permite a vizualização dos dados armazenados no banco de dados do sistema, facilitando a análise das informações já registradas. Além de permitir a exportação dos dados em formato .csv.
        ''')

    with st.popover("Atualizar DB"):
        st.write('''
            Oferece a funcionalidade de inserir novos dados no banco de dados, garantindo que as informações estejam sempre atualizadas. Faz a atualização dos dados por meio do web scraping do site da B3.
        ''')

    with st.popover("Consultar Curvas"):
        st.write('''
            Exibe as curvas de taxas ou preços escolhidos, calculadas com base nos dados armazenados, permitindo a análise da estrutura da curva ao longo dos vencimentos. Além de contar com a interpolação das curvas, construída a partir do modelo Nelson-Siegel-Svensson.
        ''')

    with st.popover("Comparar Curvas"):
        st.write('''
            Exibe as curvas de diferentes datas, permitindo a análise das tendências e variações ao longo do tempo. 
        ''')


if __name__ == "__main__":
    main()
