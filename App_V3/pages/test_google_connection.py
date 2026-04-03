import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


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

    except Exception as exc:
        st.error(f"Error de conexión: {exc}")