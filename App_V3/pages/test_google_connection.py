import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from services.notas_service import (cargar_notas, _preparar_base_notas)
from services.google_sheets_service import _obtener_sheet_id_principal, _obtener_gid_notas, construir_url_csv, leer_hoja_csv


def render_test_google_connection() -> None:
    st.title("Prueba de conexión con Google Sheets")

    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes,
        )

        client = gspread.authorize(creds)

        sheet = client.open_by_key("15ELuuOC2jO_bQzl9pDqhiMfE4EunZRw2f89p-0-dORE")
        worksheets = sheet.worksheets()

        st.success("Conexión exitosa con Google Sheets")
        st.write("Hojas encontradas:")
        st.write([ws.title for ws in worksheets])

        # Cargar notas de un grupo especifico
        grupo = st.session_state.get("grupo", "801")
        periodo = st.session_state.get("periodo", "P1")
        
        df_notas = cargar_notas(grupo, periodo)
        df_notas = _preparar_base_notas(df_notas)
        st.write(f"Notas para el grupo {grupo} y periodo {periodo}:")
        st.dataframe(df_notas)


    except Exception as exc:
        st.error(f"Error de conexión: {exc}")