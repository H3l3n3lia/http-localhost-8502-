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

# =====================================
# ARQUIVO
# =====================================
arquivo = "gestao_menottech.xlsx"

# =====================================
# LEITURA DAS ABAS
# =====================================
clientes = pd.read_excel(arquivo, sheet_name="Clientes")
pedidos = pd.read_excel(arquivo, sheet_name="Pedido_Vendas")
financeiro = pd.read_excel(arquivo, sheet_name="Financeiro_Comercial")

# =====================================
# PADRONIZAR COLUNAS
# =====================================
pedidos = padronizar_colunas(pedidos)
financeiro = padronizar_colunas(financeiro)

# =====================================
# PREPARAÇÃO DOS DADOS (PEDIDOS)
# =====================================
pedidos["data"] = pd.to_datetime(pedidos["data"])
pedidos["mes"] = pedidos["data"].dt.strftime("%m/%Y")

# 👉 lucro calculado corretamente com base no seu Excel
pedidos["lucro"] = (
    pedidos["valor_de_venda"]
    - pedidos["custo_do_produto"]
    - pedidos["custo_instalacao"]
)

# =====================================
# PARÂMETROS FINANCEIROS
# =====================================
meta = financeiro["meta_do_mes"].iloc[0]

# ticket médio calculado automaticamente
ticket_medio = pedidos["valor_de_venda"].mean()

# =====================================
# FILTRO LATERAL
# =====================================
mes_selecionado = st.sidebar.selectbox(
    "📅 Selecione o mês",
    sorted(pedidos["mes"].unique())
)

df = pedidos[pedidos["mes"] == mes_selecionado]

# =====================================
# MÉTRICAS
# =====================================
total_vendido = df["valor_de_venda"].sum()
lucro_total = df["lucro"].sum()
qtd_pedidos = len(df)

faltam = max(0, meta - total_vendido)
vendas_previstas = int((faltam / ticket_medio) + 0.99)

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Total Vendido", f"R$ {total_vendido:,.2f}")
c2.metric("📈 Lucro", f"R$ {lucro_total:,.2f}")
c3.metric("🧾 Pedidos", qtd_pedidos)
c4.metric("🎯 Meta Atingida", f"{(total_vendido / meta) * 100:.0f}%")

st.progress(min(total_vendido / meta, 1.0))

st.info(
    f"🔮 Faltam R$ {faltam:,.2f} para a meta "
    f"(≈ {vendas_previstas} vendas no ticket médio)"
)

# =====================================
# GRÁFICOS
# =====================================
st.subheader("📊 Lucro por Fornecedor")
st.bar_chart(df.groupby("fornecedor")["lucro"].sum())

st.subheader("📋 Pedidos do mês")
st.dataframe(df)
