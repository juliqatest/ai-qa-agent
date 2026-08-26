
def generar_playwright(
    client,
    model,
    test,
    headless,
    base_url,
    site_context,
    test_username,
    test_password
):

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
{base_url}

CONTEXTO REAL DEL SITIO:

Título:
{site_context["title"]}

Formularios detectados:
{site_context.get("forms", [])}

Texto visible de la página:
{site_context.get("page_text_preview", "")}

Elementos interactivos detectados:
{site_context["elements"]}

Credenciales proporcionadas por el usuario:

usuario/email: {test_username or "No proporcionado"}
password: {test_password or "No proporcionado"}

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
- Basate en los elementos reales detectados.
- No inventes selectores si el contexto contiene información suficiente.
- Priorizá locators semánticos de Playwright:
  get_by_role
  get_by_label
  get_by_placeholder
  get_by_text
- Evitá XPath.
- Evitá selectores CSS frágiles cuando exista un locator semántico.
- Si no hay credenciales proporcionadas, no inventes usuario ni contraseña.
- Si el caso requiere autenticación y no hay credenciales suficientes, generá un test que valide lo que pueda observarse sin inventar datos.
- Usá las credenciales proporcionadas únicamente cuando el caso lo requiera.
- Usá el contexto real del sitio para decidir qué elementos interactuar.
- Priorizá get_by_role, get_by_label, get_by_placeholder y get_by_text.
- Si un formulario fue detectado, usá sus campos y botones reales.
- No inventes elementos que no estén presentes en el contexto.
- Si el sitio no tiene elementos suficientes para ejecutar el caso solicitado, generá un test que falle de forma clara indicando que el escenario no es automatizable con la información disponible.

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
