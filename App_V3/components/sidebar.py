import streamlit as st

from config.sheets_config import SHEETS_CONFIG
from services.auth_service import cerrar_sesion
from services.google_sheets_service import (
    limpiar_cache_datos,
    obtener_periodos_disponibles_por_grupo,
)


def _obtener_opciones_menu() -> list[str]:
    """
    Retorna las opciones visibles del menú lateral.
    """
    return [
        "Inicio",
        "Consulta de notas",
        "Informe académico",
        "Material del área",
        "Recuperaciones",
    ]


def _render_datos_usuario() -> None:
    """
    Muestra un resumen del usuario autenticado.
    """
    nombre = st.session_state.get("nombre", "Usuario")
    grupo = st.session_state.get("grupo")
    rol = st.session_state.get("rol", "estudiante")

    st.markdown(f"### {nombre}")
    st.caption(f"Rol: {rol}")

    if grupo:
        st.caption(f"Grupo: {grupo}")


def _resolver_periodos_disponibles(grupo: str | None) -> list[str]:
    """
    Obtiene los periodos realmente disponibles para el grupo autenticado.
    Si no hay configuración específica, usa los periodos globales.
    """
    if not grupo:
        return SHEETS_CONFIG.get("periodos_disponibles", ["P1", "P2", "P3", "P4"])

    periodos = obtener_periodos_disponibles_por_grupo(grupo)

    if not periodos:
        return SHEETS_CONFIG.get("periodos_disponibles", ["P1", "P2", "P3", "P4"])

    return periodos


def _render_filtros_generales() -> None:
    """
    Renderiza filtros generales de trabajo en la barra lateral.
    """
    anios = SHEETS_CONFIG.get("anios_disponibles", [])
    grupo = st.session_state.get("grupo")
    anio_actual = st.session_state.get("anio_academico")
    periodo_actual = st.session_state.get("periodo")

    if anios:
        index_anio = anios.index(anio_actual) if anio_actual in anios else 0
        st.session_state["anio_academico"] = st.selectbox(
            "Año académico",
            options=anios,
            index=index_anio,
        )

    periodos_disponibles = _resolver_periodos_disponibles(grupo)

    if periodos_disponibles:
        if periodo_actual not in periodos_disponibles:
            st.session_state["periodo"] = periodos_disponibles[0]
            periodo_actual = periodos_disponibles[0]

        index_periodo = (
            periodos_disponibles.index(periodo_actual)
            if periodo_actual in periodos_disponibles
            else 0
        )

        st.session_state["periodo"] = st.selectbox(
            "Periodo",
            options=periodos_disponibles,
            index=index_periodo,
        )


def _render_acciones() -> None:
    """
    Muestra acciones globales como refrescar datos o cerrar sesión.
    """
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Actualizar", use_container_width=True):
            limpiar_cache_datos()
            st.success("La caché de datos fue limpiada correctamente.")
            st.rerun()

    with col2:
        if st.button("Salir", use_container_width=True):
            cerrar_sesion()
            st.rerun()


def render_sidebar() -> str:
    """
    Renderiza la barra lateral completa y retorna la opción de menú seleccionada.
    """
    with st.sidebar:
        st.title("Menú")
        st.divider()

        _render_datos_usuario()
        st.divider()

        menu_opciones = _obtener_opciones_menu()
        menu_actual = st.session_state.get("menu", "Inicio")
        index_menu = menu_opciones.index(menu_actual) if menu_actual in menu_opciones else 0

        menu_seleccionado = st.radio(
            "Navegación",
            options=menu_opciones,
            index=index_menu,
            label_visibility="collapsed",
        )

        st.session_state["menu"] = menu_seleccionado

        st.divider()
        st.subheader("Filtros")
        _render_filtros_generales()

        st.divider()
        _render_acciones()

    return menu_seleccionado