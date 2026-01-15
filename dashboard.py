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
        .str.replace("/", "_")
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    return df

# =====================================
# LEITURA DOS DADOS
# =====================================
try:
    clientes = pd.read_excel("gestao_menottech.xlsx", sheet_name="Clientes")
    pedidos = pd.read_excel("gestao_menottech.xlsx", sheet_name="Pedido_Vendas")
    tecnicos = pd.read_excel("gestao_menottech.xlsx", sheet_name="Tecnicos_Parceiros")
    financeiro = pd.read_excel("gestao_menottech.xlsx", sheet_name="Financeiro_Comercial")
except FileNotFoundError:
    st.error("⚠️ Arquivo 'gestao_menottech.xlsx' não encontrado. Verifique se ele está na mesma pasta do dashboard.")
    st.stop()

# =====================================
# PADRONIZAÇÃO DE COLUNAS
# =====================================
clientes = padronizar_colunas(clientes)
pedidos = padronizar_colunas(pedidos)
tecnicos = padronizar_colunas(tecnicos)
financeiro = padronizar_colunas(financeiro)

# =====================================
# TRATAMENTO DE PEDIDOS
# =====================================
pedidos["data"] = pd.to_datetime(pedidos["data"], errors="coerce")
pedidos = pedidos.dropna(subset=["data"])  # remove linhas sem data
pedidos["mes"] = pedidos["data"].dt.strftime("%m/%Y")

# Calcula lucro bruto se não existir
if "lucro_bruto" not in pedidos.columns:
    pedidos["lucro_bruto"] = pedidos["valor_de_venda"] - (pedidos.get("custo_do_produto", 0) + pedidos.get("custo_instalacao", 0))

# =====================================
# FILTRO DE MÊS
# =====================================
meses_disponiveis = sorted(pedidos["mes"].unique())
if not meses_disponiveis:
    st.warning("⚠️ Não há dados de pedidos disponíveis.")
    st.stop()

mes_selecionado = st.sidebar.selectbox(
    "📅 Selecione o mês",
    meses_disponiveis
)

df = pedidos[pedidos["mes"] == mes_selecionado]

# =====================================
# PARÂMETROS FINANCEIROS
# =====================================
financeiro["mes"] = financeiro["mes_ano"].astype(str)
meta_mes = financeiro.loc[financeiro["mes"] == mes_selecionado, "meta_do_mes"]

if meta_mes.empty:
    st.warning(f"⚠️ Não existe meta cadastrada para {mes_selecionado}")
    meta = None
else:
    meta = meta_mes.iloc[0]

ticket_medio = pedidos["valor_de_venda"].mean()

# =====================================
# MÉTRICAS PRINCIPAIS
# =====================================
total_vendido = df["valor_de_venda"].sum()
lucro_total = df["lucro_bruto"].sum()
qtd_pedidos = len(df)

if meta:
    faltam = max(0, meta - total_vendido)
else:
    faltam = 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Vendido", f"R$ {total_vendido:,.2f}")
col2.metric("📈 Lucro", f"R$ {lucro_total:,.2f}")
col3.metric("🧾 Pedidos", qtd_pedidos)
if meta:
    col4.metric("🎯 Meta Atingida", f"{(total_vendido/meta)*100:.0f}%")
else:
    col4.metric("🎯 Meta", "Não cadastrada")

# Barra de progresso
if meta:
    st.progress(min(total_vendido/meta, 1.0))

st.info(f"🔮 Faltam R$ {faltam:,.2f} | ≈ {int((faltam/ticket_medio)+0.99)} vendas para a meta")

# =====================================
# GRÁFICOS
# =====================================
st.subheader("Lucro por Técnico")
if "tecnico" in df.columns:
    st.bar_chart(df.groupby("tecnico")["lucro_bruto"].sum())
else:
    st.info("⚠️ Coluna 'tecnico' não encontrada nos pedidos.")

st.subheader("Pedidos do Mês")
st.dataframe(df)
