import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Análise DOU", layout="wide")

st.title("📄 Análise das Primeiras 1000 Publicações dos Ministérios do Governo Lula")


@st.cache_data
def load_data():
    df = pd.read_csv("projeto_pf.csv")
    return df

df = load_data()

st.subheader("Filtros das Publicações")



tipo_lista = sorted(df["tipo_edicao"].dropna().unique())
tipo_escolhido = st.multiselect("Filtrar por Tipo de Edição:", tipo_lista)


orgao_lista = sorted(df["orgao"].dropna().unique())
orgao_escolhido = st.multiselect("Filtrar por Órgão:", orgao_lista)


ementa_busca = st.text_input("Buscar na Ementa (texto livre):")



df_filtrado = df.copy()

if tipo_escolhido:
    df_filtrado = df_filtrado[df_filtrado["tipo_edicao"].isin(tipo_escolhido)]

if orgao_escolhido:
    df_filtrado = df_filtrado[df_filtrado["orgao"].isin(orgao_escolhido)]

if ementa_busca:
    df_filtrado = df_filtrado[
        df_filtrado["ementa"].str.contains(ementa_busca, case=False, na=False)
    ]



st.subheader("Resultados Filtrados")
st.write(f"Total de publicações encontradas: **{len(df_filtrado)}**")

st.dataframe(df_filtrado, use_container_width=True)



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
            tooltip=["data_publicacao", "count()"],
            color="data_publicacao:N"
        )
    )

    st.altair_chart(grafico_tipo, use_container_width=True)



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
            tooltip=["orgao", "count()"],
            color="orgao:N"
        )
    )

    st.altair_chart(grafico_orgao, use_container_width=True)
