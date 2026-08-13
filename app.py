import json
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.test_generator import generar_casos
from src.playwright_generator import generar_playwright
from src.failure_analyzer import analizar_fallo
from src.report_generator import generar_reporte
from src.bug_report_generator import generar_bug_report
from src.test_runner import ejecutar_test
from src.code_validator import validar_codigo_python
from src.code_fixer import corregir_codigo
from src.config import MODEL, TEST_TIMEOUT

load_dotenv()

client = genai.Client()

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

try:
    datos = generar_casos(
        client=client,
        model=MODEL,
        historia=historia
    )

except json.JSONDecodeError:
    print("❌ Gemini no devolvió JSON válido.")
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

    codigo = generar_playwright(
        client=client,
        model=MODEL,
        test=test,
        headless=HEADLESS
    )

    validacion = validar_codigo_python(codigo)

    if not validacion["valid"]:
        print("⚠️ Gemini generó Python inválido.")
        print(f"   {validacion['error']}")
        print("🔧 Intentando autocorrección...")

        codigo = corregir_codigo(
            client=client,
            model=MODEL,
            codigo=codigo,
            error=validacion["error"],
            test=test,
            headless=HEADLESS
        )

        segunda_validacion = validar_codigo_python(codigo)

        if not segunda_validacion["valid"]:
            print("❌ TEST_ERROR: la autocorrección también es inválida.")

            resultados.append({
                "id": test_id,
                "title": titulo,
                "status": "FAIL",
                "failure_type": "TEST_ERROR",
                "error": segunda_validacion["error"]
            })

            continue

        print("✅ Código corregido y validado.")

    archivo_test = f"test_{test_id}.py"

    with open(archivo_test, "w", encoding="utf-8") as archivo:
        archivo.write(codigo.strip())

    print("🧪 Ejecutando Playwright...")

    resultado = ejecutar_test(
        archivo_test=archivo_test,
	timeout=TEST_TIMEOUT
    )

    if resultado["failure_type"] == "TIMEOUT":

        print("⏱️ TIMEOUT")

        resultados.append({
            "id": test_id,
            "title": titulo,
            "status": "FAIL",
            "failure_type": "TIMEOUT",
            "error": resultado["stderr"]
        })

        continue

    if resultado["status"] == "PASS":

        print("✅ PASS")

        resultados.append({
            "id": test_id,
            "title": titulo,
            "status": "PASS"
        })

        continue
    if resultado["status"] == "PASS":
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

    error = resultado["stderr"]
    screenshot = f"evidence_{test_id}.png"

    analisis = analizar_fallo(
        client=client,
        model=MODEL,
        historia=historia,
        test=test,
        error=error,
        screenshot=screenshot
    )

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

        contenido_bug = generar_bug_report(
            test=test,
            analisis=analisis,
            screenshot=screenshot if os.path.exists(screenshot) else None
        )

        with open(nombre_bug, "w", encoding="utf-8") as archivo:
            archivo.write(contenido_bug)

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

reporte = generar_reporte(
    client=client,
    model=MODEL,
    resultados=resultados
)

with open("qa_report.md", "w", encoding="utf-8") as archivo:
    archivo.write(reporte)

print("\n📄 results.json generado")
print("📄 qa_report.md generado")
print("\n✅ Ejecución finalizada.")
