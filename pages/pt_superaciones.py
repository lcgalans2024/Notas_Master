import streamlit as st
import matplotlib.pyplot as plt
from funciones import color_calificacion, barra_progreso, color_condicional, resaltar_aciertos, resaltar_aciertos1#, #resaltar_preguntas2

def superaciones():

    st.title("Resultados")

    # verificar si hay resultados disponibles
    if 'df_usuario1' in st.session_state and not st.session_state.df_usuario1.empty and st.session_state.selected_periodo != None:
        df_usuario1 = st.session_state.df_usuario1
        df_usuario1.reset_index(drop=True, inplace=True)

        # Mostrar los resultados del estudiante
        #1023530033
        st.subheader(f"Estudiante: {df_usuario1['NOMBRE_COMPLETO'].iloc[0]}")
        #st.subheader(f"Nota general de la recuperación: {df_usuario1['PUNTAJE'].iloc[0]}")

        # Mostrar la barra de progreso
        nota_acumulada = df_usuario1['PUNTAJE'].iloc[0]
        fig = barra_progreso(5, nota_acumulada, 3,"Nota de la recuperación")
        st.pyplot(fig)

        if df_usuario1['PUNTAJE'].iloc[0] >= 3.0:
            st.success("¡Felicidades! Has recuperado el area para el primer periodo.")
        else:
            st.error("No has recuperado el área para el primer periodo. Debes prepararte para un nuevo intento.")
        
        # Tabla de resultados detallados
        st.subheader("Resultados Detallados de la prueba de superación")

        df1 = df_usuario1[["PREGUNTA","CATEGORIA"]].reset_index(drop=True).copy()

        # Aplicar estilo condicional SOLO a la columna PREGUNTA
        def resaltar_preguntas2(valores):
            return ['background-color: lightgreen' if acierto == 1 else '' 
                    for acierto in df_usuario1['ACIERTOS']]

        #styled_df = df1.style.applymap(color_condicional, subset=['ACIERTOS'])
        styled_df = df1.style.apply(resaltar_preguntas2, subset=['PREGUNTA'], axis=0)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)


    else:
        st.warning("")