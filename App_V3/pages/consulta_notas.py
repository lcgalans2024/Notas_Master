import streamlit as st

from components.alerts import render_empty_state, render_error_box, render_info_box
from components.visual_helpers import mostrar_tabla_notas
from utils.dataframe_utils import (seleccionar_columnas_existentes, 
                                   verificar_columnas_requeridas, 
                                   renombrar_columnas_si_existen, 
                                   merge_seguro,
                                   melt_seguro,
                                   
                                   )
from services.google_sheets_service import obtener_debug_notas
from services.google_sheets_service import obtener_debug_notas, cargar_notas_debug
"""Se agregan funciones:
_detectar_actividades,
_diccionario_actividades,
_obtener_columnas_validas,
_preparar_base_notas,
_filtrar_notas_columnas_validas
 para depuración en la carga de notas."""
from services.notas_service import obtener_notas_usuario, melt_notas_usuario, _detectar_actividades,_diccionario_actividades,_obtener_columnas_validas, _preparar_base_notas, _filtrar_notas_columnas_validas


def _mostrar_encabezado() -> None:
    """
    Renderiza el encabezado de la página.
    """
    st.title("Consulta de notas")
    st.caption("Consulta las calificaciones registradas para el periodo seleccionado.")


def _mostrar_resumen_usuario() -> None:
    """
    Muestra información básica del estudiante autenticado.
    """
    nombre = st.session_state.get("nombre", "Usuario")
    grupo = st.session_state.get("grupo", "No definido")
    periodo = st.session_state.get("periodo", "No definido")
    anio = st.session_state.get("anio_academico", "No definido")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Estudiante", nombre)

    with col2:
        st.metric("Grupo", grupo)

    with col3:
        st.metric("Periodo", f"{periodo} · {anio}")


def _mostrar_tabla_notas(df_notas) -> None:
    """
    Muestra la tabla principal de notas.
    """
    st.subheader("Detalle de calificaciones")
    st.dataframe(df_notas, use_container_width=True, hide_index=True)


def render_consulta_notas() -> None:
    """
    Renderiza la página de consulta de notas del usuario autenticado.
    """
    _mostrar_encabezado()
    _mostrar_resumen_usuario()
    st.divider()

    usuario = st.session_state.get("usuario")
    matricula = st.session_state.get("matricula")
    grupo = st.session_state.get("grupo")
    periodo = st.session_state.get("periodo")

    if not usuario:
        render_info_box("No hay un usuario autenticado en la sesión.")
        return

    if not grupo:
        render_error_box("No fue posible identificar el grupo asociado al usuario.")
        return

    if not periodo:
        render_error_box("No fue posible identificar el periodo activo.")
        return
    #########################################################################
    with st.expander("Depuración de carga de notas"):
        st.write("Usuario:", usuario)
        st.write("Matrícula:", matricula)
        st.write("Grupo:", grupo)
        st.write("Periodo:", periodo)

        debug_info = obtener_debug_notas(grupo=grupo, periodo=periodo)
        st.write("Resolución de hoja:", debug_info)

        if debug_info["existe_configuracion"]:
            df_debug = cargar_notas_debug(grupo=grupo, periodo=periodo)
            df_debug_preparado = _preparar_base_notas(df_debug)
            st.write("Dimensión:", df_debug.shape)
            st.write("Columnas:", df_debug.columns.tolist())
            index_campo, df_actividades = _detectar_actividades(df_debug_preparado)
            st.write("Índice de actividades detectado:", index_campo)
            st.write("Actividades detectadas:", df_actividades)
            dict_actividades = _diccionario_actividades(df_debug_preparado)
            st.write("Diccionario de actividades:", dict_actividades.items())
            columnas_validas = _obtener_columnas_validas(df_debug_preparado)[0]
            st.write("Columnas válidas:", columnas_validas)
            st.dataframe(df_debug.head(), use_container_width=True)
            st.write("Columnas antes de preparación:", df_debug.columns.tolist())
            st.dataframe(df_debug_preparado.head(), use_container_width=True)
            st.write("Columnas después de preparación:", df_debug_preparado.columns.tolist())
            df_notas_filtradas_col = _filtrar_notas_columnas_validas(df_debug_preparado)[0]
            #st.write("Columnas filtradas:", df_notas_filtradas_col.columns.tolist())
            st.dataframe(df_notas_filtradas_col.head(), use_container_width=True)
    ##########################################################################
    try:
        df_notas = melt_notas_usuario(
            matricula=matricula,
            grupo=grupo,
            periodo=periodo,
        )
    except Exception as exc:
        render_error_box(f"Ocurrió un error al consultar las notas: {exc}")
        return

    if df_notas is None or df_notas.empty:
        render_empty_state(
            title="No hay notas disponibles",
            message="Aún no se encontraron calificaciones registradas para este estudiante en el periodo seleccionado.",
        )
        return


    tabla_notas = seleccionar_columnas_existentes(df_notas, ["Proceso","Actividad", "Calificación"])

    _mostrar_tabla_notas(tabla_notas)

    mostrar_tabla_notas(tabla_notas)