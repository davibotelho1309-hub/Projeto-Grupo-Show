import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análise DOU", layout="wide")

# Carrega os dados do JSON
@st.cache_data
def load_data():
    return pd.read_json("dados.json")

df = load_data()

st.title("📊 Análises do Diário Oficial da União")

st.markdown("""
Este painel utiliza a base enviada para gerar gráficos sobre:

- Quantidade de publicações por **órgão**  
- Quantidade de publicações por **ementa**
""")

# ---------------------
# Gráfico 1: Publicações por órgão
# ---------------------
st.header("🔹 Quantidade de Publicações por Órgão")

publicacoes_orgao = df["orgao"].value_counts()

fig1, ax1 = plt.subplots(figsize=(10,6))
publicacoes_orgao.plot(kind="bar", ax=ax1)
ax1.set_title("Publicações por órgão")
ax1.set_ylabel("Quantidade")
ax1.set_xlabel("Órgão")
plt.xticks(rotation=90)

st.pyplot(fig1)

# ---------------------
# Gráfico 2: Publicações por ementa
# ---------------------
st.header("🔹 Quantidade de Publicações por Ementa")

# trata ementas vazias
df["ementa_tratada"] = df["ementa"].fillna("").replace("", "Sem ementa")

publicacoes_ementa = df["ementa_tratada"].value_counts().head(30)  # mostra só 30 maiores

fig2, ax2 = plt.subplots(figsize=(10,6))
publicacoes_ementa.plot(kind="bar", ax=ax2)
ax2.set_title("Publicações por ementa (top 30)")
ax2.set_ylabel("Quantidade")
ax2.set_xlabel("Ementa")
plt.xticks(rotation=90)

st.pyplot(fig2)

st.markdown("✔️ **Painel concluído!**")
