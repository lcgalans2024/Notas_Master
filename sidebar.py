import streamlit as st
import pandas as pd
import numpy as np

def sidebar_config():

    st.sidebar.header("Filtros del Dashboard")

    st.sidebar.header("DATOS DEL USUARIO")
    ############################### Load Data ###############################
    file_path = "data/Notas_Master.xlsx"

    # Usar ExcelFile para obtener los nombres de las hojas
    excel_file = pd.ExcelFile(file_path)

    # Obtener los nombres de las hojas
    sheet_names = excel_file.sheet_names

    # Obtener los nombres de las hojas
    periodo_number = ["",1,2,3]

    documento_estudiante = st.sidebar.text_input("Documento", type='password')

    # Crear un selector en Streamlit con los nombres de las hojas
    selected_sheet_grupo = st.sidebar.selectbox("Seleccione su grupo", [""] + sheet_names, index= 0)

    # Crear un selector en Streamlit con los periodod
    selected_periodo = st.sidebar.selectbox("Seleccione el periodo académico", periodo_number, index= 0)

    submitted = st.sidebar.button("Consultar")

    