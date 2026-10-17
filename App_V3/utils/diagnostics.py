import os
import time
import uuid
import threading
import psutil
import streamlit as st


# ---------------------------------------------------------
# Registro compartido por todas las sesiones de la app
# ---------------------------------------------------------
@st.cache_resource
def _runtime_registry():
    return {
        "sessions": {},
        "peak_rss_mb": 0.0,
        "peak_active_sessions": 0,
        "rss_at_peak_sessions_mb": 0.0,
        "lock": threading.Lock(),
    }


def _get_memory_limit_mb():
    """
    Intenta detectar el límite de memoria del contenedor Linux.
    En ejecución local (Windows) puede devolver None.
    """

    paths = [
        "/sys/fs/cgroup/memory.max",                   # cgroup v2
        "/sys/fs/cgroup/memory/memory.limit_in_bytes" # cgroup v1
    ]

    for path in paths:
        try:
            with open(path, "r") as f:
                value = f.read().strip()

            if value == "max":
                continue

            limit_bytes = int(value)

            # Evita interpretar valores prácticamente infinitos
            if 0 < limit_bytes < 10**15:
                return limit_bytes / (1024 ** 2)

        except (FileNotFoundError, ValueError, PermissionError):
            continue

    return None


def _get_process_memory_mb():
    """
    RAM utilizada por el proceso principal y sus procesos hijos.
    """

    process = psutil.Process(os.getpid())

    total = process.memory_info().rss

    try:
        for child in process.children(recursive=True):
            try:
                total += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except psutil.Error:
        pass

    return total / (1024 ** 2)


def track_session(active_window_seconds=300):
    """
    Se debe ejecutar una vez en cada rerun.

    Registra:
    - sesión
    - número de reruns
    - RAM actual
    - pico de RAM
    - sesiones vistas en los últimos N segundos
    """

    if "_diag_session_id" not in st.session_state:
        st.session_state["_diag_session_id"] = uuid.uuid4().hex[:8]

    if "_diag_reruns" not in st.session_state:
        st.session_state["_diag_reruns"] = 0

    st.session_state["_diag_reruns"] += 1

    session_id = st.session_state["_diag_session_id"]
    now = time.time()

    rss_mb = _get_process_memory_mb()

    registry = _runtime_registry()

    with registry["lock"]:

        # Compatibilidad por si el registro ya estaba creado
        # antes de agregar las nuevas métricas.
        registry.setdefault("peak_rss_mb", 0.0)
        registry.setdefault("peak_active_sessions", 0)
        registry.setdefault("rss_at_peak_sessions_mb", 0.0)

        # Registrar actividad de esta sesión
        registry["sessions"][session_id] = now

        # Eliminar sesiones sin actividad reciente
        expired = [
            sid
            for sid, last_seen in registry["sessions"].items()
            if now - last_seen > active_window_seconds
        ]

        for sid in expired:
            del registry["sessions"][sid]

        active_sessions = len(registry["sessions"])

        # -----------------------------------------------------
        # Pico general de RAM
        # -----------------------------------------------------
        registry["peak_rss_mb"] = max(
            registry["peak_rss_mb"],
            rss_mb
        )

        # -----------------------------------------------------
        # Pico de sesiones
        # -----------------------------------------------------
        if active_sessions > registry["peak_active_sessions"]:

            registry["peak_active_sessions"] = active_sessions

            # RAM observada al alcanzar ese nuevo pico
            registry["rss_at_peak_sessions_mb"] = rss_mb

        elif active_sessions == registry["peak_active_sessions"]:

            # Si seguimos en el mismo máximo de sesiones,
            # conservar la mayor RAM observada con esa carga.
            registry["rss_at_peak_sessions_mb"] = max(
                registry["rss_at_peak_sessions_mb"],
                rss_mb
            )

        peak_rss_mb = registry["peak_rss_mb"]
        peak_active_sessions = registry["peak_active_sessions"]
        rss_at_peak_sessions_mb = registry[
            "rss_at_peak_sessions_mb"
        ]

    return {
    "session_id": session_id,
    "reruns": st.session_state["_diag_reruns"],
    "active_sessions": active_sessions,
    "peak_active_sessions": peak_active_sessions,
    "rss_mb": rss_mb,
    "peak_rss_mb": peak_rss_mb,
    "rss_at_peak_sessions_mb": rss_at_peak_sessions_mb,
}


def render_diagnostics(diag, execution_time=None):

    process = psutil.Process(os.getpid())

    # 0.1 s solamente cuando el administrador abre/visualiza
    # el diagnóstico.
    cpu = process.cpu_percent(interval=0.1)

    threads = process.num_threads()

    uptime_seconds = time.time() - process.create_time()

    memory_limit_mb = _get_memory_limit_mb()

    with st.sidebar.expander(
        "🛠️ Diagnóstico de la app",
        expanded=False
    ):

        st.caption("Recursos del proceso actual")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "RAM actual",
                f"{diag['rss_mb']:.0f} MB"
            )

        with col2:
            st.metric(
                "Pico RAM",
                f"{diag['peak_rss_mb']:.0f} MB"
            )

        if memory_limit_mb:

            porcentaje = (
                diag["rss_mb"] / memory_limit_mb
            ) * 100

            st.progress(
                min(porcentaje / 100, 1.0)
            )

            st.caption(
                f"RAM: {porcentaje:.1f}% "
                f"de {memory_limit_mb:.0f} MB detectados"
            )

            if porcentaje >= 85:
                st.error(
                    "⚠️ Consumo de memoria muy alto."
                )

            elif porcentaje >= 70:
                st.warning(
                    "RAM acercándose a un nivel elevado."
                )

        col3, col4 = st.columns(2)

        with col3:
            st.metric(
                "CPU",
                f"{cpu:.1f}%"
            )

        with col4:
            st.metric(
                "Hilos",
                threads
            )

        st.divider()

        col5, col6 = st.columns(2)

        with col5:
            st.metric(
                "Reruns",
                diag.get("reruns", 0)
            )

        with col6:
            st.metric(
                "Sesiones recientes",
                diag.get("active_sessions", 0)
            )

        col7, col8 = st.columns(2)

        with col7:
            st.metric(
                "Pico sesiones",
                diag.get("peak_active_sessions", 0)
            )
        
        with col8:
            st.metric(
                "RAM en pico sesiones",
                f"{diag.get('rss_at_peak_sessions_mb', 0):.0f} MB"
            )


        if execution_time is not None:
            st.metric(
                "Tiempo del rerun",
                f"{execution_time:.3f} s"
            )

        uptime_minutes = uptime_seconds / 60

        st.caption(
            f"Proceso activo: {uptime_minutes:.1f} min"
        )

        st.caption(
            f"ID sesión: {diag['session_id']}"
        )

        st.caption(
            "Sesiones recientes = sesiones con actividad "
            "durante los últimos 5 minutos."
        )