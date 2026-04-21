from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _obtener_cliente_gspread() -> gspread.Client:
    """
    Crea y retorna un cliente autenticado de gspread usando st.secrets.
    """
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def _abrir_spreadsheet(sheet_id: str) -> gspread.Spreadsheet:
    """
    Abre un Google Spreadsheet por su ID.
    """
    client = _obtener_cliente_gspread()
    return client.open_by_key(sheet_id)


def obtener_worksheet(sheet_id: str, worksheet_name: str) -> gspread.Worksheet:
    """
    Obtiene una hoja específica dentro de un spreadsheet.
    """
    spreadsheet = _abrir_spreadsheet(sheet_id)
    return spreadsheet.worksheet(worksheet_name)


def append_row_to_worksheet(
    sheet_id: str,
    worksheet_name: str,
    row_values: list,
) -> None:
    """
    Inserta una nueva fila al final de una hoja.
    """
    worksheet = obtener_worksheet(sheet_id, worksheet_name)
    worksheet.append_row(row_values, value_input_option="USER_ENTERED")


def get_all_records_from_worksheet(
    sheet_id: str,
    worksheet_name: str,
) -> list[dict]:
    """
    Retorna todos los registros de una hoja como lista de diccionarios.
    """
    worksheet = obtener_worksheet(sheet_id, worksheet_name)
    return worksheet.get_all_records()


def estudiante_ya_respondio_autoevaluacion(
    sheet_id: str,
    worksheet_name: str,
    documento: str,
    anio_academico: str,
    periodo: str,
) -> bool:
    """
    Verifica si un estudiante ya tiene registrada una autoevaluación
    para un año académico y periodo dados.
    """
    registros = get_all_records_from_worksheet(sheet_id, worksheet_name)

    documento = str(documento).strip()
    anio_academico = str(anio_academico).strip()
    periodo = str(periodo).strip()

    for fila in registros:
        if (
            str(fila.get("documento", "")).strip() == documento
            and str(fila.get("anio_academico", "")).strip() == anio_academico
            and str(fila.get("periodo", "")).strip() == periodo
        ):
            return True

    return False


def guardar_autoevaluacion(
    sheet_id: str,
    worksheet_name: str,
    payload: dict,
) -> None:
    """
    Guarda una autoevaluación en una hoja de Google Sheets.

    El payload esperado debe contener, como mínimo:
    - documento
    - estudiante
    - grupo
    - matricula
    - anio_academico
    - periodo
    - criterio_1 ... criterio_10
    - nota_final
    """
    fecha_registro = datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S")

    row_values = [
        payload.get("documento"),
        payload.get("estudiante"),
        payload.get("grupo"),
        payload.get("matricula"),
        payload.get("anio_academico"),
        payload.get("periodo"),
        payload.get("criterio_1"),
        payload.get("criterio_2"),
        payload.get("criterio_3"),
        payload.get("criterio_4"),
        payload.get("criterio_5"),
        payload.get("criterio_6"),
        payload.get("criterio_7"),
        payload.get("criterio_8"),
        payload.get("criterio_9"),
        payload.get("criterio_10"),
        payload.get("nota_final"),
        fecha_registro,
    ]

    append_row_to_worksheet(
        sheet_id=sheet_id,
        worksheet_name=worksheet_name,
        row_values=row_values,
    )

def actualizar_celda_por_matricula_y_columna(
    sheet_id: str,
    worksheet_name: str,
    matricula: str,
    nombre_columna_objetivo: str,
    valor,
    nombre_columna_matricula: str = "MATRICULA",
) -> None:
    """
    Actualiza una celda en una hoja de Google Sheets buscando:
    - la fila por matrícula
    - la columna por nombre de encabezado

    Parámetros:
    - sheet_id: ID del spreadsheet
    - worksheet_name: nombre de la hoja
    - matricula: matrícula del estudiante
    - nombre_columna_objetivo: encabezado de la columna a actualizar, ej. "3.1"
    - valor: valor a escribir
    - nombre_columna_matricula: encabezado de la columna de matrícula
    """
    worksheet = obtener_worksheet(sheet_id, worksheet_name)

    valores = worksheet.get_all_values()
    if not valores:
        raise ValueError("La hoja está vacía.")

    encabezados = valores[0]

    try:
        col_idx_objetivo = encabezados.index(nombre_columna_objetivo) + 1
    except ValueError:
        raise KeyError(
            f"No se encontró la columna objetivo '{nombre_columna_objetivo}' en la hoja '{worksheet_name}'."
        )

    try:
        col_idx_matricula = encabezados.index(nombre_columna_matricula) + 1
    except ValueError:
        raise KeyError(
            f"No se encontró la columna de matrícula '{nombre_columna_matricula}' en la hoja '{worksheet_name}'."
        )

    matricula = str(matricula).strip()
    fila_objetivo = None

    for i, fila in enumerate(valores[1:], start=2):
        valor_matricula = fila[col_idx_matricula - 1] if len(fila) >= col_idx_matricula else ""
        if str(valor_matricula).strip() == matricula:
            fila_objetivo = i
            break

    if fila_objetivo is None:
        raise ValueError(
            f"No se encontró la matrícula '{matricula}' en la hoja '{worksheet_name}'."
        )

    worksheet.update_cell(fila_objetivo, col_idx_objetivo, valor)


