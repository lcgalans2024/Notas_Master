import streamlit as st

from components.alerts import render_empty_state, render_error_box, render_info_box
from services.notas_service import obtener_notas_usuario


def _mostrar_encabezado() -> None:
    """
    Renderiza el encabezado de la página.
    """
    st.title("Consulta de notas")
    st.caption("Consulta las calificaciones registradas para el periodo seleccionado.")


def _mostrar_resumen_usuario() -> None:
    """
    Muestra información básica del estudiante autenticado.
    """
    nombre = st.session_state.get("nombre", "Usuario")
    grupo = st.session_state.get("grupo", "No definido")
    periodo = st.session_state.get("periodo", "No definido")
    anio = st.session_state.get("anio_academico", "No definido")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Estudiante", nombre)

    with col2:
        st.metric("Grupo", grupo)

    with col3:
        st.metric("Periodo", f"{periodo} · {anio}")


def _mostrar_tabla_notas(df_notas) -> None:
    """
    Muestra la tabla principal de notas.
    """
    st.subheader("Detalle de calificaciones")
    st.dataframe(df_notas, use_container_width=True, hide_index=True)


def render_consulta_notas() -> None:
    """
    Renderiza la página de consulta de notas del usuario autenticado.
    """
    _mostrar_encabezado()
    _mostrar_resumen_usuario()
    st.divider()

    usuario = st.session_state.get("usuario")
    grupo = st.session_state.get("grupo")
    periodo = st.session_state.get("periodo")

    if not usuario:
        render_info_box("No hay un usuario autenticado en la sesión.")
        return

    if not grupo:
        render_error_box("No fue posible identificar el grupo asociado al usuario.")
        return

    if not periodo:
        render_error_box("No fue posible identificar el periodo activo.")
        return

    try:
        df_notas = obtener_notas_usuario(
            documento=usuario,
            grupo=grupo,
            periodo=periodo,
        )
    except Exception as exc:
        render_error_box(f"Ocurrió un error al consultar las notas: {exc}")
        return

    if df_notas is None or df_notas.empty:
        render_empty_state(
            title="No hay notas disponibles",
            message="Aún no se encontraron calificaciones registradas para este estudiante en el periodo seleccionado.",
        )
        return

    _mostrar_tabla_notas(df_notas)