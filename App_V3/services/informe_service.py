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

def _mean_row_multiindex_3p(
        df: pd.DataFrame,
        subniveles: list[str] | None=None
        ) -> pd.DataFrame:
    """Calcular el promedio por fila para cada sub nivel
    y agrgarlo c en las respectivas columnas al df"""
    periodos = ['P1', 'P2', 'P3']
    # Calcular promedio por fila según el periodo inclullendo las celdas con '#', sin eliminar los '#' del promedio
    for periodo in periodos:
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
    for periodo in periodos:
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

def _pasar_a_multi_index_3p(
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

    df = _mean_row_multiindex_3p(df, subniveles)

    # Agregar columnas de promedio, superación y reprobación al índice del DataFrame
    
    df.set_index(['PROMEDIO_P1', 'PROMEDIO_P2', 'PROMEDIO_P3','REPROBADAS_P1', 'SUPERADAS_P1', 'REPROBADAS_P2', 'SUPERADAS_P2',  'REPROBADAS_P3', 'SUPERADAS_P3'], append=True, inplace=True)

    return df

def derretir_VP(
        df: pd.DataFrame,
        subniveles: list[str] | None=None,
        subniveles_eliminar: list[str] | None=None
        ) -> pd.DataFrame:
    columnas_interes = list(set(["P1", "P2", "P3", "A","P","FN"]) - set(subniveles_eliminar))
    #columnas_interes = ['P1']
    df_largo = (
        df.stack(level=0)  # Materias como variable
        .loc[:, columnas_interes]  # Nos quedamos solo con esas columnas
        .reset_index()
        .rename(columns={"level_13": "Materia"})
    )
    # ordenar por la columna 'Nombre completo'
    df_largo = df_largo.sort_values(by='Nombre completo')

    return df_largo

def _asignar_desempeno_v2(nota):
    # Verificar si la nota es un string y contiene '#'
    if isinstance(nota, str) and '#' in nota:
        # Asignar desempeño según la nota y si contiene '#'
        if float(nota.lstrip('#')) < 3.0:
            return "Bj"
        elif float(nota.lstrip('#')) < 4.0:
            return "Ba"
        elif float(nota.lstrip('#')) < 4.5:
            return "Al"
        else:
            return "Su"
    else:
        # Asignar desempeño según la nota si es un número
        if float(nota) < 3.0:
            return "Bj"
        elif float(nota) < 4.0:
            return "Ba"
        elif float(nota) < 4.5:
            return "Al"
        else:
            return "Su"

def estado_materia(df,subniveles):
    for periodo in subniveles:
        df[f'Superaciones_{periodo}'] = df[periodo].apply(lambda x: "S" if isinstance(x, str) and '#' in x and float(x.lstrip('#')) == 3.0
                                                            else("R" if isinstance(x, str) and '#' in x and float(x.lstrip('#')) < 3.0
                                                                 else ("R" if isinstance(x, str) and float(x) < 3.0
                                                                       else ("A" if isinstance(x, str) and float(x) >= 3.0
                                                                             else ("R" if float(x) < 3.0 else "A")))))

def eliminar_sharp(df, subniveles):
    for periodo in subniveles:
        df[periodo] = df[periodo].apply(lambda x: float(x.lstrip('#')) if isinstance(x, str) and '#' in x else float(x) if pd.notnull(x) else 0)

def informe_año(df, matricula):
    # Seleccionar estudiante para ver su desempeño en las materias
    df_estudiante = df[df['Matrícula'] == matricula]
    nombre_estudiante = df_estudiante['Nombre completo'].iloc[0]
    print(f"Desempeño del estudiante {nombre_estudiante} en las materias:")
    if (df_estudiante['Superaciones_P1'] == 'A').all():
        print("El estudiante no tiene superaciones en el periodo P1.")
        df_informe = df_estudiante[['Materia', 'Desempeño_P1', 'Desempeño_P2', 'Desempeño_P3', 'Estado_año']]
        df_informe.rename(columns={'Desempeño_P1': 'P1', 'Desempeño_P2': 'P2', 'Desempeño_P3': 'P3'}, inplace=True)
    else:
        print("El estudiante tiene superaciones en el periodo P1.")
        df_informe = df_estudiante[['Materia',
                                    'Desempeño_P1',
                                    #'Superaciones_P1',
                                    'Desempeño_P2',
                                    'Desempeño_P3',
                                    #'FN',
                                    'Estado_año'
                                    ]]
        df_informe.rename(columns={'Desempeño_P1': 'P1', 'Desempeño_P2': 'P2', 'Desempeño_P3': 'P3'}, inplace=True)

    return df_informe


# Función para consolidar promedios, reprobadas, superadas y resultados por materia para varios periodos de cada estudiante
def consolidar_balance_vp(grupo: str, ano: str) -> pd.DataFrame:
    """
    Consolida los datos de balance por periodo, sumando las reprobadas y superadas,
    y calculando el promedio de notas.
    """
    df_consolidado_vp = cargar_consolidado_año_vp(grupo, ano)

    Df = _pasar_a_multi_index_3p(df_consolidado_vp,["P1", "P2", "P3", "A","P","FN"])

    df_est = Df.index.to_frame(index=False)
    # Completar columna Est con activos e Identificar cancelados
    df_est.Est = df_est.Est.fillna("A")

    df_est_materia = derretir_VP(Df,subniveles=["P1", "P2", "P3", "A","P","FN"], subniveles_eliminar=["A","P"])

    df_est_materia = df_est_materia[df_est_materia.Est != 'C'].copy()

    df_est_materia = df_est_materia.drop(columns=['Est', 'Total faltas', 'PROMEDIO_P1',
           'PROMEDIO_P2', 'PROMEDIO_P3', 'REPROBADAS_P1', 'SUPERADAS_P1', 'REPROBADAS_P2',
           'SUPERADAS_P2', 'REPROBADAS_P3', 'SUPERADAS_P3'])

    # Aplicar la función a la columna 'P1' y 'P2'
    for periodo in ['P1', 'P2', 'P3']:
        df_est_materia[f'Desempeño_{periodo}'] = df_est_materia[periodo].apply(_asignar_desempeno_v2)

    # Crear columna de estado materia en periodo por periodo según las reglas especificadas
    estado_materia(df_est_materia, ["P1", "P2", "P3"])

    # Eliminar los "#" de las columnas de periodo para que solo queden los valores numéricos
    eliminar_sharp(df_est_materia, ["P1", "P2", "P3"])

    # Crear columna "Estado_año", si "FN" es mayor que 0.0, entonces "REPROBADA" si es igual a 0.0, entonces "APROBADA". insertarla al lado de "Materia"
    # pasar a float la columna FN
    df_est_materia['FN'] = df_est_materia['FN'].replace(',', '.', regex=True).astype(float)
    Estado_año = df_est_materia['FN'].apply(lambda x: 'REPROBADA' if x > 0.0 else 'APROBADA')
    df_est_materia.insert(3, 'Estado_año', Estado_año)

    df_materias = df_est_materia[['Materia', 'P1', 'P2', 'P3']].copy()

    return df_est, df_est_materia, df_materias
