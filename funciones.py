import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def cargar_datos_all(file_path, nombre_hoja):
    df = pd.read_excel(file_path,sheet_name=nombre_hoja)
    return df

@st.cache_data
def cargar_datos(file_path, nombre_hoja, numero_periodo):
    df = pd.read_excel(file_path,sheet_name=nombre_hoja)
    df = df[df.PERIODO == numero_periodo]
    return df

@st.cache_data
def filtrar_datos(usuario, df):
    df_filtrado = df[df['DOCUMENTO'] == str(usuario)]
    return df_filtrado.round(2)

# Función de formato condicional
def color_calificacion(val):
    if val >= 4.5:
        color = 'background-color: #00b050; color: black'  # Verde
    elif val >= 4:
        color = 'background-color: #ffff00; color: black'  # Amarillo claro
    elif val >= 3:
        color = 'background-color: #ffc000; color: black'  # Naranja
    else:
        color = 'background-color: #ff0000; color: white'  # Rojo
    return color