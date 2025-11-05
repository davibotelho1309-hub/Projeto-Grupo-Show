pip install -r requirements.txt

import streamlit as st
from utils.gemini_client import GeminiClient
from utils.stf_client import buscar_decisoes_stf
from utils.youtube_client import buscar_videos_youtube

st.set_page_config(page_title="STF Explicado por IA", page_icon="⚖️", layout="wide")

st.title("⚖️ STF Explicado por IA")
st.markdown("Explore decisões reais do Supremo Tribunal Federal explicadas por Inteligência Artificial.")

user_query = st.text_input("Digite sua dúvida jurídica:")

if user_query:
    with st.spinner("Analisando sua dúvida..."):
        gemini = GeminiClient()
        tema = gemini.classify_theme(user_query)
    st.success(f"🧠 Tema identificado: **{tema}**")

    with st.spinner("Buscando decisões no STF..."):
        decisoes = buscar_decisoes_stf(tema)

    if decisoes.empty:
        st.warning("Nenhuma decisão encontrada sobre esse tema.")
    else:
        st.info(f"Foram encontradas **{len(decisoes)} decisões** relacionadas ao tema **{tema}**.")

        ementas = decisoes["ementa"].dropna().tolist()[:10]

        with st.spinner("Gerando resumo com Gemini..."):
            resumo = gemini.summarize_decisions(ementas, tema)
        st.markdown("### 📄 Resumo das decisões do STF")
        st.write(resumo)

        st.markdown("---")
        st.markdown("### 🎥 Expanda seu aprendizado com vídeos relacionados")
        videos = buscar_videos_youtube(tema)

        for v in videos:
            st.markdown(f"**[{v['titulo']}]({v['url']})** — *{v['canal']}*")

st.markdown("---")
st.caption("Desenvolvido por Davi — IA + Dados Abertos do STF + Gemini + YouTube API")
