import streamlit as st

from components.alerts import render_empty_state, render_error_box, render_info_box
from services.informe_service import obtener_informe_usuario


def _mostrar_encabezado() -> None:
    """
    Renderiza el encabezado principal de la página.
    """
    st.title("Informe académico")
    st.caption(
        "Consulta el resumen académico disponible para el estudiante en el periodo seleccionado."
    )


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


def _mostrar_informe(df_informe) -> None:
    """
    Muestra el informe académico en formato tabular.
    """
    st.subheader("Resumen académico")
    st.dataframe(df_informe, use_container_width=True, hide_index=True)


def render_informe() -> None:
    """
    Renderiza la página de informe académico.
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
        df_informe = obtener_informe_usuario(
            documento=usuario,
            grupo=grupo,
            periodo=periodo,
        )
    except Exception as exc:
        render_error_box(f"Ocurrió un error al consultar el informe académico: {exc}")
        return

    if df_informe is None or df_informe.empty:
        render_empty_state(
            title="No hay informe disponible",
            message=(
                "Aún no se encontró información de informe académico "
                "para este estudiante en el periodo seleccionado."
            ),
        )
        return

    _mostrar_informe(df_informe)