from urllib.parse import urlparse
import ipaddress
import socket


def validar_url(url):
    if not url:
        return {
            "valid": False,
            "error": "La URL está vacía."
        }

    try:
        parsed = urlparse(url)
    except ValueError:
        return {
            "valid": False,
            "error": "La URL no es válida."
        }

    if parsed.scheme not in ("http", "https"):
        return {
            "valid": False,
            "error": "Solo se permiten URLs http o https."
        }

    if not parsed.hostname:
        return {
            "valid": False,
            "error": "La URL no contiene un dominio válido."
        }

    hostname = parsed.hostname.lower()

    bloqueados = {
        "localhost",
        "0.0.0.0",
        "::1"
    }

    if hostname in bloqueados:
        return {
            "valid": False,
            "error": "No se permiten direcciones locales."
        }

    try:
        ip = ipaddress.ip_address(hostname)

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        ):
            return {
                "valid": False,
                "error": "No se permiten direcciones IP privadas o internas."
            }

    except ValueError:
        pass

    try:
        direcciones = socket.getaddrinfo(
            hostname,
            None
        )

        for direccion in direcciones:
            ip_texto = direccion[4][0]

            try:
                ip = ipaddress.ip_address(ip_texto)

                if (
                    ip.is_private
                    or ip.is_loopback
                    or ip.is_link_local
                    or ip.is_reserved
                    or ip.is_multicast
                ):
                    return {
                        "valid": False,
                        "error": (
                            "El dominio apunta a una dirección "
                            "privada o interna."
                        )
                    }

            except ValueError:
                continue

    except socket.gaierror:
        pass

    return {
        "valid": True,
        "error": None
    }
