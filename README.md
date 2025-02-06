# b3-futures-net

## 📈 Sistema de Cálculo de Derivativos e Ajustes da B3  

Este projeto implementa um sistema para cálculos de futuros, web scrapping e armazenamento de ajustes da B3 e modelagem da curva de juros usando o modelo **Nelson-Siegel-Svensson (NSS)**.  

Criado "for the joy of coding", este projeto serve como uma vitrine das minhas habilidades no meu portfólio pessoal. A inspiração vem do curso "100 Days of Code: The Complete Python Pro Bootcamp" de Angela Yu. Enquanto o curso forneceu orientação e ensinou algumas valiosas ferramentas, este projeto representa minha interpretação pessoal e aplicação dos conceitos aprendidos, com grande parte do trabalho sendo de minha autoria.
Também não poderia deixar de agradecer o professor Ricardo Rochman, que em seu [canal de youtube](https://www.youtube.com/@incredulofinanceiro) me deu a inspiração para o conteúdo deste projeto.

## Funcionalidades  

- **Web Scraping**: Baixa os dados de ajustes da B3.  
- **Banco de Dados**: Armazena as informações em um banco relacional com SQLAlchemy.  
- **Cálculo de Futuros**: Implementa fórmulas para DI1, DAP, DDI e DCO.  
- **Curva de Juros**: Ajusta a curva de juros com o modelo NSS usando otimização numérica.  

## Instalação  

### Clonar o repositório
```bash  
git clone https://github.com/mattbreitenbach/b3-futures-net.git  
cd b3-futures-net
```

### Criar ambiente virtual e instalar dependências
```bash
python -m venv venv  
source venv/bin/activate  # No Windows: venv\Scripts\activate  
pip install -r requirements.txt  
```

### Rodar o streamlit
```bash
streamlit run home.py
```

## Principais Dependências
- Python
- BeautifulSoup
- SQLAlchemy 
- Pandas
- Streamlit
- Plotly
- Numpy & Scipy

## Aviso

Este sistema não deve ser utilizado para decisões de investimento. Os cálculos podem conter erros e não substituem uma análise profissional.