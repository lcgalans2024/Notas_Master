from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.dataframe_utils import (eliminar_columnas_vacías,
                                   eliminar_filas_vacías,
                                      eliminar_primeras_filas,
                                      eliminar_columnas_por_nombre,
                                      eliminar_filas_por_valor_en_columna,
                                      eliminar_columnas_unnamed,
                                      melt_seguro,
                                      )

from utils.normalizers import (homologar_columnas_estudiantes,
                               normalizar_columnas_dataframe, normalizar_documento,
                               normalizar_matricula, normalizar_nombre_persona,
                               normalizar_puntaje)

from components.visual_helpers import (color_calificacion,
)


"""
Funciones para balance de notas:
- eliminar_columnas_vacías: Elimina columnas que estén completamente vacías.
- eliminar_filas_vacías: Elimina filas que estén completamente vacías.
- eliminar_primeras_filas: Elimina las primeras n filas, útil para limpiar encabezados o metadatos.
Estas funciones son genéricas y pueden ser usadas en cualquier parte del proyecto donde se necesite limpiar DataFrames de manera segura.
"""

# obtener indice de fila de "No aprobados" en la columna Ord, luego filtrar el df hasta esa fila (sin incluirla)
def _obtener_indice_no_aprobados(df: pd.DataFrame, columna: str = "Ord") -> int:
    return df[df[columna] == "No aprobados"].index[0]

def _filtrar_hasta_no_aprobados(df: pd.DataFrame, columna: str = "ord") -> pd.DataFrame:
    indice = _obtener_indice_no_aprobados(df, columna)
    return df.iloc[:indice]

def preparar_balance_notas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara un DataFrame de notas para su análisis, aplicando limpieza y normalización.
    """
    df = eliminar_columnas_vacías(df)
    df = eliminar_filas_vacías(df)
    df = eliminar_primeras_filas(df, n=1)
    df = homologar_columnas_estudiantes(df)
    df = _filtrar_hasta_no_aprobados(df)
    df = eliminar_filas_por_valor_en_columna(df, columna="est", valor="C")
    df = eliminar_columnas_por_nombre(df, nombres=["ord", "est", "com", "no_evaluados"])
    df = eliminar_columnas_unnamed(df)
    
    df["documento"] = df["documento"].apply(normalizar_documento)
    df["matricula"] = df["matricula"].apply(normalizar_matricula)

    for col in df.columns:
        if col not in ["documento", "matricula", "nombre"]:
            df[col] = df[col].apply(normalizar_puntaje)

    # calcular promedio de las columnas de notas (todas excepto documento, matricula y nombre) y agregar una columna "promedio"
    columnas_notas = [col for col in df.columns if col not in ["documento", "matricula", "nombre","total_faltas", "no_aprobados"]]
    df["Nota_promedio"] = df[columnas_notas].mean(axis=1)
    
    return df