import time
import streamlit as st

from config.settings import APP_CONFIG
from core.session_state import inicializar_session_state
from utils.diagnostics import (
    track_session,
)
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

    # 1. Primera llamada de Streamlit
    configurar_pagina()

    # 2. Inicializar estado general de la sesión
    inicializar_session_state()

    # 3. Iniciar medición del rerun
    inicio_rerun = time.perf_counter()

    # 4. Registrar diagnóstico
    diag = track_session()

    st.session_state["diagnostics"] = diag

    # 5. Renderizar aplicación
    render_app()

    # 6. Guardar duración del rerun
    st.session_state["diagnostics"]["execution_time"] = (
        time.perf_counter() - inicio_rerun
    )


if __name__ == "__main__":
    main()