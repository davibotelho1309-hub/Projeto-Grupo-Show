import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("A variável GEMINI_API_KEY não foi configurada.")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-1.5-flash"

    def classify_theme(self, user_query: str) -> str:
        prompt = f"""
        Classifique a dúvida jurídica abaixo em um tema ou ramo do direito.
        Pergunta: "{user_query}"
        Responda apenas com o tema (ex: direito civil, liberdade de expressão, etc.)
        """
       response = self.client.models.generate_content(
    model=self.model,
    contents=prompt
)
        return resp.text.strip()

    def summarize_decisions(self, ementas: list[str], tema: str) -> str:
        if not ementas:
            return "Não foram encontradas decisões do STF sobre o tema."
        joined = "\n\n".join(f"- {e}" for e in ementas)
        prompt = f"""
        Abaixo estão ementas de decisões do STF sobre o tema "{tema}".
        Gere um resumo claro e acessível sobre:
        - principais entendimentos do STF;
        - fundamentos jurídicos mais citados;
        - relevância das decisões.
        Ementas:
        {joined}
        """
        resp = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        return resp.text.strip()
