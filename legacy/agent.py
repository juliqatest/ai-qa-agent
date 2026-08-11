from google import genai
from dotenv import load_dotenv
import json

load_dotenv()

client = genai.Client()

print("🤖 AI QA Agent")
print("Escribí una historia de usuario.")
print("Escribí 'salir' para terminar.")
print()

while True:
    historia = input("Historia de usuario: ")

    if historia.lower() == "salir":
        print("Agente finalizado.")
        break

    prompt = f"""
Sos un QA Analyst Senior.

Analizá esta historia de usuario:

{historia}

Generá casos de prueba y devolvé ÚNICAMENTE un JSON válido.

La estructura debe ser exactamente:

{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "Título del caso",
      "priority": "High",
      "steps": [
        "Paso 1",
        "Paso 2"
      ],
      "expected_result": "Resultado esperado"
    }}
  ],
  "edge_cases": [
    "Edge case 1",
    "Edge case 2"
  ],
  "risks": [
    "Riesgo 1",
    "Riesgo 2"
  ],
  "questions": [
    "Pregunta 1",
    "Pregunta 2"
  ]
}}

No agregues texto antes ni después del JSON.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    try:
        resultado = json.loads(response.text)

        with open("tests.json", "w", encoding="utf-8") as archivo:
            json.dump(resultado, archivo, indent=2, ensure_ascii=False)

        print("\n✅ Análisis generado correctamente.")
        print("📄 Guardado en: tests.json\n")

        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    except json.JSONDecodeError:
        print("\n⚠️ El modelo no devolvió un JSON válido:")
        print(response.text)
