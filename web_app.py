import streamlit as st
import os
import streamlit as st

from pathlib import Path
from src.url_validator import validar_url

st.set_page_config(
    page_title="AI QA Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI QA Agent")

st.write(
    "Generá y ejecutá pruebas automatizadas con IA "
    "sobre una aplicación web."
)

st.subheader("Configuración de la prueba")

base_url = st.text_input(
    "URL de la aplicación",
    placeholder="https://ejemplo.com"
)

historia = st.text_area(
    "Historia de usuario",
    placeholder=(
        "Como usuario quiero iniciar sesión "
        "para acceder al sistema."
    )
)

col1, col2 = st.columns(2)

with col1:
    test_username = st.text_input(
        "Usuario o email (opcional)"
    )

with col2:
    test_password = st.text_input(
        "Contraseña (opcional)",
        type="password"
    )

ejecutar = st.button(
    "🚀 Ejecutar QA",
    type="primary"
)

if ejecutar:
    validacion_url = validar_url(base_url)

    if not validacion_url["valid"]:
        st.error(
            f"URL no válida: {validacion_url['error']}"
        )

    elif not historia:
        st.error("Ingresá una historia de usuario.")

    else:
        from src.agent_engine import ejecutar_agente
        import json

        try:
            with st.status(
                "Ejecutando AI QA Agent...",
                expanded=True
            ) as status:

                st.write("🔎 Inspeccionando sitio...")
                st.write("🤖 Generando casos de prueba...")
                st.write("🧪 Generando y ejecutando Playwright...")

                resultado = ejecutar_agente(
                    base_url=base_url,
                    historia=historia,
                    test_username=test_username,
                    test_password=test_password,
                    headless=True
                )

                status.update(
                    label="Ejecución finalizada",
                    state="complete"
                )

            st.success("✅ QA finalizado correctamente.")

            st.caption(
                f"Run ID: {resultado['run_id']}"
            )

            resultados = resultado["results"]

            total = len(resultados)
            passed = sum(
                1 for test in resultados
                if test["status"] == "PASS"
            )
            failed = total - passed

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total", total)

            with col2:
                st.metric("PASS", passed)

            with col3:
                st.metric("FAIL", failed)

            st.subheader("🧪 Resultados de pruebas")

            for test in resultados:
                titulo = f"{test['id']} — {test['title']}"

                with st.expander(titulo):
                    if test["status"] == "PASS":
                        st.success("PASS")

                    else:
                        st.error("FAIL")

                        failure_type = test.get(
                            "failure_type"
                        )

                        if failure_type:
                            st.write(
                                "Tipo de fallo:",
                                failure_type
                            )

                        analisis = test.get("analysis")

                        if analisis:
                            st.write(
                                "Clasificación:",
                                analisis.get(
                                    "classification",
                                    "No determinada"
                                )
                            )

                            st.write(
                                "Severidad:",
                                analisis.get(
                                    "severity",
                                    "No determinada"
                                )
                            )

                            st.write(
                                "Causa:",
                                analisis.get(
                                    "cause",
                                    "No determinada"
                                )
                            )

                        screenshot = test.get("screenshot")

                        if (
                            screenshot
                            and os.path.exists(screenshot)
                        ):
                            st.image(
                                screenshot,
                                caption=f"Evidencia {test['id']}"
                            )

            st.subheader("📄 Reporte QA")
            st.markdown(resultado["report"])

            st.subheader("⬇️ Descargas")

            results_json = json.dumps(
                resultados,
                indent=2,
                ensure_ascii=False
            )

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="Descargar results.json",
                    data=results_json,
                    file_name="results.json",
                    mime="application/json"
                )

            with col2:
                st.download_button(
                    label="Descargar qa_report.md",
                    data=resultado["report"],
                    file_name="qa_report.md",
                    mime="text/markdown"
                )

            run_dir = Path(resultado["run_dir"])

            evidencias = list(
                run_dir.glob("evidence_*.png")
            )

            bug_reports = list(
                run_dir.glob("bug_report_*.md")
            )

            if evidencias:
                st.subheader("📸 Evidencias")

                for evidencia in evidencias:
                    st.image(
                        str(evidencia),
                        caption=evidencia.name
                    )

                    with open(evidencia, "rb") as archivo:
                        st.download_button(
                            label=f"Descargar {evidencia.name}",
                            data=archivo.read(),
                            file_name=evidencia.name,
                            mime="image/png",
                            key=f"download_{evidencia.name}"
                        )

            if bug_reports:
                st.subheader("🐛 Bug Reports")

                for bug_report in bug_reports:
                    contenido = bug_report.read_text(
                        encoding="utf-8"
                    )

                    with st.expander(bug_report.name):
                        st.markdown(contenido)

                        st.download_button(
                            label=f"Descargar {bug_report.name}",
                            data=contenido,
                            file_name=bug_report.name,
                            mime="text/markdown",
                            key=f"download_{bug_report.name}"
                        )

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(
                "Ocurrió un error inesperado durante la ejecución."
            )

            with st.expander("Ver detalle técnico"):
                st.exception(error)
