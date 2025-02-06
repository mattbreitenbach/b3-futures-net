import numpy as np
from scipy.optimize import minimize
import pandas as pd


VERTICES_PADRAO = [21, 63, 126, 189, 252, 378, 504, 630, 756, 882, 1008,
                   1134, 1260, 1386, 1512, 1638, 1764, 1890, 2016, 2142, 2268, 2394, 2520]


def calc_nss(tau: float, beta_0: float, beta_1: float, beta_2: float, beta_3: float, lambda_1: float, lambda_2: float) -> float:
    """
    Calcula a taxa de juros para o periodo tau (du/360) com base no modelo Nelson-Siegel-Svensson (NSS).

    Args:
        tau (float): Tempo até o vencimento (maturidade) expresso em anos.
        beta_0 (float): Parâmetro de nível da curva (intercepto).
        beta_1 (float): Parâmetro de inclinação da curva.
        beta_2 (float): Parâmetro de curvatura de curto prazo.
        beta_3 (float): Parâmetro de curvatura de longo prazo.
        lambda_1 (float): Parâmetro que controla a taxa de decaimento dos fatores de curto prazo.
        lambda_2 (float): Parâmetro que controla a taxa de decaimento dos fatores de longo prazo.

    Returns:
        float: Taxa de juros estimada pelo modelo NSS para o prazo `tau` (du/360).
    """

    part_1 = beta_0
    part_2 = (beta_1*(1-np.exp(-lambda_1*tau))/(lambda_1*tau))
    part_3 = (beta_2*((1-np.exp(-lambda_1*tau)) /
              (lambda_1*tau)-np.exp(-lambda_1*tau)))
    part_4 = (beta_3*((1-np.exp(lambda_2*tau)) /
              (lambda_2*tau)-np.exp(-lambda_2*tau)))

    return part_1 + part_2 + part_3 + part_4


def objective_function(params: list, df: pd.DataFrame) -> float:
    """
    Função objetivo para ajustar os parâmetros do modelo NSS minimizando o erro quadrático.

    Args:
        params (list): Lista com os seis parâmetros do modelo NSS [beta_0, beta_1, beta_2, beta_3, lambda_1, lambda_2].
        df (pd.DataFrame): DataFrame contendo as colunas:
                - 'tau': maturidade em anos (du / 360)
                - 'taxa': taxa observada.

    Returns:
        float: Soma dos erros quadráticos entre as taxas observadas e as taxas estimadas pelo modelo NSS.
    """
    beta_0, beta_1, beta_2, beta_3, lambda_1, lambda_2 = params
    df["nss"] = df.apply(lambda row: calc_nss(
        row["tau"], beta_0, beta_1, beta_2, beta_3, lambda_1, lambda_2), axis=1)
    erro = ((df["taxa"] - df["nss"])**2).sum()
    return erro


def calc_params_nss(df: pd.DataFrame) -> np.ndarray:
    """
    Ajusta os parâmetros do modelo Nelson-Siegel-Svensson (NSS) para a curva de juros. Utiliza o método de otimização 'BFGS' para minimizar a diferença entre as taxas DI observadas e as estimadas pelo modelo NSS.

    Args
    df (pd.DataFrame): DataFrame contendo as colunas:
            - 'du': dias úteis até o vencimento do contrato.
            - 'taxa': taxa observada.

    Returns
        np.ndarray: Vetor contendo os seis parâmetros ótimos do modelo NSS ajustados aos dados.
    """
    df = df[df["du"] >= 21]
    df["tau"] = df["du"] / 360

    beta_0, beta_1, beta_2, beta_3 = 0.01, 0.01, 0.01, 0.01
    lambda_1, lambda_2 = 0.1, -0.1
    initial_params = [beta_0, beta_1, beta_2, beta_3, lambda_1, lambda_2]

    result = minimize(objective_function, initial_params,
                      args=(df,), method='BFGS')

    optimal_params = result.x
    return optimal_params


def generate_curve(beta_0: float, beta_1: float, beta_2: float, beta_3: float, lambda_1: float, lambda_2: float) -> pd.DataFrame:
    """
    Com base nos parametros passados, retorna uma df, com a curva interpolada para vertices padrão.

    Args:
        tau (float): Tempo até o vencimento (maturidade) expresso em anos.
        beta_0 (float): Parâmetro de nível da curva (intercepto).
        beta_1 (float): Parâmetro de inclinação da curva.
        beta_2 (float): Parâmetro de curvatura de curto prazo.
        beta_3 (float): Parâmetro de curvatura de longo prazo.
        lambda_1 (float): Parâmetro que controla a taxa de decaimento dos fatores de curto prazo.
        lambda_2 (float): Parâmetro que controla a taxa de decaimento dos fatores de longo prazo.

    Returns:
        pd.DataFrame: Df com uma curva padrão interpolada
    """
    df = pd.DataFrame({"vertices": VERTICES_PADRAO})
    df["tau"] = df["vertices"] / 360

    df["taxa"] = df.apply(lambda row: calc_nss(
        row["tau"], beta_0, beta_1, beta_2, beta_3, lambda_1, lambda_2), axis=1)

    return df
