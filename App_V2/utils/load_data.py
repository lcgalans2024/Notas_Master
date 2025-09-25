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

def construir_url(SHEET_ID,gid):
    try:
        return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={gid}#gid={gid}"
    
    except Exception as e:
        print(f"Error construyendo URL: {e}")
        return None
    
@st.cache_data(ttl=60)
def load_hoja_google_consolidados(SHEET_ID, GIDS, worksheet_name):
    """
    Carga una hoja de Google Sheets usando el ID del documento y el GID de la hoja.
    """
    url = construir_url(SHEET_ID, GIDS[worksheet_name])
    df = cargar_hoja_publica(url)

    return df
    
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
def load_planilla_google(SHEET_ID ,GIDS, grupo ="701",periodo="1"):
    url = construir_url(SHEET_ID, GIDS[f'notas_{grupo}_P{periodo}'])
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

# === Carga de datos y limpieza inicial ===
@st.cache_data(ttl=60)
def cargar_datos_grupo(ruta_notas, grupo, periodo="1", SHEET_ID="SHEET_ID_PM" , GIDS = "GIDS_PM"):
    try:
        # Cargar el DataFrame desde el archivo Excel
        df = pd.read_excel(ruta_notas, sheet_name=f"G{grupo}_P{periodo}", engine='openpyxl')
    except:
        # Si falla, intentar cargarlo como CSV
        df = load_planilla_google(SHEET_ID, GIDS, grupo,periodo)
    df.columns = df.columns.str.strip()
    df.rename(columns={
        'Nombre_estudiante': 'NOMBRE_ESTUDIANTE'
    }, inplace=True)
    df["Matricula"] = df["Matricula"].astype(str).str.strip()
    df = df.drop(index=0).reset_index(drop=True)
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
    # Eliminar segunda fila
    #df = df.drop(index=0).reset_index(drop=True)
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

    return df_estudiantes

def agregar_documento(df1, df_estudiantes):
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
    df_melt['Sort_Key'] = df_melt['NOMBRE_ESTUDIANTE'].astype(str).apply(collator.sort_key)

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

# Procesamiento de consolidados
@st.cache_data(ttl=60)
def procesar_consolidados(df):
    """
    Carga los datos consolidados desde Google Sheets.
    """
    df1 = df.copy()
    # Eliminar columnas vacias
    df1.dropna(axis=1, how='all', inplace=True)
    # Eliminar columnas que contienen "Unnamed"
    df2 = df1.loc[:, ~df1.columns.str.contains('Unnamed')]
    #try:
    #   # eliminar fila por indice 26, 40 y 41 si existen
    #   df2 = df2.drop(index=[2,
    #                         16,
    #                         #24,
    #                         27,
    #                         30,
    #                         36,
    #                         42
    #                         ]).reset_index(drop=True)
    #except:
    #   pass
    #df2 = df2.drop(index=[26,35,41]).reset_index(drop=True)
    # obtener indice de fila de No aprobados en la columna Ord
    ind_max = df2[df2['Ord'] == "No aprobados"].index[0]
    # Eliminar la primera fila
    df3 = df2.iloc[1:ind_max, :].copy()
    df3 = df3[df3['Est'] != 'C']
    df3.drop(columns=['Est'], inplace=True)
    df3.drop(columns=['COM'], inplace=True)
    # Cambiar Matricula y documento a integer
    try:
        df3["Nro Documento"] = df3["Nro Documento"].astype(int)
    except:
        pass
    # Cambiar a str
    df3["Matricula"] = df3.Matricula.astype(str)
    df3["Nro Documento"] = df3["Nro Documento"].astype(str)
    # Corregir conteo no aprobadas
    df3['No aprobados'] = df3['No aprobados'].astype(int)
    df3['No aprobados'] = df3['No aprobados']-1
    # Renombrar columnas
    df3.rename(columns={'Nombre completo':'Nombre_estudiante'
                  ,'Nro Documento':'DOCUMENTO'
                  ,'Total faltas':'Total_faltas'
                  ,'No aprobados':'No_Aprobados'
                   } , inplace=True)
    
    # Derretir la tabla
    melted_df = pd.melt(df3, id_vars=['Ord', 'Matricula', 'DOCUMENTO', 'Nombre_estudiante', 'Total_faltas', 'No_Aprobados'], var_name='MATERIA', value_name='NOTA')
    melted_df.sort_values(['Nombre_estudiante'], inplace=True)

    # Mapear MATERIA con el diccionario materias
    melted_df['MATERIA'] = melted_df['MATERIA'].map(st.session_state.materias)

    try:
        melted_df.loc[melted_df.NOTA.str.contains('#'), 'ESTADO'] = "S"
        melted_df.NOTA = melted_df.NOTA.str.replace('#', '', regex=False)
    except:
        pass

    melted_df.NOTA = melted_df.NOTA.astype(float)
    melted_df.loc[melted_df.NOTA < 3.0, 'ESTADO'] = "R"
    melted_df.loc[(melted_df.NOTA >= 3.0) & (melted_df.ESTADO != 'S'), 'ESTADO'] = "G"

    # mostrar los tipos de las columnas
    #st.write("Tipos de las columnas del DataFrame de consolidados:")
    #st.table(df3.dtypes)
    return melted_df[melted_df.DOCUMENTO == st.session_state['usuario']][['MATERIA', 'NOTA', 'ESTADO']]  # Filtrar por usuario actual
 
