import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

class STFClient:
    def __init__(self, excel_path="data/stf_decisoes.xlsx"):
        self.excel_path = excel_path
        self.df = None

        if os.path.exists(excel_path):
            try:
                self.df = pd.read_excel(excel_path)
                print(f"✅ Base local carregada: {len(self.df)} decisões.")
            except Exception as e:
                print(f"⚠️ Erro ao carregar Excel: {e}")
        else:
            print("⚠️ Nenhum arquivo Excel encontrado — usando apenas dataset remoto.")

    def search_local_excel(self, query, year_from=2020, year_to=2025, limit=3):
        """Busca na planilha local"""
        if self.df is None:
            return []

        df = self.df.copy()
        if 'data' in df.columns:
            df['ano'] = pd.to_datetime(df['data'], errors='coerce').dt.year
            df = df[(df['ano'] >= year_from) & (df['ano'] <= year_to)]

        mask = df.apply(lambda row: query.lower() in str(row).lower(), axis=1)
        results = df[mask].head(limit)

        return results.to_dict(orient='records')

    def search_dataset(self, query, year_from=2020, year_to=2025, limit=3):
        """
        Exemplo genérico de busca num dataset remoto.
        Aqui você pode integrar com:
        - BaseDosDados (tabela 'br_stf_julgados')
        - CorteAberta
        - endpoint JSON do portal STF
        """
        # Exemplo fictício (substitua por query real)
        url = "https://dadosabertos.stf.jus.br/api/jurisprudencia"
        params = {"termo": query, "anoInicial": year_from, "anoFinal": year_to, "limite": limit}
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                # Adaptar para formato compatível
                return data.get("decisoes", [])
        except Exception:
            pass
        return []

    def search_by_query(self, query, theme=None, year_from=2020, year_to=2025, limit=3):
        # 1️⃣ Tenta Excel local
        local_results = self.search_local_excel(query, year_from, year_to, limit)
        if local_results:
            print("✅ Resultados encontrados na base local (Excel).")
            return local_results

        # 2️⃣ Tenta dataset remoto
        dataset_results = self.search_dataset(query, year_from, year_to, limit)
        if dataset_results:
            print("✅ Resultados encontrados via dataset remoto.")
            return dataset_results

        # 3️⃣ Fallback web
        print("⚠️ Nenhum resultado local ou remoto — tentando busca web.")
        return self.search_web(query, limit)

    def search_web(self, query, limit=3):
        """Busca simples no portal STF (fallback apenas)."""
        try:
            url = "https://portal.stf.jus.br/services/search"
            r = requests.get(url, params={"q": query, "rows": limit})
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                return []
        except Exception:
            pass
        return []
