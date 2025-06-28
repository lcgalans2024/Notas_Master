import streamlit as st
import pandas as pd
import urllib.parse
from utils.load_data import construir_url,cargar_datos_grupo, obtener_diccionario_actividades, limpiar_y_seleccionar_notas, agregar_documento, formar_pares, comparar_y_promediar, preparar_df2, obtener_columnas_validas, transformar_melt, cargar_estudiantes

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
    "notas_701_P1": "1779130150"
}

# guardar en session state para evitar recargas innecesarias
if 'SHEET_ID_PM' not in st.session_state:
    st.session_state.SHEET_ID_PM = SHEET_ID_PM
if 'GIDS_PM' not in st.session_state:
    st.session_state.GIDS_PM = GIDS_PM

# === PARÁMETROS ===
grupo = "701"
periodo = "1"
ruta_notas = construir_url(st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM['notas_701_P1'])#"O:/Mi unidad/Orestes/Planilla_Master_IEOS.xlsx"
# cargar estudiantes

#dict_orden_act = {
#  "1.1":1,
#  "1.3":2,
#  "1.5":3,
#  "1.7":4,
#  "1.9":5,
#  "1.11":6,
#  "2.1":7,
#  "2.3":8,
#  "2.5":9,
#  "2.7":10,
#  "2.9":11,
#  "3.1":12,
#  "3.2":13,
#  "4.1":14
#}
#dict_orden_proc = {
#  'HACER':1,
#  'SABER':2,
#  'AUTOEVALUACIÓN':3,
#  'PRUEBA_PERIODO':4
#}

def mostrar(grupo, periodo, ruta_notas, ruta_estudiantes, dict_orden_act, dict_orden_proc):
    # === PROCESO ===
    df = cargar_datos_grupo(ruta_notas, grupo, periodo,st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM)
    mi_diccionario, idx_campo = obtener_diccionario_actividades(df)
    df1 = limpiar_y_seleccionar_notas(df, idx_campo, mi_diccionario)

    df_est = cargar_estudiantes(ruta_estudiantes, "All_7")
    df1 = agregar_documento(df1, df_est)

    pares = formar_pares(obtener_columnas_validas(mi_diccionario))
    df1 = comparar_y_promediar(df1, pares)
    df2 = preparar_df2(df1, obtener_columnas_validas(mi_diccionario), pares)
    df_final = transformar_melt(df2, mi_diccionario, dict_orden_act, dict_orden_proc, periodo)

    return df_final