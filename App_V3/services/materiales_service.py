from __future__ import annotations

import pandas as pd
import streamlit as st

from services.google_sheets_service import cargar_materiales
from utils.normalizers import normalizar_columnas_dataframe, normalizar_grupo


COLUMNAS_MATERIALES_PRIORIZADAS = [
    "titulo",
    "descripcion",
    "grupo",
    "anio_academico",
    "materia",
    "enlace",
    "archivo",
    "fecha",
]


def _preparar_base_materiales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base de materiales.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = normalizar_columnas_dataframe(df).copy()

    if "grupo" in df.columns:
        df["grupo"] = df["grupo"].apply(normalizar_grupo)

    if "anio_academico" not in df.columns and "anio" in df.columns:
        df["anio_academico"] = df["anio"]

    if "año_academico" in df.columns and "anio_academico" not in df.columns:
        df["anio_academico"] = df["año_academico"]

    return df


def _filtrar_por_grupo_y_anio(
    df: pd.DataFrame,
    grupo: str,
    anio_academico: str | None = None,
) -> pd.DataFrame:
    """
    Filtra materiales por grupo y, si existe la columna, por año académico.
    """
    if df.empty:
        return df

    grupo = normalizar_grupo(grupo)
    df_filtrado = df.copy()

    if "grupo" in df_filtrado.columns:
        df_filtrado = df_filtrado.loc[df_filtrado["grupo"] == grupo].copy()

    if anio_academico and "anio_academico" in df_filtrado.columns:
        df_filtrado = df_filtrado.loc[
            df_filtrado["anio_academico"].astype(str) == str(anio_academico)
        ].copy()

    return df_filtrado.reset_index(drop=True)


def _seleccionar_columnas_visibles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona columnas prioritarias para visualización.
    Si no están todas, conserva las disponibles.
    """
    if df.empty:
        return df

    columnas_visibles = [col for col in COLUMNAS_MATERIALES_PRIORIZADAS if col in df.columns]

    if not columnas_visibles:
        columnas_visibles = df.columns.tolist()

    return df[columnas_visibles].copy()


def _formatear_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Embellece los nombres de columnas para mostrar en pantalla.
    """
    if df.empty:
        return df

    df = df.copy()
    df.columns = [col.replace("_", " ").strip().title() for col in df.columns]
    return df


@st.cache_data(ttl=120, show_spinner=False)
def obtener_materiales_usuario(grupo: str, anio_academico: str | None = None) -> pd.DataFrame:
    """
    Obtiene los materiales disponibles para el grupo del usuario.
    """
    if not grupo:
        return pd.DataFrame()

    df_materiales = cargar_materiales()
    df_materiales = _preparar_base_materiales(df_materiales)

    if df_materiales.empty:
        return pd.DataFrame()

    df_materiales = _filtrar_por_grupo_y_anio(
        df_materiales,
        grupo=grupo,
        anio_academico=anio_academico,
    )

    if df_materiales.empty:
        return pd.DataFrame()

    df_materiales = _seleccionar_columnas_visibles(df_materiales)
    df_materiales = _formatear_columnas(df_materiales)

    return df_materiales.reset_index(drop=True)

