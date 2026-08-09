import subprocess
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

print("🤖 AI QA AGENT")
print("================")
print("Ejecutando prueba...\n")

resultado = subprocess.run(
    ["python", "generated_test_fail.py"],
    capture_output=True,
    text=True
)

if resultado.returncode == 0:
    print("✅ TEST PASÓ")
    print(resultado.stdout)

else:
    print("❌ TEST FALLÓ\n")

    error = resultado.stderr

    print("Analizando fallo con Gemini...\n")

    prompt = f"""
Sos un QA Analyst Senior.

Una prueba automatizada de Playwright falló.

Analizá este error:

{error}

Determiná:

1. Resultado
2. Causa probable
3. Severidad
4. ¿Es un bug real?
5. Evidencia
6. Recomendación

Diferenciá entre:
- defecto real de la aplicación
- error del test
- datos de prueba incorrectos
- problema de configuración

No inventes información.
Respondé en español.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    print("===== ANÁLISIS DE GEMINI =====")
    print(response.text)
