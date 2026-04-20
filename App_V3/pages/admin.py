import streamlit as st


def render_admin() -> None:
    if st.session_state.get("rol") != "admin":
        st.error("No tienes permisos para acceder a esta sección.")
        return

    st.title("Panel de administración")
    st.write("Aquí podrás ubicar herramientas exclusivas para administradores.")