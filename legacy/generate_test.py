from google import genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = genai.Client()

with open("tests.json", "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)

test = datos["test_cases"][0]

prompt = f"""
Sos un QA Automation Engineer experto en Playwright con Python.

Tenés que convertir este caso de prueba en un SCRIPT COMPLETO Y EJECUTABLE:

ID: {test["id"]}
Título: {test["title"]}
Pasos: {test["steps"]}
Resultado esperado: {test["expected_result"]}

La aplicación es:
https://www.saucedemo.com/

Usuario:
standard_user

Password:
secret_sauce

REGLAS ABSOLUTAS:

1. Usá exactamente:
from playwright.sync_api import sync_playwright, expect

2. El programa debe comenzar con:
with sync_playwright() as p:

3. Debe abrir Chromium con:
browser = p.chromium.launch(headless=False)

4. Debe crear:
page = browser.new_page()

5. Debe navegar a:
https://www.saucedemo.com/

6. Debe ejecutar las acciones necesarias.

7. Debe realizar las assertions correspondientes.

8. Debe cerrar el navegador con:
browser.close()

9. NO uses pytest.

10. NO uses funciones test_*.

11. NO uses fixtures.

12. NO uses Page como parámetro.

13. NO uses Markdown.

14. NO uses ```.

15. NO uses backticks.

16. NO agregues explicaciones.

17. Devolvé ÚNICAMENTE código Python ejecutable.

El resultado debe poder ejecutarse directamente con:

python generated_test.py
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt
)

codigo = response.text.strip()

# Eliminar posibles bloques Markdown que Gemini pueda agregar
codigo = re.sub(r"```python", "", codigo)
codigo = re.sub(r"```", "", codigo)

with open("generated_test.py", "w", encoding="utf-8") as archivo:
    archivo.write(codigo.strip())

print("✅ Test generado correctamente.")
print("📄 Archivo: generated_test.py")
