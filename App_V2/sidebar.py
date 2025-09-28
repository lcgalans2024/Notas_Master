import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import qrcode
from io import BytesIO
from utils.visual_helpers import mostrar_tabla_notas, calcular_nota_acumulada, mostrar_barra_progreso, color_informe, color_fila, color_estado
from utils.load_data import load_hoja_google_consolidados,cargar_estudiantes, agregar_documento, load_planilla_google, load_notas_google, load_recuperaciones_google, load_comparativos_google,construir_url
from components import auth, consulta_notas, materiales, recuperaciones, informe#, comparativos

def sidebar_config():
    if "adm" in st.session_state: #st.session_state.get('usuario') == "0":
        st.sidebar.write("👤 Usuario: **Administrador**")
        st.session_state['nombre'] = "Administrador"
        # Selector de grupo
        grupos = ['601','602','701','702','703','704']#st.session_state.df_estudiantes['GRUPO'].unique().tolist()
        grupos = sorted(grupos)  # Ordenar los grupos alfabéticamente
        grupo = st.sidebar.selectbox("👥 Selecciona tu grupo", grupos)
        st.session_state.grupo1 = grupo
        # Selector de usuario
        estudiantes = st.session_state.df_estudiantes[st.session_state.df_estudiantes.GRUPO == f'{grupo}00']['NOMBRE_ESTUDIANTE'].unique().tolist()
        estudiante = st.sidebar.selectbox("👤 Selecciona tu usuario", estudiantes)

        # Obtener el documento del estudiante seleccionado
        documento = st.session_state.df_estudiantes[st.session_state.df_estudiantes['NOMBRE_ESTUDIANTE'] == estudiante]['DOCUMENTO'].values[0]
        st.session_state['usuario'] = documento

    # Selector de grupo y periodo
    st.sidebar.write("Grupo actual:", st.session_state.grupo1)
    # Selector de periodo
    periodo = st.sidebar.selectbox("🗓️ Periodo", ["1", "2", "3", "Final"], 
                               index=["1", "2", "3", "Final"].index(st.session_state.periodo1))
    st.session_state.periodo1 = periodo

    ruta_notas = construir_url(st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM[f'notas_{st.session_state.grupo1}_P{periodo}'])
    st.session_state.ruta_notas = ruta_notas

    if "usuario" in st.session_state:
        # Verificamos si el estudiante tiene recuperaciones / verificar si st.session_state.df_recuperaciones esta vacío
        d = st.session_state.df_recuperaciones.shape[0] if 'df_recuperaciones' in st.session_state else 0
        tiene_recuperaciones = not st.session_state.df_recuperaciones[st.session_state.df_recuperaciones["DOCUMENTO"] == st.session_state['usuario']].empty

        # Construimos el menú condicionalmente
        opciones_menu = ["📘 Consulta de notas"]
        if tiene_recuperaciones:
            opciones_menu.append("♻️ Recuperaciones")

        # verificar si el usuario es del grupo 701
        if st.session_state.grupo1 == "701":
            opciones_menu.append("📝 Informes")
        
        #opciones_menu += ["📊 Comparativos", "📎 Material del área y comunicados"]
        opciones_menu += ["📎 Material del área y comunicados"]

        # si el grupo es 601 o 602, mostrar solo consultas de notas
        if st.session_state.grupo1 in ["601", "602"]:
            opciones_menu = ["📘 Consulta de notas"]

        menu = st.sidebar.radio("Ir a:", opciones_menu)
        #periodo = st.sidebar.selectbox("🗓️ Selecciona el periodo", ["Periodo 1", "Periodo 2", "Periodo 3", "Final"])

        if menu == "📘 Consulta de notas":
            # Si el grupo es 601 o 602, definir area como "Artística"
            if st.session_state.grupo1 in ["601", "602"]:
                st.session_state.area = "Artística"
            else:
                st.session_state.area = "Matemáticas"
            # Mostrar el título del área
            area = st.session_state.area
            st.sidebar.write(f"Área: **{area}**")
            st.header(f"📄 Notas de {st.session_state.area}")

            # Agregar una nota aclaratoria
            st.markdown('''**Nota:** Las calificaciones se muestran en una escala de 0 a 5, 
                        donde 0.2 indica que no se ha realizado la actividad y en consecuencia no se ha evaluado.''')

            st.markdown('''La nota de **Heteroevaluación:** es una nota que se evalua en el aula, clase a clase segun el desempeño integral del estudiante en el área.''') 

            df5 = consulta_notas.mostrar(st.session_state.grupo1, periodo, ruta_notas, st.session_state.ruta_estudiantes,
                                         st.session_state.dict_orden_act, st.session_state.dict_orden_proc
                                         )  # Mostrar notas por defecto
            #st.write(f"dimensiones df: {df5.shape[0]} filas, {df5.shape[1]} columnas")
            
            df6 = df5[df5['DOCUMENTO'] == st.session_state['usuario']].copy()
            
            # mostrar os tipos de las columnas de df6
            #st.write("Tipos de las columnas del DataFrame de notas:")
            #st.table(st.session_state.df_recuperaciones.dtypes)
           
            #st.dataframe(st.session_state.df_recuperaciones[(st.session_state.df_recuperaciones["DOCUMENTO"] == st.session_state['usuario']) 
            #                                                &
            #                                                (st.session_state.df_recuperaciones["PERIODO"] == periodo)
            #                                                ]
            #                                                )

            # Mostrar tabla con formato
            mostrar_tabla_notas(df6)

            # Mostrar barra de progreso
            nota_acumulada = calcular_nota_acumulada(df6)
            # Si la nota acumulada es None, no mostrar la barra de progreso
            if nota_acumulada is not None:
                nota_max = 5
                meta = 3
                fig = mostrar_barra_progreso(nota_acumulada)
                st.pyplot(fig)
        elif menu == "📝 Informes":
            st.header("Informe de Notas")
            st.markdown("""El presente informe permite ver las materias perdidas en periodos anteriores y si estas han sido superadas o no. 
                        Adicionalmente, muestra las materias alertadas en el presente periodo, las cuales deben ser atendidas con prioridad para 
                        evitar que se conviertan en materias perdidas en el periodo actual. 
            """)
            # Mostrar el informe del estudiante
            df = informe.mostrar_informe()
            #mostrar el dataframe original
            #st.dataframe(df, use_container_width=True)
