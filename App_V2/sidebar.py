import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import qrcode
from io import BytesIO
from utils.visual_helpers import mostrar_tabla_notas, calcular_nota_acumulada, mostrar_barra_progreso, color_informe, color_fila, color_estado, color_calificacion, mostrar_tabla_informe, obtener_color
from utils.load_data import load_hoja_google_consolidados,procesar_consolidados2,cargar_estudiantes, agregar_documento, load_planilla_google, load_notas_google, load_recuperaciones_google, load_comparativos_google,construir_url
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

    #st.session_state.consolidado = informe.mostrar_informe()

    if "usuario" in st.session_state:
        # Verificamos si el estudiante tiene recuperaciones / verificar si st.session_state.df_recuperaciones esta vacío
        d = st.session_state.df_recuperaciones.shape[0] if 'df_recuperaciones' in st.session_state else 0
        tiene_recuperaciones = not st.session_state.df_recuperaciones[st.session_state.df_recuperaciones["DOCUMENTO"] == st.session_state['usuario']].empty

        # Construimos el menú condicionalmente
        opciones_menu = []
        # verificar si el usuario es del grupo 701
        #if st.session_state.grupo1 in ["701","702","703","704"]:
        #opciones_menu.append("📘 Consulta de notas")
        #if tiene_recuperaciones:
        #    opciones_menu.append("♻️ Recuperaciones")

        # verificar si el usuario es del grupo 701
        if st.session_state.grupo1 in ["701","702","703","704"]:
            opciones_menu.append("📝 Informes")
        
        #opciones_menu += ["📊 Comparativos", "📎 Material del área y comunicados"]
        #opciones_menu += ["📎 Material del área y comunicados"]

        if "adm" in st.session_state:
            opciones_menu.append("♻️ Balances")

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
        elif (menu == "📝 Informes"):

            if st.session_state.grupo1 == "701":
                st.header("Informe de Notas")
                st.markdown("""El presente informe permite ver las materias reprobadas en los tres periodos académicos, evidenciando si han sido superadas o no.""")
                
                st.markdown(
                    """
                    <div style='
                        background-color:#f0f6ff; 
                        padding:12px;
                        border-radius:10px;
                        border: 1px solid #d0d0d0;
                        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.0);
                        text-align:left
                    '>
                    <span style='font-size:22px; font-weight:600'>  
                    <span style='color:#d62728'>¡IMPORTANTE!</span>
                        </span>

                    <ul style='font-size:18px;'>
                        <li>El estudiante que al finalizar el tercer periodo tenga <strong>tres o más áreas en desempeño bajo</strong> <span style='color:#1f77b4'>será reprobado</span>.</li>
                        <li><strong>Cronograma:</strong></li>
                    </ul>
                    <table style='width:100%; border-collapse:collapse; font-size:16px;'>
                        <tr style='background-color:#dce6f7; font-weight:bold;'>
                            <td style='padding:8px; border:1px solid #ccc;'>Fecha – Día</td>
                            <td style='padding:8px; border:1px solid #ccc;'>Bloque 1 (6:00–7:50)</td>
                            <td style='padding:8px; border:1px solid #ccc;'>Bloque 2 (8:00–9:50)</td>
                            <td style='padding:8px; border:1px solid #ccc;'>Bloque 3 (10:00–12:00)</td>
                        </tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>18/11/2025 – Martes</td><td style='padding:8px; border:1px solid #ccc;'>Educación Artística</td><td style='padding:8px; border:1px solid #ccc;'>Tecnología</td><td style='padding:8px; border:1px solid #ccc;'>Ética</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>19/11/2025 – Miércoles</td><td style='padding:8px; border:1px solid #ccc;'>Educación Física</td><td style='padding:8px; border:1px solid #ccc;'>Religión</td><td style='padding:8px; border:1px solid #ccc;'>Lengua Castellana</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>20/11/2025 – Jueves</td><td colspan='3' style='padding:8px; border:1px solid #ccc;'>🚫 No se programa – Noche de los Mejores</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>21/11/2025 – Viernes</td><td style='padding:8px; border:1px solid #ccc;'>Matemáticas</td><td style='padding:8px; border:1px solid #ccc;'>Inglés</td><td style='padding:8px; border:1px solid #ccc;'>Ciencias Naturales</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>24/11/2025 – Lunes</td><td colspan='3' style='padding:8px; border:1px solid #ccc;'>🚫 No se programa – Autoevaluación Institucional</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>25/11/2025 – Martes</td><td colspan='3' style='padding:8px; border:1px solid #ccc;'>🚫 No se programa – Entrega de Símbolos</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>26/11/2025 – Miércoles</td><td style='padding:8px; border:1px solid #ccc;'>Matemáticas (pendientes)</td><td style='padding:8px; border:1px solid #ccc;'>Inglés (pendientes)</td><td style='padding:8px; border:1px solid #ccc;'>Ciencias Naturales (pendientes)</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>27/11/2025 – Jueves</td><td style='padding:8px; border:1px solid #ccc;'>Lengua Castellana (pendientes)</td><td style='padding:8px; border:1px solid #ccc;'>Ciencias Sociales (pendientes)</td><td style='padding:8px; border:1px solid #ccc;'>Tecnología (pendientes)</td></tr>
                        <tr><td style='padding:8px; border:1px solid #ccc;'>28/11/2025 – Viernes</td><td style='padding:8px; border:1px solid #ccc;'>Educación Artística (pendientes)</td><td style='padding:8px; border:1px solid #ccc;'>Ética (pendientes)</td><td style='padding:8px; border:1px solid #ccc;'>Ciencias Sociales (pendientes)</td></tr>
                    </table>

                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Mostrar el informe del estudiante
                df = informe.mostrar_informe()
            
                # Agregar columna de email
                if hasattr(st.session_state, "emails"):
                    df["EMAIL"] = df["MATERIA"].map(st.session_state.emails)
                    
                else:
                    emails = {
                        "CIENCIAS NATURALES Y EDUCACIÓN AMBIENTAL": "mayra.parra@itagui.edu.co",
                        "EDUCACIÓN ARTISTICA Y CULTURAL": "mauriciorgomezr@itagui.edu.co",
                        "EDUCACION ETICA  Y  EN VALORES HUMANOS": "dianajlozanod@itagui.edu.co",
                        "EDUCACIÓN FÍSICA, RECREACIÓN Y DEPORTES": "gabrielhortizr@itagui.edu.co",
                        "LENGUA EXTRANJERA INGLES": "ferney.rios@itagui.edu.co",
                        "MATEMÁTICAS": "maycol.segura@itagui.edu.co",
                        "CIENCIAS SOCIALES": "veronica.usuga@itagui.edu.co",
                        "TECNOLOGIA E INFORMÁTICA": "paolaoochoas@itagui.edu.co",
                        "EDUCACION RELIGIOSA": "dianajlozanod@itagui.edu.co",
                        "LENGUA CASTELLANA": "ruthfmontoyam@itagui.edu.co"
                    }
                    st.session_state.emails = emails
                    df["EMAIL"] = df["MATERIA"].map(emails)
                
                # Obtener el dataframe individual del estudiante
                df_individual = df[df['DOCUMENTO'] == st.session_state['usuario']].copy()
                #df_individual["PROMEDIO AÑO"] = round((df_individual["PERÍODO 1"] + df_individual["PERÍODO 2"] + df_individual["PERÍODO 3"])/3,1)
                #df_individual["ESTADO AÑO"] = np.where(df_individual["PROMEDIO AÑO"] >= 3.0, "APROBADA", "REPROBADA")
                #st.dataframe(df_individual, use_container_width=True, hide_index=True)

                # si dataframe no esta vacío
                if df.shape[0] == 0:
                    st.warning("No hay datos disponibles para mostrar el informe.")
                else:
                    # Dos columnas para las leyendas
                    col1, col2 = st.columns(2)

                    with col1:
                        # Leyenda de colores con emoji para desempeño
                        st.markdown("""
                        **Leyenda de colores para desempeño:**

                        🟩 **Verde**: Desempeño superior          
                        🟨 **Amarillo**: Desempeño alto         
                        🟧 **Naranja**: Desempeño basico         
                        🟥 **Rojo**: Desempeño bajo  

                        """)
                    with col2:
                        # Leyenda de colores con emoji para estado
                        st.markdown("""
                        **Leyenda de estado en la materia:**

                        ✅ **Aprobado**: (G)  
                        ⛔️ **Reprobado**: (R)  
                        🎚️ **Superada**: (S)
                        """)
                    #st.dataframe(st.session_state.consolidado_P1_P2)
                    #st.dataframe(st.session_state.consolidado_P3)
                    #st.dataframe(st.session_state.consolidado_P1_P2_P3)
                    # Aplicar el estilo de color a las filas según el estado
                    #styled_df = df.style.apply(color_fila, axis=1)
                    #st.dataframe(df, use_container_width=True, hide_index=True)

                # Calcular y mostrar el promedio general de PERÍODO 1 y PERÍODO 2
                prom_P1 = df_individual['PERÍODO 1'].mean().round(2)
                # mostrar barra de progreso del promedio P1
                fig = mostrar_barra_progreso(prom_P1, titulo='Promedio General PERÍODO 1')
                #st.pyplot(fig)
                prom_P2 = df_individual['PERÍODO 2'].mean().round(2)
                # mostrar barra de progreso del promedio P2
                fig = mostrar_barra_progreso(prom_P2, titulo='Promedio General PERÍODO 2')
                #st.pyplot(fig)
                prom_P3 = df_individual['PERÍODO 3'].mean().round(2)
                # mostrar barra de progreso del promedio P2
                fig = mostrar_barra_progreso(prom_P3, titulo='Promedio General PERÍODO 3')
                
                # mostrar tabla de informe con formato
                mostrar_tabla_informe(df_individual)

                # Crear grafico de barras para promedios por periodo
                # Crear gráfico de barras para promedios por periodo
                df_promedios = pd.DataFrame({
                    "Periodo": ["PERÍODO 1", "PERÍODO 2", "PERÍODO 3"],
                    "Promedio": [prom_P1, prom_P2, prom_P3]
                })

                df_promedios["Color"] = df_promedios["Promedio"].apply(obtener_color)

                fig_bar = px.bar(
                    df_promedios,
                    x="Promedio",
                    y="Periodo",
                    text="Promedio",
                    color="Color",
                    color_discrete_map="identity",  # Usa los colores tal cual,
                    title="Desempeño por Periodo"
                )
                fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig_bar.update_layout(xaxis_range=[0, 5], xaxis_title="Promedio", yaxis_title="Periodo")

                st.plotly_chart(fig_bar)
                
                st.subheader("📧 Contacto docente")

                col1, col2 = st.columns(2)

                for i, row in df_individual.iterrows():
                    target_col = col1 if i % 2 == 0 else col2
                    with target_col.expander(f"{row['MATERIA']}"):
                        st.write(row['EMAIL'])

            elif st.session_state.grupo1 in ["702","703","704"]:
                st.header("Resultado Periodos")

                # Dos columnas para las leyendas
                col1, col2 = st.columns(2)
                with col1:
                    # Leyenda de colores con emoji para desempeño
                    st.markdown("""
                    **Leyenda de colores para desempeño:**
                                
                    🟩 **Verde**: Desempeño superior          
                    🟨 **Amarillo**: Desempeño alto         
                    🟧 **Naranja**: Desempeño basico         
                    🟥 **Rojo**: Desempeño bajo  
                    """)
                with col2:
                    # Leyenda de colores con emoji para estado
                    st.markdown("""
                    **Leyenda de estado en la materia:**
                                
                    ✅ **Aprobado**: (G)  
                    ⛔️ **Reprobado**: (R)  
                    🎚️ **Superada**: (S)
                    """)

                df_702 = informe.mostrar_informe2(st.session_state.ruta_estudiantes,st.session_state.grupo1)
                #st.dataframe(df_702, use_container_width=True, hide_index=True)

                # mostrar tabla de informe con formato
                mostrar_tabla_informe(df_702[df_702.DOCUMENTO == st.session_state['usuario']][['MATERIA','PERÍODO 1','ESTADO_P1','PERÍODO 2','ESTADO_P2','PERÍODO 3','ESTADO_P3']])

        elif menu == "♻️ Recuperaciones":
            st.header("♻️ Recuperaciones")
            recuperaciones.mostrar(st.session_state.df_recuperaciones, st.session_state['usuario'], st.session_state['nombre'], periodo)
              
        elif menu == "📊 Comparativos":
            st.header("📊 Comparativos")
            #comparativos.mostrar(df_comparativos, doc_id, nombre_estudiante)
        elif menu == "📎 Material del área y comunicados":
            st.header(f"📎 Material del área y comunicados")
            materiales.mostrar()

        elif menu == "♻️ Balances":
            st.header("♻️ Balances")
            st.write("Funcionalidad en desarrollo...")

            # Tabs principales del Dashboard
            tabs = [
                "Diregrupo",
                "Matemáticas"
            ]

            if st.session_state.grupo1 == "701":
                st.subheader("Diregrupo")
                df = informe.mostrar_informe()

                st.dataframe(df, use_container_width=True, hide_index=True)
                # Sumar las notas de los dos periodos y agregar columna con la diferencia a 9
                df['NOTA_TOTAL'] = df['PERÍODO 1'].fillna(0) + df['PERÍODO 2'].fillna(0) + + df['PERÍODO 3'].fillna(0)
                df['FALTANTE'] = df['NOTA_TOTAL'].apply(lambda x: max(0,9-x))
                # Contar los periodos con nota menor a 3.0
                df["PENDIENTES"] = (df[["PERÍODO 1", "PERÍODO 2", "PERÍODO 3"]] < 3.0).sum(axis=1)
                # Eliminar documentos de estudiantes cancelados
                df = df[~(df.DOCUMENTO.isin(['1035980132','1155713584','1015191755','7925234','1040575437']))]

                # crear un dataframe con el numero de materias por estudiante que no han alcanzado la nota minima de 9
                df_faltantes = df[df.FALTANTE > 0.0].groupby(['Matricula','DOCUMENTO','Nombre_estudiante']).size().reset_index(name='Materias Reprobadas para el Año')
                # order by Materias_Faltantes descending
                df_faltantes = df_faltantes.sort_values(by='Materias Reprobadas para el Año', ascending=False)
                st.dataframe(df_faltantes[['Nombre_estudiante','Materias Reprobadas para el Año']], use_container_width=True, hide_index=True)

                st.write(f"Total {df_faltantes['Materias Reprobadas para el Año'].sum()}")

                st.dataframe(df[df.DOCUMENTO == st.session_state['usuario']][['Nombre_estudiante', 'MATERIA','PERÍODO 1','PERÍODO 2', 'PERÍODO 3',"PENDIENTES",'FALTANTE']].sort_values(by=['FALTANTE'], ascending=False), use_container_width=True, hide_index=True)

                dk = df[['Matricula','DOCUMENTO','Nombre_estudiante',"PENDIENTES"]].groupby(['Matricula','DOCUMENTO','Nombre_estudiante']).sum().reset_index()
                st.dataframe(dk, use_container_width=True, hide_index=True)
                st.write(f"Total {dk['PENDIENTES'].sum()}")

                materia = st.multiselect(
                "Selecciona el grupo", 
                df['MATERIA'].unique().tolist(),
                default=df['MATERIA'].unique().tolist()
                )

                # Aplicar filtros
                df1 = df[df['MATERIA'].isin(materia)]
                df2 = df1[['Matricula','DOCUMENTO','Nombre_estudiante',"PENDIENTES"]].groupby(['Matricula','DOCUMENTO','Nombre_estudiante']).sum().reset_index()
                st.write(f"Total {df2['PENDIENTES'].sum()}")
                st.dataframe(df2[df2.PENDIENTES > 0.0], use_container_width=True, hide_index=True)

            else:
                st.subheader("Matemáticas")
                # Cargar consolidados 702
                st.session_state.consolidado_702 = informe.mostrar_informe2(st.session_state.ruta_estudiantes,grupo = '702')
                st.session_state.consolidado_702['GRUPO'] = '702'
                # Cargar consolidados 703
                st.session_state.consolidado_703 = informe.mostrar_informe2(st.session_state.ruta_estudiantes,grupo = '703')
                st.session_state.consolidado_703['GRUPO'] = '703'
                # Cargar consolidados 704
                st.session_state.consolidado_704 = informe.mostrar_informe2(st.session_state.ruta_estudiantes,grupo = '704')
                st.session_state.consolidado_704['GRUPO'] = '704'
                st.dataframe(st.session_state.consolidado_702, use_container_width=True, hide_index=True)
                st.dataframe(st.session_state.consolidado_703, use_container_width=True, hide_index=True)
                st.dataframe(st.session_state.consolidado_704, use_container_width=True, hide_index=True)
                # Concatenar
                df_7 = pd.concat([st.session_state.consolidado_702,
                                        st.session_state.consolidado_703,
                                        st.session_state.consolidado_704
                                        ])[['GRUPO','NOMBRE_ESTUDIANTE', 'PERÍODO 1','PERÍODO 2', 'PERÍODO 3']]
                
                p = st.multiselect(
                "Selecciona el periodo", 
                ['P1','P2','P3'],
                default=['P1','P2','P3']
                )
                if len(p) == 1 and p[0] == 'P1':
                    st.dataframe(df_7[(df_7['PERÍODO 1'] < 3.0) & 
                                  ~(df_7['PERÍODO 2'] < 3.0) & 
                                  ~(df_7['PERÍODO 3'] < 3.0)], use_container_width=True, hide_index=True)
                elif len(p) == 1 and p[0] == 'P2':
                    st.dataframe(df_7[~(df_7['PERÍODO 1'] < 3.0) & 
                                  (df_7['PERÍODO 2'] < 3.0) & 
                                  ~(df_7['PERÍODO 3'] < 3.0)], use_container_width=True, hide_index=True)
                elif len(p) == 1 and p[0] == 'P3':
                    st.dataframe(df_7[~(df_7['PERÍODO 1'] < 3.0) & 
                                  ~(df_7['PERÍODO 2'] < 3.0) & 
                                  (df_7['PERÍODO 3'] < 3.0)], use_container_width=True, hide_index=True)
                elif len(p) == 2 and 'P1' in p and 'P2' in p:
                    st.dataframe(df_7[(df_7['PERÍODO 1'] < 3.0) & 
                                  (df_7['PERÍODO 2'] < 3.0) & 
                                  ~(df_7['PERÍODO 3'] < 3.0)], use_container_width=True, hide_index=True)
                elif len(p) == 2 and 'P1' in p and 'P3' in p:
                    st.dataframe(df_7[(df_7['PERÍODO 1'] < 3.0) & 
                                  ~(df_7['PERÍODO 2'] < 3.0) & 
                                  (df_7['PERÍODO 3'] < 3.0)], use_container_width=True, hide_index=True)
                elif len(p) == 2 and 'P2' in p and 'P3' in p:
                    st.dataframe(df_7[~(df_7['PERÍODO 1'] < 3.0) & 
                                  (df_7['PERÍODO 2'] < 3.0) & 
                                  (df_7['PERÍODO 3'] < 3.0)], use_container_width=True, hide_index=True)
                elif len(p) == 3:
                    st.dataframe(df_7[(df_7['PERÍODO 1'] < 3.0) & 
                                  (df_7['PERÍODO 2'] < 3.0) & 
                                  (df_7['PERÍODO 3'] < 3.0)], use_container_width=True, hide_index=True)

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
    try:
        #st.sidebar.image("C:/Users/Durley/Documents/Maycol/Repositorios/Notas_Master/App_V2/escudo_oreste.png", use_container_width=True)  # Logo de la institución
        #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app1.png", use_container_width=True)
        #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_2.png", use_container_width=True)
        #st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_3.png", use_container_width=True)
        st.sidebar.image("D:/Repositorios/Notas_Master/App_V2/logo_app_3.png", use_container_width=True)
    except:
        st.sidebar.image("App_V2/logo_app_4.png", use_container_width=True)
    sidebar_config()

