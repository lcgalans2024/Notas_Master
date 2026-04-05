import streamlit as st

from components.alerts import render_empty_state, render_error_box
from services.materiales_service import (obtener_materiales_usuario,
                                         mostrar_actividades,
                                         mostrar_recursos,
)


def _mostrar_encabezado() -> None:
    """
    Renderiza el encabezado principal de la página.
    """
    st.title("Material del área")
    st.caption(
        "Consulta guías, enlaces, recursos y materiales de apoyo disponibles para tu grupo."
    )


def _mostrar_resumen_usuario() -> None:
    """
    Muestra información básica del estudiante autenticado.
    """
    nombre = st.session_state.get("nombre", "Usuario")
    grupo = st.session_state.get("grupo", "No definido")
    anio = st.session_state.get("anio_academico", "No definido")

    st.metric("Estudiante", nombre)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Grupo", grupo)

    with col2:
        st.metric("Año académico", anio)


def _mostrar_materiales(df_materiales) -> None:
    """
    Renderiza la tabla de materiales.
    """
    st.subheader("Recursos disponibles")
    st.dataframe(df_materiales, use_container_width=True, hide_index=True)


def render_materiales() -> None:
    """
    Renderiza la página de materiales del área.
    """
    _mostrar_encabezado()
    _mostrar_resumen_usuario()
    st.divider()

    grupo = st.session_state.get("grupo")
    anio = st.session_state.get("anio_academico")

    if not grupo:
        render_error_box("No fue posible identificar el grupo asociado al usuario.")
        return

    # crear pestañas para actividades y recursos
    tab_actividades, tab_recursos = st.tabs(["Actividades", "Recursos"])
    with tab_actividades:
        mostrar_actividades()
    with tab_recursos:
        mostrar_recursos()