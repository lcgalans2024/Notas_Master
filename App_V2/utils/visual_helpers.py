import streamlit as st
import matplotlib.pyplot as plt
import base64

# Función de formato condicional
@st.cache_data(ttl=60)
def color_calificacion(val):
    if float(val) >= 4.5:
        color = 'background-color: #00b050; color: black'  # Verde
    elif float(val) >= 4:
        color = 'background-color: #ffff00; color: black'  # Amarillo claro
    elif float(val) >= 3:
        color = 'background-color: #ffc000; color: black'  # Naranja
    elif float(val) == 0.2:
        color = ' '  # sin color
    else:
        color = 'background-color: #ff0000; color: white'  # Rojo
    return color

# Mapea el color según la función color_calificacion
def obtener_color(val):
    color = color_calificacion(val)
    # Extrae el color de fondo de la cadena CSS
    if "#00b050" in color:
        return "#00b050"  # Verde
    elif "#ffff00" in color:
        return "#ffff00"  # Amarillo
    elif "#ffc000" in color:
        return "#ffc000"  # Naranja
    elif "#ff0000" in color:
        return "#ff0000"  # Rojo
    else:
        return "#cccccc"  # Gris por defecto
# Colorear el informe segun el estado
@st.cache_data(ttl=60)
def color_informe(val):
    if val == 'G':
        color = 'background-color: #00b050; color: black'  # Verde
    elif val == 'S':
        color = 'background-color: #ffff00; color: black'  # Amarillo claro
    else:
        color = 'background-color: #ff0000; color: white'  # Rojo
    return color

def color_fila(row):
    estado = row['ESTADO']
    if estado == 'G':
        return ['background-color: #00b050; color: black'] * len(row)
    elif estado == 'S':
        return ['background-color: #ffff00; color: black'] * len(row)
    else:
        return ['background-color: #ff0000; color: white'] * len(row)
    
# colorear NOTA_P1 y NOTA_P2 segun ESTADO_P1 y ESTADO_P2
def color_estado(row):
    color_map = {
        'G': 'background-color: #00b050; color: black',  # Verde
        'S': 'background-color: #ffff00; color: black',  # Amarillo claro
        'R': 'background-color: #ff0000; color: white'   # Rojo
    }
    if row['ESTADO_P1'] == 'G' and row['ESTADO_P2'] == 'G':
        return [''] + [color_map['G']]*4
    elif row['ESTADO_P1'] == 'R' and row['ESTADO_P2'] == 'R':
        return [''] + [color_map['R']]*4
    elif row['ESTADO_P1'] == 'S' and row['ESTADO_P2'] == 'S':
        return [''] + [color_map['S']]*4
    elif row['ESTADO_P1'] == 'G' and row['ESTADO_P2'] == 'S':
        return [''] + [color_map['G'],color_map['G'], color_map['S'], color_map['S']]
    elif row['ESTADO_P1'] == 'S' and row['ESTADO_P2'] == 'G':
        return [''] + [color_map['S'],color_map['S'], color_map['G'], color_map['G']]
    elif row['ESTADO_P1'] == 'G' and row['ESTADO_P2'] == 'R':
        return [''] + [color_map['G'],color_map['G'], color_map['R'], color_map['R']]
    elif row['ESTADO_P1'] == 'R' and row['ESTADO_P2'] == 'G':
        return [''] + [color_map['R'],color_map['R'], color_map['G'], color_map['G']]
    elif row['ESTADO_P1'] == 'S' and row['ESTADO_P2'] == 'R':
        return [''] + [color_map['S'],color_map['S'],color_map['R'], color_map['R']]
    else:
        return [''] + [color_map['R'],color_map['R'], color_map['S'], color_map['S']]

