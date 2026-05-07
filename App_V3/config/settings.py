from pathlib import Path

# -------------------------------------------------------------------
# Rutas base del proyecto
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
MATERIALES_DIR = ASSETS_DIR / "materiales"

# -------------------------------------------------------------------
# Configuración general de la app
# -------------------------------------------------------------------
APP_CONFIG = {
    "page_title": "Plataforma Académica",
    "page_icon": "📘",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# -------------------------------------------------------------------
# Identidad visual y textos globales
# -------------------------------------------------------------------
APP_INFO = {
    "app_name": "Plataforma Académica",
    "institution_name": "Institución Educativa Oreste Sindici",
    "welcome_title": "Bienvenido a la plataforma académica",
    "welcome_subtitle": (
        "Aquí podrás consultar notas, informes, materiales del área "
        "y demás información académica relevante."
    ),
}

# -------------------------------------------------------------------
# Recursos visuales
# -------------------------------------------------------------------
IMAGE_PATHS = {
    "escudo": IMAGES_DIR / "escudo_oreste.png",
    "logo_1": IMAGES_DIR / "logo_app_1.png",
    "logo_2": IMAGES_DIR / "logo_app_2.png",
    "logo_3": IMAGES_DIR / "logo_app_3.png",
    "logo_4": IMAGES_DIR / "logo_app_4.png",
}

# -------------------------------------------------------------------
# Parámetros globales de funcionamiento
# -------------------------------------------------------------------
APP_DEFAULTS = {
    "anio_academico": "2026",
    "periodo": "P1",
    "grupo": None,
    "usuario": None,
    "matricula": None,
    "nombre": None,
    "rol": "estudiante",
    "adm": False,
    "authenticated": False,
    "vista_actual": "Inicio",
    "anio_usuario_contexto": None,
}

# -------------------------------------------------------------------
# Configuración de cache
# -------------------------------------------------------------------
CACHE_CONFIG = {
    "ttl_estudiantes": 60,
    "ttl_notas": 60,
    "ttl_materiales": 120,
    "ttl_recuperaciones": 60,
    "ttl_usuarios": 120,
}

# -------------------------------------------------------------------
# Mensajes globales reutilizables
# -------------------------------------------------------------------
MESSAGES = {
    "login_required": "Ingresa con el documento del estudiante para continuar.",
    "no_data": "No hay información disponible en este momento.",
    "loading": "Cargando información...",
    "error_general": "Ocurrió un error al procesar la información.",
}

# -------------------------------------------------------------------
# Diccionarios de mapeo y homologación
# -------------------------------------------------------------------
MATERIAS = {
            "CNS": "CIENCIAS NATURALES Y EDUCACIÓN AMBIENTAL",
            "ART": "EDUCACIÓN ARTISTICA Y CULTURAL",
            "ETI": "EDUCACION ETICA  Y  EN VALORES HUMANOS",
            "EDF": "EDUCACIÓN FÍSICA, RECREACIÓN Y DEPORTES",
            "LEI": "LENGUA EXTRANJERA INGLES",
            "MAT": "MATEMÁTICAS",
            "CIE": "CIENCIAS SOCIALES",
            "TEC": "TECNOLOGIA E INFORMÁTICA",
            "REL": "EDUCACION RELIGIOSA",
            "LEN": "LENGUA CASTELLANA"
        }