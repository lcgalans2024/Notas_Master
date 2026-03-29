from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_notas
from utils.normalizers import (
    normalizar_columnas_dataframe,
    normalizar_dataframe_notas,
    normalizar_documento,
)


COLUMNAS_META_EXCLUIDAS = {
    "documento",
    "nombre",
    "grupo",
    "periodo",
    "anio",
    "año",
    "observaciones",
    "puesto",
    "promedio",
    "definitiva",
    "resultado",
}


def _detectar_columna_documento(df: pd.DataFrame) -> str | None:
    candidatos = ["documento", "matricula", "numero_documento", "identificacion"]
    for col in candidatos:
        if col in df.columns:
            return col
    return None


def _detectar_columna_nombre(df: pd.DataFrame) -> str | None:
    candidatos = ["nombre", "nombre_completo", "estudiante"]
    for col in candidatos:
        if col in df.columns:
            return col
    return None


def _preparar_base_notas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base de notas para trabajarla internamente.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = normalizar_columnas_dataframe(df)
    df = normalizar_dataframe_notas(df).copy()

    col_doc = _detectar_columna_documento(df)
    col_nombre = _detectar_columna_nombre(df)

    if col_doc and col_doc != "documento":
        df["documento"] = df[col_doc].apply(normalizar_documento)

    if col_nombre and col_nombre != "nombre":
        df["nombre"] = df[col_nombre]

    if "documento" in df.columns:
        df["documento"] = df["documento"].apply(normalizar_documento)

    return df


def _filtrar_estudiante(df: pd.DataFrame, documento: str) -> pd.DataFrame:
    """
    Filtra el DataFrame para dejar únicamente el registro del estudiante consultado.
    """
    if df.empty or "documento" not in df.columns:
        return pd.DataFrame()

    documento = normalizar_documento(documento)
    filtrado = df.loc[df["documento"] == documento].copy()

    return filtrado.reset_index(drop=True)


def _seleccionar_columnas_visibles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona y organiza las columnas que se mostrarán al usuario.
    """
    if df.empty:
        return df

    columnas_fijas = [col for col in ["nombre", "documento"] if col in df.columns]

    columnas_notas = []
    for col in df.columns:
        if col in columnas_fijas:
            continue
        if col in COLUMNAS_META_EXCLUIDAS:
            continue
        columnas_notas.append(col)

    columnas_finales = columnas_fijas + columnas_notas

    if not columnas_finales:
        return df

    return df[columnas_finales].copy()


def _formatear_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mejora la presentación de los nombres de columnas para visualización.
    """
    if df.empty:
        return df

    def embellecer(col: str) -> str:
        return col.replace("_", " ").strip().title()

    df = df.copy()
    df.columns = [embellecer(col) for col in df.columns]
    return df


@st.cache_data(ttl=60, show_spinner=False)
def obtener_notas_usuario(documento: str, grupo: str, periodo: str) -> pd.DataFrame:
    """
    Obtiene las notas del estudiante autenticado para un grupo y periodo dados.

    Retorna un DataFrame listo para visualización.
    """
    if not documento or not grupo or not periodo:
        return pd.DataFrame()

    df_notas = cargar_notas(grupo=grupo, periodo=periodo)
    df_notas = _preparar_base_notas(df_notas)

    if df_notas.empty:
        return pd.DataFrame()

    df_estudiante = _filtrar_estudiante(df_notas, documento=documento)

    if df_estudiante.empty:
        return pd.DataFrame()

    df_estudiante = _seleccionar_columnas_visibles(df_estudiante)
    df_estudiante = _formatear_nombres_columnas(df_estudiante)

    return df_estudiante.reset_index(drop=True)