import pandas as pd
import streamlit as st
import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from pyuca import Collator

def load_notas():
    return pd.read_csv("data/notas.csv")

def load_recuperaciones():
    return pd.read_csv("data/recuperaciones.csv")

def load_comparativos():
    return pd.read_csv("data/comparativos.csv")

# Opción 1: Leer hoja pública de Google Sheets como CSV (formato correcto)
@st.cache_data(ttl=30)
def cargar_hoja_publica(sheet_url):
    """
    Carga una hoja pública de Google Sheets exportándola como CSV.
    La URL debe ser la vista de navegador con gid al final.
    """
    try:
        # Extraer doc_id y gid de la URL
        parts = sheet_url.split("/")
        doc_id = parts[5]
        gid = sheet_url.split("gid=")[-1]
        export_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"
        df = pd.read_csv(export_url)
        return df
    except Exception as e:
        print(f"Error cargando hoja pública: {e}")
        return pd.DataFrame()

# Opción 2: Leer hoja privada de Google Sheets usando credenciales
@st.cache_data(ttl=30)
def cargar_hoja_privada(sheet_name, worksheet_name, cred_path="credenciales.json"):
    """
    Carga una hoja privada de Google Sheets autenticándose con una cuenta de servicio.
    - sheet_name: nombre del documento.
    - worksheet_name: nombre de la pestaña/hoja.
    - cred_path: ruta al archivo JSON de credenciales.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name)
        worksheet = sheet.worksheet(worksheet_name)
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        return df
    except Exception as e:
        print(f"Error cargando hoja privada: {e}")
        return pd.DataFrame()
    
#https://docs.google.com/spreadsheets/d/1J-CZASJTrqhLXlmkFY_DavyG2aQ5HBaS/edit?usp=sharing&ouid=105878547600010956430&rtpof=true&sd=true
# Cargamos los datos de las hojas públicas

## Configuración centralizada del libro de Google Sheets
#SHEET_ID = "1mS9mpj5ubrYHbKg707EVMxHVhV6H1gEB50DoM5DK4VM" #Hoja ejemplo
#
#GIDS = {
#    "notas": "0",
#    "recuperaciones": "451207441",
#    "comparativos": "357866733"
#}
#
## guardar en session state para evitar recargas innecesarias
#if 'SHEET_ID' not in st.session_state:
#    st.session_state.SHEET_ID = SHEET_ID
#if 'GIDS' not in st.session_state:
#    st.session_state.GIDS = GIDS
#
#SHEET_ID_PM = "1J-CZASJTrqhLXlmkFY_DavyG2aQ5HBaS" #Hoja Planila Master IEOS
#GIDS_PM = {
#    "notas": "0",
#    "notas_701_P1": "1779130150"
#}
#
## guardar en session state para evitar recargas innecesarias
#if 'SHEET_ID_PM' not in st.session_state:
#    st.session_state.SHEET_ID_PM = SHEET_ID_PM
#if 'GIDS_PM' not in st.session_state:
#    st.session_state.GIDS_PM = GIDS_PM

def construir_url(SHEET_ID,gid):
    try:
        return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={gid}#gid={gid}"
    
    except Exception as e:
        print(f"Error construyendo URL: {e}")
        return None
    
@st.cache_data(ttl=60)
def load_hoja_google(SHEET_ID, GIDS, worksheet_name):
    """
    Carga una hoja de Google Sheets usando el ID del documento y el GID de la hoja.
    """
    url = construir_url(SHEET_ID, GIDS[worksheet_name])
    df = cargar_hoja_publica(url)
    df.columns = df.columns.str.strip()

    return df

@st.cache_data(ttl=60)
def load_planilla_google(SHEET_ID ,GIDS,periodo="1"):
    url = construir_url(SHEET_ID, GIDS[f'notas_701_P{periodo}'])
    df = cargar_hoja_publica(url)
    df.rename(columns={
        'Nombre_estudiante': 'NOMBRE_ESTUDIANTE'
    }, inplace=True)
    #df["DOCUMENTO"] = df["DOCUMENTO"].astype(str)
    
    return df

@st.cache_data(ttl=60)
def load_notas_google(SHEET_ID ,GIDS):
    url = construir_url(SHEET_ID, GIDS["notas"])
    df = cargar_hoja_publica(url)
    print(df.columns)
    df["DOCUMENTO"] = df["DOCUMENTO"].astype(str)
    
    return df

#@st.cache_data(ttl=60)
#def load_notas_google():
#    url = construir_url(GIDS["notas"])
#    df = cargar_hoja_publica(url)
#    df["DOCUMENTO"] = df["DOCUMENTO"].astype(str)
#    return df

@st.cache_data(ttl=60)
def load_recuperaciones_google(SHEET_ID, GIDS):
    url = construir_url(SHEET_ID, GIDS["recuperaciones"])
    df = cargar_hoja_publica(url)
    df["DOCUMENTO"] = df["DOCUMENTO"].astype(str)
    return df

@st.cache_data(ttl=60)
def load_comparativos_google(SHEET_ID, GIDS):
    url = construir_url(SHEET_ID, GIDS["comparativos"])
    df = cargar_hoja_publica(url)
    df["DOCUMENTO"] = df["DOCUMENTO"].astype(str)
    return df

############################### Notas de grupo ##########################################

# === PARÁMETROS ===
#grupo = "701"
#periodo = "1"
#ruta_notas = "O:/Mi unidad/Orestes/Planilla_Master_IEOS.xlsx"
#ruta_estudiantes = "O:/Mi unidad/Notebooks/Listas_estudiantes_oreste.xlsx"



# === Carga de datos y limpieza inicial ===
@st.cache_data(ttl=60)
def cargar_datos_grupo(ruta_notas, grupo, periodo="1", SHEET_ID="SHEET_ID_PM" , GIDS = "GIDS_PM"):
    try:
        # Cargar el DataFrame desde el archivo Excel
        df = pd.read_excel(ruta_notas, sheet_name=f"G{grupo}_P{periodo}", engine='openpyxl')
    except:
        # Si falla, intentar cargarlo como CSV
        df = load_planilla_google(SHEET_ID, GIDS,periodo)
    df.columns = df.columns.str.strip()
    df.rename(columns={
        'Nombre_estudiante': 'NOMBRE_ESTUDIANTE'
    }, inplace=True)
    df["Matricula"] = df["Matricula"].astype(str).str.strip()
    return df

def obtener_diccionario_actividades(df):
    index_campo = df[df['Matricula'] == "Campo"].index[0]
    df_actividades = df.iloc[index_campo:, :2].copy()
    df_actividades.columns = df_actividades.iloc[0]
    df_actividades = df_actividades[1:].dropna()
    df_actividades['Campo'] = df_actividades['Campo'].str.replace('_', '.')
    return df_actividades.set_index('Campo')['Nombre actividad'].to_dict(), index_campo

def obtener_columnas_validas(mi_diccionario):
    """
    Filtra las claves del diccionario de actividades para obtener únicamente las columnas válidas,
    deteniéndose cuando encuentre la primera actividad vacía, y agregando siempre las actividades fijas.
    """
    #fijas_inicial = ['Matricula', 'Nombre_estudiante']
    fijas_final = ['3.1', '3.2', '4.1', '4.2']
    columnas_validas = [
        clave for clave, valor in mi_diccionario.items()
        if isinstance(valor, str) and valor.strip() != "" and clave not in fijas_final
    ]

    #columnas_validas.extend(fijas)  # asegurar inclusión de las fijas
    return columnas_validas + fijas_final

def formar_pares(columnas_validas):
    """
    Forma pares (col1, col2) dentro del mismo grupo, recorriendo de dos en dos.
    Evita solapamientos y asegura que cada par esté bien formado.
    """
    pares = []
    i = 0
    while i < len(columnas_validas) - 1:
        actual = columnas_validas[i]
        siguiente = columnas_validas[i + 1]

        grupo_actual = actual.split('.')[0]
        grupo_siguiente = siguiente.split('.')[0]

        if grupo_actual == grupo_siguiente:
            pares.append((actual, siguiente))
            i += 2  # avanzar de dos en dos si se forma un par válido
        else:
            i += 1  # avanzar solo uno si no forma par válido

    return pares

def limpiar_y_seleccionar_notas(df, index_campo, mi_diccionario):
    df = df.iloc[:int(index_campo) - 2].copy()
    #columnas = ['Matricula', 'Nombre_estudiante'] + [f'{i}.{j}' for i in range(1, 5) for j in range(1, 3) if not (i == 3 and j == 2)]
    columnas = ['Matricula', 'NOMBRE_ESTUDIANTE'] + obtener_columnas_validas(mi_diccionario)
    columnas = [c for c in columnas if c in df.columns]  # evitar errores
    df1 = df[columnas].copy()
    df1.replace(0, 1, inplace=True)
    df1.fillna(0.2, inplace=True)
    return df1

def cargar_estudiantes(ruta_estudiantes, sheet_name="All_COL"):
    """
    Carga el DataFrame de estudiantes desde un archivo Excel.
    Asegura que las columnas 'MATRICULA' y 'DOCUMENTO' sean del tipo string.
    """
    # Cargar el DataFrame desde el archivo Excel
    try:
        df_estudiantes = pd.read_excel(ruta_estudiantes, sheet_name=sheet_name, engine='openpyxl')
    except:
        df_estudiantes = cargar_hoja_publica(ruta_estudiantes)

    df_estudiantes.rename(columns={
        'ESTUDIANTE': 'NOMBRE_ESTUDIANTE'
    }, inplace=True)

    # Eliminamos filas con MATRÍCULA vacía
    df_estudiantes.dropna(subset=['MATRICULA'], inplace=True)

    # Covertir columna a tipo int
    df_estudiantes["MATRICULA"] = df_estudiantes.MATRICULA.astype(int)

    #df_estudiantes["ID"] = df_estudiantes.ID.astype(str)
    df_estudiantes["MATRICULA"] = df_estudiantes.MATRICULA.astype(str)
    df_estudiantes["DOCUMENTO"] = df_estudiantes.DOCUMENTO.astype(str)

    #df_estudiantes['MATRICULA'] = df_estudiantes['MATRICULA'].astype(str).str.strip()
    #df_estudiantes['DOCUMENTO'] = df_estudiantes['DOCUMENTO'].astype(str).str.strip()
    return df_estudiantes

def agregar_documento(df1, df_estudiantes):
    #df_estudiantes["MATRICULA"] = df_estudiantes["MATRICULA"].astype(str)
    #df_estudiantes["DOCUMENTO"] = df_estudiantes["DOCUMENTO"].astype(str)
    dict_doc = df_estudiantes.set_index("MATRICULA")['DOCUMENTO'].to_dict()
    idx = df1.columns.get_loc('NOMBRE_ESTUDIANTE')
    df1.insert(idx, 'DOCUMENTO', df1['Matricula'].map(dict_doc))
    return df1

def comparar_y_promediar(df1, columnas_pares):
    columnas_pares.pop(-2)  # Eliminar el penúltimo elemento de la lista si es necesario
    for col1, col2 in columnas_pares:
        df1[[col1, col2]] = df1[[col1, col2]].apply(pd.to_numeric, errors='coerce')
        df1[col2] = df1[[col1, col2]].max(axis=1)
        df1[f'{col1}_prom'] = df1[[col1, col2]].mean(axis=1)
    return df1

def preparar_df2(df1, columnas_validas, pares):
    """
    Construye dinámicamente las columnas finales del df2 con base en las columnas válidas
    y los pares definidos para los promedios.
    """
    columnas_finales = ['Matricula', 'DOCUMENTO', 'NOMBRE_ESTUDIANTE']
    ya_agregadas = set()

    for col in columnas_validas:
        # Si la columna es la primera de un par, agregar la versión con _prom
        if any(col == p[0] for p in pares):
            col_prom = f"{col}_prom"
            if col_prom in df1.columns:
                columnas_finales.append(col_prom)
                ya_agregadas.add(col)
                ya_agregadas.add(next(p[1] for p in pares if p[0] == col))
        elif col not in ya_agregadas:
            # Si no forma parte de ningún par (como 3.1, 3.2), usarla directamente
            if col in df1.columns:
                columnas_finales.append(col)

    return df1[columnas_finales].copy()

def transformar_melt(df2, mi_diccionario, dict_orden_act, dict_orden_proc, periodo):
    df2.rename(columns={k+'_prom':k for k in dict_orden_act.keys() if k+'_prom' in df2.columns}, inplace=True)
    df_melt = pd.melt(df2, id_vars=['Matricula', 'DOCUMENTO', 'NOMBRE_ESTUDIANTE'],
                      var_name='Tarea', value_name='Calificación')
    df_melt['ACTIVIDAD'] = df_melt['Tarea'].map(mi_diccionario)
    df_melt['ORDEN_ACT'] = df_melt['Tarea'].map(dict_orden_act)
    df_melt['PROCESO'] = df_melt['Tarea'].apply(agregar_dimension)
    df_melt['ORDEN_PROCESO'] = df_melt['PROCESO'].map(dict_orden_proc)
    collator = Collator()
    df_melt['Sort_Key'] = df_melt['NOMBRE_ESTUDIANTE'].apply(collator.sort_key)

    df_grouped = df_melt.groupby([
        'PROCESO', 'Matricula', 'DOCUMENTO', 'NOMBRE_ESTUDIANTE',
        'ORDEN_ACT', 'Tarea', 'ACTIVIDAD', 'Sort_Key'
    ]).agg(Calificación=('Calificación', 'mean')).reset_index()
    df_grouped = df_grouped.sort_values(['Sort_Key', 'ORDEN_ACT']).drop(columns=['Sort_Key'])
    df_grouped.insert(8, 'PERIODO', [periodo]*df_grouped.shape[0])
    return df_grouped

def agregar_dimension(tarea):
    if tarea.startswith('1'):
        return 'HACER'
    elif tarea.startswith('2'):
        return 'SABER'
    elif tarea.startswith('3'):
        return 'AUTOEVALUACIÓN'
    elif tarea.startswith('4'):
        return 'PRUEBA_PERIODO'
    return None
 
