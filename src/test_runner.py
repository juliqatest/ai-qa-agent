import subprocess


def ejecutar_test(archivo_test, timeout=45):
    try:
        resultado = subprocess.run(
            ["python", archivo_test],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "status": "PASS" if resultado.returncode == 0 else "FAIL",
            "returncode": resultado.returncode,
            "stdout": resultado.stdout,
            "stderr": resultado.stderr,
            "failure_type": None
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL",
            "returncode": None,
            "stdout": "",
            "stderr": "El test excedió el timeout máximo.",
            "failure_type": "TIMEOUT"
        }
