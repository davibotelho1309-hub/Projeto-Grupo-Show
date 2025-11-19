import streamlit as st
import pandas as pd
import basedosdados as bd
import plotly.express as px

# ----------------------------------------
# CONFIGURAÇÃO INICIAL DO APP
# ----------------------------------------
st.set_page_config(
    page_title="Análise do Diário Oficial da União",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Análise do Diário Oficial da União (DOU)")
st.write("Este aplicativo utiliza a base pública do DOU via *basedosdados* para gerar visualizações interativas.")

# ----------------------------------------
# INPUT DO USUÁRIO – BILLING ID
# ----------------------------------------
billing_id = st.text_input(
    "Digite seu Billing ID do Google Cloud (necessário para acessar a base):",
    type="default"
)

if billing_id:
    st.success("Billing ID carregado com sucesso! Agora você pode executar a consulta.")

    # ----------------------------------------
    # CONSULTA SQL
    # ----------------------------------------
    query = """
        SELECT
            dados.orgao AS orgao,
            dados.data_publicacao AS data_publicacao,
            dados.url_versao_certificada AS url_versao_certificada,
            dados.ementa AS ementa
        FROM `basedosdados.br_imprensa_nacional_dou.secao_1` AS dados
        WHERE data_publicacao IS NOT NULL
    """

    st.subheader("📥 Carregando dados do DOU...")

    try:
        df = bd.read_sql(query=query, billing_project_id=billing_id)

        st.success("Dados carregados com sucesso!")
        st.write(f"Quantidade de registros obtidos: **{len(df):,}**")

        # --------------------------
        # PRÉ-PROCESSAMENTO
        # --------------------------
        df["data_publicacao"] = pd.to_datetime(df["data_publicacao"])
        df["ano"] = df["data_publicacao"].dt.year

        # --------------------------
        # DOWNLOAD DA BASE
        # --------------------------
        st.download_button(
            label="📥 Baixar base de dados (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="dou_dados.csv",
            mime="text/csv"
        )

        # --------------------------
        # GRÁFICO 1: Publicações por órgão
        # --------------------------
        st.subheader("🏛️ Quantidade de publicações por órgão")

        orgao_count = df["orgao"].value_counts().reset_index()
        orgao_count.columns = ["orgao", "quantidade"]

        fig1 = px.bar(
            orgao_count.head(30),  # mostra só os 30 maiores
            x="quantidade",
            y="orgao",
            orientation="h",
            title="Top 30 órgãos com mais publicações no DOU",
        )
        st.plotly_chart(fig1, use_container_width=True)

        # --------------------------
        # GRÁFICO 2: Publicações por ano
        # --------------------------
        st.subheader("📆 Quantidade de publicações por ano")

        ano_count = df["ano"].value_counts().sort_index()

        fig2 = px.line(
            x=ano_count.index,
            y=ano_count.values,
            markers=True,
            title="Publicações no DOU por ano"
        )

        fig2.update_layout(
            xaxis_title="Ano",
            yaxis_title="Quantidade de Publicações"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # --------------------------
        # VISUALIZAÇÃO DA TABELA
        # --------------------------
        st.subheader("📄 Amostra dos dados carregados")
        st.dataframe(df.head(50))

    except Exception as e:
        st.error("❌ Erro ao consultar a base:")
        st.code(str(e))

else:
    st.info("⏳ Digite seu Billing ID para iniciar a consulta.")
