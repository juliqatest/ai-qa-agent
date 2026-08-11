import json
import os
import subprocess

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

MODEL = "gemini-3.5-flash-lite"
IS_CI = os.getenv("GITHUB_ACTIONS") == "true"
HEADLESS = IS_CI

print("\n🤖 AI QA AGENT")
print("============================")
print("Historia → Tests → Playwright → Análisis → Reporte\n")

ci_story = os.getenv("CI_STORY")

if ci_story:
    historia = ci_story.strip()
    print(f"Historia de usuario: {historia}")
else:
    historia = input("Historia de usuario: ").strip()

if historia.lower() == "salir":
    print("Agente finalizado.")
    exit()

# ============================================================
# 1. GENERAR CASOS DE PRUEBA
# ============================================================

print("\n🤖 Generando casos de prueba...")

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
    model=MODEL,
    contents=prompt_tests
)

try:
    datos = json.loads(response.text)
except json.JSONDecodeError:
    print("❌ Gemini no devolvió JSON válido.")
    print(response.text)
    exit()

with open("tests.json", "w", encoding="utf-8") as archivo:
    json.dump(datos, archivo, indent=2, ensure_ascii=False)

print(f"✅ {len(datos['test_cases'])} casos generados.")

# ============================================================
# 2. GENERAR Y EJECUTAR TODOS LOS TESTS
# ============================================================

resultados = []

for test in datos["test_cases"]:

    test_id = test["id"]
    titulo = test["title"]

    print("\n--------------------------------------")
    print(f"▶️ {test_id}: {titulo}")
    print("🤖 Generando Playwright...")

    prompt_playwright = f"""
Sos un QA Automation Engineer experto en Playwright Python.

Generá un script completo y ejecutable para este caso:

ID: {test_id}
Título: {titulo}
Pasos: {test["steps"]}
Resultado esperado: {test["expected_result"]}

Aplicación:
https://www.saucedemo.com/

Credenciales válidas:
usuario: standard_user
password: secret_sauce

REGLAS:
- Usá playwright.sync_api.
- Usá sync_playwright.
- Chromium debe abrirse con headless={HEADLESS}.
- No uses pytest.
- No uses fixtures.
- No uses funciones test_*.
- No uses Markdown.
- Devolvé únicamente Python ejecutable.
- Cerrá el navegador al finalizar.

Si ocurre cualquier error:

- Tomá screenshot.
- Guardalo exactamente como:
  evidence_{test_id}.png

Usá try/except/finally.
En el except:
- screenshot
- raise

El programa debe devolver exit code distinto de 0 si falla.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt_playwright
    )

    codigo = response.text.strip()
    codigo = codigo.replace("```python", "")
    codigo = codigo.replace("```", "")

    archivo_test = f"test_{test_id}.py"

    with open(archivo_test, "w", encoding="utf-8") as archivo:
        archivo.write(codigo.strip())

    print("🧪 Ejecutando Playwright...")

    try:
        resultado = subprocess.run(
            ["python", archivo_test],
            capture_output=True,
            text=True,
            timeout=45
        )

    except subprocess.TimeoutExpired:

        print("⏱️ TIMEOUT")

        resultados.append({
            "id": test_id,
            "title": titulo,
            "status": "FAIL",
            "failure_type": "TIMEOUT",
            "error": "El test excedió el timeout máximo."
        })

        continue

    if resultado.returncode == 0:

        print("✅ PASS")

        resultados.append({
            "id": test_id,
            "title": titulo,
            "status": "PASS"
        })

        continue

    # ========================================================
    # 3. ANALIZAR FAIL
    # ========================================================

    print("❌ FAIL")

    error = resultado.stderr
    screenshot = f"evidence_{test_id}.png"

    prompt_failure = f"""
Sos un QA Analyst Senior.

Analizá este fallo de una prueba automática.

Historia:
{historia}

Caso:
{test_id} - {titulo}

Pasos:
{test["steps"]}

Resultado esperado:
{test["expected_result"]}

Error:

{error}

Clasificá el fallo como una de estas opciones:

BUG
TEST_ERROR
TEST_DATA
ENVIRONMENT
NEEDS_INVESTIGATION

Generá además:

- cause
- severity
- bug_title
- expected
- actual
- recommendation

Respondé ÚNICAMENTE JSON válido con esta estructura:

