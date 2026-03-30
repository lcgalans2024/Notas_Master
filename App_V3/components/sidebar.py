import streamlit as st

from config.sheets_config import SHEETS_CONFIG
from services.auth_service import cerrar_sesion, refrescar_contexto_usuario_por_anio
from services.google_sheets_service import (
    limpiar_cache_datos,
    obtener_periodos_disponibles_por_grupo,
)


def _obtener_opciones_menu() -> list[str]:
    return [
        "Inicio",
        "Consulta de notas",
        "Informe académico",
        "Material del área",
        "Recuperaciones",
    ]


def _render_datos_usuario() -> None:
    nombre = st.session_state.get("nombre", "Usuario")
    grupo = st.session_state.get("grupo")
    rol = st.session_state.get("rol", "estudiante")

    st.markdown(f"### {nombre}")
    st.caption(f"Rol: {rol}")

    if grupo:
        st.caption(f"Grupo: {grupo}")


def _resolver_periodos_disponibles(grupo: str | None) -> list[str]:
    if not grupo:
        return SHEETS_CONFIG.get("periodos_disponibles", ["P1", "P2", "P3", "P4"])

    periodos = obtener_periodos_disponibles_por_grupo(grupo)

    if not periodos:
        return SHEETS_CONFIG.get("periodos_disponibles", ["P1", "P2", "P3", "P4"])

    return periodos


def _actualizar_contexto_si_cambia_anio(nuevo_anio: str) -> None:
    """
    Si el año académico cambia, actualiza el contexto del usuario
    y refresca el grupo asociado a ese año.
    """
    anio_actual = st.session_state.get("anio_academico")

    if str(nuevo_anio) == str(anio_actual):
        return

    st.session_state["anio_academico"] = str(nuevo_anio)

    ok, mensaje = refrescar_contexto_usuario_por_anio(str(nuevo_anio))

    if not ok:
        st.warning(mensaje)
        st.session_state["grupo"] = None
    else:
        grupo_actualizado = st.session_state.get("grupo")
        periodos_disponibles = _resolver_periodos_disponibles(grupo_actualizado)

        if periodos_disponibles:
            if st.session_state.get("periodo") not in periodos_disponibles:
                st.session_state["periodo"] = periodos_disponibles[0]


def _render_filtros_generales() -> None:
    anios = SHEETS_CONFIG.get("anios_disponibles", [])
    grupo = st.session_state.get("grupo")
    anio_actual = st.session_state.get("anio_academico")
    periodo_actual = st.session_state.get("periodo")

    if anios:
        index_anio = anios.index(anio_actual) if anio_actual in anios else 0
        nuevo_anio = st.selectbox(
            "Año académico",
            options=anios,
            index=index_anio,
        )
        _actualizar_contexto_si_cambia_anio(nuevo_anio)

    grupo = st.session_state.get("grupo")
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
    with st.sidebar:
        st.title("Menú")
        st.divider()

        st.subheader("Filtros")
        _render_filtros_generales()

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
        _render_acciones()

    return menu_seleccionado