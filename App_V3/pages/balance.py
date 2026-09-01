import streamlit as st
from services.balance_service import (preparar_balance_notas,
                                      preparar_balance_varios_periodos,
                                      metricas_balance,
                                      metricas_balance_por_estudiante,
                                      pasar_a_multi_index,
                                      derretir_VP,
                                      asignar_desempeno_v2,
                                      estado_materia,
                                      eliminar_sharp,
                                      mostrar_metricas_estudiante
                                      )
from services.google_sheets_service import (cargar_consolidado,
                                            cargar_consolidado_año,
                                            cargar_consolidado_año_2,
                                            cargar_notas)
from utils.dataframe_utils import (eliminar_columnas_vacías,
                                   eliminar_filas_vacías,
                                   melt_seguro)
from config.settings import (MATERIAS,
                             )

from components.visual_helpers import (color_calificacion,
)

from streamlit_extras.metric_cards import style_metric_cards

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
    ano = st.session_state.get("anio_academico", "2026")

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

    # Crear tab para balance por periodo y varios periodos
    tab1, tab2 = st.tabs(["Balance por periodo", "Balance por varios periodos"])

    with tab1:
        st.subheader("Balance por periodo")
        st.write("Balance de notas para el periodo seleccionado:")
        st.dataframe(df_balance)

    with tab2:
        st.subheader("Balance por varios periodos")

        df_consolidado_vp = cargar_consolidado_año_2(grupo, ano)
        df_consolidado_varios = cargar_consolidado_año(grupo, ano)
        df_balance_varios = preparar_balance_varios_periodos(
            df_consolidado_varios
        )
        st.write('================================================================')
        Df = pasar_a_multi_index(df_consolidado_vp,["P1", "P2"])
        
        df_est = Df.index.to_frame(index=False)

        df_est = preparar_balance_varios_periodos(df_est)

        # Completar columna Est con activos e Identificar cancelados
        df_est.est = df_est.est.fillna("A")

        Est_cancelados = df_est[df_est['est'] == 'C'].shape[0]

        df_est_materia = derretir_VP(Df,["P1", "P2"])
        df_est_materia = df_est_materia[df_est_materia.Est != 'C'].copy()
        df_est_materia = df_est_materia.drop(columns=['Est', 'Total faltas', 'PROMEDIO_P1',
                                                      'PROMEDIO_P2', 'REPROBADAS_P1', 'SUPERADAS_P1',
                                                      'REPROBADAS_P2', 'SUPERADAS_P2'
                                                      ])
        # Aplicar la función a la columna 'P1' y 'P2'
        for periodo in ['P1', 'P2']:
            df_est_materia[f'Desempeño_{periodo}'] = df_est_materia[periodo].apply(asignar_desempeno_v2)
        # Crear columna de estado materia en periodo por periodo según las reglas especificadas
        estado_materia(df_est_materia, ["P1", "P2"])
        # Eliminar los "#" de las columnas de periodo para que solo queden los valores numéricos
        eliminar_sharp(df_est_materia, ["P1", "P2"])

        df_est_materia = preparar_balance_varios_periodos(df_est_materia)

        df_materias = df_est_materia[['materia', 'p1', 'p2']].copy()

        df_est["indice_superadas_p1"] = [
                    1 if x == 0 else y / x
                    for x, y in df_est[
                        ["reprobadas_p1", "superadas_p1"]
                    ].values
                ]

        metricas = metricas_balance(df_est)

        st.dataframe(df_est)
        st.dataframe(df_est_materia)
        st.dataframe(df_materias)
        st.write('================================================================')

        #st.write(f"Balance de notas para el grupo {grupo} y año {ano}:")
        #st.dataframe(df_balance_varios)

        df_balance_varios_unicos = (
            df_balance_varios
            .drop_duplicates(subset=["matricula"])
            [
                [
                    "matricula",
                    "nombre",
                    "promedio_p1",
                    "reprobadas_p1",
                    "superadas_p1",
                    "estado_p1"
                ]
            ]
            .copy()
        )

        df_balance_varios_unicos["indice_superadas_p1"] = [
            1 if x == 0 else y / x
            for x, y in df_balance_varios_unicos[
                ["reprobadas_p1", "superadas_p1"]
            ].values
        ]

        # redondear indice_superadas_p1 a 2 decimales
        df_balance_varios_unicos["indice_superadas_p1"] = df_balance_varios_unicos["indice_superadas_p1"].round(2)

        #st.dataframe(df_balance_varios_unicos)

        st.header("Métricas individuales")


        #metricas = metricas_balance(df_est)

        # Esta sección se vuelve independiente
        mostrar_metricas_estudiante(
            df_est,
            df_est_materia
        )
        
        
