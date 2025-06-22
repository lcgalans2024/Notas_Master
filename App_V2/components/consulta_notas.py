import streamlit as st
import pandas as pd
import urllib.parse
from utils.load_data import cargar_datos_grupo, obtener_diccionario_actividades, limpiar_y_seleccionar_notas, agregar_documento, formar_pares, comparar_y_promediar, preparar_df2, obtener_columnas_validas, transformar_melt, cargar_estudiantes

# === PARÁMETROS ===
grupo = "701"
periodo = "1"
ruta_notas = "O:/Mi unidad/Orestes/Planilla_Master_IEOS.xlsx"
ruta_estudiantes = "O:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"

dict_orden_act = {
  "1.1":1,
  "1.3":2,
  "1.5":3,
  "1.7":4,
  "1.9":5,
  "1.11":6,
  "2.1":7,
  "2.3":8,
  "2.5":9,
  "2.7":10,
  "2.9":11,
  "3.1":12,
  "3.2":13,
  "4.1":14
}
dict_orden_proc = {
  'HACER':1,
  'SABER':2,
  'AUTOEVALUACIÓN':3,
  'PRUEBA_PERIODO':4
}

def mostrar(grupo, periodo, ruta_notas, ruta_estudiantes, dict_orden_act, dict_orden_proc):
    # === PROCESO ===
    df = cargar_datos_grupo(ruta_notas, grupo, periodo)
    mi_diccionario, idx_campo = obtener_diccionario_actividades(df)
    df1 = limpiar_y_seleccionar_notas(df, idx_campo, mi_diccionario)

    df_est = cargar_estudiantes(ruta_estudiantes, "All_7")
    df1 = agregar_documento(df1, df_est)

    pares = formar_pares(obtener_columnas_validas(mi_diccionario))
    df1 = comparar_y_promediar(df1, pares)
    df2 = preparar_df2(df1, obtener_columnas_validas(mi_diccionario), pares)
    df_final = transformar_melt(df2, mi_diccionario, dict_orden_act, dict_orden_proc, periodo)

    return df_final