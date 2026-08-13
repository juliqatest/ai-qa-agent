import json


def generar_reporte(client, model, resultados):
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
        model=model,
        contents=prompt_report
    )

    return response.text
