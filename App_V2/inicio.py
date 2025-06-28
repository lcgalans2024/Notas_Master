import streamlit as st
import login
import pandas as pd
from utils.load_data import load_planilla_google, load_notas_google, load_recuperaciones_google, load_comparativos_google

# usuari de prueba 6374333
def inicio():

    # Configuración centralizada del libro de Google Sheets
    SHEET_ID = "1mS9mpj5ubrYHbKg707EVMxHVhV6H1gEB50DoM5DK4VM" #Hoja ejemplo

    GIDS = {
        "notas": "0",
        "recuperaciones": "451207441",
        "comparativos": "357866733"
    }

    # guardar en session state para evitar recargas innecesarias
    if 'SHEET_ID' not in st.session_state:
        st.session_state.SHEET_ID = SHEET_ID
    if 'GIDS' not in st.session_state:
        st.session_state.GIDS = GIDS

    SHEET_ID_PM = "1J-CZASJTrqhLXlmkFY_DavyG2aQ5HBaS" #Hoja Planila Master IEOS
    GIDS_PM = {
        "notas": "0",
        "notas_701_P1": "1779130150",
        "notas_701_P2": "1360433359"  # Ejemplo de otro grupo y periodo
    }

    # guardar en session state para evitar recargas innecesarias
    if 'SHEET_ID_PM' not in st.session_state:
        st.session_state.SHEET_ID_PM = SHEET_ID_PM
    if 'GIDS_PM' not in st.session_state:
        st.session_state.GIDS_PM = GIDS_PM

    """Carga la página de inicio y genera el login"""
    #st.set_page_config(page_title="Plataforma Estudiantil", layout="wide")
    #st.title("📚 Plataforma Estudiantil")
    #st.write("Bienvenido a la plataforma estudiantil. Por favor, inicia sesión para continuar.")
    #st.header('Página :orange[principal]')
    st.title("📚 :orange[Plataforma Estudiantil]")
    # Cargar los DataFrames desde Google Sheets
    df_notas = load_notas_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
    df_recuperaciones = load_recuperaciones_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
    df_comparativos = load_comparativos_google(st.session_state.SHEET_ID ,st.session_state.GIDS)

    # Cargar datos en session state si no están ya cargados
    if 'df_notas' not in st.session_state:
        st.session_state.df_notas = df_notas
    if 'df_recuperaciones' not in st.session_state:
        st.session_state.df_recuperaciones = df_recuperaciones
    if 'df_comparativos' not in st.session_state:
        st.session_state.df_comparativos = df_comparativos

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
    # Almacenar dict_orden_act y dict_orden_proc en session state
    st.session_state.dict_orden_act = dict_orden_act
    st.session_state.dict_orden_proc = dict_orden_proc

    # cargar estudiantes
    #try:
    #ruta_estudiantes = "O:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"
    #except:
    ruta_estudiantes = "I:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"

    # Almacenar ruta_estudiantes en session state
    if 'ruta_estudiantes' not in st.session_state:
        st.session_state.ruta_estudiantes = ruta_estudiantes
        
    login.generarLogin()
    
    if 'usuario' in st.session_state:
        st.subheader('Información página principal')

    return st.session_state.df_notas, st.session_state.df_recuperaciones, st.session_state.df_comparativos, st.session_state.dict_orden_act, st.session_state.dict_orden_proc
