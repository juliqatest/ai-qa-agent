import os
import subprocess

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

print("\n🐛 AI BUG ANALYZER")
print("========================")
print("🧪 Ejecutando test fallido...\n")

resultado = subprocess.run(
    ["python", "test_TC001_fail.py"],
    capture_output=True,
    text=True
)

if resultado.returncode == 0:
    print("⚠️ El test pasó. No hay fallo para analizar.")
    exit()

error = resultado.stderr
screenshot = "evidence_TC001.png"

print("❌ Test falló correctamente.")
print("📋 Error capturado.")

prompt = f"""
Sos un QA Analyst Senior.

Analizá el siguiente fallo de una prueba automatizada.

CASO:
TC001 - Inicio de sesión exitoso con credenciales válidas

CONTEXTO:
El test original esperaba un login exitoso.

ERROR DE PLAYWRIGHT:
{error}

Determiná:

1. RESULTADO
2. CAUSA PROBABLE
3. ¿ES UN BUG REAL DE LA APLICACIÓN?
4. SEVERIDAD
5. TÍTULO SUGERIDO DEL BUG
6. PASOS PARA REPRODUCIR
7. RESULTADO ESPERADO
8. RESULTADO ACTUAL
9. EVIDENCIA
10. RECOMENDACIÓN

REGLAS:

- Analizá tanto el error como la captura si está disponible.
- Diferenciá un bug real de un dato de prueba incorrecto.
- No inventes información.
- Si no hay evidencia suficiente para afirmar que existe un bug,
  decilo explícitamente.
- Respondé en español.
"""

contenido = [prompt]

if os.path.exists(screenshot):

    print("📸 Agregando screenshot al análisis...")

    with open(screenshot, "rb") as archivo:
        image_bytes = archivo.read()

    contenido.append(
        types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png"
        )
    )

else:
    print("⚠️ No se encontró el screenshot.")

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=contenido
)

reporte = response.text

print("\n===== ANÁLISIS QA =====\n")
print(reporte)

with open(
    "bug_report_controlled_TC001.md",
    "w",
    encoding="utf-8"
) as archivo:
    archivo.write("# Bug Report - TC001\n\n")
    archivo.write(reporte)

print("\n📄 Reporte guardado en:")
print("bug_report_controlled_TC001.md")
