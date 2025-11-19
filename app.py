import streamlit as st
import pandas as pd
import plotly.express as px
import basedosdados as bd

st.set_page_config(
    page_title="Análise do Diário Oficial da União",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Análise do Diário Oficial da União (DOU)")
st.write("Este app consulta a base pública do DOU usando BigQuery via basedosdados.")

# ---------------------------------------------------------
# BILLING ID FIXO (FUNCIONA COMO API KEY)
# ---------------------------------------------------------
BILLING_ID = "stf-data-477023"   # ← COLOQUE AQUI SUA CHAVE

# ---------------------------------------------------------
# CONSULTA SQL
# ---------------------------------------------------------
query = """
    SELECT
        dados.orgao AS orgao,
        dados.data_publicacao AS data_publicacao,
        dados.url_versao_certificada AS url_versao_certificada,
        dados.ementa AS ementa
    FROM `basedosdados.br_imprensa_nacional_dou.secao_1` AS dados
    WHERE data_publicacao IS NOT NULL
"""

st.subheader("⏳ Carregando dados do DOU...")

try:
    # Consulta com billing_id já embutido no código
    df = bd.read_sql(
        query=query,
        billing_project_id=BILLING_ID
    )

    st.success("✅ Dados carregados com sucesso!")
    st.write(f"Total de registros obtidos: **{len(df):,}**")

    # ---------------------------------------------------------
    # TRATAMENTO DA BASE
    # ---------------------------------------------------------
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"])
    df["ano"] = df["data_publicacao"].dt.year

    # ---------------------------------------------------------
    # GRÁFICO 1 – Publicações por órgão
    # ---------------------------------------------------------
    st.subheader("🏛️ Quantidade de publicações por órgão (Top 30)")

    orgao_count = df["orgao"].value_counts().reset_index()
    orgao_count.columns = ["orgao", "quantidade"]

    fig1 = px.bar(
        orgao_count.head(30),
        x="quantidade",
        y="orgao",
        orientation="h",
        title="Top 30 órgãos por número de publicações"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------------------------------
    # GRÁFICO 2 – Publicações por ano
    # ---------------------------------------------------------
    st.subheader("📆 Publicações por ano")

    ano_count = df["ano"].value_counts().sort_index()

    fig2 = px.line(
        x=ano_count.index,
        y=ano_count.values,
        markers=True,
        title="Publicações no DOU por ano"
    )
    fig2.update_layout(xaxis_title="Ano", yaxis_title="Quantidade")

    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # VISUALIZAÇÃO DA TABELA
    # ---------------------------------------------------------
    st.subheader("📄 Amostra da base")
    st.dataframe(df.head(50))

    # ---------------------------------------------------------
    # DOWNLOAD
    # ---------------------------------------------------------
    st.download_button(
        label="📥 Baixar dados em CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="dou_dados.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error("❌ Erro ao consultar a base:")
    st.code(str(e))
