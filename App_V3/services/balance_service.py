from __future__ import annotations

import pandas as pd
import numpy as np
import streamlit as st

from utils.dataframe_utils import (eliminar_columnas_vacías,
                                   eliminar_filas_vacías,
                                      eliminar_primeras_filas,
                                      eliminar_columnas_por_nombre,
                                      eliminar_filas_por_valor_en_columna,
                                      eliminar_columnas_unnamed,
                                      melt_seguro,
                                      )

from utils.normalizers import (homologar_columnas_estudiantes,
                               normalizar_columnas_dataframe, normalizar_documento,
                               normalizar_matricula, normalizar_nombre_persona,
                               normalizar_puntaje)

from components.visual_helpers import (color_calificacion,
)

from streamlit_extras.metric_cards import style_metric_cards


"""
Funciones para balance de notas:
- eliminar_columnas_vacías: Elimina columnas que estén completamente vacías.
- eliminar_filas_vacías: Elimina filas que estén completamente vacías.
- eliminar_primeras_filas: Elimina las primeras n filas, útil para limpiar encabezados o metadatos.
Estas funciones son genéricas y pueden ser usadas en cualquier parte del proyecto donde se necesite limpiar DataFrames de manera segura.
"""

# obtener indice de fila de "No aprobados" en la columna Ord, luego filtrar el df hasta esa fila (sin incluirla)
def _obtener_indice_no_aprobados(df: pd.DataFrame, columna: str = "Ord") -> int:
    return df[df[columna] == "No aprobados"].index[0]

def _filtrar_hasta_no_aprobados(df: pd.DataFrame, columna: str = "ord") -> pd.DataFrame:
    indice = _obtener_indice_no_aprobados(df, columna)
    return df.iloc[:indice]

def preparar_balance_notas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara un DataFrame de notas para su análisis, aplicando limpieza y normalización.
    """
    df = eliminar_columnas_vacías(df)
    df = eliminar_filas_vacías(df)
    df = eliminar_primeras_filas(df, n=1)
    df = homologar_columnas_estudiantes(df)
    df = _filtrar_hasta_no_aprobados(df)
    df = eliminar_filas_por_valor_en_columna(df, columna="est", valor="C")
    df = eliminar_columnas_por_nombre(df, nombres=["ord", "est", "com", "no_evaluados"])
    df = eliminar_columnas_unnamed(df)
    
    df["documento"] = df["documento"].apply(normalizar_documento)
    df["matricula"] = df["matricula"].apply(normalizar_matricula)

    for col in df.columns:
        if col not in ["documento", "matricula", "nombre"]:
            df[col] = df[col].apply(normalizar_puntaje)

    # calcular promedio de las columnas de notas (todas excepto documento, matricula y nombre) y agregar una columna "promedio"
    columnas_notas = [col for col in df.columns if col not in ["documento", "matricula", "nombre","total_faltas", "no_aprobados"]]
    df["Nota_promedio"] = df[columnas_notas].mean(axis=1)
    
    return df
#######################################################------------------#############################################################
# Crear función para signar desempeño, si P4 < 3.0 entonces "Bj", si P4 <4.0 entonces "Ba", si P4 < 4.5 entonces "Al" si no "Sp"
def asignar_desempeno(nota):
    if nota < 3.0:
        return "Bj"
    elif nota < 4.0:
        return "Ba"
    elif nota < 4.6:
        return "Al"
    else:
        return "Sp"
    

def _obtener_fila_columna_texto(df, texto):
    mask = df.astype(str).apply(lambda x: x.str.lower().str.contains(texto, na=False))
    fila, columna = np.where(mask)
    return fila[0], columna[0]

# función para obtener el primer y último índice no nulo de una columna específica
def obtener_indices_no_nulos(df, columna):
    col = df.iloc[:, columna]
    primer_indice = col.first_valid_index()
    ultimo_indice = col.last_valid_index()
    return primer_indice, ultimo_indice

# función para eliminar columnas con nombre "FN" y "A"
def eliminar_columnas(df: pd.DataFrame,list_cols=['FN', 'A', 'P']) -> pd.DataFrame:
    return df.drop(columns=[col for col in df.columns if col[1] in list_cols], errors='ignore')
#==========================================================================================================
# Función para filtrar el DataFrame por un rango de filas y columnas
def _procesar_consolidado_varios_periodos(df):
    """ Permite recortar y estructurar el archivo consolidado varios periodos,
    identificando la fecha de generación del archivo la columna nombre completlo para seleccionar
    unicamente los estudiantes y la información en las respectivas materias"""
    # obtener indice de fila y columna de la celda que contiene el texto "Fecha de generación"
    fila_fecha, columna_fecha = _obtener_fila_columna_texto(df, 'fecha')
    fecha_generacion = df.iloc[fila_fecha, columna_fecha]
    print(f"Fecha de generación: {fecha_generacion}")
    # Recortar el DataFrame a partir de la primera fila no nula en la columna "Nombre completo"
    fila_Nombre_completo, columna_Nombre_completo = _obtener_fila_columna_texto(df, 'nombre completo')
    mask = df.iloc[:, columna_Nombre_completo].notnull()
    fila_No_aprobados, columna_No_aprobados = _obtener_fila_columna_texto(df, 'no aprobados')
    fila_P1, columna_P1 = _obtener_fila_columna_texto(df, 'p1')
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
#==========================================================================================================
def pasar_a_multi_index(
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

    df = eliminar_columnas(df, eliminar)

    df = _mean_row_multiindex(df, subniveles)

    # Agregar columnas de promedio, superación y reprobación al índice del DataFrame
    df.set_index(['PROMEDIO_P1', 'PROMEDIO_P2', 'REPROBADAS_P1', 'SUPERADAS_P1', 'REPROBADAS_P2', 'SUPERADAS_P2'], append=True, inplace=True)

    return df

def derretir_VP(
        df: pd.DataFrame,
        subniveles: list[str] | None=None
        ) -> pd.DataFrame:
    columnas_interes = ['P1', 'P2']
    #columnas_interes = ['P1']
    df_largo = (
        df.stack(level=0)  # Materias como variable
        .loc[:, columnas_interes]  # Nos quedamos solo con esas columnas
        .reset_index()
        .rename(columns={"level_10": "Materia"})
    )
    # ordenar por la columna 'Nombre completo'
    df_largo = df_largo.sort_values(by='Nombre completo')

    return df_largo

def asignar_desempeno_v2(nota):
    # Verificar si la nota es un string y contiene '#'
    if isinstance(nota, str) and '#' in nota:
        # Asignar desempeño según la nota y si contiene '#'
        if float(nota.lstrip('#')) <= 3.0:
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
#######################################################------------------#############################################################

def preparar_balance_varios_periodos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara un DataFrame de notas para su análisis, aplicando limpieza y normalización.
    """
    df = eliminar_columnas_vacías(df)
    #df = eliminar_filas_vacías(df)
    #df = eliminar_primeras_filas(df, n=1)
    df = homologar_columnas_estudiantes(df)
    #df = _filtrar_hasta_no_aprobados(df)
    #df = eliminar_filas_por_valor_en_columna(df, columna="est", valor="C")
    #df = eliminar_columnas_por_nombre(df, nombres=["ord", "est", "com", "no_evaluados"])
    #df = eliminar_columnas_unnamed(df)
    
    #df["documento"] = df["documento"].apply(normalizar_documento)
    df["matricula"] = df["matricula"].apply(normalizar_matricula)

    for col in df.columns:
        if col not in ["documento", "matricula", "nombre", "materia"]:
            df[col] = df[col].apply(normalizar_puntaje)

    return df



