import streamlit as st

from utils.load_data import load_hoja_google_consolidados, procesar_consolidados, procesar_consolidados2, agregar_documento, cargar_estudiantes


def mostrar_informe():
    """
    Muestra un informe de las notas de los estudiantes.
    """
    #st.title("Informe de Notas")

    k = 2

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
    #df_consolidados = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P{st.session_state.periodo1}')

    # Procesar los datos de notas
    #df_consolidados = procesar_consolidados(df_consolidados)

    ## Agregar opciones de descarga
    #csv = df_consolidados.to_csv(index=False).encode('utf-8')
    #st.download_button(
    #    label="Descargar CSV",
    #    data=csv,
    #    file_name='informe_notas.csv',
    #    mime='text/csv'
    #)

    return st.session_state.consolidado_P1_P2#df_consolidados

def mostrar_informe2(ruta_estudiantes):
    """
    Muestra un informe de las notas de los estudiantes.
    """
    #st.title("Informe de Notas")
    # Cargar consolidados 702
    st.session_state.consolidado_7 = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}')
    # Procesar consolidado P1 702
    st.session_state.consolidado_7 = procesar_consolidados2(st.session_state.consolidado_7)

    # Agregar documento
    df_est = cargar_estudiantes(ruta_estudiantes, "ALL_COL")
    df_est['MATRICULA'] = df_est['MATRICULA'].astype(str)
    st.session_state.consolidado_7 = agregar_documento(st.session_state.consolidado_7, df_est)



    


    # Cargar consolidado segun el periodo seleccionado
    #df_consolidados = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P{st.session_state.periodo1}')

    # Procesar los datos de notas
    #df_consolidados = procesar_consolidados(df_consolidados)

    ## Agregar opciones de descarga
    #csv = df_consolidados.to_csv(index=False).encode('utf-8')
    #st.download_button(
    #    label="Descargar CSV",
    #    data=csv,
    #    file_name='informe_notas.csv',
    #    mime='text/csv'
    #)

    return st.session_state.consolidado_7[st.session_state.consolidado_7.DOCUMENTO == st.session_state['usuario']][['MATERIA','PERÍODO 1','ESTADO_P1','PERÍODO 2','ESTADO_P2']]