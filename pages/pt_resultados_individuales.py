import streamlit as st
from funciones import color_calificacion

def resultado_individual():

    st.title("Resultados")
    #st.markdown("### Aquí puedes ver tus resultados individuales por curso y docente")

    # Verificar si el usuario ha ingresado su documento
    #if 'documento_estudiante' not in st.session_state or not st.session_state.documento_estudiante:
    #    st.warning("Por favor, ingresa tu documento para ver tus resultados.")
    #    return
#
    ## Mostrar el documento del estudiante
    #st.markdown(f"**Documento del Estudiante:** {st.session_state.documento_estudiante}")
#
    ## Verificar si el usuario ha seleccionado un grupo
    #if 'selected_sheet_grupo' not in st.session_state or not st.session_state.selected_sheet_grupo:
    #    st.warning("Por favor, selecciona tu grupo para ver tus resultados.")
    #    return
    #st.markdown(f"**Grupo:** {st.session_state.selected_sheet_grupo}")
    ## Verificar si el usuario ha seleccionado un periodo
    #if 'selected_periodo' not in st.session_state or not st.session_state.selected_periodo:
    #    st.warning("Por favor, selecciona un periodo académico para ver tus resultados.")
    #    return
    #st.markdown(f"**Periodo Académico:** {st.session_state.selected_periodo}")

    # Aquí iría la lógica para cargar y mostrar los resultados individuales

    #st.session_state.visibility = "visible"
    #st.session_state.disabled = False

    # verificar si hay resultados disponibles
    if 'df_usuario1' in st.session_state and not st.session_state.df_usuario1.empty and st.session_state.selected_periodo != None:
        df_usuario1 = st.session_state.df_usuario1
        df_usuario1.reset_index(drop=True, inplace=True)

        # Mostrar los resultados del estudiante
        st.subheader(f"Resultados del Estudiante: {df_usuario1['Nombre_estudiante'].iloc[0]}")
        # Aplicar estilo
        styled_df = df_usuario1[["PROCESO","ACTIVIDAD","Calificación"]].style.applymap(color_calificacion, subset=['Calificación'])
        #st.dataframe(df_usuario[["PROCESO","ACTIVIDAD","Calificación"]])

        # Mostrar en Streamlit
        st.dataframe(styled_df, use_container_width=True)

    else:
        st.warning("")