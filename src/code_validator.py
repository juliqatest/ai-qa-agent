import ast


def validar_codigo_python(codigo):
    try:
        ast.parse(codigo)

        return {
            "valid": True,
            "error": None
        }

    except SyntaxError as error:
        return {
            "valid": False,
            "error": (
                f"{error.__class__.__name__}: "
                f"{error.msg} "
                f"(línea {error.lineno})"
            )
        }
