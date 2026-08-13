import json
from google import genai


def generar_casos(client, model, historia):
    prompt_tests = f"""
Sos un QA Analyst Senior.

Analizá esta historia de usuario:

{historia}

Generá únicamente JSON válido con esta estructura:

{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "Título",
      "priority": "High",
      "steps": [
        "Paso 1",
        "Paso 2"
      ],
      "expected_result": "Resultado esperado"
    }}
  ],
  "edge_cases": [],
  "risks": [],
  "questions": []
}}

REGLAS:
- No uses Markdown.
- No agregues explicaciones.
- No inventes requisitos.
- Generá casos positivos y negativos relevantes.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt_tests
    )

    return json.loads(response.text)
