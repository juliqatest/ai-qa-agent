import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

with open("results.json", "r", encoding="utf-8") as archivo:
    resultados = json.load(archivo)

resumen = json.dumps(resultados, indent=2, ensure_ascii=False)

prompt = f"""
Sos un QA Lead Senior.

Analizá ÚNICAMENTE los resultados de pruebas proporcionados.

RESULTADOS:

{resumen}

Generá un reporte QA profesional en español.

Incluí exactamente:

1. RESUMEN DE EJECUCIÓN
- Total de tests
- Tests PASS
- Tests FAIL

2. COBERTURA
Indicar únicamente las funcionalidades que aparecen explícitamente
en los resultados.

3. ANÁLISIS DE FALLAS
Para cada FAIL:
- Test
- Causa probable
- ¿Es un bug real?
- Severidad
- Evidencia

Si no hay FAIL, escribir:
"No se detectaron fallos en esta ejecución."

4. RIESGOS
Indicar únicamente riesgos que puedan inferirse razonablemente
de los resultados.
No presentar funcionalidades NO probadas como bugs.

5. RECOMENDACIONES
Indicar mejoras de cobertura como recomendaciones futuras.
No afirmar que una vulnerabilidad existe si no fue comprobada.

6. CONCLUSIÓN
Resumir objetivamente el resultado de la ejecución.

REGLAS IMPORTANTES:

- NO inventes fechas.
- NO inventes versiones.
- NO inventes ambientes.
- NO inventes bugs.
- NO inventes evidencia.
- NO afirmes que se probaron funcionalidades que no aparecen
  en los resultados.
- Diferenciá claramente entre "resultado observado",
  "riesgo" y "recomendación".
- No agregues información que no pueda deducirse de los datos.
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt
)

reporte = response.text

print("\n========================================")
print("🤖 AI QA REPORT")
print("========================================\n")

print(reporte)

with open("qa_report.md", "w", encoding="utf-8") as archivo:
    archivo.write(reporte)

print("\n========================================")
print("📄 Reporte guardado en qa_report.md")
print("========================================")
