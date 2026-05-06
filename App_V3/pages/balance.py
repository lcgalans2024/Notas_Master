import streamlit as st
from services.balance_service import preparar_balance_notas
from services.google_sheets_service import (cargar_consolidado,
                                            cargar_notas)

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
    st.dataframe(df_balance.describe())
    st.dataframe(df_balance["no_aprobados"].value_counts())