# Colorear informe por nota de periodo segun desempeño
def color_informe_desempeño(row):
    color_map = {
        'G': 'background-color: #00b050; color: black',  # Verde
        'S': 'background-color: #ffff00; color: black',  # Amarillo claro
        'R': 'background-color: #ff0000; color: white'   # Rojo
    }
    return [color_map.get(row['ESTADO_P1'], '') if col == 'PERÍODO 1' else
            color_map.get(row['ESTADO_P2'], '') if col == 'PERÍODO 2' else ''
            for col in row.index]

def color_informe_desempeño2(row):
    color_map = {
        'Sup': 'background-color: #00b050; color: black',  # Verde
        'Alt': 'background-color: #ffff00; color: black',  # Amarillo claro
        'Bas': 'background-color: #ffc000; color: black',   # Naranja
        'Baj': 'background-color: #ff0000; color: white'   # Rojo
    }
    if row['PERÍODO 1'] < 3.0 and row['PERÍODO 2'] < 3.0:
        return [''] + [color_map['Baj']]*4
    elif row['PERÍODO 1'] < 3.0 and row['PERÍODO 2'] < 4.0:
        return [''] + [color_map['Baj']]*2 + [color_map['Bas']]*2
    elif row['PERÍODO 1'] < 4.0 and row['PERÍODO 2'] < 3.0:
        return [''] + [color_map['Bas']]*2 + [color_map['Baj']]*2
    elif row['PERÍODO 1'] < 4.0 and row['PERÍODO 2'] < 4.0:
        return [''] + [color_map['Bas']]*2 + [color_map['Bas']]*2
    elif row['PERÍODO 1'] < 3.0 and row['PERÍODO 2'] < 4.6:
        return [''] + [color_map['Baj']]*2 + [color_map['Alt']]*2
    elif row['PERÍODO 1'] < 4.6 and row['PERÍODO 2'] < 3.0:
        return [''] + [color_map['Alt']]*2 + [color_map['Baj']]*2
    elif row['PERÍODO 1'] < 4.0 and row['PERÍODO 2'] < 4.6:
        return [''] + [color_map['Bas']]*2 + [color_map['Alt']]*2
    elif row['PERÍODO 1'] < 4.6 and row['PERÍODO 2'] < 4.0:
        return [''] + [color_map['Alt']]*2 + [color_map['Bas']]*2
    elif row['PERÍODO 1'] < 4.6 and row['PERÍODO 2'] < 4.6:
        return [''] + [color_map['Alt']]*2 + [color_map['Alt']]*2
    elif row['PERÍODO 1'] < 3.0 and row['PERÍODO 2'] <= 5.0:
        return [''] + [color_map['Baj']]*2 + [color_map['Sup']]*2
    elif row['PERÍODO 1'] < 4.0 and row['PERÍODO 2'] <= 5.0:
        return [''] + [color_map['Bas']]*2 + [color_map['Sup']]*2
    elif row['PERÍODO 1'] < 4.6 and row['PERÍODO 2'] <= 5.0:
        return [''] + [color_map['Alt']]*2 + [color_map['Sup']]*2
    elif row['PERÍODO 1'] <= 5.0 and row['PERÍODO 2'] < 3.0:
        return [''] + [color_map['Sup']]*2 + [color_map['Baj']]*2
    elif row['PERÍODO 1'] <= 5.0 and row['PERÍODO 2'] < 4.0:
        return [''] + [color_map['Sup']]*2 + [color_map['Bas']]*2
    elif row['PERÍODO 1'] <= 5.0 and row['PERÍODO 2'] < 4.6:
        return [''] + [color_map['Sup']]*2 + [color_map['Alt']]*2
    elif row['PERÍODO 1'] <= 5.0 and row['PERÍODO 2'] <= 5.0:
        return [''] + [color_map['Sup']]*2 + [color_map['Sup']]*2
    
