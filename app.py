# ============================
# GRÁFICO POR ÓRGÃO
# ============================

st.subheader("📊 Quantidade de Publicações por Órgão")

if df_filtrado.empty:
    st.info("Nenhuma publicação encontrada para gerar o gráfico.")
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
