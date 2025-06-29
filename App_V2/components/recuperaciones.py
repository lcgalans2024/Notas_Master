import streamlit as st
import matplotlib

from utils.visual_helpers import mostrar_barra_progreso

def mostrar(df_recuperaciones, doc_id, nombre_estudiante, periodo):
    #st.header(f"♻️ Recuperaciones de {nombre_estudiante} - {periodo}")
    recup_filtradas = df_recuperaciones[
        (df_recuperaciones["DOCUMENTO"] == doc_id) &
        (df_recuperaciones["PERIODO"] == periodo)
    ]
    if recup_filtradas.empty:
        st.warning("No hay recuperaciones registradas para este periodo.")
    else:
        # Selecbox de Intento
        intentos = recup_filtradas['INTENTO'].unique().tolist()
        intentos = sorted(intentos, reverse=False)  # Ordenar de mayor a menor
        selected_intento = st.selectbox("Seleccione el intento", intentos, index=0)

        # Filtrar el DataFrame por el intento seleccionado
        recup_filtradas = recup_filtradas[recup_filtradas['INTENTO'] == selected_intento].reset_index(drop=True)

        # Mostrar los resultados del estudiante
        #1036690007
        #st.subheader(f"Estudiante: {recup_filtradas['NOMBRE_ESTUDIANTE'].iloc[0]}")
        #st.subheader(f"Nota general de la recuperación: {recup_filtradas['PUNTAJE'].iloc[0]}")

        # Mostrar la barra de progreso
        nota_acumulada = recup_filtradas['PUNTAJE'].iloc[0]

        fig = mostrar_barra_progreso(nota_acumulada)
        st.pyplot(fig)

        if recup_filtradas['PUNTAJE'].iloc[0] >= 3.0:
            st.success("¡Felicidades! Has recuperado el area para el primer periodo.")
        else:
            st.error("No has recuperado el área para el primer periodo. Debes prepararte para un nuevo intento.")
        #        
        # Tabla de resultados detallados
        st.subheader("Resultados Detallados de la prueba de superación")
        df1 = recup_filtradas[["PREGUNTA","CATEGORIA"]].reset_index(drop=True).copy()
        # Aplicar estilo condicional SOLO a la columna PREGUNTA
        def resaltar_preguntas2(valores):
            return ['background-color: lightgreen' if acierto == 1 else '' 
                    for acierto in recup_filtradas['ACIERTOS']]
        #styled_df = df1.style.applymap(color_condicional, subset=['ACIERTOS'])
        styled_df = df1.style.apply(resaltar_preguntas2, subset=['PREGUNTA'], axis=0)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        #recup_filtradas["mejora"] = recup_filtradas["nota_recuperacion"] - recup_filtradas["nota_original"]
        #def resaltar_mejora(val):
        #    return 'background-color: #d4edda; color: #155724;' if val >= 1.0 else ''
        #columnas = ["asignatura", "nota_original", "nota_recuperacion", "nota_definitiva", "mejora"]
        #st.dataframe(
        #    recup_filtradas[columnas].style.applymap(resaltar_mejora, subset=["mejora"]),
        #    use_container_width=True
        #)

#def superaciones():
#
#    st.title("Resultados")
#
#    # verificar si hay resultados disponibles
#    if 'df_usuario1' in st.session_state and not st.session_state.df_usuario1.empty and st.session_state.selected_periodo != None:
#        df_usuario1 = st.session_state.df_usuario1
#        df_usuario1.reset_index(drop=True, inplace=True)
#
#        # Selecbox de Intento
#        intentos = df_usuario1['INTENTO'].unique().tolist()
#        intentos = sorted(intentos, reverse=False)  # Ordenar de mayor a menor
#        selected_intento = st.selectbox("Seleccione el intento", intentos, index=0)
#
#        # Filtrar el DataFrame por el intento seleccionado
#        df_usuario1 = df_usuario1[df_usuario1['INTENTO'] == selected_intento].reset_index(drop=True)
#
#        # Mostrar los resultados del estudiante
#        #1036690007
#        st.subheader(f"Estudiante: {df_usuario1['NOMBRE_COMPLETO'].iloc[0]}")
#        #st.subheader(f"Nota general de la recuperación: {df_usuario1['PUNTAJE'].iloc[0]}")
#
#        # Mostrar la barra de progreso
#        nota_acumulada = df_usuario1['PUNTAJE'].iloc[0]
#        fig = barra_progreso(5, nota_acumulada, 3,"Nota de la recuperación")
#        st.pyplot(fig)
#
#        if df_usuario1['PUNTAJE'].iloc[0] >= 3.0:
#            st.success("¡Felicidades! Has recuperado el area para el primer periodo.")
#        else:
#            st.error("No has recuperado el área para el primer periodo. Debes prepararte para un nuevo intento.")
#        
#        # Tabla de resultados detallados
#        st.subheader("Resultados Detallados de la prueba de superación")
#
#        df1 = df_usuario1[["PREGUNTA","CATEGORIA"]].reset_index(drop=True).copy()
#
#        # Aplicar estilo condicional SOLO a la columna PREGUNTA
#        def resaltar_preguntas2(valores):
#            return ['background-color: lightgreen' if acierto == 1 else '' 
#                    for acierto in df_usuario1['ACIERTOS']]
#
#        #styled_df = df1.style.applymap(color_condicional, subset=['ACIERTOS'])
#        styled_df = df1.style.apply(resaltar_preguntas2, subset=['PREGUNTA'], axis=0)
#        st.dataframe(styled_df, use_container_width=True, hide_index=True)
#
#
#    else:
#        st.warning("")