# Mostrar tabla de informe de notas periodos
def mostrar_tabla_informe(df):
    """
    Muestra el DataFrame de informe con colores según su estado.
    """
    styled_df = (
        df[["MATERIA", "PERÍODO 1", "ESTADO_P1", "PERÍODO 2", "ESTADO_P2"]]
        .style
        .format({"PERÍODO 1": "{:.1f}", "PERÍODO 2": "{:.1f}"})
        .apply(color_informe_desempeño2, axis=1)
        .set_table_styles([
            {'selector': 'th', 'props': [
                ('text-align', 'center'),
                ('background-color', '#cce5ff')  # azul claro
            ]},
            {'selector': 'td', 'props': [('text-align', 'center')]}
        ]
        ).hide(axis="index")  # ✅ Esto quita el índice en pandas 1.4+
    )

    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

@st.cache_data(ttl=60)
def mostrar_tabla_notas(df):
    """
    Muestra el DataFrame de notas con calificaciones redondeadas a 1 decimal
    y colores según su rango.
    """
    #df = df.copy()
    # Redondear y formatear a 1 decimal en string para visualización
    df["Calificación"] = df["Calificación"].round(1)#.apply(lambda x: f"{x:.1f}")

    styled_df = (
        df[["PROCESO", "ACTIVIDAD", "Calificación"]]
        .style
        .format({"Calificación": "{:.1f}"})
        .applymap(color_calificacion, subset=["Calificación"])
        .set_table_styles([
            {'selector': 'th', 'props': [
                ('text-align', 'center'),
                ('background-color', '#cce5ff')  # azul claro
            ]},
            {'selector': 'td', 'props': [('text-align', 'center')]}
        ]
        ).hide(axis="index")  # ✅ Esto quita el índice en pandas 1.4+
    )

    #styled_df = st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

# Create a horizontal bar plot representing score
@st.cache_data
def barra_progreso(nota_max,nota,meta,titulo='Nota'):
    fig, ax = plt.subplots(figsize=(8, 2))
    # Create the bar
    ax.broken_barh([(0, nota_max)], (0.5, 1), facecolors='lightgray')
    if nota < meta:
        ax.broken_barh([(0, nota)], (0.5, 1), facecolors='lightcoral')
    elif nota < 4.0:
        ax.broken_barh([(0, nota)], (0.5, 1), facecolors='orange')
    elif nota < 4.5:
        ax.broken_barh([(0, nota)], (0.5, 1), facecolors='yellow')
    else:
        ax.broken_barh([(0, nota)], (0.5, 1), facecolors='green')

    # Add a vertical line for the score
    ax.vlines(meta, 0.5, 1.5, colors='black')

    # Colocar el valor de la nota dentro de la barra verde
    ax.text(nota, 0.95, f'{nota}', ha='right', va='center', fontsize=12, color='black', fontweight='bold')

    # Personalizar el gráfico
    ax.set_yticks([])
    ax.set_xticks(range(0, nota_max + 1))
    ax.set_xlim(0, nota_max)
    ax.set_ylim(0, 2)
    ax.set_title(titulo)

    # Mostrar los bordes del gráfico
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    return fig

def calcular_nota_acumulada(df_usuario):
    """
    Calcula la nota acumulada del estudiante.
    """
    # Definir los pesos para cada proceso
    pesos = {
        'HACER': 0.3,
        'SABER': 0.3,
        'AUTOEVALUACIÓN': 0.2,
        'PRUEBA_PERIODO': 0.2
    }

    # Calcular el promedio ponderado
    promedio_ponderado = 0

    for proceso, peso in pesos.items():
        promedio_ponderado += df_usuario[df_usuario['PROCESO'] == proceso]['Calificación'].mean() * peso

    return round(promedio_ponderado, 1)

def mostrar_barra_progreso(nota_acumulada, titulo ='Nota Acumulada'):
    """
    Muestra una barra de progreso con la nota acumulada.
    """
    nota_max = 5  # Nota máxima
    meta = 3  # Meta a alcanzar
    titulo = titulo

    #fig = barra_progreso(nota_max, nota_acumulada, meta, titulo)
    #st.pyplot(fig, use_container_width=True)
    return barra_progreso(nota_max, nota_acumulada, meta, titulo)

def mostrar_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)