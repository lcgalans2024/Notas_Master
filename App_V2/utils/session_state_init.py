import streamlit as st
from utils.load_data import construir_url

def inicializar_session_state():
    if 'SHEET_ID' not in st.session_state:
        st.session_state.SHEET_ID = "1mS9mpj5ubrYHbKg707EVMxHVhV6H1gEB50DoM5DK4VM"

    if 'GIDS' not in st.session_state:
        st.session_state.GIDS = {
            "notas": "0",
            "recuperaciones": "451207441",
            "comparativos": "357866733"
        }

    if 'SHEET_ID_PM' not in st.session_state:
        st.session_state.SHEET_ID_PM = "1J-CZASJTrqhLXlmkFY_DavyG2aQ5HBaS"

    if 'GIDS_PM' not in st.session_state:
        st.session_state.GIDS_PM = {
            "notas": "0",
            "estudiantes": "817657441",
            "notas_601_P2": "732983744",
            "notas_602_P2": "201335434",
            "notas_701_P1": "1779130150",
            "notas_701_P2": "1360433359",
            "notas_701_P3": "291117448",
            "notas_702_P1": "1659300987",
            "notas_702_P2": "1327140213",
            "notas_702_P3": "951373038",
            "notas_703_P1": "2122928690",
            "notas_703_P2": "83185436",
            "notas_703_P3": "1860654076",
            "notas_704_P1": "1926990909",
            "notas_704_P2": "1004768913",
            "notas_704_P3": "1974496332",
            "recuperaciones": "1791404525"
        }

    # Consolidados
    if 'SHEET_ID_CONSOLIDADOS' not in st.session_state:
        st.session_state.SHEET_ID_CONSOLIDADOS = "1-o01rW92IhES6rVF1Wm21ll7N5Y7R6-4"

    if 'GIDS_CONSOLIDADOS' not in st.session_state:
        st.session_state.GIDS_CONSOLIDADOS = {
            "notas": "0",
            "701_P1": "1097370573"
        }

    if 'dict_orden_act' not in st.session_state:
        st.session_state.dict_orden_act = {
            "1.1":1, "1.3":2, "1.5":3, "1.7":4, "1.9":5,
            "1.11":6, "1.13":7, "1.15":8, "2.1":9, "2.3":10, "2.5":11, "2.7":12,
            "2.9":13, "3.1":14, "3.2":15, "4.1":16
        }

    if 'dict_orden_proc' not in st.session_state:
        st.session_state.dict_orden_proc = {
            'HACER':1, 'SABER':2, 'AUTOEVALUACIÓN':3, 'PRUEBA_PERIODO':4
        }

    if 'ruta_estudiantes' not in st.session_state:
        st.session_state.ruta_estudiantes = construir_url(
            st.session_state.SHEET_ID_PM,
            st.session_state.GIDS_PM['estudiantes']
        )

    if 'periodo1' not in st.session_state:
        st.session_state.periodo1 = "2"

    # Inicializar otras claves de control
    #if 'usuario' not in st.session_state:
    #    st.session_state['usuario'] = None
    #if 'nombre' not in st.session_state:
    #    st.session_state['nombre'] = ""
    if 'grupo1' not in st.session_state:
        st.session_state['grupo1'] = "701"
    #if 'periodo1' not in st.session_state:
    #    st.session_state['periodo1'] = "1"

    if 'ruta_notas' not in st.session_state:
        st.session_state.ruta_notas = construir_url(
            st.session_state.SHEET_ID_PM,
            st.session_state.GIDS_PM[f'notas_{st.session_state.grupo1}_P{st.session_state.periodo1}']
        )

    # Diccionario de materias
    if 'materias' not in st.session_state:
        st.session_state.materias = {
            "CNS": "CIENCIAS NATURALES Y EDUCACIÓN AMBIENTAL",
            "ART": "EDUCACIÓN ARTISTICA Y CULTURAL",
            "ETI": "EDUCACION ETICA  Y  EN VALORES HUMANOS",
            "EDF": "EDUCACIÓN FÍSICA, RECREACIÓN Y DEPORTES",
            "LEI": "LENGUA EXTRANJERA INGLES",
            "MAT": "MATEMÁTICAS",
            "CIE": "CIENCIAS SOCIALES",
            "TEC": "TECNOLOGIA E INFORMÁTICA",
            "REL": "EDUCACION RELIGIOSA",
            "LEN": "LENGUA CASTELLANA"
        }