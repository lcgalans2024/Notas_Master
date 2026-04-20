import streamlit as st

from config.sheets_config import SHEETS_CONFIG
from services.auth_service import cerrar_sesion, refrescar_contexto_usuario_por_anio
from services.google_sheets_service import (
    limpiar_cache_datos,
    obtener_periodos_disponibles_por_grupo,
)

PAGINAS_DESHABILITADAS = {
    "Informe académico": "Esta sección estará disponible próximamente.",
}


def _obtener_opciones_menu() -> list[str]:
    rol = st.session_state.get("rol", "estudiante")

    opciones_estudiante = [
        "Inicio",
        "Consulta de notas",
        "Informe académico",
        "Material del área",
        "Recuperaciones",
        "Autoevaluación",
        #"Test Google Connection",
    ]

    opciones_admin = [
        "Inicio",
        "Consulta de notas",
        "Informe académico",
        "Material del área",
        "Recuperaciones",
        "Autoevaluación",
        "Administración",
    ]

    return opciones_admin if rol == "admin" else opciones_estudiante


def _render_datos_usuario() -> None:
    """
    Muestra un resumen del usuario autenticado.
    """
    nombre = st.session_state.get("nombre", "Usuario")
    matricula = st.session_state.get("matricula")
    grupo = st.session_state.get("grupo")
    rol = st.session_state.get("rol", "estudiante")

    st.markdown(f"### {nombre}")
    st.caption(f"Rol: {rol}")

    if grupo:
        if rol == "admin":
            st.caption(f"Grupo seleccionado: {grupo}")
        else:
            st.caption(f"Grupo: {grupo}")

    #if matricula:
    #    st.caption(f"Matrícula: {matricula}")

def _resolver_periodos_disponibles(grupo: str | None) -> list[str]:
    if not grupo:
        return SHEETS_CONFIG.get("periodos_disponibles", ["P1", "P2", "P3", "P4"])

    periodos = obtener_periodos_disponibles_por_grupo(grupo)

    if not periodos:
        return SHEETS_CONFIG.get("periodos_disponibles", ["P1", "P2", "P3", "P4"])

    return periodos


def _actualizar_contexto_si_cambia_anio(nuevo_anio: str) -> None:
    """
    Si el año académico cambia:
    - estudiante: actualiza contexto y grupo desde la base
    - admin: solo actualiza el año
    """
    anio_actual = st.session_state.get("anio_academico")
    rol = st.session_state.get("rol", "estudiante")

    if str(nuevo_anio) == str(anio_actual):
        return

    st.session_state["anio_academico"] = str(nuevo_anio)

    if rol == "admin":
        return

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
    """
    Renderiza filtros generales de trabajo en la barra lateral.
    - Estudiante: usa su grupo asociado.
    - Admin: puede seleccionar manualmente el grupo.
    """
    anios = SHEETS_CONFIG.get("anios_disponibles", [])
    grupos_disponibles = SHEETS_CONFIG.get("grupos_disponibles", [])
    rol = st.session_state.get("rol", "estudiante")

    anio_actual = st.session_state.get("anio_academico")
    periodo_actual = st.session_state.get("periodo")
    grupo_actual = st.session_state.get("grupo")

    # Año académico
    if anios:
        index_anio = anios.index(anio_actual) if anio_actual in anios else 0
        nuevo_anio = st.selectbox(
            "Año académico",
            options=anios,
            index=index_anio,
        )
        _actualizar_contexto_si_cambia_anio(nuevo_anio)

    # Grupo
    if rol == "admin":
        grupos_disponibles = [str(g) for g in grupos_disponibles]

        if grupos_disponibles:
            if grupo_actual not in grupos_disponibles:
                grupo_actual = grupos_disponibles[0]
                st.session_state["grupo"] = grupo_actual

            index_grupo = (
                grupos_disponibles.index(grupo_actual)
                if grupo_actual in grupos_disponibles
                else 0
            )

            st.session_state["grupo"] = st.selectbox(
                "Grupo",
                options=grupos_disponibles,
                index=index_grupo,
            )

    # Resolver periodos según el grupo ya definitivo
    grupo_definitivo = st.session_state.get("grupo")
    periodos_disponibles = _resolver_periodos_disponibles(grupo_definitivo)

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