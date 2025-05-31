import streamlit as st
import pandas as pd
import numpy as np

import funciones as fn
from funciones import cargar_datos_all,cargar_datos, filtrar_datos

def sidebar_config():

    st.sidebar.header("Filtros del Dashboard")

    st.sidebar.header("DATOS DEL USUARIO")

    # Inicializar session_state si es necesario
    if "documento_estudiante" not in st.session_state:
        st.session_state.documento_estudiante = None
    if "selected_sheet_grupo" not in st.session_state:
        st.session_state.selected_sheet_grupo = None
    if "selected_periodo" not in st.session_state:
        st.session_state.selected_periodo = None
    ############################### Load Data ###############################
    file_path = "data/Notas_Master.xlsx"

    # Usar ExcelFile para obtener los nombres de las hojas
    excel_file = pd.ExcelFile(file_path)

    # Obtener los nombres de las hojas
    sheet_names = excel_file.sheet_names

    # Obtener los nombres de las hojas
    periodo_number = ["",1,2,3]

    # Crear un selector en Streamlit con los nombres de las hojas
    selected_sheet_grupo = st.sidebar.selectbox("Seleccione su grupo", [""] + sheet_names, index= 0)

    documento_estudiante = st.sidebar.text_input("Documento", type='password')

    # Verificar si el usuario ha ingresado su documento
    if documento_estudiante:
        st.session_state.documento_estudiante = documento_estudiante
    else:
        st.session_state.documento_estudiante = None

    # Verificar si el usuario ha seleccionado un grupo
    if selected_sheet_grupo:
        st.session_state.selected_sheet_grupo = selected_sheet_grupo
    else:
        st.session_state.selected_sheet_grupo = None

    # Crear un selector en Streamlit con los periodod
    selected_periodo = st.sidebar.selectbox("Seleccione el periodo académico", periodo_number, index= 0)

    # Verificar si el usuario ha seleccionado un periodo
    if selected_periodo:
        st.session_state.selected_periodo = selected_periodo
    else:
        st.session_state.selected_periodo = None

    submitted = st.sidebar.button("Consultar")

    if st.session_state.documento_estudiante or st.session_state.selected_sheet_grupo or st.session_state.selected_periodo:
        # cargar datos en session state
        st.session_state.file_path = file_path
        #st.session_state.selected_sheet_grupo = selected_sheet_grupo
        #st.session_state.selected_periodo = selected_periodo
        #st.session_state.documento_estudiante = documento_estudiante
        # Cargar los datos
        file_path = st.session_state.file_path
        selected_sheet_grupo = st.session_state.selected_sheet_grupo
        selected_periodo = st.session_state.selected_periodo
        documento_estudiante = st.session_state.documento_estudiante
        # Cargar los datos del archivo Excel

        # Cargar los datos del archivo Excel
        st.session_state.datos = cargar_datos_all(file_path, selected_sheet_grupo)
        datos = st.session_state.datos
        
        # Convertir las columnas 'Matricula' y 'DOCUMENTO' a string para evitar problemas de tipo
        ############### Cargar Datos ################
        datos["Matricula"] = datos["Matricula"].astype(str)
        datos["DOCUMENTO"] = datos["DOCUMENTO"].astype(str)
        # Redondear las columnas numéricas a 2 decimales
        ############### Redondear Datos ################
        for col in datos.select_dtypes(include=np.float64):
            datos[col] = datos[col].round(2)

        # Verificar si el usuario ha ingresado su documento
        if not documento_estudiante:
            st.warning("Por favor, ingresa tu documento para ver tus resultados.")
            return

        # Filtrar los datos según el documento del estudiante
        st.session_state.result_df = filtrar_datos(documento_estudiante, datos)
        df_usuario = st.session_state.result_df

        # Mostrar los resultados en la barra lateral
        if df_usuario.empty:
            st.warning("No se encontraron resultados para el documento ingresado, el cual fue: {}".format(documento_estudiante))
            return
        
        # verificar si se ha ingresado el periodo
        if not selected_periodo or selected_periodo == "":
            st.warning("Por favor, seleccione un periodo académico.")
            return
        
        else:
            with st.sidebar.container(border=True):
                est_nombre = df_usuario['Nombre_estudiante'].iloc[0]
                st.markdown("**ESTUDIANTE:**")
                st.markdown(f"{est_nombre}")
                st.markdown(f"**GRUPO:** {selected_sheet_grupo}")

        st.session_state.df_usuario1 = df_usuario[df_usuario['PERIODO'] == selected_periodo]
        df_usuario1 = st.session_state.df_usuario1

    else:
        st.warning("Ingresar datos del estudiante")

    