import streamlit as st

from utils.load_data import load_hoja_google_consolidados, procesar_consolidados


def mostrar_informe():
    """
    Muestra un informe de las notas de los estudiantes.
    """
    #st.title("Informe de Notas")

    # Cargar datos de notas
    df_consolidados = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P{st.session_state.periodo1}')

    # Procesar los datos de notas
    df_consolidados = procesar_consolidados(df_consolidados)

    ## Agregar opciones de descarga
    #csv = df_consolidados.to_csv(index=False).encode('utf-8')
    #st.download_button(
    #    label="Descargar CSV",
    #    data=csv,
    #    file_name='informe_notas.csv',
    #    mime='text/csv'
    #)

    return df_consolidados