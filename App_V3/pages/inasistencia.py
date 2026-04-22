import streamlit as st
import pandas as pd
from datetime import date

from components.alerts import (
    render_error_box,
    render_info_box,
    render_success_box,
)
from config.sheets_config import SHEETS_CONFIG
from services.google_write_service import (
    guardar_inasistencia,
    existe_inasistencia_registrada,
    anular_inasistencia_por_claves,
)
from services.usuarios_service import obtener_estudiantes_por_grupo_y_anio
from services.google_sheets_service import cargar_inasistencias


INASISTENCIA_SHEET_ID = SHEETS_CONFIG["sheet_id_principal"]
INASISTENCIA_WORKSHEET = "inasistencia"

AREAS_DISPONIBLES = [
    "Matemáticas",
    "Estadística",
]

SEMANAS_PERIODO = [
    "Selecciona una semana",
    "Semana 1",
    "Semana 2",
    "Semana 3",
    "Semana 4",
    "Semana 5",
    "Semana 6",
    "Semana 7",
    "Semana 8",
    "Semana 9",
    "Semana 10",
    "Semana 11",
    "Semana 12",
    "Semana 13",
    "Semana 14",
]


def _validar_acceso() -> tuple[bool, str]:
    rol = st.session_state.get("rol", "estudiante")

    if rol not in {"admin", "monitor"}:
        return False, "No tienes permisos para acceder a esta sección."

    if not st.session_state.get("grupo"):
        return False, "No se encontró un grupo activo para registrar la inasistencia."

    if not st.session_state.get("anio_academico"):
        return False, "No se encontró el año académico activo."

    return True, ""


def _cargar_estudiantes_grupo():
    grupo = st.session_state.get("grupo")
    anio = st.session_state.get("anio_academico")

    return obtener_estudiantes_por_grupo_y_anio(
        grupo=grupo,
        anio_academico=anio,
    )

def _mostrar_historial_inasistencias(grupo: str) -> None:
    """
    Muestra un historial reciente de inasistencias del grupo seleccionado.
    """
    try:
        df_inasistencias = cargar_inasistencias()
    except Exception as exc:
        render_error_box(f"No fue posible cargar el historial de inasistencias: {exc}")
        return

    if df_inasistencias is None or df_inasistencias.empty:
        render_info_box("Aún no hay registros de inasistencia.")
        return

    columnas_esperadas = {"fecha", "grupo", "matricula", "estudiante", "area", "observaciones"}
    faltantes = columnas_esperadas - set(df_inasistencias.columns)

    if faltantes:
        render_error_box(
            f"La hoja de inasistencia no contiene las columnas esperadas: {', '.join(sorted(faltantes))}"
        )
        return

    df_inasistencias = df_inasistencias.copy()
    df_inasistencias["grupo"] = df_inasistencias["grupo"].astype(str).str.strip()

    if "estado" in df_inasistencias.columns:
        df_inasistencias["estado"] = df_inasistencias["estado"].astype(str).str.strip().str.lower()
        df_inasistencias = df_inasistencias.loc[df_inasistencias["estado"] != "anulado"].copy()

    df_grupo = df_inasistencias.loc[
        df_inasistencias["grupo"] == str(grupo).strip()
    ].copy()

    if df_grupo.empty:
        render_info_box("No hay registros de inasistencia para el grupo seleccionado.")
        return

    columnas_visibles = [
        col for col in [
            "fecha",
            "periodo",
            "semana_periodo",
            "grupo",
            "matricula",
            "estudiante",
            "area",
            "observaciones",
            "registrado_por_nombre",
            "fecha_registro",
        ]
        if col in df_grupo.columns
    ]

    df_grupo = df_grupo[columnas_visibles].copy()

    if "fecha_registro" in df_grupo.columns:
        df_grupo = df_grupo.sort_values(by="fecha_registro", ascending=False)

    st.subheader("Historial reciente de inasistencias")
    st.dataframe(df_grupo.head(20), use_container_width=True, hide_index=True)

def _render_anulacion_inasistencias(grupo: str) -> None:
    """
    Permite anular registros de inasistencia del grupo activo.
    """
    try:
        df_inasistencias = cargar_inasistencias()
    except Exception as exc:
        render_error_box(f"No fue posible cargar inasistencias para anulación: {exc}")
        return

    if df_inasistencias is None or df_inasistencias.empty:
        return

    columnas_necesarias = {"fecha", "grupo", "matricula", "estudiante", "area"}
    faltantes = columnas_necesarias - set(df_inasistencias.columns)
    if faltantes:
        return

    df = df_inasistencias.copy()
    df["grupo"] = df["grupo"].astype(str).str.strip()

    if "estado" in df.columns:
        df["estado"] = df["estado"].astype(str).str.strip().str.lower()
        df = df.loc[df["estado"] != "anulado"].copy()

    df = df.loc[df["grupo"] == str(grupo).strip()].copy()

    if df.empty:
        return

    df["label"] = df.apply(
        lambda row: f"{row['fecha']} | {row['estudiante']} | {row['matricula']} | {row['area']}",
        axis=1,
    )

    st.subheader("Anular registro")
    seleccion = st.selectbox(
        "Selecciona un registro para anular",
        options=df["label"].tolist(),
        key="anular_inasistencia_select",
    )

    if st.button("Anular registro seleccionado", type="secondary"):
        fila = df.loc[df["label"] == seleccion].iloc[0]

        try:
            anular_inasistencia_por_claves(
                sheet_id=INASISTENCIA_SHEET_ID,
                worksheet_name=INASISTENCIA_WORKSHEET,
                fecha=str(fila["fecha"]),
                grupo=str(fila["grupo"]),
                matricula=str(fila["matricula"]),
                area=str(fila["area"]),
            )
            render_success_box("El registro fue anulado correctamente.")
            st.rerun()
        except Exception as exc:
            render_error_box(f"No fue posible anular el registro: {exc}")