#
            #st.session_state['usuario']
            #st.write(f"Usuario: {st.session_state['usuario']}")
#
            #df_consolidados = load_hoja_google_consolidados(st.session_state.SHEET_ID_CONSOLIDADOS, st.session_state.GIDS_CONSOLIDADOS, f'{st.session_state.grupo1}_P{st.session_state.periodo1}')
            ## mostrar el dataframe
            #st.dataframe(df_consolidados, use_container_width=True)
            #df_consolidados.dropna(axis=1, how='all', inplace=True)
            ##mostrar el dataframe sin columnas vacías
            #st.dataframe(df_consolidados, use_container_width=True)
            #df2 = df_consolidados.loc[:, ~df_consolidados.columns.str.contains('Unnamed')]
            #st.dataframe(df2, use_container_width=True)
            #ind_max = df2[df2['Ord'] == "No aprobados"].index[0]
            #st.write(f"indice maximo: {ind_max}")
            #df3 = df2.iloc[1:ind_max, :].copy()
            #st.dataframe(df3, use_container_width=True)
            ##mostrar el typo de las columnas
            #st.write("Tipos de las columnas del DataFrame de consolidados:")
            #st.table(df3.dtypes)
            #df3.drop(columns=['COM'], inplace=True)
            ## Cambiar Matricula y documento a integer
            #df3["Matricula"] = df3.Matricula.astype(int)
            #try:
            #    df3["Nro Documento"] = df3["Nro Documento"].astype(int)
            #except:
            #    pass
            ## Cambiar a str
            #df3["Matricula"] = df3.Matricula.astype(str)
            #df3["Nro Documento"] = df3["Nro Documento"].astype(str)
            #df3['No aprobados'] = df3['No aprobados'].astype(int)
            #df3['No aprobados'] = df3['No aprobados']-1
            #
            #df3.rename(columns={'Nombre completo':'Nombre_estudiante'
            #      ,'Nro Documento':'DOCUMENTO'
            #      ,'Total faltas':'Total_faltas'
            #      ,'No aprobados':'No_Aprobados'
            #       } , inplace=True)
            #st.dataframe(df3, use_container_width=True)
            ## Derretir la tabla
            #melted_df = pd.melt(df3, id_vars=['Ord', 'Matricula', 'DOCUMENTO', 'Nombre_estudiante', 'Total_faltas', 'No_Aprobados'], var_name='MATERIA', value_name='NOTA')
            #melted_df.sort_values(['Nombre_estudiante'], inplace=True)
            ## Mapear MATERIA con el diccionario materias
            #melted_df['MATERIA'] = melted_df['MATERIA'].map(st.session_state.materias)
            #melted_df.loc[melted_df.NOTA.str.contains('#'), 'ESTADO'] = "S"
            #melted_df.NOTA = melted_df.NOTA.str.replace('#', '', regex=False)
            #melted_df.NOTA = melted_df.NOTA.astype(float)
            #melted_df.loc[melted_df.NOTA < 3.0, 'ESTADO'] = "R"
            #melted_df.loc[(melted_df.NOTA >= 3.0) & (melted_df.ESTADO != 'S'), 'ESTADO'] = "G"
            ## mostrar el dataframe derretido
            #st.dataframe(melted_df, use_container_width=True)
            ## Filtrar por el usuario actual
            #dfk = melted_df[melted_df['DOCUMENTO'] == st.session_state['usuario']].copy()
            #st.dataframe(dfk, use_container_width=True)
            #mostrar el informe
            #styled_df = df.style.applymap(color_informe, subset=['ESTADO'])
            # si dataframe no esta vacío
            if df.shape[0] == 0:
                st.warning("No hay datos disponibles para mostrar el informe.")
            else:
                # Leyenda de colores con emoji
                st.markdown("""
                ✅ **Leyenda de colores:**

                🟩 **Verde (G)**: Aprobado  
                🟥 **Rojo (R)**: Reprobado  
                🟨 **Amarillo (S)**: Superada
                """)
                # Aplicar el estilo de color a las filas según el estado
                styled_df = df.style.apply(color_fila, axis=1)
                #st.dataframe(styled_df, use_container_width=True, hide_index=True)

            # mostrar dataframe consolidados P1 y P2
            #st.markdown("### Consolidados de Periodos Anteriores") 
            #st.markdown("**Consolidado Periodo 1**")
            #st.dataframe(st.session_state.consolidado_P1, use_container_width=True, hide_index=True)
            #st.markdown("**Consolidado Periodo 2**")
            #st.dataframe(st.session_state.consolidado_P2, use_container_width=True, hide_index=True)
            #st.markdown("**Consolidado Periodo 1 y 2**")
            #st.dataframe(st.session_state.consolidado_P1_P2, use_container_width=True, hide_index=True)

            # Aplicar el estilo de color a las filas según el estado
            styled_df = (st.session_state.consolidado_P1_P2
                         .style
                         .format({"PERÍODO 1": "{:.1f}",
                                  "PERÍODO 2": "{:.1f}"})
                         .apply(color_estado, axis=1)
                        .set_table_styles([
                            {'selector': 'th', 'props': [
                                ('text-align', 'center'),
                                ('background-color', '#cce5ff')  # azul claro
                            ]},
                            {'selector': 'td', 'props': [('text-align', 'center')]}
                        ]
                        ).hide(axis="index")  # ✅ Esto quita el índice en pandas 1.4+
                        )
            # Oculta las columnas en la visualización (pandas 2.0+)
            styled_df = styled_df.hide(['ESTADO_P1', 'ESTADO_P2'], axis=1)
            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

            #st.dataframe(df, use_container_width=True, hide_index=True)
        elif menu == "♻️ Recuperaciones":
            st.header("♻️ Recuperaciones")
            recuperaciones.mostrar(st.session_state.df_recuperaciones, st.session_state['usuario'], st.session_state['nombre'], periodo)
              
        elif menu == "📊 Comparativos":
            st.header("📊 Comparativos")
            #comparativos.mostrar(df_comparativos, doc_id, nombre_estudiante)
        elif menu == "📎 Material del área y comunicados":
            st.header(f"📎 Material del área y comunicados")
            materiales.mostrar()

    # Estilos de botones en HTML + CSS
    st.markdown(
        """
        <style>
        div.stButton > button.reset-filtros {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 14px;
            margin: 4px;
            cursor: pointer;
        }
        div.stButton > button.reset-todo {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 14px;
            margin: 4px;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Dos columnas para los botones
    col1, col2 = st.sidebar.columns(2)

    with col1:
        reset_filtros = st.button("🧹 Reset Filtros", key="reset_filtros", help="Limpiar grado y año")
    with col2:
        #reset_todo = st.button("🔄 Reset Todo", key="reset_todo", help="Reiniciar toda la sesión")
        reset_cache = st.button("🔄 Actualizar", key="reset_cache", help="Limpiar la caché de datos")

    # Lógica de botones
    if reset_filtros:
        st.session_state.grado_seleccionado = None
        st.session_state.año_seleccionado = None
        st.success("Filtros reseteados. Selecciona de nuevo.")
        st.rerun()
    if reset_cache:
        #st.session_state.clear()
        st.cache_data.clear()
        st.success("Todo reseteado. Aplicación reiniciada.")
        st.rerun()
    # limpiar la cache
    #st.cache_data.clear()

# Mostrar el sidebar
def mostrar_sidebar():
    st.sidebar.title("Menú de Navegación")
    #st.sidebar.image("C:/Users/Durley/Documents/Maycol/Repositorios/Notas_Master/App_V2/escudo_oreste.png", use_container_width=True)  # Logo de la institución
    #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app1.png", use_container_width=True)
    #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_2.png", use_container_width=True)
    #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_3.png", use_container_width=True)
    #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_3.png", use_container_width=True)
    st.sidebar.image("App_V2/logo_app_4.png", use_container_width=True)
    sidebar_config()

