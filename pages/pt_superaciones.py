import streamlit as st
from funciones import color_calificacion

def superaciones():

    st.title("Resultados")

    # verificar si hay resultados disponibles
    if 'df_usuario1' in st.session_state and not st.session_state.df_usuario1.empty and st.session_state.selected_periodo != None:
        df_usuario1 = st.session_state.df_usuario1
        df_usuario1.reset_index(drop=True, inplace=True)

        # Mostrar los resultados del estudiante
        #1023530033
        st.subheader(f"Estudiante: {df_usuario1['NOMBRE_COMPLETO'].iloc[0]}")
        st.subheader(f"Nota general de la recuperación: {df_usuario1['PUNTAJE'].iloc[0]}")
        if df_usuario1['PUNTAJE'].iloc[0] >= 3.0:
            st.success("¡Felicidades! Has recuperado el area para el primer periodo.")
        else:
            st.error("No has recuperado el área para el primer periodo. Debes prepararte para un nuevo intento.")
        # Aplicar estilo
        #styled_df = df_usuario1[["PREGUNTA","CATEGORIA","ACIERTOS"]].style.applymap(color_calificacion, subset=['Calificación'])
        st.dataframe(df_usuario1[["PREGUNTA","CATEGORIA","ACIERTOS"]].reset_index(drop=True), use_container_width=True, hide_index=True)

        # Mostrar en Streamlit
        #st.dataframe(styled_df, use_container_width=True)

    else:
        st.warning("")