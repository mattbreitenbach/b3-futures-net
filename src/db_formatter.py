import pandas as pd


def scrapper_format_to_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formata um DataFrame no padrão 'scrapper' para o padrão do banco de dados.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados brutos extraídos.

    Returns:
        pd.DataFrame: DataFrame com colunas renomeadas e índice resetado.
    """
    rename_dict = {
        "Data Pregão": "data_pregao",
        "Mercadoria": "mercadoria",
        "Vct": "vencimento",
        "Preço de Ajuste Anterior": "preco_ajuste_anterior",
        "Preço de Ajuste Atual": "preco_ajuste",
        "Variação": "variacao",
        "Valor do Ajuste por Contrato (R$)": "valor_ajuste_por_contrato"
    }

    df = df.rename(columns=rename_dict)
    df.reset_index(drop=True, inplace=True)

    return df
