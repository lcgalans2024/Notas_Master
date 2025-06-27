# utils/usuarios.py
import streamlit as st
import pandas as pd
import pandas as pd
from utils.load_data import load_notas_google, load_recuperaciones_google, load_comparativos_google, cargar_estudiantes

def construir_usuarios():
    """
    Crea un diccionario de usuarios a partir de varios archivos CSV.
    
    Retorna:
        dict: Diccionario con 'documento' como clave y 'nombre' como valor.
    """
    # Cargar los datos de los archivos CSV
    df_notas = st.session_state.df_notas
    df_recuperaciones = st.session_state.df_recuperaciones
    df_comparativos = st.session_state.df_comparativos
    # Asegurar que 'documento' sea string
    df_notas["DOCUMENTO"] = df_notas["DOCUMENTO"].astype(str)
    df_recuperaciones["DOCUMENTO"] = df_recuperaciones["DOCUMENTO"].astype(str)
    df_comparativos["DOCUMENTO"] = df_comparativos["DOCUMENTO"].astype(str)

    # cargar estudiantes
    df_estudiantes = cargar_estudiantes(st.session_state.ruta_estudiantes, "ALL_COL")
    # Asegurar que 'DOCUMENTO' sea string
    df_estudiantes["DOCUMENTO"] = df_estudiantes["DOCUMENTO"].astype(str)

    # Concatenar los DataFrames
    df_total = pd.concat([df_notas[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]],    
                          df_recuperaciones[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]],
                          df_comparativos[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]],
                          df_estudiantes[["DOCUMENTO", "NOMBRE_ESTUDIANTE"]]], 
                         ignore_index=True) 
    # Eliminar duplicados y construir diccionario
    df_total = df_total.drop_duplicates()

    return dict(zip(df_total["DOCUMENTO"], df_total["NOMBRE_ESTUDIANTE"]))


#    archivos = ["data/notas.csv", "data/recuperaciones.csv", "data/comparativos.csv"]
#    df_total = pd.DataFrame()
#
#    for archivo in archivos:
#        try:
#            df = pd.read_csv(archivo)[["documento", "nombre"]]
#            df["documento"] = df["documento"].astype(str)  # Asegurar que 'documento' sea string
#            df_total = pd.concat([df_total, df])
#        except FileNotFoundError:
#            continue  # Ignorar si falta alguno
#
#    # Eliminar duplicados y construir diccionario
#    df_total = df_total.drop_duplicates()
#    return dict(zip(df_total["documento"], df_total["nombre"]))
