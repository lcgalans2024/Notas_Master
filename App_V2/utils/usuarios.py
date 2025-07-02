# utils/usuarios.py
import streamlit as st
import pandas as pd
import pandas as pd
from utils.load_data import load_notas_google, load_hoja_google, load_recuperaciones_google, load_comparativos_google, cargar_estudiantes

def construir_usuarios():
    """
    Crea un diccionario de usuarios a partir de varios archivos CSV.
    
    Retorna:
        Dict: Diccionario con 'documento' como clave y 'nombre' como valor.
    """
    #########################################################################
    df_notas = load_notas_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
    df_recuperaciones = load_hoja_google(st.session_state.SHEET_ID_PM,st.session_state.GIDS_PM,'recuperaciones')#load_recuperaciones_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
    df_comparativos = load_comparativos_google(st.session_state.SHEET_ID ,st.session_state.GIDS)

    # Asegurar que 'documento' sea string
    df_notas["DOCUMENTO"] = df_notas["DOCUMENTO"].astype(str)
    df_recuperaciones["DOCUMENTO"] = df_recuperaciones["DOCUMENTO"].astype(str)
    df_recuperaciones["PERIODO"] = df_recuperaciones["PERIODO"].astype(str)  # Asegurar que 'PERIODO' sea string
    # reemplazar , por . en la columna PUNTAJE
    df_recuperaciones["PUNTAJE"] = df_recuperaciones["PUNTAJE"].str.replace(',', '.')
    df_recuperaciones["PUNTAJE"] = df_recuperaciones["PUNTAJE"].astype(float)

    df_comparativos["DOCUMENTO"] = df_comparativos["DOCUMENTO"].astype(str)

    # renombrar las columnas para que coincidan
    df_recuperaciones.rename(columns={"NOMBRE_COMPLETO": "NOMBRE_ESTUDIANTE"}, inplace=True)

    # Cargar datos en session state si no están ya cargados
    if 'df_notas' not in st.session_state:
        st.session_state.df_notas = df_notas
    if 'df_recuperaciones' not in st.session_state:
        st.session_state.df_recuperaciones = df_recuperaciones
    if 'df_comparativos' not in st.session_state:
        st.session_state.df_comparativos = df_comparativos

    # cargar estudiantes
    df_estudiantes = cargar_estudiantes(st.session_state.ruta_estudiantes, "ALL_COL")
    # Asegurar que 'DOCUMENTO' sea string
    df_estudiantes["DOCUMENTO"] = df_estudiantes["DOCUMENTO"].astype(str)
    # guardar df_estudiantes en session state
    st.session_state.df_estudiantes = df_estudiantes
    
    # Concatenar los DataFrames
    df_total = pd.concat([df_notas[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]],    
                          df_recuperaciones[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]],
                          df_comparativos[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]],
                          df_estudiantes[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]]], 
                         ignore_index=True) 
    # Eliminar duplicados y construir diccionario
    df_total = df_total.drop_duplicates()

    return dict(zip(df_total["DOCUMENTO"], df_total["NOMBRE_ESTUDIANTE"]))