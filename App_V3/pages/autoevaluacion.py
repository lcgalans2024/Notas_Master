import streamlit as st

from components.alerts import (
    render_error_box,
    render_info_box,
    render_success_box,
    render_warning_box,
)
from config.sheets_config import SHEETS_CONFIG
from services.google_write_service import (
    estudiante_ya_respondio_autoevaluacion,
    guardar_autoevaluacion,
    escribir_autoevaluacion_en_hoja_notas,
)


AUTOEVALUACION_CRITERIOS = [
    "Asistencia a clase y actividades",
    "Responsabilidad y puntualidad",
    "Participación en el desarrollo de la clase",
    "Entrega oportuna de tareas, trabajos y talleres",
    "Comportamiento acorde con el manual de convivencia",
    "Interés, motivación y esfuerzo",
    "Manejo y uso responsable del celular durante las clases",
    "Autonomía e independencia en el desarrollo de actividades",
    "Presentación personal",
    "Trabajo colaborativo",
]

OPCIONES_VALORACION = {
    "1 - Muy bajo": 1.0,
    "2 - Bajo": 2.0,
    "3 - Básico": 3.0,
    "4 - Alto": 4.0,
    "5 - Superior": 5.0,
}


AUTOEVALUACION_SHEET_ID = SHEETS_CONFIG["sheet_id_principal"]  # Usamos el mismo sheet_id para almacenar las autoevaluaciones, pero en una hoja diferente
AUTOEVALUACION_WORKSHEET = "autoevaluaciones"


def _calcular_nota_final(respuestas: list[float]) -> float:
    if not respuestas:
        return 0.0
    return round(sum(respuestas) / 10, 2)


def _obtener_payload_autoevaluacion(respuestas: list[float], nota_final: float) -> dict:
    datos_usuario = st.session_state.get("datos_usuario", {})

    payload = {
        "documento": st.session_state.get("usuario"),
        "estudiante": st.session_state.get("nombre"),
        "grupo": st.session_state.get("grupo"),
        "matricula": datos_usuario.get("matricula"),
        "anio_academico": st.session_state.get("anio_academico"),
        "periodo": st.session_state.get("periodo"),
        "nota_final": nota_final,
    }

    for i, respuesta in enumerate(respuestas, start=1):
        payload[f"criterio_{i}"] = respuesta

    return payload


def _validar_contexto() -> tuple[bool, str]:
    if not st.session_state.get("authenticated"):
        return False, "No hay un usuario autenticado."

    if not st.session_state.get("usuario"):
        return False, "No se encontró el documento del estudiante."

    if not st.session_state.get("grupo"):
        return False, "No se encontró el grupo del estudiante."

    if not st.session_state.get("anio_academico"):
        return False, "No se encontró el año académico."

    if not st.session_state.get("periodo"):
        return False, "No se encontró el periodo académico."

    return True, ""


def render_autoevaluacion() -> None:
    st.title("Autoevaluación")
    st.caption("Responde los 10 criterios y la plataforma calculará automáticamente tu nota.")

    ok, mensaje = _validar_contexto()
    if not ok:
        render_error_box(mensaje)
        return

    documento = str(st.session_state.get("usuario"))
    anio_academico = str(st.session_state.get("anio_academico"))
    periodo = str(st.session_state.get("periodo"))

    try:
        ya_respondio = estudiante_ya_respondio_autoevaluacion(
            sheet_id=AUTOEVALUACION_SHEET_ID,
            worksheet_name=AUTOEVALUACION_WORKSHEET,
            documento=documento,
            anio_academico=anio_academico,
            periodo=periodo,
        )
    except Exception as exc:
        render_error_box(f"No fue posible validar si ya existe una respuesta: {exc}")
        return

    if ya_respondio:
        render_warning_box(
            f"Ya registraste una autoevaluación para el año {anio_academico} y el periodo {periodo}."
        )
        return

    nombre = st.session_state.get("nombre", "Estudiante")
    grupo = st.session_state.get("grupo")

    st.write(f"**Estudiante:** {nombre}")
    st.write(f"**Grupo:** {grupo}")
    st.write(f"**Año académico:** {anio_academico}")
    st.write(f"**Periodo:** {periodo}")

    render_info_box(
        "Selecciona una valoración para cada criterio. La nota final se calculará como el promedio de los 10 criterios."
    )

    with st.form("form_autoevaluacion"):
        respuestas = []

        for i, criterio in enumerate(AUTOEVALUACION_CRITERIOS, start=1):
            opcion = st.slider(
                label=f"Criterio {i}: {criterio}",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                format="%0.1f",
                #step=0.5,
                #options=list(OPCIONES_VALORACION.keys()),
            )
            respuestas.append(opcion)

        nota_previa = _calcular_nota_final(respuestas)
        #st.markdown(f"### Nota calculada: **{nota_previa:.2f}**")

        enviado = st.form_submit_button("Guardar autoevaluación", use_container_width=True)

    if not enviado:
        return

    try:
        payload = _obtener_payload_autoevaluacion(respuestas, nota_previa)

        guardar_autoevaluacion(
            sheet_id=AUTOEVALUACION_SHEET_ID,
            worksheet_name=AUTOEVALUACION_WORKSHEET,
            payload=payload,
        )

        matricula = payload.get("matricula")

        if not matricula:
            raise ValueError("No se encontró la matrícula del estudiante para actualizar la hoja de notas.")
        
        escribir_autoevaluacion_en_hoja_notas(
            matricula=str(matricula),
            grupo=str(payload["grupo"]),
            periodo=str(payload["periodo"]),
            nota_final=float(payload["nota_final"]),
            nombre_columna_objetivo="3.1",
            nombre_columna_matricula="Matricula",
        )

        render_success_box(
            f"Tu autoevaluación fue guardada correctamente. Nota final: {nota_previa:.2f}"
        )
        st.balloons()

    except Exception as exc:
        render_error_box(f"Ocurrió un error al guardar la autoevaluación: {exc}")