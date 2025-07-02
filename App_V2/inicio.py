import streamlit as st
import login
import pandas as pd
from utils.load_data import (construir_url, load_planilla_google, load_notas_google,
                            load_recuperaciones_google, load_comparativos_google,
                            cargar_hoja_publica
                            )

# usuari de prueba 6374333
def inicio():

    """Carga la página de inicio y genera el login"""
    
    st.title("📚 :orange[Plataforma Estudiantil]")
    
    ruta_estudiantes = construir_url(st.session_state.SHEET_ID_PM, st.session_state.GIDS_PM['estudiantes'])
    # Almacenar ruta_estudiantes en session state
    if 'ruta_estudiantes' not in st.session_state:
        st.session_state.ruta_estudiantes = ruta_estudiantes
        
    login.generarLogin()
    
    if 'usuario' in st.session_state:
        st.subheader('Información página principal')

    
