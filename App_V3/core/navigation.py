import streamlit as st

from config.settings import MESSAGES
from components.login_form import render_login_form
from components.sidebar import render_sidebar
from pages.inicio import render_inicio
from pages.consulta_notas import render_consulta_notas
from pages.informe import render_informe
from pages.materiales import render_materiales
from pages.recuperaciones import render_recuperaciones
from pages.autoevaluacion import render_autoevaluacion
#######################################################
from pages.test_google_connection import render_test_google_connection
######################################################################

PAGINAS_DESHABILITADAS = {
    "Informe académico": "Esta sección no se encuentra disponible.",
    "Recuperaciones": "Esta sección no se encuentra disponible.",
    #"Autoevaluación": "Esta sección no se encuentra disponible.",
}


def _render_pagina_seleccionada(menu: str) -> None:
    """
    Renderiza la página correspondiente según la opción seleccionada
    en el menú lateral.
    """
    paginas = {
        "Inicio": render_inicio,
        "Consulta de notas": render_consulta_notas,
        "Informe académico": render_informe,
        "Material del área": render_materiales,
        "Recuperaciones": render_recuperaciones,
        "Autoevaluación": render_autoevaluacion,
        "Test Google Connection": render_test_google_connection,
    }

    render_func = paginas.get(menu, render_inicio)
    render_func()


def render_app() -> None:
    """
    Orquesta el flujo principal de navegación de la aplicación.
    """
    if not st.session_state.get("authenticated", False):
        render_login_form()
        return

    menu_seleccionado = render_sidebar()
    st.session_state["vista_actual"] = menu_seleccionado

    if not menu_seleccionado:
        st.info(MESSAGES["login_required"])
        return
    
    if menu_seleccionado in PAGINAS_DESHABILITADAS:
        st.warning(PAGINAS_DESHABILITADAS[menu_seleccionado])
        return

    _render_pagina_seleccionada(menu_seleccionado)