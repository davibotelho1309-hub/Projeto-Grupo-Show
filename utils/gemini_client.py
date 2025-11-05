import os
from google import genai

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida.")
        self.client = genai.Client(api_key=self.api_key)
        # Atualizado para Gemini 2.5
        self.model = "gemini-2.5-flash"   # ou "gemini-2.5-pro" se você tiver acesso mais avançado

    def classify_theme(self, text: str) -> str:
        prompt = (
            f"Classifique em até 3 palavras o tema macro do Direito desta pergunta:\n\n\"{text}\"\n\n"
            "Retorne somente as palavras, separadas por vírgula, sem explicações."
        )
        resp = self.client.models.generate_content(model=self.model, contents=[prompt])
        # Dependendo da versão da SDK, a resposta pode estar em resp.generations[0].content ou resp.text
        try:
            out = resp.generations[0].content.strip()
        except AttributeError:
            out = resp.text.strip()
        return out

    def summarize_and_explain(self, legal_text: str) -> str:
        prompt = (
            "Resuma em até 120 palavras a decisão abaixo e explique em linguagem simples e concisa os fatores jurídicos relevantes.\n\n"
            f"Texto da decisão: {legal_text}\n\nResposta:"
        )
        resp = self.client.models.generate_content(model=self.model, contents=[prompt])
        try:
            out = resp.generations[0].content.strip()
        except AttributeError:
            out = resp.text.strip()
        return out
