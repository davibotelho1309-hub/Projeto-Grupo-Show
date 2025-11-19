import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Análise DOU", layout="wide")

st.title("📄 Análise de Publicações do Diário Oficial da União")

# ============================
# Carregamento dos dados
# ============================
@st.cache_data
def load_data():
    df = pd.read_json("dados.json")
    return df

df = load_data()

st.subheader("Filtros das Publicações")

# ============================
# FILTROS
# ============================

# filtro por tipo_edição
tipo_lista = sorted(df["tipo_edicao"].dropna().unique())
tipo_escolhido = st.multiselect("Filtrar por Tipo de Edição:", tipo_lista)

# filtro por órgão
orgao_lista = sorted(df["orgao"].dropna().unique())
orgao_escolhido = st.multiselect("Filtrar por Órgão:", orgao_lista)

# filtro por ementa (texto)
ementa_busca = st.text_input("Buscar na Ementa (texto livre):")

# ============================
# APLICAÇÃO DOS FILTROS
# ============================

df_filtrado = df.copy()

if tipo_escolhido:
    df_filtrado = df_filtrado[df_filtrado["tipo_edicao"].isin(tipo_escolhido)]

if orgao_escolhido:
    df_filtrado = df_filtrado[df_filtrado["orgao"].isin(orgao_escolhido)]

if ementa_busca:
    df_filtrado = df_filtrado[
        df_filtrado["ementa"].str.contains(ementa_busca, case=False, na=False)
    ]

# ============================
# RESULTADOS
# ============================

st.subheader("Resultados Filtrados")
st.write(f"Total de publicações encontradas: **{len(df_filtrado)}**")

st.dataframe(df_filtrado, use_container_width=True)

# ============================
# GRÁFICO
# ============================

st.subheader("📊 Quantidade de Publicações por Tipo de Edição")

grafico = (
    alt.Chart(df_filtrado)
    .mark_bar()
    .encode(
        x=alt.X("tipo_edicao:N", title="Tipo de Edição"),
        y=alt.Y("count():Q", title="Quantidade"),
        tooltip=["tipo_edicao", "count()"],
        color="tipo_edicao:N"
    )
)

st.altair_chart(grafico, use_container_width=True)

