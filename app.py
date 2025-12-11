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
    # Tentativa simples de pegar intervalo de datas como texto
    if not df_filtrado.empty and "data_publicacao" in df_filtrado.columns:
        datas_unicas = sorted(df_filtrado["data_publicacao"].dropna().unique())
        data_inicial = datas_unicas[0]
        data_final = datas_unicas[-1]
        st.metric(
            label="Período das Publicações",
            value=f"{data_inicial} → {data_final}"
        )
    else:
        st.metric(
            label="Período das Publicações",
            value="N/A"
        )

# ==============================
# ABAS: TABELA E GRÁFICOS
# ==============================
tab_tabela, tab_data, tab_orgao = st.tabs(
    ["📋 Tabela de Dados", "📆 Publicações por Data", "🏢 Publicações por Órgão"]
)

# --------- TABELA ---------
with tab_tabela:
    st.subheader("📋 Tabela de Publicações Filtradas")
    st.write(
        f"Total de publicações encontradas: **{len(df_filtrado)}**"
    )

    if df_filtrado.empty:
        st.info("Nenhuma publicação encontrada com os filtros selecionados.")
    else:
        st.dataframe(df_filtrado, use_container_width=True)

# --------- GRÁFICO POR DATA ---------
with tab_data:
    st.subheader("📊 Quantidade de Publicações por Data de Publicação")

    if df_filtrado.empty:
        st.info("Nenhuma publicação encontrada para gerar o gráfico.")
    else:
        grafico_tipo = (
            alt.Chart(df_filtrado)
            .mark_bar()
            .encode(
                x=alt.X("data_publicacao:N", title="Data de Publicação"),
                y=alt.Y("count():Q", title="Quantidade"),
                tooltip=["data_publicacao", "count()"]
            )
            .properties(height=400)
        )

        st.altair_chart(grafico_tipo, use_container_width=True)

# --------- GRÁFICO POR ÓRGÃO ---------
with tab_orgao:
    st.subheader("📊 Quantidade de Publicações por Órgão")

    if df_filtrado.empty:
        st.info("Nenhuma publicação encontrada para gerar o gráfico de órgãos.")
    else:
        grafico_orgao = (
            alt.Chart(df_filtrado)
            .mark_bar()
            .encode(
                x=alt.X("orgao:N", title="Órgão", sort="-y"),
                y=alt.Y("count():Q", title="Quantidade"),
                tooltip=["orgao", "count()"]
            )
            .properties(height=400)
        )

        st.altair_chart(grafico_orgao, use_container_width=True)

# ==============================
# RODAPÉ
# ==============================
st.markdown("---")
st.caption(
    "Painel desenvolvido para análise exploratória das publicações no DOU. "
    "Ajuste os filtros para refinar os resultados."
)
