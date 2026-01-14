import pandas as pd
import streamlit as st

st.set_page_config(page_title="MENOTTECH", layout="wide")
st.title("📊 MENOTTECH | Dashboard Gerencial")

# Ler planilha
clientes = pd.read_excel("gestao_menottech.xlsx", sheet_name="Clientes")
pedidos = pd.read_excel("gestao_menottech.xlsx", sheet_name="Pedidos")
tecnicos = pd.read_excel("gestao_menottech.xlsx", sheet_name="Tecnicos")
financeiro = pd.read_excel("gestao_menottech.xlsx", sheet_name="Financeiro")

# Preparar dados
pedidos["Data"] = pd.to_datetime(pedidos["Data"])
pedidos["Mes"] = pedidos["Data"].dt.strftime("%m/%Y")
pedidos["Lucro"] = pedidos["Valor_Venda"] - pedidos["Custo_Tecnico"]

# Parâmetros
meta = financeiro["Meta"].iloc[0]
ticket = financeiro["Ticket_Medio"].iloc[0]

# Filtro
mes = st.sidebar.selectbox("Mês", pedidos["Mes"].unique())
df = pedidos[pedidos["Mes"] == mes]

# Métricas principais
total = df["Valor_Venda"].sum()
lucro = df["Lucro"].sum()
qtd = len(df)
faltam = max(0, meta - total)
vendas_previstas = int((faltam / ticket) + 0.99)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Vendido", f"R$ {total:,.2f}")
col2.metric("📈 Lucro", f"R$ {lucro:,.2f}")
col3.metric("🧾 Pedidos", qtd)
col4.metric("🎯 Meta", f"{(total/meta)*100:.0f}%")

st.progress(min(total/meta, 1.0))
st.info(f"🔮 Faltam R$ {faltam:,.2f} | ≈ {vendas_previstas} vendas para a meta")

# Gráficos
st.subheader("Lucro por Técnico")
st.bar_chart(df.groupby("Tecnico")["Lucro"].sum())

st.subheader("Pedidos do Mês")
st.dataframe(df)
