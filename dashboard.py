# ============================================================
# MENOTTECH | DASHBOARD ENTERPRISE
# Preparado para: Cloud • VPS • SaaS • Mobile • Multiempresa
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import BytesIO

# ============================================================
# CONFIGURAÇÃO GLOBAL
# ============================================================
st.set_page_config(
    page_title="MENOTTECH",
    layout="wide",
    page_icon="logo_menottech.jpeg"
)

# ============================================================
# ESTILO GLOBAL (Dark • Power BI / Tableau)
# ============================================================
st.markdown("""
<style>
.stApp { background:#0E1117; color:#FAFAFA; }
section[data-testid="stSidebar"] { background:#020617; }

.header {
    display:flex; align-items:center; gap:15px;
    border-bottom:1px solid #1f2937;
    padding-bottom:18px; margin-bottom:20px;
}
.header h1 { color:#38BDF8; margin:0; }
.header span { color:#9CA3AF; font-size:0.9rem; }

.kpi {
    background:#111827;
    padding:18px;
    border-radius:14px;
    text-align:center;
    box-shadow:0 0 0 1px #1f2937;
}

@media (max-width: 768px) {
    .header { flex-direction:column; align-items:flex-start; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIN (PRONTO PARA BANCO / JWT FUTURO)
# ============================================================
USERS = {
    "admin": {"senha": "admin123", "perfil": "Admin", "empresa": "Menottech"},
    "user": {"senha": "user123", "perfil": "Usuario", "empresa": "Menottech"}
}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login MENOTTECH")
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u in USERS and USERS[u]["senha"] == s:
            st.session_state.auth = True
            st.session_state.perfil = USERS[u]["perfil"]
            st.session_state.empresa = USERS[u]["empresa"]
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos")
    st.stop()

# ============================================================
# CABEÇALHO
# ============================================================
st.markdown("""
<div class="header">
    <img src="logo_menottech.png" width="70">
    <div>
        <h1>MENOTTECH</h1>
        <span>Dashboard Executivo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def padronizar_colunas(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip().str.lower()
        .str.replace(" ", "_").str.replace("/", "_")
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    return df

def export_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()

# ============================================================
# DADOS (Excel → fácil trocar por banco)
# ============================================================
clientes = padronizar_colunas(pd.read_excel("gestao_menottech.xlsx", "Clientes"))
pedidos = padronizar_colunas(pd.read_excel("gestao_menottech.xlsx", "Pedido_Vendas"))
financeiro = padronizar_colunas(pd.read_excel("gestao_menottech.xlsx", "Financeiro_Comercial"))

# ============================================================
# TRATAMENTO
# ============================================================
pedidos["data"] = pd.to_datetime(pedidos["data"], errors="coerce")
pedidos = pedidos.dropna(subset=["data"])
pedidos["mes"] = pedidos["data"].dt.strftime("%m/%Y")

if "lucro_bruto" not in pedidos.columns:
    pedidos["lucro_bruto"] = pedidos["valor_de_venda"] - (
        pedidos.get("custo_do_produto", 0) +
        pedidos.get("custo_instalacao", 0)
    )

# ============================================================
# SIDEBAR
# ============================================================
meses = sorted(pedidos["mes"].unique())
mes = st.sidebar.selectbox("📅 Mês", meses)

df = pedidos[pedidos["mes"] == mes]

financeiro["mes"] = financeiro["mes_ano"].astype(str)
meta = financeiro.loc[financeiro["mes"] == mes, "meta_do_mes"]
meta = meta.iloc[0] if not meta.empty else None

# ============================================================
# MÉTRICAS
# ============================================================
total = df["valor_de_venda"].sum()
lucro = df["lucro_bruto"].sum()
ticket = df["valor_de_venda"].mean()

# ============================================================
# ABAS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Geral", "📈 Comparativos", "🏆 Rankings", "🔮 Previsão", "📤 Exportar"
])

# ============================================================
# GERAL
# ============================================================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Faturamento", f"R$ {total:,.2f}")
    c2.metric("📈 Lucro", f"R$ {lucro:,.2f}")
    c3.metric("🎫 Ticket Médio", f"R$ {ticket:,.2f}")
    if meta:
        c4.metric("🎯 Meta", f"{(total/meta)*100:.0f}%")
        st.progress(min(total/meta, 1.0))

# ============================================================
# COMPARATIVOS
# ============================================================
with tab2:
    mensal = pedidos.groupby("mes", as_index=False)["valor_de_venda"].sum()
    fig = px.line(mensal, x="mes", y="valor_de_venda", markers=True)
    fig.update_layout(
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font_color="#FAFAFA"
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# RANKING
# ============================================================
with tab3:
    if "tecnico" in df.columns:
        ranking = (
            df.groupby("tecnico", as_index=False)["lucro_bruto"]
            .sum()
            .sort_values("lucro_bruto", ascending=False)
        )
        st.dataframe(ranking, use_container_width=True)

# ============================================================
# PREVISÃO (Linear simples – segura)
# ============================================================
with tab4:
    if len(mensal) > 2:
        x = np.arange(len(mensal))
        y = mensal["valor_de_venda"].values
        coef = np.polyfit(x, y, 1)
        previsao = coef[0] * (x[-1] + 1) + coef[1]
        st.metric("🔮 Próximo Mês (estimado)", f"R$ {previsao:,.2f}")

# ============================================================
# EXPORTAÇÃO
# ============================================================
with tab5:
    st.download_button(
        "📥 Baixar pedidos do mês",
        data=export_excel(df),
        file_name=f"pedidos_{mes}.xlsx"
    )

# ============================================================
# FOOTER
# ============================================================
st.caption("© Menottech • Dashboard Executivo • Pronto para SaaS")
