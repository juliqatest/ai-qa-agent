def corregir_codigo(
    client,
    model,
    codigo,
    error,
    test,
    headless
):
    prompt = f"""
Sos un QA Automation Engineer experto en Playwright Python.

La IA generó este código inválido:

--- CÓDIGO ---
{codigo}
--- FIN CÓDIGO ---

Python detectó este error:

{error}

Caso de prueba:
ID: {test["id"]}
Título: {test["title"]}
Pasos: {test["steps"]}
Resultado esperado: {test["expected_result"]}

Corregí el script completo.

REGLAS:
- Devolvé únicamente Python válido.
- No uses Markdown.
- No uses bloques de código.
- Usá playwright.sync_api.
- Usá sync_playwright.
- Chromium con headless={headless}.
- No uses pytest.
- No uses fixtures.
- No uses funciones test_*.
- Mantené el objetivo original del test.
- Cerrá el navegador al finalizar.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    codigo_corregido = response.text.strip()
    codigo_corregido = codigo_corregido.replace("```python", "")
    codigo_corregido = codigo_corregido.replace("```", "")

    return codigo_corregido
