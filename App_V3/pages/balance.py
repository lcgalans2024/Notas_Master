import streamlit as st
from services.balance_service import preparar_balance_notas
from services.google_sheets_service import (cargar_consolidado,
                                            cargar_notas)
from utils.dataframe_utils import (eliminar_columnas_vacías,
                                   eliminar_filas_vacías,
                                   melt_seguro)
from config.settings import (MATERIAS,
                             )

from components.visual_helpers import (color_calificacion,
)

"""Funciones para balance de notas:
- preparar_balance_notas: Aplica una serie de transformaciones para limpiar y homogeneizar un DataFrame de notas, dejándolo listo para análisis o visualización. Esto incluye eliminar columnas y filas vacías, eliminar filas iniciales que puedan contener metadatos, y homologar las columnas para asegurar consistencia en los nombres.
Estas funciones son genéricas y pueden ser usadas en cualquier parte del proyecto donde se necesite preparar un DataFrame de notas para su uso posterior.
"""

def render_balance() -> None:
    st.title("Balance de notas")
    st.caption("Visualiza un balance limpio y preparado de las notas registradas para el periodo seleccionado.")

    # Aquí podríamos agregar opciones para seleccionar grupo, periodo, etc.
    # Por simplicidad, usaremos valores fijos o los que estén en session_state
    grupo = st.session_state.get("grupo", "801")
    periodo = st.session_state.get("periodo", "P1")

    # Cargar consolidado sin procesar (esto podría venir de Google Sheets o de un archivo local)
    df_consolidado = cargar_consolidado(grupo, periodo)

    # Preparar el balance de notas aplicando las transformaciones necesarias
    df_balance = preparar_balance_notas(df_consolidado)

    # Mostrar el balance preparado
    st.write(f"Balance de notas para el grupo {grupo} y periodo {periodo}:")
    st.dataframe(df_balance)
    
    # Habilitar un multiselect para elegir el estudiante y mostrar solo sus notas
    estudiantes = df_balance["nombre"].unique()
    estudiante_seleccionado = st.multiselect("Selecciona un estudiante:", estudiantes)
    if estudiante_seleccionado:
        df_balance = df_balance[df_balance["nombre"].isin(estudiante_seleccionado)]
        
    # Hacer un melt para tener una fila por cada materia
    columnas_notas = [col for col in df_balance.columns if col not in ["documento", "matricula", "nombre","total_faltas", "no_aprobados", "Nota_promedio"]]
    df_melted = melt_seguro(df_balance, id_vars=["documento", "matricula", "nombre"], value_vars=columnas_notas, var_name="materia", value_name="nota")
    # Pasar columna de materia a mayúscula y eliminar espacios
    df_melted["materia"] = df_melted["materia"].str.upper().str.replace(" ", "")
    # mapear nombres de materias
    df_melted["materia"] = df_melted["materia"].map(MATERIAS)
    st.write("Balance de notas de " + ", ".join(estudiante_seleccionado) + ": ")
    tabla_coloreada = df_melted[["materia", "nota"]].style.format({"nota": "{:.1f}"}).applymap(color_calificacion, subset=["nota"])
    st.dataframe(tabla_coloreada)