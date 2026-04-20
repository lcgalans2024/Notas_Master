from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_estudiantes
from utils.normalizers import (
    normalizar_dataframe_estudiantes,
    normalizar_documento,
    normalizar_matricula,
)


@st.cache_data(ttl=120, show_spinner=False)
def construir_catalogo_usuarios(anio_academico: str) -> pd.DataFrame:
    """
    Construye el catálogo base de usuarios a partir de la hoja de estudiantes.

    Retorna un DataFrame normalizado con, como mínimo:
    - documento
    - matricula
    - nombre
    - grupo
    - rol
    """
    df_estudiantes = cargar_estudiantes(anio_academico)

    if df_estudiantes is None or df_estudiantes.empty:
        return pd.DataFrame(columns=["documento", "matricula", "nombre", "grupo", "rol"])

    df_estudiantes = normalizar_dataframe_estudiantes(df_estudiantes)

    columnas_requeridas = {"documento", "matricula", "nombre", "grupo"}
    faltantes = columnas_requeridas - set(df_estudiantes.columns)

    if faltantes:
        raise ValueError(
            "La base de estudiantes no contiene las columnas requeridas: "
            f"{', '.join(sorted(faltantes))}"
        )

    catalogo = (
        df_estudiantes[["documento", "matricula", "nombre", "grupo"]]
        .dropna(subset=["documento"])
        .copy()
    )

    catalogo["documento"] = catalogo["documento"].apply(normalizar_documento)
    catalogo["matricula"] = catalogo["matricula"].apply(normalizar_matricula)
    catalogo["grupo"] = catalogo["grupo"].astype(str).str.strip()

    catalogo = (
        catalogo.loc[catalogo["documento"] != ""]
        .drop_duplicates(subset=["documento"])
        .reset_index(drop=True)
    )

    catalogo["rol"] = "estudiante"

    return catalogo


def obtener_catalogo_usuarios() -> pd.DataFrame:
    """
    Obtiene el catálogo de usuarios usando el año académico activo de la sesión.
    """
    anio_academico = st.session_state.get("anio_academico", "2025")
    return construir_catalogo_usuarios(anio_academico)


def obtener_usuario_por_documento(documento: str) -> dict | None:
    """
    Busca un usuario por documento y retorna un diccionario con su información.
    """
    documento = normalizar_documento(documento)

    if not documento:
        return None

    catalogo = obtener_catalogo_usuarios()

    if catalogo.empty:
        return None

    coincidencias = catalogo.loc[catalogo["documento"] == documento]

    if coincidencias.empty:
        return None

    fila = coincidencias.iloc[0]

    return {
        "documento": str(fila["documento"]),
        "matricula": str(fila["matricula"]),
        "nombre": str(fila["nombre"]),
        "grupo": str(fila["grupo"]) if pd.notna(fila["grupo"]) else None,
        "rol": str(fila.get("rol", "estudiante")),
    }


def existe_usuario(documento: str) -> bool:
    """
    Indica si existe un usuario registrado con el documento dado.
    """
    return obtener_usuario_por_documento(documento) is not None

def obtener_catalogo_usuarios_por_anio(anio_academico: str) -> pd.DataFrame:
    """
    Obtiene el catálogo de usuarios para un año académico específico.
    """
    return construir_catalogo_usuarios(str(anio_academico))


def obtener_usuario_por_documento_y_anio(documento: str, anio_academico: str) -> dict | None:
    """
    Busca un usuario por documento en el catálogo del año académico indicado.
    """
    documento = normalizar_documento(documento)

    if not documento:
        return None

    catalogo = obtener_catalogo_usuarios_por_anio(anio_academico)

    if catalogo.empty:
        return None

    coincidencias = catalogo.loc[catalogo["documento"] == documento]

    if coincidencias.empty:
        return None

    fila = coincidencias.iloc[0]

    return {
        "documento": str(fila["documento"]),
        "matricula": str(fila["matricula"]),
        "nombre": str(fila["nombre"]),
        "grupo": str(fila["grupo"]) if pd.notna(fila["grupo"]) else None,
        "rol": str(fila.get("rol", "estudiante")),
    }

def obtener_estudiantes_por_grupo_y_anio(grupo: str, anio_academico: str) -> pd.DataFrame:
    """
    Retorna los estudiantes del grupo y año académico indicados.
    """
    df_estudiantes = cargar_estudiantes(anio_academico)

    if df_estudiantes is None or df_estudiantes.empty:
        return pd.DataFrame()

    df_estudiantes = normalizar_dataframe_estudiantes(df_estudiantes)

    columnas_requeridas = {"documento", "nombre", "grupo"}
    faltantes = columnas_requeridas - set(df_estudiantes.columns)

    if faltantes:
        raise ValueError(
            "La base de estudiantes no contiene las columnas requeridas: "
            f"{', '.join(sorted(faltantes))}"
        )

    grupo = str(grupo).strip()

    df_filtrado = df_estudiantes.loc[
        df_estudiantes["grupo"].astype(str).str.strip() == grupo
    ].copy()

    columnas_visibles = [col for col in ["documento", "nombre", "grupo", "matricula"] if col in df_filtrado.columns]

    return df_filtrado[columnas_visibles].drop_duplicates().reset_index(drop=True)