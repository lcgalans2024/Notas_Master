import streamlit as st
import login
import pandas as pd
from utils.load_data import load_notas_google, load_recuperaciones_google, load_comparativos_google

def inicio():
    """Carga la página de inicio y genera el login"""
    #st.set_page_config(page_title="Plataforma Estudiantil", layout="wide")
    #st.title("📚 Plataforma Estudiantil")
    #st.write("Bienvenido a la plataforma estudiantil. Por favor, inicia sesión para continuar.")
    #st.header('Página :orange[principal]')
    st.title("📚 :orange[Plataforma Estudiantil]")
    # Cargar los DataFrames desde Google Sheets
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
    login.generarLogin()
    if 'usuario' in st.session_state:
        st.subheader('Información página principal')
