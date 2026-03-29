from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_recuperaciones
from utils.normalizers import (
    normalizar_columnas_dataframe,
    normalizar_grupo,
    normalizar_periodo,
)


COLUMNAS_RECUPERACIONES_PRIORIZADAS = [
    "titulo",
    "descripcion",
    "grupo",
    "periodo",
    "anio_academico",
    "materia",
    "fecha_entrega",
    "enlace",
    "archivo",
    "observaciones",
]


def _preparar_base_recuperaciones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base de recuperaciones.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = normalizar_columnas_dataframe(df).copy()

    if "grupo" in df.columns:
        df["grupo"] = df["grupo"].apply(normalizar_grupo)

    if "periodo" in df.columns:
        df["periodo"] = df["periodo"].apply(normalizar_periodo)

    if "anio_academico" not in df.columns and "anio" in df.columns:
        df["anio_academico"] = df["anio"]

    if "año_academico" in df.columns and "anio_academico" not in df.columns:
        df["anio_academico"] = df["año_academico"]

    return df


def _filtrar_recuperaciones(
    df: pd.DataFrame,
    grupo: str,
    anio_academico: str | None = None,
    periodo: str | None = None,
) -> pd.DataFrame:
    """
    Filtra recuperaciones por grupo, año académico y periodo cuando existan
    las columnas correspondientes.
    """
    if df.empty:
        return df

    df_filtrado = df.copy()

    grupo = normalizar_grupo(grupo)
    if "grupo" in df_filtrado.columns:
        df_filtrado = df_filtrado.loc[df_filtrado["grupo"] == grupo].copy()

    if anio_academico and "anio_academico" in df_filtrado.columns:
        df_filtrado = df_filtrado.loc[
            df_filtrado["anio_academico"].astype(str) == str(anio_academico)
        ].copy()

    if periodo and "periodo" in df_filtrado.columns:
        periodo = normalizar_periodo(periodo)
        df_filtrado = df_filtrado.loc[df_filtrado["periodo"] == periodo].copy()

    return df_filtrado.reset_index(drop=True)


def _seleccionar_columnas_visibles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona las columnas prioritarias para visualización.
    """
    if df.empty:
        return df

    columnas_visibles = [
        col for col in COLUMNAS_RECUPERACIONES_PRIORIZADAS if col in df.columns
    ]

    if not columnas_visibles:
        columnas_visibles = df.columns.tolist()

    return df[columnas_visibles].copy()


def _formatear_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Embellece los nombres de columnas para visualización.
    """
    if df.empty:
        return df

    df = df.copy()
    df.columns = [col.replace("_", " ").strip().title() for col in df.columns]
    return df


@st.cache_data(ttl=120, show_spinner=False)
def obtener_recuperaciones_usuario(
    grupo: str,
    anio_academico: str | None = None,
    periodo: str | None = None,
) -> pd.DataFrame:
    """
    Obtiene las recuperaciones disponibles para el grupo del usuario.
    """
    if not grupo:
        return pd.DataFrame()

    df_recuperaciones = cargar_recuperaciones()
    df_recuperaciones = _preparar_base_recuperaciones(df_recuperaciones)

    if df_recuperaciones.empty:
        return pd.DataFrame()

    df_recuperaciones = _filtrar_recuperaciones(
        df_recuperaciones,
        grupo=grupo,
        anio_academico=anio_academico,
        periodo=periodo,
    )

    if df_recuperaciones.empty:
        return pd.DataFrame()

    df_recuperaciones = _seleccionar_columnas_visibles(df_recuperaciones)
    df_recuperaciones = _formatear_columnas(df_recuperaciones)

    return df_recuperaciones.reset_index(drop=True)