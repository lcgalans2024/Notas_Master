import streamlit as st
import sidebar
from pages import pt_resultados_individuales

############################### Page configuration ###############################
st.set_page_config(
    page_title="Dashboard Notas Master",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded")

st.title("Notas Master")

# Configurar sidebar y cargar datos
sidebar.sidebar_config()

# Tabs principales del Dashboard
tabs = [
    "Análisis Puntaje Global",
    "Análisis Por Area",
    "Análisis Por Grupo",
    "Análisis Por Año",
    "Olimpiadas Institucionales",
    "Descarga de Datos"
]

# Crear Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs)

# Lógica de cada pantalla
with tab1:
    try:
        pt_resultados_individuales.resultado_individual()

    except Exception as e:
        st.error(f"Error al cargar la pantalla de análisis global: {e}")

        # Mostrar mensaje de error y sugerencia
        st.error("No se pudo cargar el análisis global. Por favor, verifica los datos o intenta más tarde.")

        # Opción para volver a cargar la página
        #if st.button("Recargar"):
         #   st.experimental_rerun()