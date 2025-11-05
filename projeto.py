import streamlit as st
from dotenv import load_dotenv
import os

from utils.gemini_client import GeminiClient
from utils.stf_client import STFClient
from utils.youtube_client import YouTubeClient

load_dotenv()

st.set_page_config(page_title="STF Assistente (Gemini)", layout="wide")

st.title("Assistente de Jurisprudência — STF (2020–2025)")

user_query = st.text_area("Descreva a questão jurídica (ex.: 'Existe previsão do STF sobre fake news nas eleições 2022?')", height=120)

col1, col2 = st.columns([2,1])

with col2:
    st.write("Parâmetros")
    max_results = st.slider("Máx. decisões a buscar", min_value=1, max_value=10, value=3)

if st.button("Pesquisar"):
    if not user_query.strip():
        st.warning("Digite uma pergunta.")
    else:
        with st.spinner("Processando com Gemini..."):
            gemini = GeminiClient()
            theme = gemini.classify_theme(user_query)   # retorna string curta de tema
            st.markdown(f"**Tema identificado (por Gemini):** {theme}")

        st.info("Buscando decisões relevantes (2020–2025)...")
        stf = STFClient()
        results = stf.search_by_query(user_query, theme=theme, year_from=2020, year_to=2025, limit=max_results)

        if not results:
            st.warning("Nenhuma decisão encontrada com os parâmetros atuais.")
        else:
            for r in results:
                st.subheader(r.get("titulo") or r.get("ementa") or "Decisão")
                st.write(f"**Órgão:** {r.get('orgao','-')}  •  **Data:** {r.get('data','-')}  •  **Relator:** {r.get('relator','-')}")
                st.write("**Ementa / trecho relevante:**")
                st.write(r.get("trecho", r.get("ementa","(sem texto)"))[:2000])

                with st.expander("Resumo explicativo (linguagem simples)"):
                    summary = gemini.summarize_and_explain(r.get("trecho") or r.get("ementa",""))
                    st.write(summary)

            # Sugestão de vídeos
            st.markdown("---")
            st.markdown("### Vídeos sugeridos (YouTube)")
            yt = YouTubeClient()
            videos = yt.search_videos(query=theme or user_query, max_results=3)
            for v in videos:
                st.markdown(f"- [{v['title']}]({v['url']}) — {v['channelTitle']} ({v['publishedAt'][:10]})")

        st.success("Pronto ✅")
