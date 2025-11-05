import basedosdados as bd
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

BILLING_ID = os.getenv("BIGQUERY_BILLING_ID")

def buscar_decisoes_stf(tema: str, limit: int = 100) -> pd.DataFrame:
    query = f"""
        SELECT
            dados.ano AS ano,
            dados.assunto_processo AS assunto_processo,
            dados.ramo_direito AS ramo_direito,
            dados.ementa AS ementa,
            dados.resultado AS resultado
        FROM `basedosdados.br_stf_corte_aberta.decisoes` AS dados
        WHERE LOWER(dados.assunto_processo) LIKE '%{tema.lower()}%'
           OR LOWER(dados.ramo_direito) LIKE '%{tema.lower()}%'
           OR LOWER(dados.ementa) LIKE '%{tema.lower()}%'
        LIMIT {limit}
    """
    try:
        df = bd.read_sql(query=query, billing_project_id=BILLING_ID)
        return df
    except Exception as e:
        print(f"Erro ao consultar base do STF: {e}")
        return pd.DataFrame()
