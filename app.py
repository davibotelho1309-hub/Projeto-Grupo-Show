# app.py
import json
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
import altair as alt

# -------------------------
# Config / Helpers
# -------------------------
st.set_page_config(page_title="DOU — Visualizador", layout="wide", initial_sidebar_state="expanded")

DEFAULT_DATAFILE = Path("data.json")  # coloque seu JSON no repositório com esse nome

SUBJECT_REGEX = re.compile(r"\d+\s*-\s*([^|]+)")  # captura o "1 - Texto do assunto" -> pega "Texto do assunto"

@st.cache_data
def load_json_file(path: Path) -> pd.DataFrame:
    raw = json.loads(path.read_text(encoding="utf-8"))
    df = pd.DataFrame(raw)
    return df

@st.cache_data
def load_uploaded_file(uploaded) -> pd.DataFrame:
    # aceita .json, .csv
    if uploaded.name.lower().endswith(".json"):
        raw = json.load(uploaded)
        df = pd.DataFrame(raw)
    else:
        # tenta CSV
        df = pd.read_csv(uploaded)
    return df

def extract_main_subject(text: str) -> str:
    if not isinstance(text, str):
        return "Desconhecido"
    m = SUBJECT_REGEX.search(text)
    if m:
        return m.group(1).strip()
    # fallback: pega até o primeiro "||" ou todo texto
    if "||" in text:
        return text.split("||")[0].strip()
    return text.strip()

# -------------------------
# UI: Side bar
# -------------------------
st.sidebar.title("Configurações")
st.sidebar.markdown("Carregue uma base (JSON ou CSV) ou use a base padrão incluída no repositório.")
uploaded_file = st.sidebar.file_uploader("Upload: JSON/CSV (opcional)", type=["json", "csv"])

show_table = st.sidebar.checkbox("Mostrar tabela de dados", value=False)
top_n_subjects = st.sidebar.number_input("Top N assuntos (para gráfico)", min_value=3, max_value=50, value=10)

# -------------------------
# Load data
# -------------------------
df: Optional[pd.DataFrame] = None
if uploaded_file:
    try:
        df = load_uploaded_file(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"Erro ao ler arquivo enviado: {e}")
else:
    if DEFAULT_DATAFILE.exists():
        try:
            df = load_json_file(DEFAULT_DATAFILE)
        except Exception as e:
            st.sidebar.error(f"Erro ao ler {DEFAULT_DATAFILE}: {e}")
    else:
        st.sidebar.warning(f"{DEFAULT_DATAFILE} não encontrado no repositório. Faça upload de um arquivo JSON/CSV.")
        df = pd.DataFrame()  # vazio

# -------------------------
# Basic validation / normalization
# -------------------------
if df is None or df.empty:
    st.title("DOU — Visualizador")
    st.info("Nenhum dado carregado. Coloque um arquivo `data.json` no repositório ou faça upload aqui.")
    st.stop()

# normaliza colunas: termos em minúsculas para checar existência
cols_lower = {c.lower(): c for c in df.columns}
# campo ano
if "ano" in cols_lower:
    ano_col = cols_lower["ano"]
else:
    # tenta achar coluna parecida
    candidates = [c for c in df.columns if "ano" in c.lower()]
    ano_col = candidates[0] if candidates else None

if ano_col is None:
    st.error("Não foi possível encontrar uma coluna 'ano' (necessary). Renomeie a coluna do ano para 'ano' ou envie um CSV/JSON com essa coluna.")
    st.stop()

# campo assunto_processo
assunto_col = cols_lower.get("assunto_processo") or (cols_lower.get("assunto") if "assunto" in cols_lower else None)
if assunto_col is None:
    # tenta escolher a coluna que mais se parece
    candidates = [c for c in df.columns if "assunto" in c.lower() or "processo" in c.lower()]
    assunto_col = candidates[0] if candidates else None

# campo orgao (se existir no dataset)
orgao_col = cols_lower.get("orgao") or cols_lower.get("órgão") or None
if not orgao_col:
    # procura colunas comuns
    for c in df.columns:
        if any(k in c.lower() for k in ("org", "orga", "órg", "unidade", "ente", "entidade")):
            orgao_col = c
            break

