import streamlit as st

from config.settings import APP_CONFIG
from core.session_state import inicializar_session_state
from core.navigation import render_app


def configurar_pagina() -> None:
    """Configura la página principal de Streamlit."""
    st.set_page_config(
        page_title=APP_CONFIG["page_title"],
        page_icon=APP_CONFIG["page_icon"],
        layout=APP_CONFIG["layout"],
        initial_sidebar_state=APP_CONFIG["initial_sidebar_state"],
    )


def main() -> None:
    """Punto de entrada principal de la aplicación."""
    configurar_pagina()
    inicializar_session_state()
    render_app()


if __name__ == "__main__":
    main()