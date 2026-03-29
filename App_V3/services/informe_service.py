from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_notas
from utils.normalizers import (
    normalizar_columnas_dataframe,
    normalizar_dataframe_notas,
    normalizar_documento,
)


COLUMNAS_PRIORIZADAS_INFORME = [
    "nombre",
    "documento",
    "promedio",
    "definitiva",
    "resultado",
    "observaciones",
]


def _preparar_base_informe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base para extraer un resumen tipo informe.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = normalizar_columnas_dataframe(df)
    df = normalizar_dataframe_notas(df).copy()

    if "documento" in df.columns:
        df["documento"] = df["documento"].apply(normalizar_documento)

    return df


def _filtrar_estudiante(df: pd.DataFrame, documento: str) -> pd.DataFrame:
    """
    Deja únicamente el registro del estudiante consultado.
    """
    if df.empty or "documento" not in df.columns:
        return pd.DataFrame()

    documento = normalizar_documento(documento)
    df_filtrado = df.loc[df["documento"] == documento].copy()

    return df_filtrado.reset_index(drop=True)


def _seleccionar_columnas_informe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona las columnas más útiles para un informe académico resumido.
    Si no existen todas, toma las disponibles.
    """
    if df.empty:
        return df

    columnas_disponibles = [col for col in COLUMNAS_PRIORIZADAS_INFORME if col in df.columns]

    if not columnas_disponibles:
        columnas_disponibles = df.columns.tolist()[:8]

    return df[columnas_disponibles].copy()


def _formatear_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mejora la visualización final de nombres de columnas.
    """
    if df.empty:
        return df

    df = df.copy()
    df.columns = [col.replace("_", " ").strip().title() for col in df.columns]
    return df


@st.cache_data(ttl=60, show_spinner=False)
def obtener_informe_usuario(documento: str, grupo: str, periodo: str) -> pd.DataFrame:
    """
    Obtiene un resumen académico del estudiante para el grupo y periodo dados.

    En esta primera versión se apoya en la misma fuente de notas y extrae
    las columnas más cercanas a un informe resumido.
    """
    if not documento or not grupo or not periodo:
        return pd.DataFrame()

    df_base = cargar_notas(grupo=grupo, periodo=periodo)
    df_base = _preparar_base_informe(df_base)

    if df_base.empty:
        return pd.DataFrame()

    df_estudiante = _filtrar_estudiante(df_base, documento=documento)

    if df_estudiante.empty:
        return pd.DataFrame()

    df_estudiante = _seleccionar_columnas_informe(df_estudiante)
    df_estudiante = _formatear_columnas(df_estudiante)

    return df_estudiante.reset_index(drop=True)