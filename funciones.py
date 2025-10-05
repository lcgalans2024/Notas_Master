import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#@st.cache_data
def cargar_datos_all(file_path, nombre_hoja):
    df = pd.read_excel(file_path,sheet_name=nombre_hoja)
    return df

#@st.cache_data
def cargar_datos(file_path, nombre_hoja, numero_periodo):
    df = pd.read_excel(file_path,sheet_name=nombre_hoja)
    df = df[df.PERIODO == numero_periodo]
    return df

#@st.cache_data
def filtrar_datos(usuario, df):
    df_filtrado = df[df['DOCUMENTO'] == str(usuario)]
    return df_filtrado.round(2)

# Función de formato condicional
def color_calificacion(val):
    if val >= 4.5:
        color = 'background-color: #00b050; color: black'  # Verde
    elif val >= 4:
        color = 'background-color: #ffff00; color: black'  # Amarillo claro
    elif val >= 3:
        color = 'background-color: #ffc000; color: black'  # Naranja
    else:
        color = 'background-color: #ff0000; color: white'  # Rojo
    return color

def color_condicional(val):
    if val == 1:
        color = 'background-color: #00b050; color: black'  # Verde
    else:
        color = 'background-color: #ff0000; color: white'  # Rojo
    return color

# Función para aplicar el estilo condicional
def resaltar_aciertos(row):
    if row['ACIERTOS'] == 1:
        return ['background-color: lightgreen', '', '']
    else:
        return ['', '', '']
    
def resaltar_aciertos1(row):
    styles = []
    if row['ACIERTOS'] == 1:
        styles.append('background-color: lightgreen')  # PREGUNTA
    else:
        styles.append('')  # PREGUNTA
    styles.append('')  # CATEGORIA
    styles.append('')  # ACIERTOS (aunque se ocultará)
    return styles

#@st.cache_data
# Create a horizontal bar plot representing score
def barra_progreso(M,nota,meta,titulo='Nota'):
    fig, ax = plt.subplots(figsize=(8, 2))
    # Create the bar
    ax.broken_barh([(0, M)], (0.5, 1), facecolors='lightgray')
    ax.broken_barh([(0, nota)], (0.5, 1), facecolors='lightgreen')

    # Add a vertical line for the score
    ax.vlines(meta, 0.5, 1.5, colors='black')

    # Colocar el valor de la nota dentro de la barra verde
    ax.text(nota, 0.95, f'{nota}', ha='right', va='center', fontsize=12, color='black', fontweight='bold')

    # Personalizar el gráfico
    ax.set_yticks([])
    ax.set_xticks(range(0, M + 1))
    ax.set_xlim(0, M)
    ax.set_ylim(0, 2)
    ax.set_title(titulo)

    # Mostrar los bordes del gráfico
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    return fig