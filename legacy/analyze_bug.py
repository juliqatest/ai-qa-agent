import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

with open("results.json", "r", encoding="utf-8") as archivo:
    resultados = json.load(archivo)

fallos = [
    resultado
    for resultado in resultados
    if resultado["status"] == "FAIL"
]

if not fallos:
    print("\n✅ No hay tests fallidos.")
    print("No es necesario generar Bug Reports.")
    exit()

print("\n🐛 AI BUG ANALYZER")
print("========================")

for fallo in fallos:

    test_id = fallo["id"]
    titulo = fallo["title"]
    error = fallo.get("error", "")
    screenshot = fallo.get("screenshot")

    print(f"\n🔎 Analizando {test_id}: {titulo}")

    contenido = f"""
Sos un QA Analyst Senior.

Analizá este fallo de automatización.

TEST:
{test_id}

TÍTULO:
{titulo}

ERROR:
{error}

Determiná:

1. Si es un bug real de la aplicación.
2. Causa probable.
3. Severidad: Critical, High, Medium o Low.
4. Título del bug.
5. Pasos para reproducir.
6. Resultado esperado.
7. Resultado actual.
8. Evidencia.
9. Recomendación.

IMPORTANTE:

- No confundas un error del test con un bug de la aplicación.
- No inventes información.
- Si la evidencia no permite confirmar que es un bug,
  indicá que necesita investigación.
- Respondé en español.
"""

    partes = [contenido]

    if screenshot and os.path.exists(screenshot):

        print(f"   📸 Cargando evidencia: {screenshot}")

        imagen = client.files.upload(file=screenshot)

        partes.append(imagen)

    else:

        print("   ⚠️ No se encontró screenshot.")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=partes
    )

    reporte = response.text

    print("\n===== BUG REPORT =====")
    print(reporte)

    nombre_archivo = f"bug_report_{test_id}.md"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(f"# Bug Report - {test_id}\n\n")
        archivo.write(reporte)

    print(f"\n📄 Bug Report guardado en: {nombre_archivo}")