from config.sheets_config import SHEETS_CONFIG


def obtener_nombre_hoja_notas(grupo: str, periodo: str) -> str:
    """
    Construye el nombre de la hoja de notas según tu convención real.
    Ejemplo: grupo=801, periodo=P1 -> notas_801_P1
    """
    return f"{grupo}_{periodo}"


def escribir_autoevaluacion_en_hoja_notas(
    matricula: str,
    grupo: str,
    periodo: str,
    nota_final: float,
    nombre_columna_objetivo: str = "3.1",
    nombre_columna_matricula: str = "Matricula",
) -> None:
    """
    Escribe la nota de autoevaluación en la hoja de notas del grupo/periodo.
    """
    sheet_id = SHEETS_CONFIG["sheet_id_principal"]
    worksheet_name = obtener_nombre_hoja_notas(grupo, periodo)

    actualizar_celda_por_matricula_y_columna(
        sheet_id=sheet_id,
        worksheet_name=worksheet_name,
        matricula=matricula,
        nombre_columna_objetivo=nombre_columna_objetivo,
        valor=nota_final,
        nombre_columna_matricula=nombre_columna_matricula,
    )

def guardar_inasistencia(
    sheet_id: str,
    worksheet_name: str,
    payload: dict,
) -> None:
    """
    Guarda un registro de inasistencia en Google Sheets.
    """
    fecha_registro = datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S")

    row_values = [
        payload.get("fecha"),
        payload.get("periodo"),
        payload.get("semana_periodo"),
        payload.get("area"),
        payload.get("grupo"),
        payload.get("matricula"),
        payload.get("estudiante"),
        payload.get("observaciones"),
        payload.get("registrado_por_documento"),
        payload.get("registrado_por_nombre"),
        payload.get("rol_registrador"),
        fecha_registro,
        "activo",
    ]

    append_row_to_worksheet(
        sheet_id=sheet_id,
        worksheet_name=worksheet_name,
        row_values=row_values,
    )

def existe_inasistencia_registrada(
    sheet_id: str,
    worksheet_name: str,
    fecha: str,
    grupo: str,
    matricula: str,
    area: str,
) -> bool:
    """
    Verifica si ya existe un registro de inasistencia con la misma combinación:
    fecha + grupo + matrícula + área
    """
    registros = get_all_records_from_worksheet(sheet_id, worksheet_name)

    fecha = str(fecha).strip()
    grupo = str(grupo).strip()
    matricula = str(matricula).strip()
    area = str(area).strip().lower()

    for fila in registros:
        if (
            str(fila.get("fecha", "")).strip() == fecha
            and str(fila.get("grupo", "")).strip() == grupo
            and str(fila.get("matricula", "")).strip() == matricula
            and str(fila.get("area", "")).strip().lower() == area
        ):
            return True

    return False

def anular_inasistencia_por_claves(
    sheet_id: str,
    worksheet_name: str,
    fecha: str,
    grupo: str,
    matricula: str,
    area: str,
) -> None:
    """
    Marca como 'anulado' un registro de inasistencia
    identificado por fecha + grupo + matrícula + área.
    """
    worksheet = obtener_worksheet(sheet_id, worksheet_name)
    valores = worksheet.get_all_values()

    if not valores:
        raise ValueError("La hoja está vacía.")

    encabezados = valores[0]

    columnas_requeridas = ["fecha", "grupo", "matricula", "area", "estado"]
    indices = {}

    for col in columnas_requeridas:
        if col not in encabezados:
            raise KeyError(f"No se encontró la columna '{col}' en la hoja '{worksheet_name}'.")
        indices[col] = encabezados.index(col) + 1

    fecha = str(fecha).strip()
    grupo = str(grupo).strip()
    matricula = str(matricula).strip()
    area = str(area).strip().lower()

    fila_objetivo = None

    for i, fila in enumerate(valores[1:], start=2):
        val_fecha = fila[indices["fecha"] - 1] if len(fila) >= indices["fecha"] else ""
        val_grupo = fila[indices["grupo"] - 1] if len(fila) >= indices["grupo"] else ""
        val_matricula = fila[indices["matricula"] - 1] if len(fila) >= indices["matricula"] else ""
        val_area = fila[indices["area"] - 1] if len(fila) >= indices["area"] else ""

        if (
            str(val_fecha).strip() == fecha
            and str(val_grupo).strip() == grupo
            and str(val_matricula).strip() == matricula
            and str(val_area).strip().lower() == area
        ):
            fila_objetivo = i
            break

    if fila_objetivo is None:
        raise ValueError("No se encontró el registro de inasistencia a anular.")

    worksheet.update_cell(fila_objetivo, indices["estado"], "anulado")