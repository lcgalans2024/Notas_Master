import streamlit as st
import pandas as pd
import urllib.parse
from utils.load_data import (construir_url, cargar_datos_grupo, obtener_diccionario_actividades,
                            limpiar_y_seleccionar_notas, agregar_documento, formar_pares,
                            comparar_y_promediar, preparar_df2, obtener_columnas_validas,
                            transformar_melt, cargar_estudiantes)

def mostrar(grupo, periodo, ruta_notas, ruta_estudiantes, dict_orden_act, dict_orden_proc):
    ruta_notas = construir_url(st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM['notas_701_P1'])
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