from __future__ import annotations

import re
import unicodedata

import pandas as pd


def normalizar_texto_basico(valor) -> str:
    """
    Convierte un valor a texto limpio:
    - elimina espacios extremos,
    - colapsa espacios internos repetidos.
    """
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def quitar_acentos(texto: str) -> str:
    """
    Elimina acentos y marcas diacríticas de un texto.
    """
    if not texto:
        return ""

    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def normalizar_nombre_columna(nombre_columna) -> str:
    """
    Normaliza nombres de columnas para facilitar homologación:
    - quita acentos,
    - pasa a minúsculas,
    - reemplaza espacios y símbolos por guion bajo,
    - elimina guiones bajos repetidos.
    """
    texto = normalizar_texto_basico(nombre_columna)
    texto = quitar_acentos(texto).lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = re.sub(r"_+", "_", texto).strip("_")
    return texto


def normalizar_documento(documento) -> str:
    """
    Normaliza documentos:
    - convierte a string,
    - elimina espacios,
    - elimina terminación '.0' típica de Excel/pandas.
    """
    texto = normalizar_texto_basico(documento)

    if not texto:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto

def normalizar_matricula(matricula) -> str:
    """
    Normaliza matrículas:
    - convierte a string,
    - elimina espacios,
    - elimina terminación '.0' típica de Excel/pandas.
    """
    texto = normalizar_texto_basico(matricula)

    if not texto:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def normalizar_nombre_persona(nombre) -> str:
    """
    Normaliza nombres de personas para visualización:
    - limpia espacios,
    - conserva mayúsculas sostenidas si vienen así,
    - de lo contrario aplica formato título.
    """
    texto = normalizar_texto_basico(nombre)

    if not texto:
        return ""

    if texto.isupper():
        return texto

    return texto.title()


def normalizar_periodo(periodo) -> str:
    """
    Homologa valores de periodo a formato tipo P1, P2, P3, etc.
    """
    texto = normalizar_texto_basico(periodo).upper().replace(" ", "")

    if not texto:
        return ""

    if texto in {"1", "P1", "PERIODO1", "PERIODO_1"}:
        return "P1"
    if texto in {"2", "P2", "PERIODO2", "PERIODO_2"}:
        return "P2"
    if texto in {"3", "P3", "PERIODO3", "PERIODO_3"}:
        return "P3"
    if texto in {"4", "P4", "PERIODO4", "PERIODO_4"}:
        return "P4"

    return texto


def normalizar_grupo(grupo) -> str:
    """
    Normaliza el grupo académico.

    Casos esperados:
    - 70100 -> 701
    - 70200 -> 702
    - " 70300 " -> 703
    - 801 -> 801

    Regla:
    Si el valor termina en '00' y tiene al menos 5 caracteres numéricos,
    se recortan los dos últimos ceros.
    """
    texto = normalizar_texto_basico(grupo)

    if not texto:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    texto = texto.replace(" ", "")

    if texto.isdigit() and len(texto) >= 5 and texto.endswith("00"):
        texto = texto[:-2]

    return texto


def normalizar_puntaje(valor):
    """
    Convierte puntajes escritos con coma decimal o texto numérico
    a float. Si no se puede convertir, retorna el valor original.
    """
    if pd.isna(valor):
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = normalizar_texto_basico(valor).replace(",", ".")

    if not texto:
        return None

    try:
        return float(texto)
    except ValueError:
        return valor


def normalizar_columnas_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna una copia del DataFrame con nombres de columnas normalizados.
    """
    df = df.copy()
    df.columns = [normalizar_nombre_columna(col) for col in df.columns]
    return df


def homologar_columnas_estudiantes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Homologa posibles variantes de columnas de la base de estudiantes
    a nombres estándar esperados por la app, evitando colisiones.
    """
    df = normalizar_columnas_dataframe(df)

    mapa_renombre = {
        "documento": "documento",
        "numero_documento": "documento",
        "n_documento": "documento",
        "identificacion": "documento",

        "nombre": "nombre",
        "nombre_completo": "nombre",
        "estudiante": "nombre",
        "nombres_y_apellidos": "nombre",

        "grupo": "grupo",
        "curso": "grupo",

        "grado": "grado",
        "matrícula": "matricula",
        "matricula": "matricula",
        "tipo_doc": "tipo_doc",
    }

    columnas_renombradas = {}
    columnas_destino_usadas = set()

    for col in df.columns:
        destino = mapa_renombre.get(col)
        if destino and destino not in columnas_destino_usadas:
            columnas_renombradas[col] = destino
            columnas_destino_usadas.add(destino)

    df = df.rename(columns=columnas_renombradas)
    return df


def normalizar_dataframe_estudiantes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y homologa la base de estudiantes a un formato estándar.
    Columnas esperadas al final:
    - documento
    - nombre
    - grupo
    """
    df = homologar_columnas_estudiantes(df)

    if "documento" in df.columns:
        df["documento"] = df["documento"].apply(normalizar_documento)

    if "matricula" in df.columns:
        df["matricula"] = df["matricula"].apply(normalizar_matricula)

    if "nombre" in df.columns:
        df["nombre"] = df["nombre"].apply(normalizar_nombre_persona)

    if "grupo" in df.columns:
        df["grupo"] = df["grupo"].apply(normalizar_grupo)

    return df


def normalizar_dataframe_notas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza básica y homogénea para bases de notas.
    """
    df = normalizar_columnas_dataframe(df)

    posibles_documento = ["documento", "numero_documento", "identificacion"]
    posibles_matricula = ["matricula", "matrícula"]
    posibles_nombre = ["nombre", "nombre_completo", "estudiante"]
    posibles_periodo = ["periodo"]
    posibles_puntaje = ["puntaje", "nota", "calificacion"]

    for col in posibles_documento:
        if col in df.columns:
            df["documento"] = df[col].apply(normalizar_documento)
            break

    for col in posibles_matricula:
        if col in df.columns:
            df["matricula"] = df[col].apply(normalizar_matricula)
            break

    for col in posibles_nombre:
        if col in df.columns:
            df["nombre"] = df[col].apply(normalizar_nombre_persona)
            break

    for col in posibles_periodo:
        if col in df.columns:
            df["periodo"] = df[col].apply(normalizar_periodo)
            break

    for col in posibles_puntaje:
        if col in df.columns:
            df[col] = df[col].apply(normalizar_puntaje)

    return df