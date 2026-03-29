import streamlit as st

from config.settings import APP_INFO, IMAGE_PATHS
from components.alerts import render_info_box


def _mostrar_encabezado() -> None:
    """
    Muestra el encabezado principal de la página de inicio.
    """
    col1, col2 = st.columns([1, 5], vertical_alignment="center")

    with col1:
        escudo_path = IMAGE_PATHS.get("escudo")
        if escudo_path and escudo_path.exists():
            st.image(str(escudo_path), use_container_width=True)

    with col2:
        st.title(APP_INFO["app_name"])
        st.subheader(APP_INFO["institution_name"])
        st.caption(APP_INFO["welcome_subtitle"])


def _mostrar_bienvenida_usuario() -> None:
    """
    Muestra saludo personalizado al usuario autenticado.
    """
    nombre = st.session_state.get("nombre", "Usuario")
    grupo = st.session_state.get("grupo")

    st.markdown(f"### Hola, **{nombre}** 👋")

    if grupo:
        st.write(f"Grupo asociado: **{grupo}**")


def _mostrar_tarjetas_resumen() -> None:
    """
    Muestra tarjetas simples con las secciones disponibles en la plataforma.
    """
    tarjetas = [
        {
            "titulo": "Consulta de notas",
            "descripcion": "Revisa las calificaciones registradas en el periodo académico.",
        },
        {
            "titulo": "Informe académico",
            "descripcion": "Consulta observaciones, desempeño y seguimiento académico.",
        },
        {
            "titulo": "Material del área",
            "descripcion": "Accede a recursos, guías y material de apoyo.",
        },
        {
            "titulo": "Recuperaciones",
            "descripcion": "Consulta actividades y procesos de recuperación disponibles.",
        },
    ]

    cols = st.columns(2)

    for i, tarjeta in enumerate(tarjetas):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"#### {tarjeta['titulo']}")
                st.write(tarjeta["descripcion"])


def render_inicio() -> None:
    """
    Renderiza la página principal de inicio de la aplicación.
    """
    _mostrar_encabezado()
    st.divider()

    _mostrar_bienvenida_usuario()
    st.divider()

    render_info_box(
        "Usa el menú lateral para navegar entre las diferentes secciones de la plataforma."
    )

    _mostrar_tarjetas_resumen()