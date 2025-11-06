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
        prompt = f"Resuma a decisão do STF abaixo de forma clara e didática:\n\n{text}"
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()

    def classify_theme(self, question):
        prompt = f"Qual é o tema jurídico principal desta questão?\nPergunta: {question}"
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()
