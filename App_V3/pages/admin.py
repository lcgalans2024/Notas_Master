import streamlit as st
from services.google_sheets_service import cargar_roles
from utils.diagnostics import render_diagnostics

def render_admin() -> None:
    if st.session_state.get("rol") != "admin":
        st.error("No tienes permisos para acceder a esta sección.")
        return

    st.title("Panel de administración")
    st.write("Aquí podrás ubicar herramientas exclusivas para administradores.")

    st.divider()
    st.subheader("Prueba de carga de roles")
    df_roles = cargar_roles()
    st.dataframe(df_roles, use_container_width=True)

    diag = st.session_state.get("diagnostics")

    if diag is None:
        st.info("Diagnóstico aún no disponible.")
        return

    render_diagnostics(diag)