def mostrar_actividades() -> None:
    """
    Función principal para mostrar las actividades en la página.
    """
    st.title("Actividades")

    grupo = st.session_state.get("grupo")
    anio_academico = st.session_state.get("anio_academico")
    periodo = st.session_state.get("periodo")

    
    if not grupo:
        st.warning("No se ha identificado tu grupo. Por favor, asegúrate de que tu perfil esté completo.")
        return
    
    elif grupo in ["801"]:
        st.info("Los materiales para el periodo P1 estarán disponibles próximamente.")

        if periodo == "P1":
            ##############################################################
            st.markdown("###### - Taller de activación: números enteros")
            try:
                with open("App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: tablas de frecuencia")
            try:
                with open("App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: Razones")
            try:
                with open("App_V3/docs/actividades/Razones G_ASF7B.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Razones G_ASF7B.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Razones G_ASF7B.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Razones G_ASF7B.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: Proporciones")
            try:
                with open("App_V3/docs/actividades/Proporciones G_ASF7B.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Proporciones G_ASF7B.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Proporciones G_ASF7B.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Proporciones G_ASF7B.pdf",
                        mime="application/pdf"
                    )
            ###############################################################
            st.markdown("###### - 📝 Consulta conjuntos numéricos")
            descripción = "Consultar por qué se usan las letras N, Z, Q, R para representar diferentes conjuntos numéricos. Resolver en el cuaderno."
            st.write(descripción)
            ##############################################################
            st.markdown("###### - Expresiones algebraicas")
            descripción = "Se debe tener en el cuaderno el resumen de la pagina 59, " \
            "luego se deben escribir y resolver las actividades 72 a 88 de la guía adjunta."
            st.write(descripción)
            try:
                with open("App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            return st.write("Acá vamos a mostrar un mensaje bonito con un ícono de construcción 🚧")
    ################################################################################################################################    
    elif grupo == "802":
        st.info("Los materiales para el periodo P1 estarán disponibles próximamente.")

        if periodo == "P1":
            ##############################################################
            st.markdown("###### - Taller de activación: números enteros")
            try:
                with open("App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: tablas de frecuencia")
            try:
                with open("App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ubicación de números irracionales en la recta numérica")
            try:
                with open("App_V3/docs/actividades/Actividad Ubicacion de irracionales.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad Ubicacion de irracionales.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad Ubicacion de irracionales.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad Ubicacion de irracionales.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Expresiones algebraicas")
            descripción = "Se debe tener en el cuaderno el resumen de la pagina 59, " \
            "luego se deben escribir y resolver las actividades 72 a 88 de la guía adjunta."
            st.write(descripción)
            try:
                with open("App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            return
    #################################################################################################################################
    elif grupo == "803":
        st.info("Los materiales para el periodo P1 estarán disponibles próximamente.")

        if periodo == "P1":
            ##############################################################
            st.markdown("###### - Taller de activación: números enteros")
            try:
                with open("App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: Razones")
            try:
                with open("App_V3/docs/actividades/Razones G_ASF7B.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Razones G_ASF7B.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Razones G_ASF7B.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Razones G_ASF7B.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: Conjuntos numéricos")
            try:
                with open("App_V3/docs/actividades/Actividad conjuntos numericos.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad conjuntos numericos.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad conjuntos numericos.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad conjuntos numericos.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: tablas de frecuencia")
            try:
                with open("App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Expresiones algebraicas")
            descripción = "Se debe tener en el cuaderno el resumen de la pagina 59, " \
            "luego se deben escribir y resolver las actividades 72 a 88 de la guía adjunta."
            st.write(descripción)
            try:
                with open("App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            return 
    ################################################################################################################################
    elif grupo == "804":
        st.info("Los materiales para el periodo P1 estarán disponibles próximamente.")

        if periodo == "P1":
            ##############################################################
            st.markdown("###### - Taller Diagnóstico numeros enteros")
            try:
                with open("App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/TALLER DE ACTIVACIÓN ENTEROS.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="TALLER DE ACTIVACIÓN ENTEROS.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: Conjuntos numéricos")
            try:
                with open("App_V3/docs/actividades/Actividad conjuntos numericos.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad conjuntos numericos.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad conjuntos numericos.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad conjuntos numericos.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Ficha: tablas de frecuencia")
            try:
                with open("App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A5_8.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Expresiones algebraicas")
            descripción = "Se debe tener en el cuaderno el resumen de la pagina 59, " \
            "luego se deben escribir y resolver las actividades 72 a 88 de la guía adjunta."
            st.write(descripción)
            try:
                with open("App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/GuiaExpresionesAlgebraicas51_59.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Guía](#)",
                        data=file,
                        file_name="GuiaExpresionesAlgebraicas51_59.pdf",
                        mime="application/pdf"
                    )
            return
    elif grupo == "805":
        st.info("Los materiales para el periodo P1 estarán disponibles próximamente.")

        if periodo == "P1":
            ##############################################################
            st.markdown("###### - Actividad: tablas de frecuencia")
            try:
                with open("App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A4_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A4_8.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad_tablas_frecuencia_ASF7_B4_A4_8.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad_tablas_frecuencia_ASF7_B4_A4_8.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Actividad: tablas distribución de frecuencia")
            try:
                with open("App_V3/docs/actividades/Actividad tablas distribución de frecuencia.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad tablas distribución de frecuencia.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad tablas distribución de frecuencia.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad tablas distribución de frecuencia.pdf",
                        mime="application/pdf"
                    )
            ##############################################################
            st.markdown("###### - Actividad: datos agrupados")
            try:
                with open("App_V3/docs/actividades/Actividad Datos Agrupados.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad Datos Agrupados.pdf",
                        mime="application/pdf"
                    )
            except:
                with open("D:/Repositorios/Notas_Master/App_V3/docs/actividades/Actividad Datos Agrupados.pdf", "rb") as file:
                    st.download_button(
                        label="- [📥 Descargar Actividad](#)",
                        data=file,
                        file_name="Actividad Datos Agrupados.pdf",
                        mime="application/pdf"
                    )
            return
    try:
        df_materiales = obtener_materiales_usuario(grupo=grupo, anio_academico=anio_academico)
    except Exception as exc:
        st.error(f"Ocurrió un error al cargar los materiales: {exc}")
        return

    if df_materiales.empty:
        st.info("No hay materiales disponibles para tu grupo en este momento.")
        return

    st.write("Materiales disponibles:")

def mostrar_recursos() -> None:
    """
    Función principal para mostrar los recursos en la página.
    """
    st.title("Recursos")
    st.info("En esta sección podrás encontrar recursos adicionales para el fortalecimiento del aprendizaje.")
    if not st.session_state.get("grupo"):
        st.warning("No se ha identificado tu grupo. Por favor, asegúrate de que tu perfil esté completo.")
        return
    
    elif st.session_state.get("grupo") == "801":

        if st.session_state.get("periodo") == "P1":
            ##############################################################
            # agregar recurso en formato de lista con íconos
            st.markdown("""## - Expresiones algebraicas
- [🔗 Video: Introducción](https://youtu.be/UJiUu8-fYgI?si=EnL4eo5YcEr_7Zd8,v=VIDEO_ID)
    - expresiones algebraicas definición
    - Términos semejantes
    - Suma de expresiones algebraicas
- [🔗 Video: Términos algebraicos y sus partes](https://youtu.be/0BxsA64gE4c?si=oDxrs93fCGKX1x-5,v=VIDEO_ID)
    - Término algebraico
- [🔗 Video: ¿Qué son los Términos Semejantes?](https://youtu.be/VCWhGoTiegw?si=mVo0Nifx1R6ie9vG,v=VIDEO_ID)
    - Términos semejantes
- [🔗 Video: Reducción de términos semejantes](https://youtu.be/Ge0qmA7-VXo?si=KOIjx87vKVZ4IRJH,v=VIDEO_ID)
    - Términos semejantes
- [🔗 Video: Casificación de expresiones algebraicas](https://youtu.be/YvpBCJQIrXY?si=S_wbk1SWuUgXET8W,v=VIDEO_ID)
    - Término algebraico
    - Monomio
    - Binomio
    - Trinomio
    - Polinomio
- [🔗 Video: Suma y resta de monomios](https://youtu.be/N3vD22wJfyw?si=N6s8RVtFyNFzYAwa,v=VIDEO_ID)
    - Suma y resta de monomios""")


            
    