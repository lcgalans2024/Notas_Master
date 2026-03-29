App_V2/
│
├── app.py
├── requirements.txt
├── README.md
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   ├── images/
│   │   ├── escudo_oreste.png
│   │   ├── logo_app_1.png
│   │   ├── logo_app_2.png
│   │   ├── logo_app_3.png
│   │   └── logo_app_4.png
│   └── styles/
│       └── custom.css
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── sheets_config.py
│   └── menu_config.py
│
├── core/
│   ├── __init__.py
│   ├── session_state.py
│   ├── navigation.py
│   ├── auth_guard.py
│   └── constants.py
│
├── services/
│   ├── __init__.py
│   ├── google_sheets_service.py
│   ├── auth_service.py
│   ├── usuarios_service.py
│   ├── notas_service.py
│   ├── informe_service.py
│   ├── materiales_service.py
│   └── recuperaciones_service.py
│
├── utils/
│   ├── __init__.py
│   ├── normalizers.py
│   ├── formatters.py
│   ├── validators.py
│   ├── dataframe_utils.py
│   └── cache_utils.py
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py
│   ├── header.py
│   ├── login_form.py
│   ├── filtros.py
│   ├── tablas.py
│   ├── metricas.py
│   ├── alerts.py
│   └── visual_helpers.py
│
├── pages/
│   ├── __init__.py
│   ├── inicio.py
│   ├── consulta_notas.py
│   ├── informe.py
│   ├── materiales.py
│   ├── recuperaciones.py
│   └── admin.py
│
├── data/
│   ├── cache/
│   ├── exports/
│   └── temp/
│
├── docs/
│   └── arquitectura_app.md
│
└── tests/
    ├── __init__.py
    ├── test_normalizers.py
    ├── test_notas_service.py
    └── test_auth_service.py