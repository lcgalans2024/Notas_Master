import streamlit as st
import sidebar
import inicio
import login
from components import auth, consulta_notas, materiales#, recuperaciones, comparativos
from utils.load_data import construir_url,load_notas_google, load_recuperaciones_google, load_comparativos_google, cargar_datos_grupo, obtener_diccionario_actividades, limpiar_y_seleccionar_notas, cargar_estudiantes, agregar_documento, formar_pares, comparar_y_promediar, preparar_df2, obtener_columnas_validas, transformar_melt

# Configuración general
st.set_page_config(page_title="Plataforma Estudiantil", layout="wide")

# cargar la página de inicio
inicio.inicio()

# Cargar sidebar
if 'usuario' not in st.session_state:
    st.warning("Por favor, inicia sesión para continuar.")
else:
    #st.session_state.usuario = login.obtener_usuario()
    #st.session_state.documento = login.obtener_documento()
    #st.session_state.nombre = login.obtener_nombre()
    #st.session_state.grupo = login.obtener_grupo()
    #st.session_state.periodo = login.obtener_periodo()
  sidebar.sidebar_config()

# Cargar los DataFrames desde Google Sheets
df_notas = load_notas_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
df_recuperaciones = load_recuperaciones_google(st.session_state.SHEET_ID ,st.session_state.GIDS)
df_comparativos = load_comparativos_google(st.session_state.SHEET_ID ,st.session_state.GIDS)

# === PARÁMETROS ===
grupo = "701"
periodo = "1"
ruta_notas = construir_url(st.session_state.SHEET_ID_PM ,st.session_state.GIDS_PM['notas_701_P1'])#"O:/Mi unidad/Orestes/Planilla_Master_IEOS.xlsx"
ruta_estudiantes = "O:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"

dict_orden_act = {
  "1.1":1,
  "1.3":2,
  "1.5":3,
  "1.7":4,
  "1.9":5,
  "1.11":6,
  "2.1":7,
  "2.3":8,
  "2.5":9,
  "2.7":10,
  "2.9":11,
  "3.1":12,
  "3.2":13,
  "4.1":14
}
dict_orden_proc = {
  'HACER':1,
  'SABER':2,
  'AUTOEVALUACIÓN':3,
  'PRUEBA_PERIODO':4
}

# cargar el sidebar

#df5 = consulta_notas.mostrar(grupo, periodo, ruta_notas, ruta_estudiantes, dict_orden_act, dict_orden_proc)  # Mostrar notas por defecto
# Mostrar DataFrame de notas
#st.header("📄 Notas desde Google Sheets (público)")
#st.dataframe(df5)

# Autenticación
#doc_id, nombre_estudiante = auth.login()
#
#if doc_id:
#    st.sidebar.success(f"Bienvenido, {nombre_estudiante}")
#
#    # Verificar si el estudiante tiene recuperaciones
#    tiene_recuperaciones = not df_recuperaciones[df_recuperaciones["documento"] == doc_id].empty
#
#    # Menú lateral
#    opciones_menu = ["📘 Consulta de notas"]
#    if tiene_recuperaciones:
#        opciones_menu.append("♻️ Recuperaciones")
#    opciones_menu += ["📊 Comparativos", "📎 Material y comunicaciones"]
#
#    menu = st.sidebar.radio("Ir a:", opciones_menu)
#    periodo = st.sidebar.selectbox("🗓️ Selecciona el periodo", ["Periodo 1", "Periodo 2", "Periodo 3", "Final"])
#
#    if menu == "📘 Consulta de notas":
#        consulta_notas.mostrar(df_notas, doc_id, nombre_estudiante, periodo)
#    elif menu == "♻️ Recuperaciones":
#        #recuperaciones.mostrar(df_recuperaciones, doc_id, nombre_estudiante, periodo)
#        st.dataframe(df_recuperaciones[df_recuperaciones["documento"] == doc_id], use_container_width=True)
#    elif menu == "📊 Comparativos":
#        #comparativos.mostrar(df_comparativos, doc_id, nombre_estudiante)
#        st.dataframe(df_comparativos[df_comparativos["documento"] == doc_id], use_container_width=True)
#    elif menu == "📎 Material y comunicaciones":
#        materiales.mostrar()
#else:
#    st.warning("Ingrese un documento válido para continuar.")
#