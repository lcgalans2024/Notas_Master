import streamlit as st
import pandas as pd
import numpy as np
from utils.load_data import load_notas_google, load_recuperaciones_google, load_comparativos_google
from components import auth, consulta_notas, materiales#, recuperaciones, comparativos

df_notas = load_notas_google()
df_recuperaciones = load_recuperaciones_google()
df_comparativos = load_comparativos_google()

# Cargar datos en session state si no están ya cargados
if 'df_notas' not in st.session_state:
    st.session_state.df_notas = df_notas
if 'df_recuperaciones' not in st.session_state:
    st.session_state.df_recuperaciones = df_recuperaciones
if 'df_comparativos' not in st.session_state:
    st.session_state.df_comparativos = df_comparativos
# === PARÁMETROS ===
grupo = "701"
periodo = "1"
ruta_notas = "O:/Mi unidad/Orestes/Planilla_Master_IEOS.xlsx"
ruta_estudiantes = "O:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"

dict_orden_act = {
          "1.1":1,
          "1.3":2,
          "1.5":3,
          "1.7":4,
          "1.9":5,
          "1.11":6,
          "2.1":7,
          "2.3":8,
          "2.5":9,
          "2.7":10,
          "2.9":11,
          "3.1":12,
          "3.2":13,
          "4.1":14
        }
dict_orden_proc = {
          'HACER':1,
          'SABER':2,
          'AUTOEVALUACIÓN':3,
          'PRUEBA_PERIODO':4
        }

#Almacenar dict_orden_act y dict_orden_proc en session state
st.session_state.dict_orden_act = dict_orden_act
st.session_state.dict_orden_proc = dict_orden_proc

def sidebar_config():
    st.sidebar.header("Auntentificación del Usuario")

    if "usuario" in st.session_state:
        # Verificamos si el estudiante tiene recuperaciones
        tiene_recuperaciones = not df_recuperaciones[df_recuperaciones["DOCUMENTO"] == st.session_state['usuario']].empty

        # Construimos el menú condicionalmente
        opciones_menu = ["📘 Consulta de notas"]
        if tiene_recuperaciones:
            opciones_menu.append("♻️ Recuperaciones")
        opciones_menu += ["📊 Comparativos", "📎 Material y comunicaciones"]

        menu = st.sidebar.radio("Ir a:", opciones_menu)
        #periodo = st.sidebar.selectbox("🗓️ Selecciona el periodo", ["Periodo 1", "Periodo 2", "Periodo 3", "Final"])

        if menu == "📘 Consulta de notas":
            st.header("📄 Notas Matemáticas")
            df5 = consulta_notas.mostrar(grupo, periodo, ruta_notas, ruta_estudiantes, dict_orden_act, dict_orden_proc)  # Mostrar notas por defecto
            # Mostrar DataFrame de notas
            st.dataframe(df5[df5['DOCUMENTO'] == st.session_state['usuario']])
        elif menu == "♻️ Recuperaciones":
            st.header("♻️ Recuperaciones")
            #recuperaciones.mostrar(df_recuperaciones, doc_id, nombre_estudiante, periodo)
        elif menu == "📊 Comparativos":
            st.header("📊 Comparativos")
            #comparativos.mostrar(df_comparativos, doc_id, nombre_estudiante)
        elif menu == "📎 Material y comunicaciones":
            st.header("📎 Material y comunicaciones")
            #materiales.mostrar()