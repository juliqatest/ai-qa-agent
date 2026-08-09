from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

error = """
AssertionError: Page URL expected to be:
https://www.saucedemo.com/inventory.html

Actual value:
https://www.saucedemo.com/

The application displayed:
"Epic sadface: Username and password do not match any user in this service"

Test data:
Username: standard_user
Password: wrong_password
"""

prompt = f"""
Sos un QA Analyst Senior especializado en análisis de fallos
de pruebas automatizadas.

Analizá el siguiente fallo de Playwright:

{error}

Generá un reporte con exactamente estas secciones:

1. RESULTADO
2. CAUSA PROBABLE
3. SEVERIDAD
4. ¿ES UN BUG?
5. EVIDENCIA
6. RECOMENDACIÓN

Importante:
- Diferenciá un fallo provocado intencionalmente por datos inválidos
  de un defecto real del sistema.
- No inventes información.
- Respondé en español.
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt
)

print("\n===== ANÁLISIS DEL FALLO =====\n")
print(response.text)

