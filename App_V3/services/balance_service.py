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

def preparar_balance_varios_periodos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara un DataFrame de notas para su análisis, aplicando limpieza y normalización.
    """
    df = eliminar_columnas_vacías(df)
    #df = eliminar_filas_vacías(df)
    #df = eliminar_primeras_filas(df, n=1)
    df = homologar_columnas_estudiantes(df)
    #df = _filtrar_hasta_no_aprobados(df)
    #df = eliminar_filas_por_valor_en_columna(df, columna="est", valor="C")
    #df = eliminar_columnas_por_nombre(df, nombres=["ord", "est", "com", "no_evaluados"])
    #df = eliminar_columnas_unnamed(df)
    
    #df["documento"] = df["documento"].apply(normalizar_documento)
    df["matricula"] = df["matricula"].apply(normalizar_matricula)

    for col in df.columns:
        if col not in ["documento", "matricula", "nombre", "materia"]:
            df[col] = df[col].apply(normalizar_puntaje)

    return df



def metricas_balance(df: pd.DataFrame) -> dict:
    """
    Calcula métricas básicas del balance de notas.
    """
    total_estudiantes = df.shape[0]
    promedio_p1 = df["promedio_p1"].mean()
    promedio_p1 = round(promedio_p1, 2) if not pd.isna(promedio_p1) else 0.0
    try:
        promedio_p2 = df["promedio_p2"].mean()
        promedio_p2 = round(promedio_p2, 2) if not pd.isna(promedio_p2) else 0.0
    except KeyError:
        promedio_p2 = 0.0
    #promedio_p3 = df["promedio_p3"].mean()
    #promedio_p3 = round(promedio_p3, 2) if not pd.isna(promedio_p3) else 0.0
    #promedio_p4 = df["promedio_p4"].mean()
    #promedio_p4 = round(promedio_p4, 2) if not pd.isna(promedio_p4) else 0.0
    #aprobados_p1 = df[df["estado_p1"] == "A"].shape[0]
    promedio_no_aprobados_p1 = df[df["reprobadas_p1"] > 0]["reprobadas_p1"].mean()
    promedio_no_aprobados_p1 = round(promedio_no_aprobados_p1, 2) if not pd.isna(promedio_no_aprobados_p1) else 0.0
    indice_reprobacion_p1 = df[df["reprobadas_p1"] > 0].shape[0] / total_estudiantes if total_estudiantes > 0 else 0.0

    return {
        "total_estudiantes": total_estudiantes,
        "promedio_p1": promedio_p1,
        "promedio_p2": promedio_p2,
        #"promedio_p3": promedio_p3,
        #"promedio_p4": promedio_p4,
        "promedio_no_aprobados_p1": promedio_no_aprobados_p1,
        "indice_reprobacion_p1": indice_reprobacion_p1
    }

def metricas_balance_por_estudiante(df: pd.DataFrame, estudiante: str) -> pd.DataFrame:
    # Calcula métricas básicas del balance de notas por estudiante.

    # Selector de estudiante
    df_estudiante = df[df["nombre"] == estudiante][["materia", "p1", "p2", "estado_p1","estado_p2"]].copy()

    return df_estudiante