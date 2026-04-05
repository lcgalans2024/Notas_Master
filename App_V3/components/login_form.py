import streamlit as st

from config.settings import APP_INFO
from services.auth_service import autenticar_usuario


def render_login_form() -> None:
    """
    Renderiza el formulario de inicio de sesión.
    """
    st.title(APP_INFO["welcome_title"])
    st.caption(APP_INFO["welcome_subtitle"])

    with st.container(border=True):
        st.subheader("Ingreso a la plataforma")

        documento = st.text_input(
            "Documento del estudiante",
            placeholder="Ingresa el número de documento",
            type="password",
        ).strip()

        col1, col2 = st.columns([1, 3])

        with col1:
            ingresar = st.button("Ingresar", use_container_width=True)

        with col2:
            pass

        if ingresar:
            if not documento:
                st.warning("Por favor, ingresa un documento válido.")
                return

            ok, mensaje = autenticar_usuario(documento)

            if ok:
                st.success(mensaje)
                st.rerun()
            else:
                st.error(mensaje)