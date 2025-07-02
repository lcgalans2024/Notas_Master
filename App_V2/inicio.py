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
        
    login.generarLogin()
    
    if 'usuario' in st.session_state:
        st.subheader('Información página principal')

    