def render_inasistencia() -> None:
    st.title("Registro de inasistencia")
    st.caption("Registra la inasistencia de estudiantes del grupo seleccionado.")

    ok, mensaje = _validar_acceso()
    if not ok:
        render_error_box(mensaje)
        return

    grupo = st.session_state.get("grupo")
    rol = st.session_state.get("rol")
    usuario = st.session_state.get("usuario")
    nombre_usuario = st.session_state.get("nombre")

    try:
        df_estudiantes = _cargar_estudiantes_grupo()
    except Exception as exc:
        render_error_box(f"No fue posible cargar los estudiantes del grupo: {exc}")
        return

    if df_estudiantes.empty:
        render_error_box("No se encontraron estudiantes para el grupo seleccionado.")
        return

    if "matricula" not in df_estudiantes.columns:
        render_error_box("La base de estudiantes no contiene la columna 'matricula'.")
        return

    df_estudiantes = df_estudiantes.copy()
    df_estudiantes["label"] = df_estudiantes.apply(
        lambda row: f"{row['nombre']} | Matrícula: {row['matricula']}",
        axis=1,
    )

    render_info_box(
        "Verifica cuidadosamente los datos antes de guardar el registro."
    )

    if st.session_state.get("reset_form_inasistencia", False):
        st.session_state["semana_periodo_inasistencia"] = "Selecciona una semana"
        st.session_state["reset_form_inasistencia"] = False

    if st.session_state.get("mostrar_balloons_inasistencia", False):
        st.balloons()
        st.session_state["mostrar_balloons_inasistencia"] = False

    with st.form("form_inasistencia"):
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            fecha = st.date_input("Fecha", value=date.today())
        with col2:
            periodo = st.text_input("Periodo", value=st.session_state.get("periodo"), disabled=True)
        with col3:
            semana_periodo = st.selectbox(
                "Semana del periodo",
                SEMANAS_PERIODO,
                key="semana_periodo_inasistencia",
                index=0,
                )
        with col4:
            if grupo == "801":
                area = st.text_input("Área", value="Todas", disabled=True)
            else:
                area = st.selectbox("Área", AREAS_DISPONIBLES)
        with col5:
            grupo_form = st.text_input("Grupo", value=str(grupo), disabled=True)

        seleccion_estudiante = st.selectbox(
            "Estudiante",
            options=df_estudiantes["label"].tolist(),
        )

        col1, col2, col3, col4 = st.columns(4)

        fila = df_estudiantes.loc[df_estudiantes["label"] == seleccion_estudiante].iloc[0]
        matricula = str(fila["matricula"])
        estudiante = str(fila["nombre"])

        with col1:
            st.text_input("Matrícula", value=matricula, disabled=True)
        with col2:
            st.text_input("Estudiante", value=estudiante, disabled=True)

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Escribe aquí la observación correspondiente...",
        )

        enviado = st.form_submit_button("Guardar registro", use_container_width=True)

    with st.expander("Ver historial de inasistencias del grupo", expanded=True):
            #df_inasistencias = cargar_inasistencias()  # Recargar para mostrar el registro recién agregado
            df_hoy = df_inasistencias.copy()
            df_hoy["fecha"] = pd.to_datetime(df_hoy["fecha"], errors="coerce").dt.date
            df_hoy = df_hoy.loc[(df_hoy["fecha"] == fecha) & (df_hoy["grupo"] == int(grupo_form))].copy()
    
            if not df_hoy.empty:
                st.dataframe(df_hoy[["fecha", "grupo", "matricula", "estudiante", "area", "observaciones"]], use_container_width=True, hide_index=True)
            else:
                st.write("No hay registros de inasistencia para hoy.")

            st.divider()
            _render_anulacion_inasistencias(grupo=str(grupo))

    if semana_periodo == "Selecciona una semana":
        render_error_box("Debes seleccionar la semana del periodo para continuar.")
        return 
     
    try:
        ya_existe = existe_inasistencia_registrada(
            sheet_id=INASISTENCIA_SHEET_ID,
            worksheet_name=INASISTENCIA_WORKSHEET,
            fecha=str(fecha),
            grupo=str(grupo),
            matricula=str(matricula),
            area=str(area),
        )
    except Exception as exc:
        render_error_box(f"Ocurrió un error al verificar registros existentes: {exc}")
        return

    if ya_existe:
        render_error_box(
            "Ya existe un registro de inasistencia para este estudiante en esa fecha y área."
        )
        return

    try:
        payload = {
            "fecha": str(fecha),
            "periodo": str(periodo),
            "semana_periodo": semana_periodo,
            "area": area,
            "grupo": str(grupo),
            "matricula": matricula,
            "estudiante": estudiante,
            "observaciones": observaciones.strip(),
            "registrado_por_documento": str(usuario),
            "registrado_por_nombre": str(nombre_usuario),
            "rol_registrador": str(rol),
        }

        guardar_inasistencia(
            sheet_id=INASISTENCIA_SHEET_ID,
            worksheet_name=INASISTENCIA_WORKSHEET,
            payload=payload,
        )

        render_success_box("La inasistencia fue registrada correctamente.")
        st.session_state["mostrar_balloons_inasistencia"] = True
        st.session_state["reset_form_inasistencia"] = True
        df_inasistencias = cargar_inasistencias()
        if enviado:
            st.cache_data.clear()
            st.rerun()
        #st.rerun()        

    except Exception as exc:
        render_error_box(f"Ocurrió un error al guardar la inasistencia: {exc}")

    
    
    


    
    