"""
Regla simple para decidir si una función va ahí

Hazte esta pregunta:

¿Esta función serviría también en otra parte del proyecto, sin saber nada de notas, estudiantes o materiales?
Si la respuesta es sí, entonces probablemente deba ir en utils/dataframe_utils.py.

Utilidades para manejo seguro de DataFrames: 
validación de columnas, merges robustos, 
melt sin fallos,
reordenamiento flexible. 
Diseñado para evitar errores comunes al manipular datos con pandas."""

from __future__ import annotations

import pandas as pd


def verificar_columnas_requeridas(
    df: pd.DataFrame,
    columnas_requeridas: list[str] | set[str],
) -> tuple[bool, list[str]]:
    """
    Verifica si el DataFrame contiene todas las columnas requeridas.

    Retorna:
        (True, []) si están todas.
        (False, [faltantes]) si faltan columnas.
    """
    columnas_requeridas = list(columnas_requeridas)
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    return len(faltantes) == 0, faltantes

"""
Ejemplo de uso:

ok, faltantes = verificar_columnas_requeridas(
    df_estudiantes,
    {"documento", "nombre", "grupo"}
)
if not ok:
    raise ValueError(f"Faltan columnas requeridas: {faltantes}")
"""


def seleccionar_columnas_existentes(
    df: pd.DataFrame,
    columnas: list[str],
) -> pd.DataFrame:
    """
    Retorna una copia del DataFrame solo con las columnas que sí existen.
    No falla si alguna columna no está presente.
    """
    columnas_existentes = [col for col in columnas if col in df.columns]
    return df[columnas_existentes].copy()


def renombrar_columnas_si_existen(
    df: pd.DataFrame,
    mapa_renombre: dict[str, str],
) -> pd.DataFrame:
    """
    Renombra únicamente las columnas que existan en el DataFrame.
    """
    df = df.copy()
    mapa_filtrado = {k: v for k, v in mapa_renombre.items() if k in df.columns}
    return df.rename(columns=mapa_filtrado)

# convertir columna a tipo numérico, si no se puede convertir dejar en ""

def convertir_a_numerico_si_es_posible(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    if columna in df.columns:
        df[columna] = pd.to_numeric(df[columna], errors='coerce')
        
    return df


def merge_seguro(
    izquierda: pd.DataFrame,
    derecha: pd.DataFrame,
    on: str | list[str],
    how: str = "left",
    suffixes: tuple[str, str] = ("_x", "_y"),
) -> pd.DataFrame:
    """
    Realiza un merge solo si las columnas clave existen en ambos DataFrames.
    Si no existen, lanza un error claro.
    """
    claves = [on] if isinstance(on, str) else on

    faltantes_izq = [col for col in claves if col not in izquierda.columns]
    faltantes_der = [col for col in claves if col not in derecha.columns]

    if faltantes_izq or faltantes_der:
        raise KeyError(
            "No se puede realizar el merge. "
            f"Faltan en izquierda: {faltantes_izq}. "
            f"Faltan en derecha: {faltantes_der}."
        )

    return izquierda.merge(derecha, on=claves, how=how, suffixes=suffixes)


def ordenar_columnas_con_prioridad(
    df: pd.DataFrame,
    columnas_prioridad: list[str],
) -> pd.DataFrame:
    """
    Reordena columnas poniendo primero las prioritarias que existan
    y luego el resto en su orden original.
    """
    existentes_prioridad = [col for col in columnas_prioridad if col in df.columns]
    restantes = [col for col in df.columns if col not in existentes_prioridad]
    return df[existentes_prioridad + restantes].copy()


def melt_seguro(
    df: pd.DataFrame,
    id_vars: list[str],
    value_vars: list[str] | None = None,
    var_name: str = "variable",
    value_name: str = "value",
) -> pd.DataFrame:
    """
    Ejecuta un melt seguro:
    - valida que id_vars existan,
    - usa solo value_vars presentes,
    - evita fallos por columnas ausentes.

    Si value_vars es None, usa todas las columnas excepto id_vars.
    Si no hay columnas para derretir, retorna un DataFrame vacío
    con las columnas esperadas.
    """
    faltantes_id = [col for col in id_vars if col not in df.columns]
    if faltantes_id:
        raise KeyError(f"Faltan columnas id_vars requeridas: {faltantes_id}")

    if value_vars is None:
        value_vars = [col for col in df.columns if col not in id_vars]
    else:
        value_vars = [col for col in value_vars if col in df.columns]

    if not value_vars:
        return pd.DataFrame(columns=id_vars + [var_name, value_name])

    return df.melt(
        id_vars=id_vars,
        value_vars=value_vars,
        var_name=var_name,
        value_name=value_name,
    )

dict_orden_actividades = {
            "1.2":1, "1.4":2, "1.6":3, "1.8":4, "1.10":5,"1.12":6, "1.14":7, "1.16":8, "1.18":9, "1.20":10,
            "2.2":11, "2.4":12, "2.6":13, "2.8":14, "2.10":15,
            "3.1":16, "3.2":17,
            "4.1":18
        }

dict_orden_procesos = {
            'HACER':1, 'SABER':2, 'AUTOEVALUACIÓN':3, 'PRUEBA_PERIODO':4
        }

def eliminar_columnas_vacías(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina columnas que están completamente vacías (todas las filas son NaN).
    """
    return df.dropna(axis=1, how='all')

def eliminar_filas_vacías(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina filas que están completamente vacías (todas las columnas son NaN).
    """
    return df.dropna(axis=0, how='all')

def eliminar_primeras_filas(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    Elimina las primeras n filas del DataFrame.
    """
    return df.iloc[n:].reset_index(drop=True)

def eliminar_columnas_por_nombre(df: pd.DataFrame, nombres: list[str]) -> pd.DataFrame:
    """
    Elimina columnas que coincidan exactamente con los nombres proporcionados.
    """
    return df.drop(columns=[col for col in nombres if col in df.columns], errors='ignore')

def eliminar_filas_por_valor_en_columna(df: pd.DataFrame, columna: str, valor) -> pd.DataFrame:
    """
    Elimina filas donde la columna especificada tenga el valor dado.
    """
    if columna in df.columns:
        return df[df[columna] != valor].reset_index(drop=True)
    return df

# Eliminar columnas que contienen "Unnamed" en su nombre, común en archivos CSV exportados desde Excel o Google Sheets
def eliminar_columnas_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina columnas cuyo nombre contiene "Unnamed", común en CSV exportados de Excel/Google Sheets.
    """
    return df.loc[:, ~df.columns.str.contains("Unnamed", case=False, na=False)] 
