import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import qrcode
from io import BytesIO
from utils.visual_helpers import mostrar_tabla_notas, calcular_nota_acumulada, mostrar_barra_progreso
from utils.load_data import cargar_estudiantes, agregar_documento, load_planilla_google, load_notas_google, load_recuperaciones_google, load_comparativos_google,construir_url
from components import auth, consulta_notas, materiales, recuperaciones#, comparativos

def sidebar_config():
    #st.sidebar.header("Auntentificación del Usuario")

    # Selector de grupo y periodo
    st.sidebar.write("Grupo actual:", st.session_state.grupo1)
    periodo = st.sidebar.selectbox("Periodo", ["1", "2", "3", "Final"])
    st.session_state.periodo1 = periodo

    ruta_notas = construir_url(st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM[f'notas_701_P{periodo}'])
    st.session_state.ruta_notas = ruta_notas

    if "usuario" in st.session_state:
        # Verificamos si el estudiante tiene recuperaciones / verificar si st.session_state.df_recuperaciones esta vacío
        d = st.session_state.df_recuperaciones.shape[0] if 'df_recuperaciones' in st.session_state else 0
        tiene_recuperaciones = not st.session_state.df_recuperaciones[st.session_state.df_recuperaciones["DOCUMENTO"] == st.session_state['usuario']].empty

        # Construimos el menú condicionalmente
        opciones_menu = ["📘 Consulta de notas"]
        if tiene_recuperaciones:
            opciones_menu.append("♻️ Recuperaciones")
        opciones_menu += ["📊 Comparativos", "📎 Material del área y comunicados"]

        menu = st.sidebar.radio("Ir a:", opciones_menu)
        #periodo = st.sidebar.selectbox("🗓️ Selecciona el periodo", ["Periodo 1", "Periodo 2", "Periodo 3", "Final"])

        if menu == "📘 Consulta de notas":
            st.header("📄 Notas Matemáticas")

            # Agregar una nota aclaratoria
            st.markdown('''**Nota:** Las calificaciones se muestran en una escala de 0 a 5, 
                        donde 0.2 indica que no se ha realizado la actividad y en consecuencia no se ha evaluado.''') 

            df5 = consulta_notas.mostrar(st.session_state.grupo1, periodo, ruta_notas, st.session_state.ruta_estudiantes, st.session_state.dict_orden_act, st.session_state.dict_orden_proc)  # Mostrar notas por defecto
            df6 = df5[df5['DOCUMENTO'] == st.session_state['usuario']].copy()

            # mostrar os tipos de las columnas de df6
            st.write("Tipos de las columnas del DataFrame de notas:")
            #st.table(st.session_state.df_recuperaciones.dtypes)
           
            #st.dataframe(st.session_state.df_recuperaciones[(st.session_state.df_recuperaciones["DOCUMENTO"] == st.session_state['usuario']) 
            #                                                &
            #                                                (st.session_state.df_recuperaciones["PERIODO"] == periodo)
            #                                                ]
            #                                                )

            # Mostrar tabla con formato
            mostrar_tabla_notas(df6)

            # Mostrar barra de progreso
            nota_acumulada = calcular_nota_acumulada(df6)
            # Si la nota acumulada es None, no mostrar la barra de progreso
            if nota_acumulada is not None:
                nota_max = 5
                meta = 3
                fig = mostrar_barra_progreso(nota_acumulada)
                st.pyplot(fig)
    
        elif menu == "♻️ Recuperaciones":
            st.header("♻️ Recuperaciones")
            recuperaciones.mostrar(st.session_state.df_recuperaciones, st.session_state['usuario'], st.session_state['nombre'], periodo)
        elif menu == "📊 Comparativos":
            st.header("📊 Comparativos")
            #comparativos.mostrar(df_comparativos, doc_id, nombre_estudiante)
        elif menu == "📎 Material del área y comunicados":
            st.header("📎 Material del área y comunicados")
            materiales.mostrar()

# Mostrar el sidebar
def mostrar_sidebar():
    st.sidebar.title("Menú de Navegación")
    #st.sidebar.image("C:/Users/Durley/Documents/Maycol/Repositorios/Notas_Master/App_V2/escudo_oreste.png", use_container_width=True)  # Logo de la institución
    #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app1.png", use_container_width=True)
    #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_2.png", use_container_width=True)
    #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_3.png", use_container_width=True)
    st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_4.png", use_container_width=True)
    sidebar_config()

