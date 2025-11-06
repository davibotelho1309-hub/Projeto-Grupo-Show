import os
from google import genai

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("A variável de ambiente GEMINI_API_KEY não foi configurada.")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-1.5-flash"

    def summarize_text(self, text):
        prompt = f"Resuma a decisão do STF abaixo de forma clara, concisa e compreensível:\n\n{text}"
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ]
            )
            return response.text.strip()
        except Exception as e:
            return f"Erro ao resumir texto: {e}"

    def classify_theme(self, question):
        prompt = f"Identifique o tema jurídico principal desta questão e retorne apenas o nome do tema:\n\n{question}"
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ]
            )
            return response.text.strip()
        except Exception as e:
            return f"Erro ao classificar tema: {e}"
