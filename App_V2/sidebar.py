import streamlit as st
import pandas as pd
import numpy as np
from utils.visual_helpers import mostrar_tabla_notas
from utils.load_data import cargar_estudiantes, agregar_documento, load_planilla_google, load_notas_google, load_recuperaciones_google, load_comparativos_google,construir_url
from components import auth, consulta_notas, materiales#, recuperaciones, comparativos

## Configuración centralizada del libro de Google Sheets
#SHEET_ID = "1mS9mpj5ubrYHbKg707EVMxHVhV6H1gEB50DoM5DK4VM" #Hoja ejemplo
#
#GIDS = {
#    "notas": "0",
#    "recuperaciones": "451207441",
#    "comparativos": "357866733"
#}
#
## guardar en session state para evitar recargas innecesarias
#if 'SHEET_ID' not in st.session_state:
#    st.session_state.SHEET_ID = SHEET_ID
#if 'GIDS' not in st.session_state:
#    st.session_state.GIDS = GIDS
#
#SHEET_ID_PM = "1J-CZASJTrqhLXlmkFY_DavyG2aQ5HBaS" #Hoja Planila Master IEOS
#GIDS_PM = {
#    "notas": "0",
#    "notas_701_P1": "1779130150",
#    "notas_701_P2": "1360433359"
#}
#
## guardar en session state para evitar recargas innecesarias
#if 'SHEET_ID_PM' not in st.session_state:
#    st.session_state.SHEET_ID_PM = SHEET_ID_PM
#if 'GIDS_PM' not in st.session_state:
#    st.session_state.GIDS_PM = GIDS_PM

#df_notas = load_notas_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
#df_recuperaciones = load_recuperaciones_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
#df_comparativos = load_comparativos_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
#
## Cargar datos en session state si no están ya cargados
#if 'df_notas' not in st.session_state:
#    st.session_state.df_notas = df_notas
#if 'df_recuperaciones' not in st.session_state:
#    st.session_state.df_recuperaciones = df_recuperaciones
#if 'df_comparativos' not in st.session_state:
#    st.session_state.df_comparativos = df_comparativos
# === PARÁMETROS ===
grupo = "701"
#"O:/Mi unidad/Orestes/Planilla_Master_IEOS.xlsx"
#try:
#    ruta_estudiantes = "O:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"
#except:
#    ruta_estudiantes = "I:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"

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

    # Selector de grupo y periodo
    st.sidebar.subheader("Configuración")
    st.sidebar.write("Selecciona el grupo y periodo para ver las notas correspondientes.")
    #grupo1 = st.sidebar.selectbox("Grupo", ["701", "702", "703"])
    #if 'grupo1' in st.session_state:
    st.sidebar.write("Grupo actual:", st.session_state.grupo1)
    periodo = st.sidebar.selectbox("Periodo", ["1", "2", "3", "Final"])
    #st.session_state.grupo1 = grupo1
    st.session_state.periodo1 = periodo

    #periodo = st.session_state.get('periodo1', "1")  # Usar el periodo del session state o por defecto "1"
    ruta_notas = construir_url(st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM[f'notas_701_P{periodo}'])
    st.session_state.ruta_notas = ruta_notas
    st.session_state.ruta_estudiantes = "I:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"  # Ruta de estudiantes
    #st.session_state.dict_orden_act = dict_orden_act
    #st.session_state.dict_orden_proc = dict_orden_proc

    if "usuario" in st.session_state:
        # Verificamos si el estudiante tiene recuperaciones
        tiene_recuperaciones = not st.session_state.df_recuperaciones[st.session_state.df_recuperaciones["DOCUMENTO"] == st.session_state['usuario']].empty

        # Construimos el menú condicionalmente
        opciones_menu = ["📘 Consulta de notas"]
        if tiene_recuperaciones:
            opciones_menu.append("♻️ Recuperaciones")
        opciones_menu += ["📊 Comparativos", "📎 Material y comunicaciones"]

        menu = st.sidebar.radio("Ir a:", opciones_menu)
        #periodo = st.sidebar.selectbox("🗓️ Selecciona el periodo", ["Periodo 1", "Periodo 2", "Periodo 3", "Final"])

        if menu == "📘 Consulta de notas":
            st.header("📄 Notas Matemáticas")
            # Agregar una nota aclaratoria
            st.markdown('''**Nota:** Las calificaciones se muestran en una escala de 0 a 5, 
                        donde 0.2 indica que no se ha realizado la actividad y en consecuencia no se ha evaluado.''')

            #df_planilla = load_planilla_google(st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM)
            #st.dataframe(df_planilla)
#
            #df_estudiantes = cargar_estudiantes(st.session_state.ruta_estudiantes, "ALL_COL")
            #st.dataframe(df_estudiantes)
#
            #df_planilla1 = agregar_documento(df_planilla, df_estudiantes)
            #st.dataframe(df_planilla1)    

            df5 = consulta_notas.mostrar(grupo, periodo, ruta_notas, st.session_state.ruta_estudiantes, st.session_state.dict_orden_act, st.session_state.dict_orden_proc)  # Mostrar notas por defecto
            df6 = df5[df5['DOCUMENTO'] == st.session_state['usuario']].copy()
            # redondear las calificaciones a 1 decimal
            # Tu dataframe filtrado, por ejemplo:
            #df_filtrado = df6[["PROCESO", "ACTIVIDAD", "Calificación"]]

            # Mostrar tabla con formato
            mostrar_tabla_notas(df6)
            #df6['Calificación'] = df6['Calificación'].round(1)#.astype(str)
            ## Aplicar estilo
            #styled_df = df6[["PROCESO","ACTIVIDAD","Calificación"]].style.format({"Calificación": "{:.1f}"}).applymap(color_calificacion, subset=['Calificación'])
            ## Mostrar DataFrame de notas
            #
            #st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
        elif menu == "♻️ Recuperaciones":
            st.header("♻️ Recuperaciones")
            #recuperaciones.mostrar(df_recuperaciones, doc_id, nombre_estudiante, periodo)
        elif menu == "📊 Comparativos":
            st.header("📊 Comparativos")
            #comparativos.mostrar(df_comparativos, doc_id, nombre_estudiante)
        elif menu == "📎 Material y comunicaciones":
            st.header("📎 Material y comunicaciones")
            #materiales.mostrar()

        
    

# Mostrar el sidebar
def mostrar_sidebar():
    st.sidebar.title("Menú de Navegación")
    st.sidebar.image("C:/Users/Durley/Documents/Maycol/Repositorios/Notas_Master/App_V2/escudo_oreste.png", use_container_width=True)  # Logo de la institución
    sidebar_config()

