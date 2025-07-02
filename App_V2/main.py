import streamlit as st

from utils.session_state_init import inicializar_session_state

# Inicialización robusta de session_state
inicializar_session_state()

# Configuración general
st.set_page_config(page_title="Plataforma Estudiantil", layout="wide")

import sidebar
import inicio
import login
from components import auth, consulta_notas, materiales#, recuperaciones, comparativos
from utils.load_data import (construir_url,load_notas_google, load_recuperaciones_google,
                             load_comparativos_google, cargar_datos_grupo, obtener_diccionario_actividades,
                             limpiar_y_seleccionar_notas, cargar_estudiantes, agregar_documento,
                             formar_pares, comparar_y_promediar, preparar_df2,
                             obtener_columnas_validas, transformar_melt
                             )
#st.write(st.session_state)
# cargar la página de inicio
inicio.inicio()

#st.markdown(st.session_state['usuario'])

# Cargar sidebar
if 'usuario' not in st.session_state:
    st.warning("Por favor, inicia sesión para continuar.")
else:
    # Mostrar el sidebar
    sidebar.mostrar_sidebar()