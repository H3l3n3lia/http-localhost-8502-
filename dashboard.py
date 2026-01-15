import pandas as pd
import streamlit as st

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================
st.set_page_config(page_title="MENOTTECH", layout="wide")
st.title("📊 MENOTTECH | Dashboard Gerencial")

# =====================================
# FUNÇÃO PARA PADRONIZAR COLUNAS
# =====================================
def padronizar_colunas(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    return df

# =====================================
# LEITURA DO EXCEL
# =====================================
arquivo = "gestao_menottech.xlsx"

clientes = pd.read_excel(arquivo, sheet_name="Clientes")
pedidos = pd.read_excel(arquivo, sheet_name="Pedido_Vendas")
tecnicos = pd.read_excel(arquivo, sheet_name="Tecnicos_Parceiros")
financeiro = pd.read_excel(arquivo, sheet_name="Financeiro_Comercial")

# =====================================
# PADRONIZAR COLUNAS
# =====================================
pedidos = padronizar_colunas(pedidos)
financeiro = padronizar_colunas(financeiro)

# =====================================
# PREPARAÇÃO DOS DADOS
# =====================================
pedidos["data"] = pd.to_datetime(pedidos["data"])
pedidos["mes"] = pedidos["data"].dt.strftime("%m/%Y")
pedidos["lucro"] = pedidos["valor_venda"] - pedidos["custo_tecnico"]

# =====================================
# PARÂMETROS FINANCEIROS
# =====================================
meta = financeiro["meta"].iloc[0]
ticket = financeiro["ticket_medio"].iloc[0]

# =====================================
# FILTRO LATERAL
# =====================================
mes_selecionado = st.sidebar.selectbox(
    "📅 Selecione o mês",
    sorted(pedidos["mes"].unique())
)

df = pedidos[pedidos["mes"] == mes_selecionado]

# =====================================
# MÉTRICAS PRINCIPAIS
# =====================================
total_vendido = df["valor_venda"].sum()
lucro_total = df["lucro"].sum()
quantidade_pedidos = len(df)

faltam = max(0, meta - total_vendido)
vendas_previstas = int((faltam / ticket) + 0.99)

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Vendido", f"R$ {total_vendido:,.2f}")
col2.metric("📈 Lucro", f"R$ {lucro_total:,.2f}")
col3.metric("🧾 Pedidos", quantidade_pedidos)
col4.metric("🎯 Meta Atingida", f"{(total_vendido / meta) * 100:.0f}%")

st.progress(min(total_vendido / meta, 1.0))
st.info(
    f"🔮 Faltam R$ {faltam:,.2f} para a meta "
    f"(≈ {vendas_previstas} vendas)"
)

# =====================================
# GRÁFICOS
# =====================================
st.subheader("📊 Luc
