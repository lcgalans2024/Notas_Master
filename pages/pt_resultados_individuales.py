import streamlit as st

def resultado_individual():

    st.title("Resultados Individuales")
    st.markdown("### Aquí puedes ver tus resultados individuales por curso y docente")

    # Verificar si el usuario ha ingresado su documento
    if 'documento_estudiante' not in st.session_state or not st.session_state.documento_estudiante:
        st.warning("Por favor, ingresa tu documento para ver tus resultados.")
        return

    # Mostrar el documento del estudiante
    st.markdown(f"**Documento del Estudiante:** {st.session_state.documento_estudiante}")

    # Aquí iría la lógica para cargar y mostrar los resultados individuales
    # Por ejemplo, podrías cargar un DataFrame con los resultados y mostrarlos en una tabla
    # df_resultados = cargar_datos(st.session_state.documento_estudiante)
    # st.dataframe(df_resultados)