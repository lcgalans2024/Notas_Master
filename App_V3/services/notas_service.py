from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_notas
from utils.normalizers import (
    normalizar_columnas_dataframe,
    normalizar_dataframe_notas,
    normalizar_documento,
    normalizar_matricula,
)


COLUMNAS_META_EXCLUIDAS = {
    "documento",
    "matricula",
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
    candidatos = ["documento", "numero_documento", "identificacion"]
    for col in candidatos:
        if col in df.columns:
            return col
    return None

def _detectar_columna_matricula(df: pd.DataFrame) -> str | None:
    candidatos = ["matricula", "matricula_estudiante", "matrícula"]
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

def _detectar_actividades(df: pd.DataFrame) -> list[str]:
    actividades = []
    df = normalizar_columnas_dataframe(df)
    index_campo = df[df['matricula'] == "Campo"].index[0]
    df_actividades = df.iloc[index_campo:, :2].copy()
    df_actividades.columns = df_actividades.iloc[0]
    df_actividades = df_actividades[1:].dropna()
    return index_campo, df_actividades


def _preparar_base_notas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base de notas para trabajarla internamente.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = normalizar_columnas_dataframe(df)
    df = normalizar_dataframe_notas(df).copy()

    col_doc = _detectar_columna_documento(df)
    col_mat = _detectar_columna_matricula(df)
    col_nombre = _detectar_columna_nombre(df)

    if col_doc and col_doc != "documento":
        df["documento"] = df[col_doc].apply(normalizar_documento)

    if col_mat and col_mat != "matricula":
        df["matricula"] = df[col_mat].apply(normalizar_documento)

    if col_nombre and col_nombre != "nombre":
        df["nombre"] = df[col_nombre]

    if "documento" in df.columns:
        df["documento"] = df["documento"].apply(normalizar_documento)

    if "matricula" in df.columns:
        df["matricula"] = df["matricula"].apply(normalizar_matricula)

    return df


def _filtrar_estudiante(df: pd.DataFrame, matricula: str) -> pd.DataFrame:
    """
    Filtra el DataFrame para dejar únicamente el registro del estudiante consultado.
    """
    if df.empty or "matricula" not in df.columns:
        return pd.DataFrame()

    matricula = normalizar_matricula(matricula)
    filtrado = df.loc[df["matricula"] == matricula].copy()

    return filtrado.reset_index(drop=True)


def _seleccionar_columnas_visibles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona y organiza las columnas que se mostrarán al usuario.
    """
    if df.empty:
        return df

    columnas_fijas = [col for col in ["nombre", "documento", "matricula"] if col in df.columns]

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
def obtener_notas_usuario(matricula: str, grupo: str, periodo: str) -> pd.DataFrame:
    """
    Obtiene las notas del estudiante autenticado para un grupo y periodo dados.

    Retorna un DataFrame listo para visualización.
    """
    if not matricula or not grupo or not periodo:
        return pd.DataFrame()

    df_notas = cargar_notas(grupo=grupo, periodo=periodo)
    df_notas = _preparar_base_notas(df_notas)

    #####################################
    index_campo = _detectar_actividades(df_notas)
    #if index_campo is not None:
    #    st.session_state["actividades"] = df_notas.loc[index_campo].to_dict()

    if df_notas.empty:
        return pd.DataFrame()

    df_estudiante = _filtrar_estudiante(df_notas, matricula=matricula)

    if df_estudiante.empty:
        return pd.DataFrame()

    df_estudiante = _seleccionar_columnas_visibles(df_estudiante)
    #df_estudiante = _formatear_nombres_columnas(df_estudiante)

    return df_estudiante.reset_index(drop=True), index_campo