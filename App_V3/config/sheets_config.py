from __future__ import annotations

SHEETS_CONFIG = {
    # ======================================================
    # ID principal del Google Sheet
    # ======================================================
    #"sheet_id_principal": "1J-CZASJTrqhLXlmkFY_DavyG2aQ5HBaS",
    "sheet_id_principal": "15ELuuOC2jO_bQzl9pDqhiMfE4EunZRw2f89p-0-dORE",


    # ======================================================
    # En esta primera versión usamos el mismo archivo
    # también para las hojas de notas por grupo/periodo
    # ======================================================
    "sheet_id_periodos": "1J-CZASJTrqhLXlmkFY_DavyG2aQ5HBaS",

    # ======================================================
    # Hoja de respuesta de autoevaluación
    # ======================================================
    "sheet_id_autoevaluacion": "1eZ7NtWyFr0Terc0sBLkVIZ5iQfsfLnm6oYT7--itdhQ",
    "gid_autoevaluacion": "0",


    # ======================================================
    # Hojas de estudiantes por año académico
    # ======================================================
    "gids_estudiantes": {
        "2025": "817657441",
        "2026": "542997900",
    },

    # ======================================================
    # Hojas de notas por grupo y periodo
    # IMPORTANTE:
    # Aquí se conservan las claves reales que tú ya manejas.
    # ======================================================
    "gids_notas": {
        "notas_601_P2": "732983744",
        "notas_601_P3": "2075067324",
        "notas_602_P2": "201335434",
        "notas_701_P1": "1779130150",
        "notas_701_P2": "1360433359",
        "notas_701_P3": "291117448",
        "notas_702_P1": "1659300987",
        "notas_702_P2": "1327140213",
        "notas_702_P3": "951373038",
        "notas_703_P1": "2122928690",
        "notas_703_P2": "83185436",
        "notas_703_P3": "1860654076",
        "notas_704_P1": "1926990909",
        "notas_704_P2": "1004768913",
        "notas_704_P3": "1974496332",
        "notas_801_P1": "17714330",
        "notas_802_P1": "162417486",
        "notas_803_P1": "714528096",
        "notas_804_P1": "548002678",
        "notas_805_P1": "1994348554",
    },

    # ======================================================
    # Hojas auxiliares
    # ======================================================
    "gid_recuperaciones": "1791404525",
    "gid_materiales": None,
    "gid_roles": "767080748",
    "gid_inasistencia": "1735563087",

    # ======================================================
    # Catálogos base de trabajo
    # ======================================================
    "anios_disponibles": ["2025", "2026"],
    "periodos_disponibles": ["P1", "P2", "P3", "P4"],
    "grupos_disponibles": [
        "601",
        "602",
        "701",
        "702",
        "703",
        "704",
        "801",
        "802",
        "803",
        "804",
        "805",
    ],

    # ======================================================
    # Información auxiliar
    # ======================================================
    "emails_admin": [],
    "materias_disponibles": [
        "Matemáticas",
    ],
}