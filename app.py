import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="Dashboard de Suprimentos",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Dashboard de Acompanhamento de Suprimentos")

# ---------------- UPLOAD DOS ARQUIVOS ----------------
st.sidebar.header("📁 Upload de Arquivos")

file_pedidos = st.sidebar.file_uploader("Planilha de Pedidos", type=["xlsx"])
file_trocas = st.sidebar.file_uploader("Planilha de Trocas/Proativo", type=["xlsx"])

# ---------------- PROCESSAMENTO ----------------
if file_pedidos and file_trocas:

    df_pedidos = pd.read_excel(file_pedidos)
    df_trocas = pd.read_excel(file_trocas)

    # 🔗 JUNÇÃO DAS PLANILHAS
    df = pd.merge(
        df_pedidos,
        df_trocas[['NumeroPedido', 'TrocaAntecipada', 'ProAtivo']],
        on='NumeroPedido',
        how='left'
    )

    # 🧹 TRATAR VALORES NULOS
    df['TrocaAntecipada'] = df['TrocaAntecipada'].fillna(0)
    df['ProAtivo'] = df['ProAtivo'].fillna(0)

    # ---------------- FILTROS ----------------
    st.sidebar.header("🔎 Filtros")

    estados = st.sidebar.multiselect(
        "Estado",
        options=df['Estado'].dropna().unique(),
        default=df['Estado'].dropna().unique()
    )

    df = df[df['Estado'].isin(estados)]

    # ---------------- KPIs ----------------
    total_pedidos = len(df)
    entregues = df[df['Status'] == 'Entregue'].shape[0]
    pendentes = df[df['Status'] == 'Pendente'].shape[0]
    quantidade_total = df['Quantidade'].sum()
    trocas = df['TrocaAntecipada'].sum()
    proativos = df['ProAtivo'].sum()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total Pedidos", total_pedidos)
    col2.metric("Entregues", entregues)
    col3.metric("Pendentes", pendentes)
    col4.metric("Quantidade", quantidade_total)
    col5.metric("Trocas Antecipadas", trocas)
    col6.metric("Proativos", proativos)

    st.markdown("---")

    # ---------------- GRÁFICOS ----------------
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        pedidos_estado = df['Estado'].value_counts().reset_index()
        pedidos_estado.columns = ['Estado', 'Quantidade']

        fig_bar = px.bar(
            pedidos_estado,
            x='Estado',
            y='Quantidade',
            title="📍 Pedidos por Estado",
            text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        status = df['Status'].value_counts().reset_index()
        status.columns = ['Status', 'Quantidade']

        fig_pie = px.pie(
            status,
            names='Status',
            values='Quantidade',
            title="📦 Status dos Pedidos",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------- TABELA ----------------
    st.markdown("### 📋 Dados detalhados")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("⚠️ Faça upload das duas planilhas para visualizar o dashboard.")