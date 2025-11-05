import os
from google import genai

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi configurada.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-exp"  # modelos 2.x estão no endpoint experimental por enquanto

    def classify_theme(self, query: str) -> str:
        prompt = f"""
        Classifique o tema jurídico principal da pergunta abaixo:
        Pergunta: "{query}"
        Retorne apenas o tema (ex: Constitucional, Penal, Trabalhista etc.).
        ""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[{"role": "user", "parts": [{"text": prompt}]}]
            )
            return response.output_text.strip()
        except Exception as e:
            print("Erro ao classificar tema:", e)
            return "Tema não identificado"

    def summarize_and_explain(self, legal_text: str) -> str:
        prompt = f"""
        Resuma e explique, em linguagem simples, a seguinte decisão do STF:
        {legal_text}
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[{"role": "user", "parts": [{"text": prompt}]}]
            )
            return response.output_text.strip()
        except Exception as e:
            print("Erro ao resumir decisão:", e)
            return "Não foi possível resumir a decisão."