{{
  "classification": "BUG",
  "cause": "",
  "severity": "",
  "bug_title": "",
  "expected": "",
  "actual": "",
  "recommendation": ""
}}

No inventes información.
"""

    contenido = [prompt_failure]

    if os.path.exists(screenshot):

        with open(screenshot, "rb") as archivo:
            imagen = archivo.read()

        contenido.append(
            types.Part.from_bytes(
                data=imagen,
                mime_type="image/png"
            )
        )

    response = client.models.generate_content(
        model=MODEL,
        contents=contenido
    )

    try:
        analisis = json.loads(response.text)
    except json.JSONDecodeError:
        analisis = {
            "classification": "NEEDS_INVESTIGATION",
            "cause": response.text,
            "severity": "Unknown",
            "bug_title": "",
            "expected": test["expected_result"],
            "actual": "No determinado",
            "recommendation": "Revisión manual"
        }

    print(
        "🤖 Clasificación:",
        analisis["classification"]
    )

    resultado_final = {
        "id": test_id,
        "title": titulo,
        "status": "FAIL",
        "error": error,
        "screenshot": screenshot if os.path.exists(screenshot) else None,
        "analysis": analisis
    }

    resultados.append(resultado_final)

    # ========================================================
    # 4. CREAR BUG REPORT SI ES BUG
    # ========================================================

    if analisis["classification"] == "BUG":

        nombre_bug = f"bug_report_{test_id}.md"

        with open(nombre_bug, "w", encoding="utf-8") as archivo:

            archivo.write(f"# Bug Report - {test_id}\n\n")

            archivo.write(
                f"## Título\n{analisis['bug_title']}\n\n"
            )

            archivo.write(
                f"## Severidad\n{analisis['severity']}\n\n"
            )

            archivo.write("## Pasos para reproducir\n")

            for paso in test["steps"]:
                archivo.write(f"- {paso}\n")

            archivo.write(
                f"\n## Resultado esperado\n"
                f"{analisis['expected']}\n\n"
            )

            archivo.write(
                f"## Resultado actual\n"
                f"{analisis['actual']}\n\n"
            )

            archivo.write(
                f"## Causa probable\n"
                f"{analisis['cause']}\n\n"
            )

            if os.path.exists(screenshot):
                archivo.write(
                    f"## Evidencia\n{screenshot}\n\n"
                )

            archivo.write(
                f"## Recomendación\n"
                f"{analisis['recommendation']}\n"
            )

        print(f"🐛 Bug Report creado: {nombre_bug}")

# ============================================================
# 5. GUARDAR RESULTADOS
# ============================================================

with open("results.json", "w", encoding="utf-8") as archivo:
    json.dump(
        resultados,
        archivo,
        indent=2,
        ensure_ascii=False
    )

# ============================================================
# 6. GENERAR REPORTE FINAL
# ============================================================

total = len(resultados)
passed = sum(
    1 for r in resultados
    if r["status"] == "PASS"
)

failed = total - passed

bugs = sum(
    1
    for r in resultados
    if r.get("analysis", {}).get("classification") == "BUG"
)

print("\n======================================")
print("📊 RESUMEN FINAL")
print("======================================")
print(f"Total: {total}")
print(f"PASS:  {passed}")
print(f"FAIL:  {failed}")
print(f"BUGS:  {bugs}")
print("======================================")

resumen_json = json.dumps(
    resultados,
    indent=2,
    ensure_ascii=False
)

prompt_report = f"""
Sos un QA Lead Senior.

Generá un reporte QA profesional basándote únicamente
en estos resultados:

{resumen_json}

Incluí:

1. Resumen de ejecución
2. Cobertura
3. Fallos
4. Bugs confirmados
5. Errores de automatización o datos
6. Riesgos
7. Recomendaciones
8. Conclusión

REGLAS:
- No inventes fechas.
- No inventes ambientes.
- No inventes bugs.
- Diferenciá claramente bug de error de test.
- Respondé en español.
"""

response = client.models.generate_content(
    model=MODEL,
    contents=prompt_report
)

with open("qa_report.md", "w", encoding="utf-8") as archivo:
    archivo.write(response.text)

print("\n📄 results.json generado")
print("📄 qa_report.md generado")
print("\n✅ Ejecución finalizada.")
