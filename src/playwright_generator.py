from src.config import BASE_URL, TEST_USERNAME, TEST_PASSWORD

def generar_playwright(client, model, test, headless):
    test_id = test["id"]
    titulo = test["title"]

    prompt_playwright = f"""
Sos un QA Automation Engineer experto en Playwright Python.

Generá un script completo y ejecutable para este caso:

ID: {test_id}
Título: {titulo}
Pasos: {test["steps"]}
Resultado esperado: {test["expected_result"]}

Aplicación:
{BASE_URL}

Credenciales válidas:
usuario: {TEST_USERNAME}
password: {TEST_PASSWORD}

REGLAS:
- Usá playwright.sync_api.
- Usá sync_playwright.
- Chromium debe abrirse con headless={headless}.
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
- Usá try/except/finally.
- En el except hacé screenshot y luego raise.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt_playwright
    )

    codigo = response.text.strip()
    codigo = codigo.replace("```python", "")
    codigo = codigo.replace("```", "")

    return codigo
