from google import genai
from google.genai import types
import os

class GeminiClient:
    def __init__(self):
        # O client lê variáveis de ambiente conforme README do sdk:
        # - Para Gemini Developer API: export GEMINI_API_KEY
        # - Para Vertex AI (Gemini on Vertex): export GOOGLE_GENAI_USE_VERTEXAI=true + GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION
        self.client = genai.Client()

        # modelo: escolha um modelo de texto compatível (ex: "gemini-1.5" / "gemini-2.1" / "gemini-2.5-pro")
        self.model = "gemini-2.1"  # ajuste conforme sua conta / disponibilidade

    def classify_theme(self, text):
        prompt = f"Classifique em 1-3 palavras o tema macro do Direito desta pergunta: \"{text}\". Apenas retorne as palavras, sem explicações."
        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        out = resp.generations[0].content.strip()
        return out

    def summarize_and_explain(self, legal_text):
        prompt = (
            "Resuma em até 120 palavras a decisão abaixo e explique em linguagem simples e concisa os fatores jurídicos relevantes.\n\n"
            f"Decisão / texto: {legal_text}\n\nResposta:"
        )
        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        return resp.generations[0].content.strip()
