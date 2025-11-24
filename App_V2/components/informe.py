import streamlit as st
import numpy as np

from utils.load_data import (load_hoja_google_consolidados, 
                             procesar_consolidados, 
                             procesar_consolidados2, 
                             agregar_documento, 
                             cargar_estudiantes, 
                             procesar_consolidados_varios_periodos,
                             procesar_consolidados_P4_grupos
                             )


def mostrar_informe():
    """
    Muestra un informe de las notas de los estudiantes.
    """
    #st.title("Informe de Notas")

    k = 2

    # Cargar consolidados
    st.session_state.consolidado_P1 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P1')
    # procesar consolidados P1
    st.session_state.consolidado_P1 = procesar_consolidados(st.session_state.consolidado_P1)
    # cargar consolidados P2  
    st.session_state.consolidado_P2 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P2')
    # procesar consolidados P2
    st.session_state.consolidado_P2 = procesar_consolidados(st.session_state.consolidado_P2)
    # cargar consolidados P3  
    st.session_state.consolidado_P3 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P3')
    # procesar consolidados P3
    st.session_state.consolidado_P3 = procesar_consolidados(st.session_state.consolidado_P3)
    # Unificar los consolidados P1 y P2 en un solo dataframe con metodo merge
    st.session_state.consolidado_P1_P2 = st.session_state.consolidado_P1.merge(st.session_state.consolidado_P2,
                                                                               on=['MATRICULA','DOCUMENTO','NOMBRE_ESTUDIANTE','MATERIA'],
                                                                               how='outer',
                                                                               suffixes=('_P1', '_P2')
                                                                               )#[['MATRICULA','DOCUMENTO','Nombre_estudiante','MATERIA','NOTA_P1', 'ESTADO_P1','NOTA_P2','ESTADO_P2']]
    # Unificar los consolidados P1, P2 y P3 en un solo dataframe con metodo merge
    st.session_state.consolidado_P1_P2_P3 = st.session_state.consolidado_P1_P2.merge(st.session_state.consolidado_P3,
                                                                                     on=['MATRICULA','DOCUMENTO','NOMBRE_ESTUDIANTE','MATERIA'],
                                                                                     how='outer',
                                                                                     suffixes=('_P12', '_P3')
                                                                                     )[['MATRICULA','DOCUMENTO','NOMBRE_ESTUDIANTE','MATERIA','NOTA_P1', 'ESTADO_P1','NOTA_P2','ESTADO_P2','NOTA','ESTADO']]
    # renombrar columnas Nota_P1 a PERÍODO 1 y Nota_P2 a PERÍODO 2
    st.session_state.consolidado_P1_P2_P3 = st.session_state.consolidado_P1_P2_P3.rename(columns={'NOTA_P1': 'PERÍODO 1', 'NOTA_P2': 'PERÍODO 2','NOTA': 'PERÍODO 3', 'ESTADO': 'ESTADO_P3'})
    
    st.session_state.consolidado_P1_P2_P3["PROMEDIO AÑO"] = round((st.session_state.consolidado_P1_P2_P3["PERÍODO 1"] + 
                                                                   st.session_state.consolidado_P1_P2_P3["PERÍODO 2"] + 
                                                                   st.session_state.consolidado_P1_P2_P3["PERÍODO 3"])/3,1
                                                                   )
    st.session_state.consolidado_P1_P2_P3["ESTADO AÑO"] = np.where(st.session_state.consolidado_P1_P2_P3["PROMEDIO AÑO"] >= 3.0, "APROBADA", "REPROBADA")

    return st.session_state.consolidado_P1_P2_P3#df_consolidados
# Informe periodos grupos
def mostrar_informe2(ruta_estudiantes,grupo = None):
    """
    Muestra un informe de las notas de los estudiantes.
    """
    #st.title("Informe de Notas")
    # Cargar consolidados 702
    st.session_state.consolidado_7 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, grupo)
    # Procesar consolidado P1 702
    st.session_state.consolidado_7 = procesar_consolidados2(st.session_state.consolidado_7)

    # Agregar documento
    df_est = cargar_estudiantes(ruta_estudiantes, "ALL_COL")
    df_est['MATRICULA'] = df_est['MATRICULA'].astype(str)
    st.session_state.consolidado_7 = agregar_documento(st.session_state.consolidado_7, df_est)

    return st.session_state.consolidado_7#[st.session_state.consolidado_7.DOCUMENTO == st.session_state['usuario']][['MATERIA','PERÍODO 1','ESTADO_P1','PERÍODO 2','ESTADO_P2','PERÍODO 3','ESTADO_P3']]
# Informe periodo 4 diregrupo
def mostrar_informe3():
    """
    Muestra un informe de las notas de los estudiantes para el año.
    """
    #st.title("Informe de Notas")

    # Cargar consolidados
    st.session_state.consolidado_P4 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P4')
    # procesar consolidados P4
    st.session_state.consolidado_P4 = procesar_consolidados_varios_periodos(st.session_state.consolidado_P4)

    # Agregar documento
    df_est = cargar_estudiantes(st.session_state.ruta_estudiantes, "ALL_COL")
    df_est['MATRICULA'] = df_est['MATRICULA'].astype(str)
    # renombrar columna "Nombre completo" a "NOMBRE_ESTUDIANTE"
    st.session_state.consolidado_P4 = st.session_state.consolidado_P4.rename(columns={"Nombre completo": "NOMBRE_ESTUDIANTE",
                                                                                      "Matrícula": "MATRICULA",})
    st.session_state.consolidado_P4 = agregar_documento(st.session_state.consolidado_P4, df_est)

    return st.session_state.consolidado_P4

# Informe periodo 4 grupos
def mostrar_informe_grupos_P4():
    """
    Muestra un informe de las notas de los estudiantes para el año de los diferentes grupos.
    """
    #st.title("Informe de Notas")

    # Cargar consolidados
    st.session_state.consolidado_grupos_P4 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P4')
    # procesar consolidados P4
    st.session_state.consolidado_grupos_P4 = procesar_consolidados_P4_grupos(st.session_state.consolidado_grupos_P4)

    # Agregar documento
    df_est = cargar_estudiantes(st.session_state.ruta_estudiantes, "ALL_COL")
    df_est['MATRICULA'] = df_est['MATRICULA'].astype(str)
    # renombrar columna "Nombre completo" a "NOMBRE_ESTUDIANTE"
    #st.session_state.consolidado_grupos_P4 = st.session_state.consolidado_grupos_P4.rename(columns={"Nombre completo": "NOMBRE_ESTUDIANTE",
    #                                                                                  "Matrícula": "MATRICULA",})
    st.session_state.consolidado_grupos_P4 = agregar_documento(st.session_state.consolidado_grupos_P4, df_est)

    # Agregar estado año
    st.session_state.consolidado_grupos_P4["ESTADO AÑO"] = np.where(st.session_state.consolidado_grupos_P4["PERÍODO 4"] >= 3.0, "APROBADA", "REPROBADA")

    # Renombrar columna PERÍODO 4 a NOTA AÑO
    st.session_state.consolidado_grupos_P4 = st.session_state.consolidado_grupos_P4.rename(columns={"PERÍODO 4": "NOTA AÑO"})

    return st.session_state.consolidado_grupos_P4