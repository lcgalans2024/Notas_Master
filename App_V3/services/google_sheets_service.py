from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd
import requests
import streamlit as st

from config.sheets_config import SHEETS_CONFIG
from config.settings import CACHE_CONFIG


def construir_url_csv(sheet_id: str, gid: str | int) -> str:
    """
    Construye la URL pública de exportación CSV para una hoja de Google Sheets.
    """
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


@st.cache_data(ttl=300, show_spinner=False)
def leer_hoja_csv(url: str) -> pd.DataFrame:
    """
    Lee una hoja pública de Google Sheets en formato CSV y la retorna como DataFrame.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    contenido = response.content.decode("utf-8")
    return pd.read_csv(StringIO(contenido))


def _obtener_sheet_id_principal() -> str:
    sheet_id = SHEETS_CONFIG.get("sheet_id_principal")
    if not sheet_id:
        raise ValueError("No se ha configurado 'sheet_id_principal'.")
    return sheet_id


def _obtener_sheet_id_periodos() -> str:
    sheet_id = SHEETS_CONFIG.get("sheet_id_periodos")
    if not sheet_id:
        raise ValueError("No se ha configurado 'sheet_id_periodos'.")
    return sheet_id


def _obtener_gid_estudiantes(anio_academico: str) -> str:
    gids_estudiantes = SHEETS_CONFIG.get("gids_estudiantes", {})
    gid = gids_estudiantes.get(str(anio_academico))

    if gid is None:
        raise KeyError(
            f"No existe configuración de estudiantes para el año académico '{anio_academico}'."
        )

    return str(gid)


def _obtener_gid_notas(grupo: str, periodo: str) -> str:
    """
    Construye la clave real usada en tu configuración:
    notas_{grupo}_{periodo}
    Ejemplo: notas_701_P1
    """
    gids_notas = SHEETS_CONFIG.get("gids_notas", {})
    clave = f"notas_{grupo}_{periodo}"
    gid = gids_notas.get(clave)

    if gid is None:
        raise KeyError(
            f"No existe configuración de notas para grupo='{grupo}' y periodo='{periodo}'. "
            f"Clave buscada: '{clave}'."
        )

    return str(gid)


def _obtener_gid_materiales() -> str:
    gid = SHEETS_CONFIG.get("gid_materiales")

    if gid in (None, "", "None"):
        raise KeyError("No se ha configurado la hoja de materiales en 'gid_materiales'.")

    return str(gid)


def _obtener_gid_recuperaciones() -> str:
    gid = SHEETS_CONFIG.get("gid_recuperaciones")

    if gid in (None, "", "None"):
        raise KeyError("No se ha configurado la hoja de recuperaciones en 'gid_recuperaciones'.")

    return str(gid)


@st.cache_data(ttl=CACHE_CONFIG["ttl_estudiantes"], show_spinner=False)
def cargar_estudiantes(anio_academico: str) -> pd.DataFrame:
    """
    Carga la hoja de estudiantes correspondiente al año académico indicado.
    """
    sheet_id = _obtener_sheet_id_principal()
    gid = _obtener_gid_estudiantes(anio_academico)
    url = construir_url_csv(sheet_id, gid)
    return leer_hoja_csv(url)


@st.cache_data(ttl=CACHE_CONFIG["ttl_notas"], show_spinner=False)
def cargar_notas(grupo: str, periodo: str) -> pd.DataFrame:
    """
    Carga la hoja de notas correspondiente al grupo y periodo indicados.
    """
    sheet_id = _obtener_sheet_id_principal()
    gid = _obtener_gid_notas(grupo, periodo)
    url = construir_url_csv(sheet_id, gid)
    return leer_hoja_csv(url)


@st.cache_data(ttl=CACHE_CONFIG["ttl_materiales"], show_spinner=False)
def cargar_materiales() -> pd.DataFrame:
    """
    Carga la hoja de materiales.
    """
    sheet_id = _obtener_sheet_id_principal()
    gid = _obtener_gid_materiales()
    url = construir_url_csv(sheet_id, gid)
    return leer_hoja_csv(url)


@st.cache_data(ttl=CACHE_CONFIG["ttl_recuperaciones"], show_spinner=False)
def cargar_recuperaciones() -> pd.DataFrame:
    """
    Carga la hoja de recuperaciones.
    """
    sheet_id = _obtener_sheet_id_principal()
    gid = _obtener_gid_recuperaciones()
    url = construir_url_csv(sheet_id, gid)
    return leer_hoja_csv(url)

@st.cache_data(ttl=120, show_spinner=False)
def cargar_roles() -> pd.DataFrame:
    """
    Carga la hoja de roles.
    """
    sheet_id = _obtener_sheet_id_principal()
    gid = SHEETS_CONFIG.get("gid_roles")

    if gid in (None, "", "None"):
        raise KeyError("No se ha configurado la hoja de roles en 'gid_roles'.")

    url = construir_url_csv(sheet_id, gid)
    return leer_hoja_csv(url)


def existe_configuracion_notas(grupo: str, periodo: str) -> bool:
    """
    Indica si existe una hoja configurada para el grupo y periodo dados.
    """
    clave = f"notas_{grupo}_{periodo}"
    return clave in SHEETS_CONFIG.get("gids_notas", {})


def obtener_periodos_disponibles_por_grupo(grupo: str) -> list[str]:
    """
    Retorna los periodos realmente disponibles para un grupo,
    según la configuración de Google Sheets.
    """
    grupo = str(grupo).strip()
    claves = SHEETS_CONFIG.get("gids_notas", {}).keys()

    periodos = []
    prefijo = f"notas_{grupo}_"

    for clave in claves:
        if clave.startswith(prefijo):
            periodo = clave.replace(prefijo, "")
            periodos.append(periodo)

    return sorted(periodos)


def limpiar_cache_datos() -> None:
    """
    Limpia toda la cache de datos de Streamlit.
    """
    st.cache_data.clear()


def obtener_resumen_configuracion() -> dict[str, Any]:
    """
    Devuelve un resumen de la configuración activa.
    Útil para depuración controlada.
    """
    return {
        "sheet_id_principal": SHEETS_CONFIG.get("sheet_id_principal"),
        "sheet_id_periodos": SHEETS_CONFIG.get("sheet_id_periodos"),
        "anios_estudiantes": list(SHEETS_CONFIG.get("gids_estudiantes", {}).keys()),
        "claves_notas": list(SHEETS_CONFIG.get("gids_notas", {}).keys()),
        "gid_materiales": SHEETS_CONFIG.get("gid_materiales"),
        "gid_recuperaciones": SHEETS_CONFIG.get("gid_recuperaciones"),
    }

def obtener_debug_notas(grupo: str, periodo: str) -> dict:
    """
    Devuelve información de depuración sobre la hoja de notas
    que se intentará consultar.
    """
    clave = f"notas_{grupo}_{periodo}"
    gid = SHEETS_CONFIG.get("gids_notas", {}).get(clave)

    return {
        "grupo": grupo,
        "periodo": periodo,
        "clave_buscada": clave,
        "gid_encontrado": gid,
        "sheet_id": SHEETS_CONFIG.get("sheet_id_periodos"),
        "existe_configuracion": gid is not None,
        "url_csv": construir_url_csv(
            SHEETS_CONFIG.get("sheet_id_periodos"),
            gid
        ) if gid is not None else None,
    }

def cargar_notas_debug(grupo: str, periodo: str) -> pd.DataFrame:
    """
    Carga notas sin ocultar el resultado, útil para depuración manual.
    """
    return cargar_notas(grupo=grupo, periodo=periodo)