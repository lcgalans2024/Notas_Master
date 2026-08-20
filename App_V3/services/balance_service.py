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

from streamlit_extras.metric_cards import style_metric_cards


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
    total_reprobadas_p1 = df["reprobadas_p1"].sum()
    total_superadas_p1 = df["superadas_p1"].sum()
    promedio_no_aprobados_p1 = df[df["reprobadas_p1"] > 0]["reprobadas_p1"].mean()
    promedio_no_aprobados_p1 = round(promedio_no_aprobados_p1, 2) if not pd.isna(promedio_no_aprobados_p1) else 0.0
    indice_reprobacion_p1 = df[df["reprobadas_p1"] > 0].shape[0] / total_estudiantes if total_estudiantes > 0 else 0.0

    metricas = {
        "total_estudiantes": total_estudiantes,
        "promedio_p1": promedio_p1,
        "promedio_p2": promedio_p2,
        #"promedio_p3": promedio_p3,
        #"promedio_p4": promedio_p4,
        "promedio_no_aprobados_p1": promedio_no_aprobados_p1,
        "indice_reprobacion_p1": indice_reprobacion_p1,
        "total_reprobadas_p1": total_reprobadas_p1,
        "total_superadas_p1": total_superadas_p1,
    }

    col1, col2, col3, col4, col5 = st.columns(5)
            
    with col1:
        st.metric(
            label="Total de estudiantes",
            value=f"{metricas['total_estudiantes']:.0f}"
        )

    with col2:
        st.metric(
            label="Promedio de grupo P1",
            value=f"{metricas['promedio_p1']:.1f}"
        )

    with col3:
        st.metric(
            label="Indice de reprobación P1",
            value=f"{metricas['indice_reprobacion_p1']:.2f}"
        )

    with col4:
        st.metric(
            label="Total de reprobadas P1",
            value=f"{metricas['total_reprobadas_p1']:.0f}"
        )

    with col5:
        st.metric(
            label="Total de superadas P1",
            value=f"{metricas['total_superadas_p1']:.0f}"
        )

    style_metric_cards(border_color="#3A74E7")

    # dataframe con los estudiantes que tienen reprobadas_p1 > 0, mostrando solo las columnas matricula, nombre, reprobadas_p1, superadas_p1, estado_p1, ordenado por reprobadas_p1 descendente 
    df_reprobados_p1 = df[df["reprobadas_p1"] > 3][["matricula", "nombre", "reprobadas_p1", "superadas_p1", "indice_superadas_p1"]].copy()
    df_reprobados_p1 = df_reprobados_p1.sort_values(by="reprobadas_p1", ascending=False)
    st.dataframe(df_reprobados_p1)

    return metricas

def metricas_balance_por_estudiante(df: pd.DataFrame, estudiante: str) -> pd.DataFrame:
    # Calcula métricas básicas del balance de notas por estudiante.

    # Selector de estudiante
    df_estudiante = df[df["nombre"] == estudiante][["materia", "p1", "p2", "estado_p1","estado_p2"]].copy()

    return df_estudiante

@st.fragment
def mostrar_metricas_estudiante(df_balance_varios_unicos, df_balance_varios):

    estudiantes = (
        df_balance_varios_unicos["nombre"]
        .dropna()
        .unique()
        .tolist()
    )

    estudiante_varios = st.selectbox(
        "Selecciona un estudiante para ver sus métricas:",
        estudiantes,
        key="balance_estudiante_varios"
    )

    df_estudiante = df_balance_varios_unicos[
        df_balance_varios_unicos["nombre"] == estudiante_varios
    ]

    if df_estudiante.empty:
        st.warning("No se encontraron datos para el estudiante seleccionado.")
        return

    estudiante = df_estudiante.iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Promedio P1",
            value=f"{estudiante['promedio_p1']:.1f}"
        )

    with col2:
        st.metric(
            label="Reprobadas P1",
            value=int(estudiante["reprobadas_p1"])
        )

    with col3:
        st.metric(
            label="Superadas P1",
            value=int(estudiante["superadas_p1"])
        )

    style_metric_cards(border_color="#3A74E7")

    df_metricas = metricas_balance_por_estudiante(
        df_balance_varios,
        estudiante_varios
    )

    st.write("Métricas de balance del estudiante seleccionado:")
    st.dataframe(df_metricas)