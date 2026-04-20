from config.roles_config import ADMIN_DOCUMENTOS


def obtener_rol_usuario(documento: str) -> str:
    documento = str(documento).strip()

    if documento in ADMIN_DOCUMENTOS:
        return "admin"

    return "estudiante"


def es_admin(documento: str) -> bool:
    return obtener_rol_usuario(documento) == "admin"