from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_notas
from utils.normalizers import (
    normalizar_texto_basico,
    normalizar_columnas_dataframe,
    normalizar_dataframe_notas,
    normalizar_documento,
    normalizar_matricula,
    homologar_columnas_estudiantes,
)
from utils.dataframe_utils import (melt_seguro,
                                   seleccionar_columnas_existentes,
                                   convertir_a_numerico_si_es_posible
                                   
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

def _agregar_dimension(tarea):
    if tarea.startswith('1'):
        return 'HACER'
    elif tarea.startswith('2'):
        return 'SABER'
    elif tarea.startswith('3'):
        return 'AUTOEVALUACIÓN'
    elif tarea.startswith('4'):
        return 'PRUEBA_PERIODO'
    return None


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

def _preparar_base_notas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base de notas para trabajarla internamente.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = homologar_columnas_estudiantes(df)
    #col_validas = _obtener_columnas_validas(df)
    df = normalizar_dataframe_notas(df).copy()

    col_doc = _detectar_columna_documento(df)
    col_mat = _detectar_columna_matricula(df)
    col_nombre = _detectar_columna_nombre(df)

    if col_doc and col_doc != "documento":
        df["documento"] = df[col_doc].apply(normalizar_documento)

    if col_mat and col_mat != "matricula":
        df["matricula"] = df[col_mat].apply(normalizar_documento)

    if col_nombre and col_nombre != "nombre":
        df["nombre"] = df[col_nombre]#.apply(lambda x: str(x).strip())

    if "documento" in df.columns:
        df["documento"] = df["documento"].apply(normalizar_documento)

    if "matricula" in df.columns:
        df["matricula"] = df["matricula"].apply(normalizar_matricula)

    return df

def _detectar_actividades(df: pd.DataFrame) -> list[str]:
    actividades = []
    df = normalizar_columnas_dataframe(df)
    index_campo = df[df['matricula'] == "Campo"].index[0]
    df_actividades = df.iloc[index_campo:, :2].copy()
    df_actividades.columns = df_actividades.iloc[0]
    df_actividades = df_actividades[1:].dropna()
    df_actividades['Campo'] = df_actividades['Campo'].apply(normalizar_texto_basico)
    df_actividades['Campo'] = df_actividades['Campo'].str.replace('_', '.')
    return index_campo, df_actividades

def _diccionario_actividades(df: pd.DataFrame) -> dict:
    index_campo, df_actividades = _detectar_actividades(df)
    dict_actividades = df_actividades.set_index('Campo')['Nombre Actividad'].to_dict()
    return dict_actividades

def _obtener_columnas_validas(df: pd.DataFrame) -> list[str]:
    dict_actividades = _diccionario_actividades(df)
    fijas_final = ['3.1', '3.2', '4.1']
    impares_no_usadas = ['1.1', '1.3', '1.5', '1.7', '1.9', '1.11', '1.13', '1.15', '1.17', '1.19', '2.1', '2.3', '2.5', '2.7', '2.9']
    columnas_validas = [
        clave for clave, valor in dict_actividades.items()
        if isinstance(valor, str) and valor.strip() != "" and clave not in fijas_final and clave not in impares_no_usadas
    ]
    return columnas_validas + fijas_final, dict_actividades

def _filtrar_notas_columnas_validas(df: pd.DataFrame) -> pd.DataFrame:
    columnas_validas, dict_actividades = _obtener_columnas_validas(df)
    columnas_a_conservar = ["matricula", "nombre"] + columnas_validas
    columnas_existentes = [col for col in columnas_a_conservar if col in df.columns]
    return df[columnas_existentes].copy(), dict_actividades

def _filtrar_estudiante(df: pd.DataFrame, matricula: str) -> pd.DataFrame:
    """
    Filtra el DataFrame para dejar únicamente el registro del estudiante consultado.
    """
    if df.empty or "matricula" not in df.columns:
        return pd.DataFrame()

    matricula = normalizar_matricula(matricula)
    df, dict_actividades = _filtrar_notas_columnas_validas(df)
    #reemlazar None por cadena vacía para evitar problemas en la comparación
    df = df.fillna("")
    filtrado = df.loc[df["matricula"] == matricula].copy()

    return filtrado.reset_index(drop=True), dict_actividades


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

    if df_notas.empty:
        return pd.DataFrame()

    df_estudiante, dict_actividades = _filtrar_estudiante(df_notas, matricula=matricula)

    if df_estudiante.empty:
        return pd.DataFrame()

    return df_estudiante.reset_index(drop=True), dict_actividades

def calcular_nota_acumulada(df_usuario):
    """
    Calcula la nota acumulada del estudiante.
    """
    # Definir los pesos para cada proceso
    pesos = {
        'HACER': 0.3,
        'SABER': 0.3,
        'AUTOEVALUACIÓN': 0.2,
        'PRUEBA_PERIODO': 0.2
    }

    # Calcular el promedio ponderado
    acumulado = 0
    ponderacion = 0
    # Carcular el length de cada proceso para determinar la ponderación real
    proceso_lengths = df_usuario['Proceso'].value_counts()

    for proceso in pesos.keys():
        promedio_proceso = df_usuario.loc[df_usuario['Proceso'] == proceso, 'Calificación'].sum() / proceso_lengths.get(proceso, 1)
        if df_usuario[df_usuario["Proceso"] == proceso]["Calificación"].notnull().sum() > 0:
            acumulado += promedio_proceso * pesos[proceso]
            ponderacion += pesos[proceso]      
    
        if ponderacion == 0:
            return 0
        else:
            promedio_ponderado = acumulado / ponderacion

    return ponderacion, round(acumulado, 1), round(promedio_ponderado, 1)

def melt_notas_usuario(matricula: str, grupo: str, periodo: str) -> pd.DataFrame:
    """
    Obtiene las notas del estudiante autenticado para un grupo y periodo dados.

    Retorna un DataFrame listo para visualización.
    """
    df_notas, dict_actividades = obtener_notas_usuario(matricula, grupo, periodo)
    df_notas_melted = melt_seguro(df_notas, id_vars=["nombre","matricula"], var_name="id_actividad", value_name="Calificación")
    df_notas_melted = convertir_a_numerico_si_es_posible(df_notas_melted, "Calificación")
    # Agregar los códigos de actividad por sus nombres descriptivos usando el diccionario
    df_notas_melted['Actividad'] = df_notas_melted['id_actividad'].map(dict_actividades).fillna(df_notas_melted['id_actividad'])
    # agregar columna de dimensión según el código de actividad
    df_notas_melted['Proceso'] = df_notas_melted['id_actividad'].apply(_agregar_dimension)


    return df_notas_melted