from datetime import datetime

import pandas as pd
from sqlalchemy import Column, DECIMAL, Date, Integer, String, UniqueConstraint, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


db = create_engine('sqlite:///src/instances/ajustes_bmf.db')
Session = sessionmaker(bind=db)
session = Session()


Base = declarative_base()


class Ajuste(Base):
    __tablename__ = "ajustes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_pregao = Column(Date, nullable=False)
    mercadoria = Column(String(50), nullable=False)
    vencimento = Column(String(3), nullable=False)
    preco_ajuste_anterior = Column(DECIMAL(13, 4), nullable=False)
    preco_ajuste = Column(DECIMAL(13, 4), nullable=False)
    variacao = Column(DECIMAL(13, 4), nullable=False)
    valor_ajuste_por_contrato = Column(DECIMAL(13, 4), nullable=False)

    __table_args__ = (
        UniqueConstraint("data_pregao", "mercadoria", "vencimento",
                         name="unique_data_pregao_mercadoria_vencimento"),
    )

    def __init__(self, data_pregao, mercadoria, vencimento, preco_ajuste_anterior, preco_ajuste, variacao, valor_ajuste_por_contrato):
        self.data_pregao = data_pregao
        self.mercadoria = mercadoria
        self.vencimento = vencimento
        self.preco_ajuste_anterior = preco_ajuste_anterior
        self.preco_ajuste = preco_ajuste
        self.variacao = variacao
        self.valor_ajuste_por_contrato = valor_ajuste_por_contrato


Base.metadata.create_all(bind=db)


def add_ajuste(ajuste: Ajuste) -> None:
    """
    Adiciona um único ajuste ao banco de dados.

    Args:
        ajuste (Ajuste): Objeto da classe Ajuste.
    """
    session_temp = Session()
    try:
        session_temp.add(ajuste)
        session_temp.commit()
        session_temp.close()

    except Exception as e:
        print(f"Ocorreu um erro ao adicionar o ajuste: {e}")
        session.rollback()
        session.close()


def add_ajustes_from_df(df: pd.DataFrame) -> bool:
    """
    Adiciona um único ajuste ao banco de dados.

    Args:
        ajuste (Ajuste): Objeto da classe Ajuste.

    Returns:
        bool: bool indicando se a operação foi bem sucedida, ou não.
    """
    session_temp = Session()
    try:
        ajustes = [
            Ajuste(
                data_pregao=row["data_pregao"],
                mercadoria=row["mercadoria"],
                vencimento=row["vencimento"],
                preco_ajuste_anterior=row["preco_ajuste_anterior"],
                preco_ajuste=row["preco_ajuste"],
                variacao=row["variacao"],
                valor_ajuste_por_contrato=row["valor_ajuste_por_contrato"]
            )
            for index, row in df.iterrows()
        ]

        session_temp.bulk_save_objects(ajustes)
        session_temp.commit()
        return True

    except Exception as e:
        session_temp.rollback()
        print(f"Erro ao adicionar ajustes do DataFrame no DB: {e}")
        return False

    finally:
        session_temp.close()


def query_db(data_pregao: str = None, mercadoria: str = None, vencimento: str = None) -> pd.DataFrame:
    """
    Consulta o banco de dados e retorna os ajustes filtrados como DataFrame.

    Args:
        data_pregao (str): Data do pregao para busca 'dd/mm/aaaa'.
        mercadoria (str): Nome da mercadoria para busca.
        vencimento (str): Vencimento da mercadoria para busca, deve estar no formato da CME "<M><YY>".

    Returns:
        pd.DataFrame: DataFrame contendo os dados da consulta.
    """
    session_temp = Session()
    try:
        query = session.query(Ajuste)

        if data_pregao:
            data_pregao = datetime.strptime(data_pregao, "%d/%m/%Y").date()
            query = query.filter_by(data_pregao=data_pregao)

        if mercadoria:
            query = query.filter_by(mercadoria=mercadoria)

        if vencimento:
            query = query.filter_by(vencimento=vencimento)

        df_query = pd.DataFrame([row.__dict__ for row in query])
        if len(df_query) == 0:
            return pd.DataFrame()

        df_query.drop("_sa_instance_state", axis=1, inplace=True)
        df_query["data_pregao"] = pd.to_datetime(df_query["data_pregao"])
        session_temp.close()
        df_query = df_query[["id", "data_pregao", "mercadoria", "vencimento",
                             "preco_ajuste_anterior", "preco_ajuste", "variacao", "valor_ajuste_por_contrato"]]

        return df_query

    except Exception as e:
        print(f"Erro na consulta ao banco: {e}")
        session_temp.close()
        return pd.DataFrame()


def query_mercadorias_na_data(data_pregao: str) -> list:
    """
    Consulta o banco de dados e retorna uma lista de mercadorias disponíveis para uma determina data.

    Args:
        data_pregao (str): Data do pregao para busca 'dd/mm/aaaa'.
    """
    df_query = query_db(data_pregao=data_pregao)

    try:
        items = df_query.mercadoria.unique().tolist()
        return items

    except:
        return []


def query_unique_in_column(nome_coluna: str) -> list:
    """
    Retorna uma lista de valores únicos para uma determinada coluna, em todas as datas.

    Args:
        nome_coluna (str): Nome da coluna de busca.
    """
    session_temp = Session()
    try:
        query = session_temp.execute(
            text(f"SELECT DISTINCT {nome_coluna} FROM ajustes;"))
        return [row[0] for row in query]

    except Exception as e:
        print(f"Erro ao buscar valores únicos na coluna {nome_coluna}: {e}")
        return []

    finally:
        session_temp.close()