def metricas_balance(df: pd.DataFrame) -> dict:
    """
    Calcula métricas básicas del balance de notas.
    """
    Est_cancelados = df[df['est'] == 'C'].shape[0]
    df = df[df.est != 'C'].copy()
    total_estudiantes = df.shape[0]

    promedio_p1 = df["promedio_p1"].mean()
    promedio_p1 = round(promedio_p1, 2) if not pd.isna(promedio_p1) else 0.0
    maximo_p1 = df["promedio_p1"].max()
    minimo_p1 = df["promedio_p1"].min()
    total_reprobadas_p1 = df["reprobadas_p1"].sum()
    total_superadas_p1 = df["superadas_p1"].sum()
    promedio_no_aprobados_p1 = df[df["reprobadas_p1"] > 0]["reprobadas_p1"].mean()
    promedio_no_aprobados_p1 = round(promedio_no_aprobados_p1, 2) if not pd.isna(promedio_no_aprobados_p1) else 0.0
    indice_reprobacion_p1 = df[df["reprobadas_p1"] > 0].shape[0] / total_estudiantes if total_estudiantes > 0 else 0.0
    try:
        promedio_p2 = df["promedio_p2"].mean()
        promedio_p2 = round(promedio_p2, 2) if not pd.isna(promedio_p2) else 0.0
        maximo_p2 = df["promedio_p2"].max()
        minimo_p2 = df["promedio_p2"].min()
        total_reprobadas_p2 = df["reprobadas_p2"].sum()
        total_superadas_p2 = df["superadas_p2"].sum()
        indice_reprobacion_p2 = df[df["reprobadas_p2"] > 0].shape[0] / total_estudiantes if total_estudiantes > 0 else 0.0
    except KeyError:
        promedio_p2 = 0.0
    #promedio_p3 = df["promedio_p3"].mean()
    #promedio_p3 = round(promedio_p3, 2) if not pd.isna(promedio_p3) else 0.0
    #promedio_p4 = df["promedio_p4"].mean()
    #promedio_p4 = round(promedio_p4, 2) if not pd.isna(promedio_p4) else 0.0
    #aprobados_p1 = df[df["estado_p1"] == "A"].shape[0]

    metricas = {
        "total_estudiantes": total_estudiantes,
        "total_cancelados": Est_cancelados,
        "promedio_p1": promedio_p1,
        "promedio_p2": promedio_p2,
        "Máximo P1": maximo_p1,
        "Máximo P2": maximo_p2,
        "Mínimo P1": minimo_p1,
        "Mínimo P2": minimo_p2,
        #"promedio_p3": promedio_p3,
        #"promedio_p4": promedio_p4,
        "promedio_no_aprobados_p1": promedio_no_aprobados_p1,
        "indice_reprobacion_p1": indice_reprobacion_p1,
        "indice_reprobacion_p2": indice_reprobacion_p2,
        "total_reprobadas_p1": total_reprobadas_p1,
        "total_superadas_p1": total_superadas_p1,
        "total_reprobadas_p2": total_reprobadas_p2,
        "total_superadas_p2": total_superadas_p2,
    }

    col1, col2, col3, col4 = st.columns(4)
                
    with col2:    
        st.metric(
                label="Total de estudiantes",
                value=f"{metricas['total_estudiantes']:.0f}"
                )
    
    with col3:
        st.metric(
                label="Cancelados",
                value=f"{metricas['total_cancelados']:.0f}"
                )

    col1, col2, col3, col4 = st.columns(4)
            
    with col1:
        st.metric(
                label="Promedio de grupo P1",
                value=f"{metricas['promedio_p1']:.1f}"
                ) 

        st.metric(
                label="Promedio de grupo P2",
                value=f"{metricas['promedio_p2']:.1f}"
                )      

    with col2:
        
        st.metric(
                label="Máximo P1",
                value=f"{metricas['Máximo P1']:.2f}"
                )

        st.metric(
                label="Máximo P2",
                value=f"{metricas['Máximo P2']:.2f}"
                )


    with col3:
        st.metric(
                label="Mínimo P1",
                value=f"{metricas['Mínimo P1']:.2f}"
                )
        
        st.metric(
                label="Mínimo P2",
                value=f"{metricas['Mínimo P2']:.2f}"
                )

    with col4:
        st.metric(
            label="Indice de reprobación P1",
            value=f"{metricas['indice_reprobacion_p1']:.2f}"
            )
        st.metric(
            label="Indice de reprobación P2",
            value=f"{metricas['indice_reprobacion_p2']:.2f}"
            )
        

    style_metric_cards(border_color="#3A74E7")

    # dataframe con los estudiantes que tienen reprobadas_p1 > 0, mostrando solo las columnas matricula, nombre, reprobadas_p1, superadas_p1, estado_p1, ordenado por reprobadas_p1 descendente 
    df_reprobados_p1 = df[df["reprobadas_p2"] > 3][["matricula", "nombre", "reprobadas_p1", "superadas_p1", "indice_superadas_p1", "reprobadas_p2"]].copy()
    df_reprobados_p1 = df_reprobados_p1.sort_values(by="reprobadas_p2", ascending=False)
    st.dataframe(df_reprobados_p1)

    return metricas

