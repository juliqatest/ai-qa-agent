def generar_bug_report(test, analisis, screenshot=None):
    test_id = test["id"]

    reporte = f"""# Bug Report - {test_id}

## Título
{analisis.get("bug_title", "Sin título")}

## Severidad
{analisis.get("severity", "No determinada")}

## Caso de prueba
{test_id} - {test["title"]}

## Pasos para reproducir
"""

    for numero, paso in enumerate(test["steps"], start=1):
        reporte += f"{numero}. {paso}\n"

    reporte += f"""
## Resultado esperado
{analisis.get("expected", test["expected_result"])}

## Resultado obtenido
{analisis.get("actual", "No determinado")}

## Causa probable
{analisis.get("cause", "No determinada")}

## Recomendación
{analisis.get("recommendation", "Revisión manual")}
"""

    if screenshot:
        reporte += f"""
## Evidencia
{screenshot}
"""

    return reporte

