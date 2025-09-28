import streamlit as st

from utils.load_data import load_hoja_google_consolidados, procesar_consolidados


def mostrar_informe():
    """
    Muestra un informe de las notas de los estudiantes.
    """
    #st.title("Informe de Notas")

    # Cargar consolidados
    st.session_state.consolidado_P1 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P1')
    # procesar consolidados P1
    st.session_state.consolidado_P1 = procesar_consolidados(st.session_state.consolidado_P1)
    # cargar consolidados P2  
    st.session_state.consolidado_P2 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P2')
    # procesar consolidados P2
    st.session_state.consolidado_P2 = procesar_consolidados(st.session_state.consolidado_P2)
    # Unificar los consolidados P1 y P2 en un solo dataframe con metodo merge
    st.session_state.consolidado_P1_P2 = st.session_state.consolidado_P1.merge(st.session_state.consolidado_P2, on=['MATERIA'], how='outer', suffixes=('_P1', '_P2'))
    # renombrar columnas Nota_P1 a PERÍODO 1 y Nota_P2 a PERÍODO 2
    st.session_state.consolidado_P1_P2 = st.session_state.consolidado_P1_P2.rename(columns={'NOTA_P1': 'PERÍODO 1', 'NOTA_P2': 'PERÍODO 2'})

    


    # Cargar consolidado segun el periodo seleccionado
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