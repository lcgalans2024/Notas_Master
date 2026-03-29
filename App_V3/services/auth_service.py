from __future__ import annotations

import streamlit as st

from services.usuarios_service import obtener_usuario_por_documento


def normalizar_documento(documento: str) -> str:
    """
    Normaliza el documento ingresado por el usuario.

    - Elimina espacios al inicio y final.
    - Conserva solo caracteres útiles para identificación.
    """
    if documento is None:
        return ""

    return str(documento).strip()


def autenticar_usuario(documento: str) -> tuple[bool, str]:
    """
    Autentica un usuario a partir de su documento.

    Retorna:
        (True, mensaje) si la autenticación fue exitosa.
        (False, mensaje) si ocurrió algún problema.
    """
    documento = normalizar_documento(documento)

    if not documento:
        return False, "Debes ingresar un documento válido."

    try:
        usuario = obtener_usuario_por_documento(documento)
    except Exception as exc:
        return False, f"No fue posible validar el usuario. Detalle: {exc}"

    if not usuario:
        return False, "No se encontró información asociada a ese documento."

    st.session_state["usuario"] = usuario["documento"]
    st.session_state["nombre"] = usuario["nombre"]
    st.session_state["grupo"] = usuario.get("grupo")
    st.session_state["rol"] = usuario.get("rol", "estudiante")
    st.session_state["datos_usuario"] = usuario
    st.session_state["authenticated"] = True
    st.session_state["menu"] = "Inicio"
    st.session_state["vista_actual"] = "Inicio"

    return True, f"Bienvenido(a), {usuario['nombre']}."


def cerrar_sesion() -> None:
    """
    Cierra la sesión del usuario actual sin destruir toda la sesión.
    """
    claves_a_limpiar = {
        "usuario": None,
        "nombre": None,
        "grupo": None,
        "rol": None,
        "datos_usuario": None,
        "authenticated": False,
        "menu": "Inicio",
        "vista_actual": "Inicio",
        "filtros": {},
    }

    for clave, valor in claves_a_limpiar.items():
        st.session_state[clave] = valor