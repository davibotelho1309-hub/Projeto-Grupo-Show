import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import unicodedata

st.set_page_config(page_title="Análise DOU", layout="wide")

# Normaliza nomes de colunas: lower, sem acentos, sem espaços
def normalize_col(name: str) -> str:
    if not isinstance(name, str):
        return name
    name = name.strip().lower()
    name = unicodedata.normalize("NFKD", name)
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    name = name.replace(" ", "_")
    return name

@st.cache_data
def load_data(path="dados.json"):
    try:
        df = pd.read_json(path)
    except Exception:
        # tenta CSV se JSON falhar
        try:
            df = pd.read_csv(path)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo '{path}': {e}")
            return None

    # renomeia colunas normalizando
    col_map = {c: normalize_col(c) for c in df.columns}
    df = df.rename(columns=col_map)
    return df

st.title("📊 Análises do Diário Oficial da União")

st.markdown("""
Painel que gera:
- Quantidade de publicações por **órgão**
- Quantidade de publicações por **ementa**
""")

# botão para carregar arquivo alternativo (opcional)
uploaded = st.file_uploader("📁 Envie um JSON/CSV com as colunas (orgao, ementa) — opcional", type=["json","csv"])
if uploaded is not None:
    # salva temporariamente e carrega
    with open("dados_temp", "wb") as f:
        f.write(uploaded.getbuffer())
    df = load_data("dados_temp")
else:
    df = load_data("dados.json")

if df is None:
    st.stop()

# Verifica nomes de colunas possíveis para 'orgao' e 'ementa'
cols = df.columns.tolist()

def find_col(candidates):
    for c in candidates:
        if c in cols:
            return c
    return None

orgao_col = find_col(["orgao","órgão","orgão","orgao_","orgao"])
ementa_col = find_col(["ementa","emento","ementa_"])

# alternativa mais ampla: procurar substring
if orgao_col is None:
    for c in cols:
        if "org" in c:
            orgao_col = c
            break
if ementa_col is None:
    for c in cols:
        if "ement" in c:
            ementa_col = c
            break

# Se faltar coluna essencial, avisa e para
if orgao_col is None and ementa_col is None:
    st.error("Não foi encontrada nenhuma coluna parecida com 'orgao' nem com 'ementa' no arquivo. Verifique o nome das colunas e envie novamente.")
    st.write("Colunas detectadas:", cols)
    st.stop()

st.sidebar.markdown("### Opções de visualização")
top_n = st.sidebar.slider("Mostrar top N de ementas", 5, 100, 30)

# Gráfico por órgão
if orgao_col is not None:
    st.header("🔹 Quantidade de Publicações por Órgão")
    publicacoes_orgao = df[orgao_col].fillna("Sem órgão").astype(str).value_counts()
    fig1, ax1 = plt.subplots(figsize=(10,6))
    publicacoes_orgao.plot(kind="bar", ax=ax1)
    ax1.set_title("Publicações por órgão")
    ax1.set_ylabel("Quantidade")
    ax1.set_xlabel("Órgão")
    plt.xticks(rotation=90)
    st.pyplot(fig1)
else:
    st.info("Coluna de órgão não encontrada — gráfico por órgão não será exibido.")

# Gráfico por ementa
if ementa_col is not None:
    st.header("🔹 Quantidade de Publicações por Ementa (Top)")
    df["ementa_tratada"] = df[ementa_col].fillna("").astype(str).replace("", "Sem ementa")
    publicacoes_ementa = df["ementa_tratada"].value_counts().head(top_n)

    fig2, ax2 = plt.subplots(figsize=(10,6))
    publicacoes_ementa.plot(kind="bar", ax=ax2)
    ax2.set_title(f"Publicações por ementa (Top {top_n})")
    ax2.set_ylabel("Quantidade")
    ax2.set_xlabel("Ementa")
    plt.xticks(rotation=90)
    st.pyplot(fig2)
else:
    st.info("Coluna de ementa não encontrada — gráfico por ementa não será exibido.")

st.markdown("---")
st.write("Colunas detectadas no arquivo:", cols)
st.success("App carregado sem dependência de coluna 'ano'.")
