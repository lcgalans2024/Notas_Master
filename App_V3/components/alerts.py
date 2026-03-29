import streamlit as st


def render_info_box(message: str) -> None:
    """
    Muestra un mensaje informativo en un contenedor visual.
    """
    with st.container(border=True):
        st.info(message)


def render_success_box(message: str) -> None:
    """
    Muestra un mensaje de éxito en un contenedor visual.
    """
    with st.container(border=True):
        st.success(message)


def render_warning_box(message: str) -> None:
    """
    Muestra un mensaje de advertencia en un contenedor visual.
    """
    with st.container(border=True):
        st.warning(message)


def render_error_box(message: str) -> None:
    """
    Muestra un mensaje de error en un contenedor visual.
    """
    with st.container(border=True):
        st.error(message)


def render_empty_state(
    title: str = "Sin información disponible",
    message: str = "No hay datos para mostrar en este momento.",
) -> None:
    """
    Muestra un estado vacío reutilizable para tablas, reportes o consultas.
    """
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.write(message)