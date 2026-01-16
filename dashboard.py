import streamlit as st
import pandas as pd
import os
import altair as alt

# ============================
# CONFIGURAÇÃO DA PÁGINA
# ============================
st.set_page_config(page_title="MENOTTECH | Dashboard", layout="wide")

# ============================
# ESTILO FUNDO ESCURO E CARDS
# ============================
st.markdown("""
<style>
.stApp { background-color: #0E1117; color: #FAFAFA; }
[data-testid="stSidebar"] { background-color: #020617; }
.stMetricLabel { color: #9CA3AF; font-size:14px;}
.stMetricValue { font-size:22px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ============================
# CABEÇALHO COM LOGO
# ============================
col_logo, col_title = st.columns([1,6])
with col_logo:
    logo_path = "logo_menottech.jpeg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.write("Logo não encontrado")
with col_title:
    st.markdown("""
    <h1 style="color:#38BDF8; margin-bottom:0;">MENOTTECH</h1>
    <span style="color:#9CA3AF;">Dashboard Gerencial</span>
    """, unsafe_allow_html=True)
st.divider()

# ============================
# SIDEBAR COM FILTRO DE MÊS
# ============================
st.sidebar.header("📅 Filtros")
mes_selecionado = st.sidebar.selectbox("Selecione o mês", ["01/2026","02/2026","03/2026"])

# ============================
# LEITURA SEGURA DO EXCEL
# ============================
excel_file = "gestao_menottech.xlsx"
if os.path.exists(excel_file):
    try:
        clientes = pd.read_excel(excel_file, sheet_name="Clientes")
        pedidos = pd.read_excel(excel_file, sheet_name="Pedido_Vendas")
        tecnicos = pd.read_excel(excel_file, sheet_name="Tecnicos_Parceiros")
        financeiro = pd.read_excel(excel_file, sheet_name="Financeiro_Comercial")
        st.success("✅ Excel carregado com sucesso")
    except:
        clientes = pedidos = tecnicos = financeiro = pd.DataFrame()
        st.error("Erro ao ler o Excel")
else:
    clientes = pedidos = tecnicos = financeiro = pd.DataFrame()
    st.warning("⚠️ Excel não encontrado, usando dados fictícios")

# ============================
# PADRONIZAÇÃO DE COLUNAS
# ============================
def padronizar_colunas(df):
    df = df.copy()
    df.columns = (df.columns.astype(str)
                  .str.strip()
                  .str.lower()
                  .str.replace(" ","_")
                  .str.replace("/","_")
                  .str.normalize("NFKD")
                  .str.encode("ascii", errors="ignore")
                  .str.decode("utf-8"))
    return df

if not pedidos.empty:
    pedidos = padronizar_colunas(pedidos)
    financeiro = padronizar_colunas(financeiro)

# ============================
# TRATAMENTO DE PEDIDOS
# ============================
if not pedidos.empty:
    pedidos["data"] = pd.to_datetime(pedidos["data"], errors="coerce")
    pedidos = pedidos.dropna(subset=["data"])
    pedidos["mes"] = pedidos["data"].dt.strftime("%m/%Y")
    pedidos["dia"] = pedidos["data"].dt.day
    if "lucro_bruto" not in pedidos.columns:
        pedidos["lucro_bruto"] = pedidos["valor_de_venda"] - (
            pedidos.get("custo_do_produto",0)+pedidos.get("custo_instalacao",0)
        )
    df = pedidos[pedidos["mes"]==mes_selecionado]
else:
    df = pd.DataFrame()

# ============================
# CÁLCULO DE KPIS E MINI GRÁFICOS
# ============================
if not df.empty and not financeiro.empty:
    total_vendido = df["valor_de_venda"].sum()
    lucro_total = df["lucro_bruto"].sum()
    qtd_pedidos = len(df)

    financeiro["mes"] = financeiro["mes_ano"].astype(str)
    meta_mes = financeiro.loc[financeiro["mes"]==mes_selecionado, "meta_do_mes"]
    meta = meta_mes.iloc[0] if not meta_mes.empty else None
    ticket_medio = df["valor_de_venda"].mean() if len(df)>0 else 1
    faltam = max(0, meta-total_vendido) if meta else 0

    # Mini gráfico Total Vendido diário
    mini_total = df.groupby("dia")["valor_de_venda"].sum().reset_index()
    chart_total = alt.Chart(mini_total).mark_line(color="#22C55E").encode(
        x="dia",
        y="valor_de_venda"
    ).properties(height=50, width=120)
    
    # Mini gráfico Lucro diário
    mini_lucro = df.groupby("dia")["lucro_bruto"].sum().reset_index()
    chart_lucro = alt.Chart(mini_lucro).mark_line(color="#38BDF8").encode(
        x="dia",
        y="lucro_bruto"
    ).properties(height=50, width=120)
    
    # Mini gráfico Pedidos diário
    mini_pedidos = df.groupby("dia").size().reset_index(name="pedidos")
    chart_pedidos = alt.Chart(mini_pedidos).mark_line(color="#FACC15").encode(
        x="dia",
        y="pedidos"
    ).properties(height=50, width=120)
else:
    total_vendido = lucro_total = qtd_pedidos = faltam = 0
    meta = None
    ticket_medio = 1
    chart_total = chart_lucro = chart_pedidos = None

# ============================
# FUNÇÃO COR KPIS
# ============================
def cor_kpi(valor, meta):
    if meta is None: return "#38BDF8"
    pct = valor/meta
    if pct>=1: return "#22C55E"
    elif pct>=0.7: return "#FACC15"
    else: return "#EF4444"

# ============================
# LAYOUT KPIS COM MINI GRÁFICOS
# ============================
st.subheader("📊 KPIs do Mês")
cols = st.columns(4)

with cols[0]:
    st.metric("💰 Total Vendido", f"R$ {total_vendido:,.2f}", delta=f"{(total_vendido/meta*100-100):.0f}%" if meta else None)
    if chart_total: st.altair_chart(chart_total, use_container_width=True)

with cols[1]:
    st.metric("📈 Lucro", f"R$ {lucro_total:,.2f}")
    if chart_lucro: st.altair_chart(chart_lucro, use_container_width=True)

with cols[2]:
    st.metric("🧾 Pedidos", qtd_pedidos)
    if chart_pedidos: st.altair_chart(chart_pedidos, use_container_width=True)

with cols[3]:
    st.metric("🎯 Meta Atingida", f"{(total_vendido/meta)*100:.0f}%" if meta else "Não cadastrada")

# Barra de progresso animada
if meta:
    st.progress(min(total_vendido/meta,1.0))

st.info(f"🔮 Faltam R$ {faltam:,.2f} | ≈ {int((faltam/ticket_medio)+0.99)} vendas para a meta")

# ============================
# GRÁFICO DE LUCRO POR TÉCNICO
# ============================
st.subheader("Lucro por Técnico")
if not df.empty and "tecnico" in df.columns:
    chart = alt.Chart(df.groupby("tecnico")["lucro_bruto"].sum().reset_index()).mark_bar(
        color="#38BDF8"
    ).encode(
        x=alt.X("tecnico", sort="-y"),
        y="lucro_bruto",
        tooltip=["tecnico","lucro_bruto"]
    )
    st.altair_chart(chart,use_container_width=True)
else:
    st.info("⚠️ Dados insuficientes para gráfico de técnicos")

# ============================
# TABELA DE PEDIDOS
# ============================
st.subheader("Pedidos do Mês")
if not df.empty:
    st.dataframe(df)
else:
    st.info("⚠️ Nenhum pedido disponível para o mês selecionado")