def metricas_balance_por_estudiante(df: pd.DataFrame, estudiante: str) -> pd.DataFrame:
    # Calcula métricas básicas del balance de notas por estudiante.

    # Selector de estudiante
    df_estudiante = df[df["nombre"] == estudiante][["materia", "p1", "p2", "superaciones_p1","superaciones_p2"]].copy()

    return df_estudiante

@st.fragment
def mostrar_metricas_estudiante(df_balance_varios_unicos, df_balance_varios):

    estudiantes = (
        df_balance_varios_unicos["nombre"]
        .dropna()
        .unique()
        .tolist()
    )

    estudiante_varios = st.selectbox(
        "Selecciona un estudiante para ver sus métricas:",
        estudiantes,
        key="balance_estudiante_varios"
    )

    df_estudiante = df_balance_varios_unicos[
        df_balance_varios_unicos["nombre"] == estudiante_varios
    ]

    if df_estudiante.empty:
        st.warning("No se encontraron datos para el estudiante seleccionado.")
        return

    estudiante = df_estudiante.iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Promedio P1",
            value=f"{estudiante['promedio_p1']:.1f}"
        )

    with col2:
        st.metric(
            label="Reprobadas P1",
            value=int(estudiante["reprobadas_p1"])
        )

    with col3:
        st.metric(
            label="Superadas P1",
            value=int(estudiante["superadas_p1"])
        )

    style_metric_cards(border_color="#3A74E7")

    df_metricas = metricas_balance_por_estudiante(
        df_balance_varios,
        estudiante_varios
    )

    st.write("Métricas de balance del estudiante seleccionado:")
    st.dataframe(df_metricas)