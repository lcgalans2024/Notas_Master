import streamlit as st


def render_inasistencia() -> None:
    rol = st.session_state.get("rol", "estudiante")

    if rol not in {"admin", "monitor"}:
        st.error("No tienes permisos para acceder a esta sección.")
        return

    st.title("Registro de inasistencia")
    st.write("Aquí podrás registrar la asistencia o inasistencia del grupo.")