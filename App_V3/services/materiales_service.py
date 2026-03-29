from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_materiales
from utils.normalizers import normalizar_columnas_dataframe, normalizar_grupo


COLUMNAS_MATERIALES_PRIORIZADAS = [
    "titulo",
    "descripcion",
    "grupo",
    "anio_academico",
    "materia",
    "enlace",
    "archivo",
    "fecha",
]


def _preparar_base_materiales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base de materiales.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = normalizar_columnas_dataframe(df).copy()

    if "grupo" in df.columns:
        df["grupo"] = df["grupo"].apply(normalizar_grupo)

    if "anio_academico" not in df.columns and "anio" in df.columns:
        df["anio_academico"] = df["anio"]

    if "año_academico" in df.columns and "anio_academico" not in df.columns:
        df["anio_academico"] = df["año_academico"]

    return df


def _filtrar_por_grupo_y_anio(
    df: pd.DataFrame,
    grupo: str,
    anio_academico: str | None = None,
) -> pd.DataFrame:
    """
    Filtra materiales por grupo y, si existe la columna, por año académico.
    """
    if df.empty:
        return df

    grupo = normalizar_grupo(grupo)
    df_filtrado = df.copy()

    if "grupo" in df_filtrado.columns:
        df_filtrado = df_filtrado.loc[df_filtrado["grupo"] == grupo].copy()

    if anio_academico and "anio_academico" in df_filtrado.columns:
        df_filtrado = df_filtrado.loc[
            df_filtrado["anio_academico"].astype(str) == str(anio_academico)
        ].copy()

    return df_filtrado.reset_index(drop=True)


def _seleccionar_columnas_visibles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona columnas prioritarias para visualización.
    Si no están todas, conserva las disponibles.
    """
    if df.empty:
        return df

    columnas_visibles = [col for col in COLUMNAS_MATERIALES_PRIORIZADAS if col in df.columns]

    if not columnas_visibles:
        columnas_visibles = df.columns.tolist()

    return df[columnas_visibles].copy()


def _formatear_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Embellece los nombres de columnas para mostrar en pantalla.
    """
    if df.empty:
        return df

    df = df.copy()
    df.columns = [col.replace("_", " ").strip().title() for col in df.columns]
    return df


@st.cache_data(ttl=120, show_spinner=False)
def obtener_materiales_usuario(grupo: str, anio_academico: str | None = None) -> pd.DataFrame:
    """
    Obtiene los materiales disponibles para el grupo del usuario.
    """
    if not grupo:
        return pd.DataFrame()

    df_materiales = cargar_materiales()
    df_materiales = _preparar_base_materiales(df_materiales)

    if df_materiales.empty:
        return pd.DataFrame()

    df_materiales = _filtrar_por_grupo_y_anio(
        df_materiales,
        grupo=grupo,
        anio_academico=anio_academico,
    )

    if df_materiales.empty:
        return pd.DataFrame()

    df_materiales = _seleccionar_columnas_visibles(df_materiales)
    df_materiales = _formatear_columnas(df_materiales)

    return df_materiales.reset_index(drop=True)