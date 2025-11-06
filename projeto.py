import streamlit as st
import pandas as pd
import basedosdados as bd
from utils.gemini_client import GeminiClient
from utils.youtube_client import YouTubeClient

st.title("📘 Jurisprudência do STF com IA e Vídeos Educativos")
st.write("Pesquise temas jurídicos e veja como o STF decidiu — com vídeos explicativos!")

query = st.text_input("Digite um tema jurídico (ex: liberdade de expressão, aborto, corrupção...)")

if "gemini" not in st.session_state:
    try:
        st.session_state.gemini = GeminiClient()
        st.session_state.youtube = YouTubeClient()
    except Exception as e:
        st.error(f"Erro ao inicializar clientes: {e}")

if st.button("Buscar decisões e vídeos"):
    if query:
        gemini = st.session_state.gemini
        youtube = st.session_state.youtube

        tema = gemini.classify_theme(query)
        st.info(f"Tema identificado: **{tema}**")

        billing_id = st.secrets["billing_id"]
        sql = f"""
            SELECT
                ano, assunto_processo, ramo_direito
            FROM `basedosdados.br_stf_corte_aberta.decisoes`
            WHERE assunto_processo LIKE '%{tema}%'
            LIMIT 100
        """
        try:
            df = bd.read_sql(query=sql, billing_project_id=billing_id)
            if df.empty:
                st.warning("Nenhuma decisão encontrada para esse tema.")
            else:
                st.dataframe(df)
                resumo = gemini.summarize_text(str(df.head(3)))
                st.subheader("🧾 Resumo gerado pela IA")
                st.write(resumo)
        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")

        # ---- VÍDEOS ----
        st.subheader("▶️ Vídeos relacionados ao tema")
        try:
            videos = youtube.search_videos(tema)
            for v in videos:
                st.markdown(f"[🎥 {v['title']}]({v['url']})")
        except Exception as e:
            st.error(f"Erro ao buscar vídeos: {e}")
    else:
        st.warning("Por favor, digite uma questão jurídica.")
