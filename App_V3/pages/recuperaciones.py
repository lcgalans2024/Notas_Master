import streamlit as st

from components.alerts import render_empty_state, render_error_box
from services.recuperaciones_service import obtener_recuperaciones_usuario


def _mostrar_encabezado() -> None:
    """
    Renderiza el encabezado principal de la página.
    """
    st.title("Recuperaciones")
    st.caption(
        "Consulta actividades, orientaciones o procesos de recuperación académica disponibles."
    )


def _mostrar_resumen_usuario() -> None:
    """
    Muestra información básica del estudiante autenticado.
    """
    nombre = st.session_state.get("nombre", "Usuario")
    grupo = st.session_state.get("grupo", "No definido")
    anio = st.session_state.get("anio_academico", "No definido")
    periodo = st.session_state.get("periodo", "No definido")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Estudiante", nombre)

    with col2:
        st.metric("Grupo", grupo)

    with col3:
        st.metric("Periodo", f"{periodo} · {anio}")


def _mostrar_recuperaciones(df_recuperaciones) -> None:
    """
    Muestra la tabla principal de recuperaciones.
    """
    st.subheader("Actividades disponibles")
    st.dataframe(df_recuperaciones, use_container_width=True, hide_index=True)


def render_recuperaciones() -> None:
    """
    Renderiza la página de recuperaciones.
    """
    _mostrar_encabezado()
    _mostrar_resumen_usuario()
    st.divider()

    grupo = st.session_state.get("grupo")
    anio = st.session_state.get("anio_academico")
    periodo = st.session_state.get("periodo")

    if not grupo:
        render_error_box("No fue posible identificar el grupo asociado al usuario.")
        return

    try:
        df_recuperaciones = obtener_recuperaciones_usuario(
            grupo=grupo,
            anio_academico=anio,
            periodo=periodo,
        )
    except Exception as exc:
        render_error_box(f"Ocurrió un error al consultar las recuperaciones: {exc}")
        return

    if df_recuperaciones is None or df_recuperaciones.empty:
        render_empty_state(
            title="No hay recuperaciones disponibles",
            message=(
                "No se encontraron actividades de recuperación publicadas "
                "para este grupo y periodo."
            ),
        )
        return

    _mostrar_recuperaciones(df_recuperaciones)