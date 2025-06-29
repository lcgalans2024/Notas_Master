import streamlit as st

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