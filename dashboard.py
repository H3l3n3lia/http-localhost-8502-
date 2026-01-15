import pandas as pd
import streamlit as st

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(page_title="MENOTTECH", layout="wide")
st.title("📊 MENOTTECH | Dashboard Gerencial")

# ===============================
# FUNÇÕES AUXILIARES
# ===============================
def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza nomes de colunas:
    - remove espaços extras
    - minúsculas
    - troca espaços por _
    - remove acentos
    """
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    return df


def carregar_excel(nome_arquivo: str, aba: str) -> pd.DataFrame:
    try
