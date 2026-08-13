import json
import os

from google.genai import types


def analizar_fallo(
    client,
    model,
    historia,
    test,
    error,
    screenshot
):
    test_id = test["id"]
    titulo = test["title"]

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

    if screenshot and os.path.exists(screenshot):
        with open(screenshot, "rb") as archivo:
            imagen = archivo.read()

        contenido.append(
            types.Part.from_bytes(
                data=imagen,
                mime_type="image/png"
            )
        )

    response = client.models.generate_content(
        model=model,
        contents=contenido
    )

    try:
        return json.loads(response.text)

    except json.JSONDecodeError:
        return {
            "classification": "NEEDS_INVESTIGATION",
            "cause": response.text,
            "severity": "Unknown",
            "bug_title": "",
            "expected": test["expected_result"],
            "actual": "No determinado",
            "recommendation": "Revisión manual"
        }
