import streamlit as st
import pandas as pd
import altair as alt

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Análise DOU - Governo Lula",
    page_icon="📄",
    layout="wide"
)

# ==============================
# TÍTULO E DESCRIÇÃO
# ==============================
st.title("📄 Análise das Primeiras 2000 Publicações dos Ministérios do Governo Lula")

st.markdown(
    """
    Este painel permite explorar as primeiras **2000 publicações** dos Ministérios 
    no Diário Oficial da União, durante o governo Lula.  
    Use os filtros à esquerda para refinar os resultados e veja os dados em tabela ou gráficos.
    """
)

# ==============================
# CARREGAMENTO DE DADOS
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("projeto_p2.csv")
    return df

df = load_data()

# ==============================
# SIDEBAR - FILTROS
# ==============================
st.sidebar.header("🔎 Filtros das Publicações")

tipo_lista = sorted(df["tipo_edicao"].dropna().unique())
tipo_escolhido = st.sidebar.multiselect(
    "Filtrar por Tipo de Edição:",
    options=tipo_lista,
    default=[]
)

orgao_lista = sorted(df["orgao"].dropna().unique())
orgao_escolhido = st.sidebar.multiselect(
    "Filtrar por Órgão:",
    options=orgao_lista,
    default=[]
)

ementa_busca = st.sidebar.text_input(
    "Buscar texto na Ementa:",
    placeholder="Ex.: portaria, nomeação, exoneração..."
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 Dica: combine filtros para análises mais específicas.")

# ==============================
# APLICAÇÃO DOS FILTROS
# ==============================
df_filtrado = df.copy()

if tipo_escolhido:
    df_filtrado = df_filtrado[df_filtrado["tipo_edicao"].isin(tipo_escolhido)]

if orgao_escolhido:
    df_filtrado = df_filtrado[df_filtrado["orgao"].isin(orgao_escolhido)]

if ementa_busca:
    df_filtrado = df_filtrado[
        df_filtrado["ementa"].str.contains(ementa_busca, case=False, na=False)
    ]

# ==============================
# RESUMO EM CARDS (KPIs)
# ==============================
st.subheader("📌 Visão Geral dos Resultados Filtrados")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total de Publicações",
        value=len(df_filtrado)
    )

with col2:
    total_orgaos = df_filtrado["orgao"].nunique()
    st.metric(
        label="Órgãos Diferentes",
        value=total_orgaos
    )

with col3:
    if not df_filtrado.empty and "data_publicacao" in df_filtrado.columns:
        datas_unicas = sorted(df_filtrado["data_publicacao"].dropna().unique())
        if len(datas_unicas) > 0:
