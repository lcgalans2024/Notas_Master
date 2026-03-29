App_Academica/
│
├── app.py                         # antes: main.py
├── requirements.txt
├── README.md
│
├── assets/
│   └── images/
│       ├── escudo_oreste.png
│       ├── logo_app_1.png
│       ├── logo_app_2.png
│       ├── logo_app_3.png
│       └── logo_app_4.png
│
├── config/
│   ├── __init__.py
│   ├── settings.py                # nombre app, page config, textos globales
│   ├── sheets_config.py           # SHEET_ID, GIDS, GIDS_PM, emails, materias
│   └── menu_config.py             # opciones de menú por rol
│
├── core/
│   ├── __init__.py
│   ├── session_state.py           # antes: utils/session_state_init.py
│   ├── navigation.py              # define qué página renderizar
│   └── auth_guard.py              # validaciones de acceso
│
├── services/
│   ├── __init__.py
│   ├── google_sheets_service.py   # antes: parte de utils/load_data.py
│   ├── auth_service.py            # antes: parte de login.py
│   ├── usuarios_service.py        # antes: utils/usuarios.py
│   ├── notas_service.py           # antes: lógica de consulta_notas.py
│   ├── informe_service.py         # lógica de informe.py
│   ├── materiales_service.py      # lógica de materiales.py
│   └── recuperaciones_service.py  # lógica de recuperaciones.py
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py                 # antes: sidebar.py, solo navegación/filtros
│   ├── header.py                  # nuevo
│   ├── login_form.py              # antes: parte visual de login.py
│   ├── filtros.py                 # nuevo
│   ├── tablas.py                  # nuevo
│   ├── alerts.py                  # nuevo
│   └── visual_helpers.py          # antes: utils/visual_helpers.py
│
├── pages/
│   ├── __init__.py
│   ├── inicio.py                  # antes: inicio.py
│   ├── consulta_notas.py          # antes: components/consulta_notas.py
│   ├── informe.py                 # antes: components/informe.py
│   ├── materiales.py              # antes: components/materiales.py
│   ├── recuperaciones.py          # antes: components/recuperaciones.py
│   └── admin.py                   # opcional
│
├── utils/
│   ├── __init__.py
│   ├── normalizers.py             # limpieza de columnas, documentos, puntajes
│   ├── dataframe_utils.py         # ayudas con pandas
│   ├── validators.py              # validaciones de columnas y datos
│   └── cache_utils.py             # limpieza/refresco de caché
│
├── data/
│   ├── cache/
│   ├── exports/
│   └── temp/
│
└── docs/
    └── arquitectura_app.md