from __future__ import annotations

import streamlit as st

from services.usuarios_service import (
    obtener_usuario_por_documento,
    obtener_usuario_por_documento_y_anio,
)
from services.roles_service import obtener_rol_usuario, es_admin


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
    
    # Caso 1: administrador
    if es_admin(documento):
        st.session_state["usuario"] = documento
        st.session_state["nombre"] = "Administrador"
        st.session_state["grupo"] = None
        st.session_state["rol"] = "admin"
        st.session_state["datos_usuario"] = {
            "documento": documento,
            "nombre": "Administrador",
            "grupo": None,
            "rol": "admin",
        }
        st.session_state["authenticated"] = True
        st.session_state["menu"] = "Inicio"
        st.session_state["vista_actual"] = "Inicio"
        st.session_state["anio_usuario_contexto"] = st.session_state.get("anio_academico")

        return True, "Ingreso exitoso como administrador."

    # Caso 2: estudiante

    try:
        usuario = obtener_usuario_por_documento(documento)
        
    except Exception as exc:
        return False, f"No fue posible validar el usuario. Detalle: {exc}"

    if not usuario:
        return False, "No se encontró información asociada a ese documento."

    rol = obtener_rol_usuario(usuario["documento"])

    st.session_state["usuario"] = usuario["documento"]
    st.session_state["nombre"] = usuario["nombre"]
    st.session_state["grupo"] = usuario.get("grupo")
    st.session_state["matricula"] = usuario.get("matricula")
    st.session_state["rol"] = rol#usuario.get("rol", "estudiante")
    st.session_state["datos_usuario"] = usuario
    st.session_state["authenticated"] = True
    st.session_state["menu"] = "Inicio"
    st.session_state["vista_actual"] = "Inicio"
    st.session_state["anio_usuario_contexto"] = st.session_state.get("anio_academico")

    return True, f"Bienvenido(a), {usuario['nombre']}."


def cerrar_sesion() -> None:
    """
    Cierra la sesión del usuario actual sin destruir toda la sesión.
    """
    claves_a_limpiar = {
        "usuario": None,
        "nombre": None,
        "grupo": None,
        "matricula": None,
        "rol": None,
        "datos_usuario": None,
        "authenticated": False,
        "menu": "Inicio",
        "vista_actual": "Inicio",
        "filtros": {},
        "anio_usuario_contexto": None,
    }

    for clave, valor in claves_a_limpiar.items():
        st.session_state[clave] = valor


def refrescar_contexto_usuario_por_anio(anio_academico: str) -> tuple[bool, str]:
    """
    Recalcula la información del usuario autenticado para el año académico dado.
    Actualiza nombre, grupo y datos_usuario en session_state.
    """
    documento = st.session_state.get("usuario")

    if not documento:
        return False, "No hay un usuario autenticado para refrescar."

    try:
        usuario = obtener_usuario_por_documento_y_anio(documento, anio_academico)
    except Exception as exc:
        return False, f"No fue posible actualizar el contexto del usuario. Detalle: {exc}"

    if not usuario:
        return False, (
            f"No se encontró información del usuario en la base de estudiantes "
            f"para el año {anio_academico}."
        )

    rol = obtener_rol_usuario(usuario["documento"])

    st.session_state["nombre"] = usuario["nombre"]
    st.session_state["grupo"] = usuario.get("grupo")
    st.session_state["matricula"] = usuario.get("matricula")
    st.session_state["rol"] = rol#usuario.get("rol", "estudiante")
    st.session_state["datos_usuario"] = usuario
    st.session_state["anio_usuario_contexto"] = str(anio_academico)

    return True, "Contexto del usuario actualizado correctamente."