from pathlib import Path

from src.code_validator import validar_codigo_python
from src.test_runner import ejecutar_test
from src.bug_report_generator import generar_bug_report


def test_code_validator_accepts_valid_python():
    codigo = 'print("hola")'

    resultado = validar_codigo_python(codigo)

    assert resultado["valid"] is True
    assert resultado["error"] is None


def test_code_validator_rejects_invalid_python():
    codigo = """
if True
    print("hola")
"""

    resultado = validar_codigo_python(codigo)

    assert resultado["valid"] is False
    assert "SyntaxError" in resultado["error"]


def test_runner_detects_pass(tmp_path):
    archivo = tmp_path / "pass_test.py"
    archivo.write_text('print("PASS")')

    resultado = ejecutar_test(str(archivo))

    assert resultado["status"] == "PASS"
    assert resultado["returncode"] == 0


def test_runner_detects_fail(tmp_path):
    archivo = tmp_path / "fail_test.py"
    archivo.write_text('raise AssertionError("fallo controlado")')

    resultado = ejecutar_test(str(archivo))

    assert resultado["status"] == "FAIL"
    assert resultado["returncode"] != 0
    assert "AssertionError" in resultado["stderr"]


def test_bug_report_generation():
    test = {
        "id": "TC001",
        "title": "Login válido",
        "steps": [
            "Abrir login",
            "Ingresar credenciales",
            "Presionar Login"
        ],
        "expected_result": "El usuario accede al sistema"
    }

    analisis = {
        "bug_title": "Login no permite acceder",
        "severity": "High",
        "expected": "El usuario accede al sistema",
        "actual": "El usuario permanece en login",
        "cause": "Error en autenticación",
        "recommendation": "Revisar servicio de login"
    }

    reporte = generar_bug_report(
        test=test,
        analisis=analisis,
        screenshot="evidence_TC001.png"
    )

    assert "Login no permite acceder" in reporte
    assert "High" in reporte
    assert "evidence_TC001.png" in reporte
    assert "El usuario accede al sistema" in reporte
