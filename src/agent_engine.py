import json
import os
import time

from google import genai
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4

from src.bug_report_generator import generar_bug_report
from src.code_fixer import corregir_codigo
from src.code_validator import validar_codigo_python
from src.config import MODEL, TEST_TIMEOUT, MAX_TEST_CASES, RUN_TIMEOUT
from src.failure_analyzer import analizar_fallo
from src.playwright_generator import generar_playwright
from src.report_generator import generar_reporte
from src.site_inspector import inspeccionar_sitio
from src.test_generator import generar_casos
from src.test_runner import ejecutar_test
from src.url_validator import validar_url
from src.run_cleanup import limpiar_runs_viejos

load_dotenv()

def ejecutar_agente(
    base_url,
    historia,
    test_username="",
    test_password="",
    headless=True
):
    inicio = time.monotonic()
    limpiar_runs_viejos(
        runs_dir="runs",
        max_age_hours=24
    )

    validacion_url = validar_url(base_url)

    if not validacion_url["valid"]:
        raise ValueError(
            f"URL no válida: {validacion_url['error']}"
        )
	
    client = genai.Client()

    run_id = uuid4().hex[:8]

    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    site_context = inspeccionar_sitio(
        base_url=base_url,
        headless=headless
    )

    datos = generar_casos(
        client=client,
        model=MODEL,
        historia=historia
    )

    datos["test_cases"] = datos["test_cases"][:MAX_TEST_CASES]
    resultados = []

    for test in datos["test_cases"]:
        test_id = test["id"]
        titulo = test["title"]

        if time.monotonic() - inicio > RUN_TIMEOUT:
            resultados.append({
                "id": "RUN",
                "title": "Timeout global",
                "status": "FAIL",
                "failure_type": "RUN_TIMEOUT",
                "error": "La ejecución superó el tiempo máximo permitido."
            })

            break

        codigo = generar_playwright(
            client=client,
            model=MODEL,
            test=test,
            headless=headless,
            base_url=base_url,
            site_context=site_context,
            test_username=test_username,
            test_password=test_password
        )

        validacion = validar_codigo_python(codigo)

        if not validacion["valid"]:
            codigo = corregir_codigo(
                client=client,
                model=MODEL,
                codigo=codigo,
                error=validacion["error"],
                test=test,
                headless=headless
            )

            segunda_validacion = validar_codigo_python(codigo)

            if not segunda_validacion["valid"]:
                resultados.append({
                    "id": test_id,
                    "title": titulo,
                    "status": "FAIL",
                    "failure_type": "TEST_ERROR",
                    "error": segunda_validacion["error"]
                })

                continue

        archivo_test = run_dir / f"test_{test_id}.py"

        with open(archivo_test, "w", encoding="utf-8") as archivo:
            archivo.write(codigo.strip())

        resultado = ejecutar_test(
            archivo_test=str(archivo_test),
            timeout=TEST_TIMEOUT
        )

        if resultado["failure_type"] == "TIMEOUT":
            resultados.append({
                "id": test_id,
                "title": titulo,
                "status": "FAIL",
                "failure_type": "TIMEOUT",
                "error": resultado["stderr"]
            })

            continue

        if resultado["status"] == "PASS":
            resultados.append({
                "id": test_id,
                "title": titulo,
                "status": "PASS"
            })

            continue

        error = resultado["stderr"]
        screenshot = str(
    run_dir / f"evidence_{test_id}.png"
)

        analisis = analizar_fallo(
            client=client,
            model=MODEL,
            historia=historia,
            test=test,
            error=error,
            screenshot=screenshot
        )

        resultado_final = {
            "id": test_id,
            "title": titulo,
            "status": "FAIL",
            "error": error,
            "screenshot": screenshot if os.path.exists(screenshot) else None,
            "analysis": analisis
        }

        resultados.append(resultado_final)

        if analisis["classification"] == "BUG":
            contenido_bug = generar_bug_report(
                test=test,
                analisis=analisis,
                screenshot=screenshot if os.path.exists(screenshot) else None
            )

            with open(
                run_dir / f"bug_report_{test_id}.md",
                "w",
                encoding="utf-8"
            ) as archivo:
                archivo.write(contenido_bug)

    with open(
        run_dir / "results.json",
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            resultados,
            archivo,
            indent=2,
            ensure_ascii=False
        )

    reporte = generar_reporte(
        client=client,
        model=MODEL,
        resultados=resultados
    )

    with open(
        run_dir / "qa_report.md",
        "w",
        encoding="utf-8"
    ) as archivo:
        archivo.write(reporte)

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "site_context": site_context,
        "test_cases": datos,
        "results": resultados,
        "report": reporte
    }
