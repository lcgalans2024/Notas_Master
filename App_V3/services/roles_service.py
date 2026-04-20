"""from config.roles_config import ADMIN_DOCUMENTOS


def obtener_rol_usuario(documento: str) -> str:
    documento = str(documento).strip()

    if documento in ADMIN_DOCUMENTOS:
        return "admin"

    return "estudiante"


def es_admin(documento: str) -> bool:
    return obtener_rol_usuario(documento) == "admin"
    """
from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_roles
from utils.normalizers import normalizar_columnas_dataframe, normalizar_documento


@st.cache_data(ttl=120, show_spinner=False)
def obtener_catalogo_roles() -> pd.DataFrame:
    """
    Carga y normaliza el catálogo de roles desde Google Sheets.
    Estructura esperada:
    - documento
    - nombre
    - rol
    - activo
    """
    df_roles = cargar_roles()

    if df_roles is None or df_roles.empty:
        return pd.DataFrame(columns=["matricula", "nombre", "rol", "activo"])

    df_roles = normalizar_columnas_dataframe(df_roles).copy()

    columnas_requeridas = {"matricula", "rol"}
    faltantes = columnas_requeridas - set(df_roles.columns)

    if faltantes:
        raise ValueError(
            f"La hoja de roles no contiene las columnas requeridas: {', '.join(sorted(faltantes))}"
        )

    df_roles["matricula"] = df_roles["matricula"].apply(normalizar_documento)

    if "nombre" not in df_roles.columns:
        df_roles["nombre"] = None

    if "activo" not in df_roles.columns:
        df_roles["activo"] = "si"

    df_roles["activo"] = (
        df_roles["activo"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df_roles["rol"] = (
        df_roles["rol"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    if "nombre" not in df_roles.columns:
        df_roles["nombre"] = None

    #df_roles = df_roles.drop_duplicates(subset=["matricula"], keep="last").reset_index(drop=True)

    df_roles = (
        df_roles.dropna(subset=["matricula"])
        .loc[df_roles["matricula"] != ""]
        .drop_duplicates(subset=["matricula"], keep="last")
        .reset_index(drop=True)
    )

    return df_roles[["matricula", "nombre", "rol", "activo"]]

def obtener_fila_rol(matricula: str) -> pd.Series | None:
    """
    Retorna la fila de roles asociada a una matrícula.
    """
    matricula = normalizar_documento(matricula)

    if not matricula:
        return None

    df_roles = obtener_catalogo_roles()

    if df_roles.empty:
        return None

    coincidencias = df_roles.loc[df_roles["matricula"] == matricula]

    if coincidencias.empty:
        return None

    return coincidencias.iloc[0]


def obtener_rol_usuario(matricula: str) -> str:
    """
    Determina el rol del usuario a partir de la hoja de roles.

    Reglas:
    - si aparece con activo != 'si' -> 'bloqueado'
    - si aparece con rol definido -> ese rol
    - si no aparece -> 'estudiante'
    """
    fila = obtener_fila_rol(matricula)

    if fila is None:
        return "estudiante"

    if str(fila["activo"]).strip().lower() != "si":
        return "bloqueado"

    rol = str(fila["rol"]).strip().lower()
    return rol if rol else "estudiante"


def es_admin(matricula: str) -> bool:
    return obtener_rol_usuario(matricula) == "admin"


def usuario_activo(matricula: str) -> bool:
    """
    Indica si el usuario está activo.
    - si no aparece en hoja de roles, se considera activo como estudiante
    - si aparece con activo != 'si', se considera bloqueado
    """
    rol = obtener_rol_usuario(matricula)
    return rol != "bloqueado"