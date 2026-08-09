import json
import subprocess
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

with open("tests.json", "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)

tests = datos["test_cases"]

print("\n🧪 AI QA AGENT - EJECUCIÓN DE TESTS")
print("====================================")

total = 0
passed = 0
failed = 0

resultados = []

for test in tests:

    total += 1

    test_id = test["id"]
    titulo = test["title"]

    print(f"\n▶️ Ejecutando {test_id}: {titulo}")
    print("   🤖 Generando código...")

    prompt = f"""
Sos un QA Automation Engineer experto en Playwright con Python.

Convertí este caso de prueba en un script Python completo y ejecutable:

ID: {test_id}
Título: {titulo}
Pasos: {test["steps"]}
Resultado esperado: {test["expected_result"]}

Aplicación:
https://www.saucedemo.com/

Usuario:
standard_user

Password:
secret_sauce

REGLAS:

- Usá playwright.sync_api.
- Usá sync_playwright.
- Chromium con headless=False.
- No uses pytest.
- No uses fixtures.
- No uses funciones test_*.
- No uses Markdown.
- Devolvé únicamente código Python.
- El script debe poder ejecutarse directamente con Python.
- El navegador debe cerrarse al finalizar.

IMPORTANTE:

Si cualquier assertion o acción falla, capturá un screenshot
antes de cerrar el navegador.

El screenshot debe guardarse exactamente como:

evidence_{test_id}.png

Usá esta estructura:

try:
    # acciones del test
    # assertions
except Exception:
    page.screenshot(
        path="evidence_{test_id}.png",
        full_page=True
    )
    raise
finally:
    browser.close()
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    codigo = response.text.strip()

    codigo = codigo.replace("```python", "")
    codigo = codigo.replace("```", "")

    archivo_test = f"test_{test_id}.py"

    with open(archivo_test, "w", encoding="utf-8") as archivo:
        archivo.write(codigo.strip())

    print("   🧪 Ejecutando Playwright...")

    resultado = subprocess.run(
        ["python", archivo_test],
        capture_output=True,
        text=True
    )

    if resultado.returncode == 0:

        print("   ✅ PASS")

        passed += 1

        resultados.append({
            "id": test_id,
            "title": titulo,
            "status": "PASS"
        })

    else:

        print("   ❌ FAIL")

        failed += 1

        resultados.append({
            "id": test_id,
            "title": titulo,
            "status": "FAIL",
            "error": resultado.stderr,
            "screenshot": f"evidence_{test_id}.png"
        })

        print("   📸 Evidencia:", f"evidence_{test_id}.png")


print("\n")
print("====================================")
print("📊 RESUMEN QA")
print("====================================")
print(f"Total:  {total}")
print(f"PASS:   {passed}")
print(f"FAIL:   {failed}")
print("====================================")

with open("results.json", "w", encoding="utf-8") as archivo:
    json.dump(
        resultados,
        archivo,
        indent=2,
        ensure_ascii=False
    )

print("\n📄 Resultados guardados en results.json")
