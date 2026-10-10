from __future__ import annotations

import pandas as pd
import numpy as np
import streamlit as st

from services.google_sheets_service import (
    cargar_notas,
    cargar_consolidado_año_vp
)
from utils.normalizers import (
    normalizar_columnas_dataframe,
    normalizar_dataframe_notas,
    normalizar_documento,
)

from utils.dataframe_utils import (
    obtener_fila_columna_texto,
    eliminar_columnas_multiindex
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

#============================================================================================================================
def _procesar_consolidado_varios_periodos(df: pd.DataFrame) -> pd.DataFrame:
    """ Permite recortar y estructurar el archivo consolidado varios periodos,
    identificando la fecha de generación del archivo la columna nombre completlo para seleccionar
    unicamente los estudiantes y la información en las respectivas materias"""
    # obtener indice de fila y columna de la celda que contiene el texto "Fecha de generación"
    fila_fecha, columna_fecha = obtener_fila_columna_texto(df, 'fecha')
    fecha_generacion = df.iloc[fila_fecha, columna_fecha]
    print(f"Fecha de generación: {fecha_generacion}")
    # Recortar el DataFrame a partir de la primera fila no nula en la columna "Nombre completo"
    fila_Nombre_completo, columna_Nombre_completo = obtener_fila_columna_texto(df, 'nombre completo')
    mask = df.iloc[:, columna_Nombre_completo].notnull()
    fila_No_aprobados, columna_No_aprobados = obtener_fila_columna_texto(df, 'no aprobados')
    fila_P1, columna_P1 = obtener_fila_columna_texto(df, 'p1')
    DF_recortado = df.iloc[np.sort(np.append(np.where(mask)[0], fila_P1)), :columna_No_aprobados+1]  # Recortar hasta la columna 32
    # pasar la primera fila como encabezado y eliminarla
    DF_recortado.columns = DF_recortado.iloc[0]
    DF_recortado = DF_recortado.iloc[1:]
    # eliminar columnas vacias
    DF_recortado.dropna(axis=1, how='all', inplace=True)
    # eliminar filas vacias
    DF_recortado.dropna(axis=0, how='all', inplace=True)
    # resetear el indice
    DF_recortado.reset_index(drop=True, inplace=True)
    #DF_recortado = DF_recortado[DF_recortado['Est'] != 'C']
    DF_recortado.drop(columns=['Ord'],inplace=True)
    DF_recortado.drop(columns=['No aprobados'],inplace=True)
    DF_recortado.set_index([ 'Nombre completo',
                            'Matrícula',
                            'Est',
                            'Total faltas'
                            ], inplace=True)

    return DF_recortado

# Contar por fila cuantas celdas contienen '#' según el periodo
def _contar_sharp_por_periodo(row, periodo):
    superadas = 0
    reprobadas = 0
    for col in row.index:
        if col[1] == periodo:
            val = row[col]
            if isinstance(val, str) and '#' in val or float(val) < 3.0:
                reprobadas += 1
            if isinstance(val, str) and '#' in val and float(val.lstrip('#')) == 3.0:
                superadas += 1
    return reprobadas, superadas

def _mean_row_multiindex(
        df: pd.DataFrame,
        subniveles: list[str] | None=None
        ) -> pd.DataFrame:
    """Calcular el promedio por fila para cada sub nivel
    y agrgarlo c en las respectivas columnas al df"""

    # Calcular promedio por fila según el periodo inclullendo las celdas con '#', sin eliminar los '#' del promedio
    for periodo in subniveles:
        # Filtrar las columnas del periodo actual
        cols_periodo = [col for col in df.columns if col[1] == periodo]

        # Calcular el promedio ponderado considerando las celdas con '#'
        promedio_ponderado = df[cols_periodo].apply(
            lambda row: row.apply(
                lambda x: float(x.lstrip('#'))
                if isinstance(x, str) and '#' in x
                else float(x)
                if pd.notnull(x)
                else 0
                ).mean(),
                axis=1)

        # Agregar la columna de promedio al DataFrame
        df[f'PROMEDIO_{periodo}'] = promedio_ponderado.round(1)

    # agregar columna de conteo de '#' por periodo
    for periodo in subniveles:
        df[f'REPROBADAS_{periodo}'] = df.apply(lambda row: _contar_sharp_por_periodo(row, periodo)[0], axis=1)
        df[f'SUPERADAS_{periodo}'] = df.apply(lambda row: _contar_sharp_por_periodo(row, periodo)[1], axis=1)

    return df

def _pasar_a_multi_index(
        df: pd.DataFrame,
        subniveles: list[str] | None=None
        ) -> pd.DataFrame:
    """Pasa el dataframe un multi index"""
    df = _procesar_consolidado_varios_periodos(df)



    colIndex = pd.MultiIndex.from_product(
        [['CIENCIAS NATURALES Y EDUCACIÓN AMBIENTAL',
          'EDUCACIÓN ARTISTICA Y CULTURAL',
          'EDUCACION ETICA  Y  EN VALORES HUMANOS',
          'EDUCACIÓN FÍSICA,'
          'RECREACIÓN Y DEPORTES',
          'EDUCACION RELIGIOSA',
          'LENGUA CASTELLANA',
          'MATEMÁTICAS',
          'TECNOLOGIA E INFORMÁTICA',
          'LENGUA EXTRANJERA INGLES',
          'CIENCIAS SOCIALES'],
          #["P1", "A","P","FN"]]
          ["P1", "P2", "P3", "A","P","FN"],
          #["P1", "P2", "P3", "P4", "A","P","FN"],
          ]
    )

    df.columns = colIndex
    df = df.iloc[1:,:]

    # sub niveles a eliminar
    eliminar = list(set(["P1", "P2", "P3", "A","P","FN"]) - set(subniveles))

    df = eliminar_columnas_multiindex(df, eliminar)

    df = _mean_row_multiindex(df, subniveles)

    # Agregar columnas de promedio, superación y reprobación al índice del DataFrame
    df.set_index(['PROMEDIO_P1', 'PROMEDIO_P2', 'REPROBADAS_P1', 'SUPERADAS_P1', 'REPROBADAS_P2', 'SUPERADAS_P2'], append=True, inplace=True)

    return df

# Función para consolidar promedios, reprobadas, superadas y resultados por materia para varios periodos de cada estudiante
def consolidar_balance_vp(grupo: str, ano: str) -> pd.DataFrame:
    """
    Consolida los datos de balance por periodo, sumando las reprobadas y superadas,
    y calculando el promedio de notas.
    """
    df_consolidado_vp = cargar_consolidado_año_vp(grupo, ano)

    Df = _pasar_a_multi_index(df_consolidado_vp,["P1", "P2"])

    df_est = Df.index.to_frame(index=False)
    # Completar columna Est con activos e Identificar cancelados
    df_est.Est = df_est.Est.fillna("A")

    return df_est
