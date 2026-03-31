import streamlit as st

from config.settings import APP_DEFAULTS


def inicializar_session_state() -> None:
    """
    Inicializa las claves base de st.session_state necesarias
    para el funcionamiento de la aplicación.

    Solo crea las claves si aún no existen, para no sobrescribir
    información activa durante la navegación del usuario.
    """
    for key, value in APP_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Claves adicionales de control interno
    claves_internas = {
        "filtros": {},
        "menu": "Inicio",
        "datos_usuario": None,
        "ultima_actualizacion": None,
        "forzar_recarga": False,
    }

    for key, value in claves_internas.items():
        if key not in st.session_state:
            st.session_state[key] = value


def resetear_sesion_usuario() -> None:
    """
    Limpia únicamente las variables asociadas al usuario autenticado,
    sin destruir toda la sesión de Streamlit.
    """
    claves_usuario = [
        "usuario",
        "matricula",
        "nombre",
        "grupo",
        "adm",
        "authenticated",
        "datos_usuario",
        "menu",
        "filtros",
        "vista_actual",
    ]

    for key in claves_usuario:
        if key in st.session_state:
            if key in APP_DEFAULTS:
                st.session_state[key] = APP_DEFAULTS[key]
            elif key == "menu":
                st.session_state[key] = "Inicio"
            elif key == "filtros":
                st.session_state[key] = {}
            else:
                st.session_state[key] = None


def actualizar_filtro(nombre_filtro: str, valor) -> None:
    """
    Actualiza un filtro dentro de session_state de forma controlada.
    """
    if "filtros" not in st.session_state or not isinstance(st.session_state.filtros, dict):
        st.session_state.filtros = {}

    st.session_state.filtros[nombre_filtro] = valor


def obtener_filtro(nombre_filtro: str, default=None):
    """
    Recupera un filtro almacenado en session_state.
    """
    filtros = st.session_state.get("filtros", {})
    return filtros.get(nombre_filtro, default)