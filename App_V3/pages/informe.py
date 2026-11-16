import streamlit as st

from components.alerts import render_empty_state, render_error_box, render_info_box
from pages.consulta_notas import (_seleccionar_estudiante_admin
                                  ,_mostrar_resumen_usuario_admin
)
from services.informe_service import (
    obtener_informe_usuario,
    consolidar_balance_vp,
    informe_año
)
from components.visual_helpers import mostrar_tabla_informe_3p


def _mostrar_encabezado() -> None:
    """
    Renderiza el encabezado principal de la página.
    """
    st.title("Informe académico")
    st.caption(
        "Consulta el resumen académico disponible para el estudiante en el periodo seleccionado."
    )


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


def _mostrar_informe(df_informe) -> None:
    """
    Muestra el informe académico en formato tabular.
    """
    st.subheader("Resumen académico")
    st.dataframe(df_informe, use_container_width=True, hide_index=True)


def render_informe() -> None:
    """
    Renderiza la página de informe académico.
    """

    rol = st.session_state.get("rol", "estudiante")

    _mostrar_encabezado()

    st.markdown(""" 
            **¡TENER PRESENTE!**
    
            **El informe acá presentado NO ES DEFINITIVO, es con la información disponible en el sistema institucional hasta el día 15 de noviembre a la 1:18 pm.**

            **El sistema se cerrara el proximo martes 17 de noviembre a las 12 del medio día**. Los cambios que se generen serán producto de las actualizaciones que realicen los maestros de cada área
            """)
    
    st.divider()

    if rol == "admin":
            matricula_consultada, nombre_consultado = _seleccionar_estudiante_admin()

    else:
            matricula_consultada = st.session_state.get("matricula")
            nombre_consultado = st.session_state.get("nombre")
    
            if not matricula_consultada:
                render_info_box("No hay un usuario autenticado en la sesión.")
                return

    col1, col2 = st.columns(2)

    with col1:
        # Leyenda de colores con emoji para desempeño
        st.markdown("""
        **Leyenda de colores para desempeño**

        🟩 **Verde**: Desempeño superior (Su)         
        🟨 **Amarillo**: Desempeño alto  (Al)       
        🟧 **Naranja**: Desempeño basico (Ba)      
        🟥 **Rojo**: Desempeño bajo (Bj)
        """)
    with col2:
        # Leyenda de colores con emoji para estado
        st.markdown(""" 
        **¡INPORTANTE!**

        De acuerdo al sistema de evaluación institucional
        **el año se reprueba si el estudiante tiene tres o más áreas reprobadas para el año.**
        """)

    #matricula_consultada, nombre_consultado = _seleccionar_estudiante_admin()
    #_mostrar_resumen_usuario()
    st.divider()

    usuario = st.session_state.get("usuario")
    grupo = st.session_state.get("grupo","801")
    #matricula = st.session_state.get("matricula_consultada") if "matricula_consultada" in st.session_state else st.session_state.get("matricula")
    periodo = st.session_state.get("periodo")
    ano = st.session_state.get("anio_academico", "2026")

    if not usuario:
        render_info_box("No hay un usuario autenticado en la sesión.")
        return

    if not grupo:
        render_error_box("No fue posible identificar el grupo asociado al usuario.")
        return

    if not periodo:
        render_error_box("No fue posible identificar el periodo activo.")
        return

    try:
        df_informe = obtener_informe_usuario(
            documento=usuario,
            grupo=grupo,
            periodo=periodo,
        )
    except Exception as exc:
        render_error_box(f"Ocurrió un error al consultar el informe académico: {exc}")
        return

    #if df_informe is None or df_informe.empty:
    #    render_empty_state(
    #        title="No hay informe disponible",
    #        message=(
    #            "Aún no se encontró información de informe académico "
    #            "para este estudiante en el periodo seleccionado."
    #        ),
    #    )

    df_est, df_est_materia, df_materias = consolidar_balance_vp(grupo, ano)

    D = informe_año(df_est_materia, matricula_consultada)

    #st.dataframe(df_est_materia)

    return mostrar_tabla_informe_3p(D)#st.dataframe(D, use_container_width=True, hide_index=True)