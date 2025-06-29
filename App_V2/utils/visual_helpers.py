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
    ax.broken_barh([(0, nota)], (0.5, 1), facecolors='lightgreen')

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

def mostrar_barra_progreso(nota_acumulada):
    """
    Muestra una barra de progreso con la nota acumulada.
    """
    nota_max = 5  # Nota máxima
    meta = 3  # Meta a alcanzar
    titulo = 'Nota Acumulada'

    #fig = barra_progreso(nota_max, nota_acumulada, meta, titulo)
    #st.pyplot(fig, use_container_width=True)
    return barra_progreso(nota_max, nota_acumulada, meta, titulo)

def mostrar_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)