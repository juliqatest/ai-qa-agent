import json
import subprocess
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

print("\n🤖 AI QA AGENT")
print("========================")
print("Escribí una historia de usuario.")
print("Escribí 'salir' para terminar.\n")

historia = input("Historia de usuario: ")

if historia.lower() == "salir":
    print("Agente finalizado.")
    exit()

# ============================================================
# 1. GENERAR CASOS DE PRUEBA
# ============================================================

prompt_tests = f"""
Sos un QA Analyst Senior.

Analizá esta historia de usuario:

{historia}

Generá ÚNICAMENTE un JSON válido con esta estructura:

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

No agregues explicaciones.
No uses Markdown.
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt_tests
)

try:
    datos = json.loads(response.text)
except json.JSONDecodeError:
    print("\n❌ Gemini no devolvió JSON válido.")
    print(response.text)
    exit()

with open("tests.json", "w", encoding="utf-8") as archivo:
    json.dump(datos, archivo, indent=2, ensure_ascii=False)

print("\n✅ Casos de prueba generados.")
print("📄 Guardados en tests.json")

# ============================================================
# 2. GENERAR TEST PLAYWRIGHT
# ============================================================

test = datos["test_cases"][0]

prompt_playwright = f"""
Sos un QA Automation Engineer experto en Playwright con Python.

Convertí este caso de prueba en un SCRIPT COMPLETO Y EJECUTABLE:

ID: {test["id"]}
Título: {test["title"]}
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
- Usá headless=False.
- El código debe ejecutarse con:
  python generated_test.py
- NO uses pytest.
- NO uses fixtures.
- NO uses funciones test_*.
- NO uses Markdown.
- NO uses bloques de código.
- Devolvé únicamente código Python ejecutable.
- Cerrá el navegador al finalizar.

El código debe comenzar con:

from playwright.sync_api import sync_playwright, expect

y utilizar:

with sync_playwright() as p:
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt_playwright
)

codigo = response.text.strip()

codigo = codigo.replace("```python", "")
codigo = codigo.replace("```", "")

with open("generated_test.py", "w", encoding="utf-8") as archivo:
    archivo.write(codigo.strip())

print("✅ Test Playwright generado.")
print("📄 Guardado en generated_test.py")

# ============================================================
# 3. EJECUTAR PLAYWRIGHT
# ============================================================

print("\n🧪 Ejecutando prueba...\n")

resultado = subprocess.run(
    ["python", "generated_test.py"],
    capture_output=True,
    text=True
)

if resultado.returncode == 0:

    print("================================")
    print("✅ TEST PASÓ")
    print("================================")

else:

    print("================================")
    print("❌ TEST FALLÓ")
    print("================================")

    error = resultado.stderr

    print("\n🤖 Analizando fallo con Gemini...\n")

    # ========================================================
    # 4. ANALIZAR Y CORREGIR
    # ========================================================

    with open("generated_test.py", "r", encoding="utf-8") as archivo:
        codigo_actual = archivo.read()

    prompt_error = f"""
Sos un QA Automation Engineer Senior especializado en Playwright Python.

La IA generó este código:

--- CÓDIGO ---
{codigo_actual}
--- FIN CÓDIGO ---

El test falló con este error:

--- ERROR ---
{error}
--- FIN ERROR ---

Analizá el problema.

Determiná:

1. Si el problema está en el código generado.
2. Qué está incorrecto.
3. Cómo debe corregirse.

Después generá una versión COMPLETA Y CORREGIDA del archivo.

REGLAS DEL CÓDIGO CORREGIDO:

- Python válido.
- Playwright sync API.
- Usar sync_playwright.
- Chromium con headless=False.
- No usar pytest.
- No usar fixtures.
- No usar Markdown.
- No usar bloques de código.
- Devolver únicamente código Python.
- Mantener el objetivo original del test.
- El código debe ejecutarse directamente con:
  python generated_test.py
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt_error
    )

    analisis = response.text.strip()

    print("===== RESPUESTA DE GEMINI =====")
    print(analisis)

    # ========================================================
    # 5. GUARDAR CÓDIGO CORREGIDO
    # ========================================================

    codigo_corregido = analisis

    codigo_corregido = codigo_corregido.replace("```python", "")
    codigo_corregido = codigo_corregido.replace("```", "")

    with open("generated_test.py", "w", encoding="utf-8") as archivo:
        archivo.write(codigo_corregido.strip())

    print("\n💾 Test corregido guardado.")
    print("🧪 Ejecutando nuevamente...\n")

    segundo_intento = subprocess.run(
        ["python", "generated_test.py"],
        capture_output=True,
        text=True
    )

    if segundo_intento.returncode == 0:

        print("================================")
        print("🎉 TEST CORREGIDO Y PASÓ")
        print("================================")

    else:

        print("================================")
        print("❌ EL TEST SIGUE FALLANDO")
        print("================================")

        print("\nNuevo error:")
        print(segundo_intento.stderr)