# -------------------------
# Preprocess DataFrame
# -------------------------
# garante colunas mínimas
df = df.copy()
# garante ano inteiro
df[ano_col] = pd.to_numeric(df[ano_col], errors="coerce").astype("Int64")

# cria coluna main_subject a partir do assunto_processo (se existir)
if assunto_col:
    df["main_subject"] = df[assunto_col].apply(lambda s: extract_main_subject(s))
else:
    df["main_subject"] = "Desconhecido"

# -------------------------
# Header
# -------------------------
st.title("Diário Oficial da União — Visualizador")
st.markdown(
    """
    Visualização de publicações do DOU (exemplo).
    - Gráficos: **Quantidade por ano** e **Quantidade por assunto**.
    - Se seu arquivo possui a coluna `orgao`, o app também exibirá **publicações por órgão**.
    """
)

# -------------------------
# Show data table (opcional)
# -------------------------
if show_table:
    st.subheader("Amostra dos dados")
    st.dataframe(df.head(500))

# -------------------------
# Chart 1: Quantidade por Ano
# -------------------------
st.subheader("Quantidade de publicações por ano")
count_by_year = df.groupby(ano_col).size().reset_index(name="count").dropna().sort_values(ano_col)
count_by_year.columns = ["ano", "count"]

chart_year = alt.Chart(count_by_year).mark_bar().encode(
    x=alt.X("ano:O", title="Ano"),
    y=alt.Y("count:Q", title="Número de publicações"),
    tooltip=["ano", "count"]
).properties(width=800, height=350)

st.altair_chart(chart_year, use_container_width=True)

# -------------------------
# Chart 2: Quantidade por Assunto (Top N)
# -------------------------
st.subheader(f"Top {top_n_subjects} assuntos (extraído de `assunto_processo`)")
subject_counts = df["main_subject"].value_counts().reset_index()
subject_counts.columns = ["main_subject", "count"]
subject_counts = subject_counts.head(top_n_subjects)

chart_subject = alt.Chart(subject_counts).mark_bar().encode(
    x=alt.X("count:Q", title="Número de publicações"),
    y=alt.Y("main_subject:N", sort='-x', title="Assunto"),
    tooltip=["main_subject", "count"]
).properties(width=800, height=400)

st.altair_chart(chart_subject, use_container_width=True)

# -------------------------
# Chart 3: Publicações por Órgão (se existir)
# -------------------------
st.subheader("Quantidade de publicações por órgão")
if orgao_col and orgao_col in df.columns:
    org_counts = df[orgao_col].fillna("Desconhecido").value_counts().reset_index()
    org_counts.columns = ["orgao", "count"]
    org_counts = org_counts.head(30)  # mostra top 30
    chart_org = alt.Chart(org_counts).mark_bar().encode(
        x=alt.X("count:Q", title="Número de publicações"),
        y=alt.Y("orgao:N", sort='-x', title="Órgão"),
        tooltip=["orgao", "count"]
    ).properties(width=800, height=450)
    st.altair_chart(chart_org, use_container_width=True)
else:
    st.warning(
        "Não foi detectada uma coluna de 'orgao' no dataset atual. "
        "Se o seu arquivo tiver a coluna `orgao`, renomeie-a para 'orgao' ou faça upload de um CSV/JSON que contenha essa coluna. "
        "Enquanto isso, mostramos os assuntos extraídos do campo `assunto_processo`."
    )

# -------------------------
# Extras: filtros e download
# -------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Exportar / Filtrar")

min_year = int(count_by_year["ano"].min())
max_year = int(count_by_year["ano"].max())
selected_years = st.sidebar.slider("Filtrar por ano (intervalo)", min_value=min_year, max_value=max_year, value=(min_year, max_year))

filtered_df = df[(df[ano_col] >= selected_years[0]) & (df[ano_col] <= selected_years[1])]

st.sidebar.markdown(f"Registros no intervalo: **{len(filtered_df)}**")
if st.sidebar.button("Baixar dados filtrados (CSV)"):
    st.download_button(
        label="Clique para baixar CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="dou_filtrado.csv",
        mime="text/csv"
    )

st.sidebar.markdown("---")
st.sidebar.markdown("📌 Dicas:\n- Se quiser o gráfico por órgão, envie um arquivo que contenha a coluna `orgao`.\n- O app tenta extrair o assunto principal do campo `assunto_processo` automaticamente.")
