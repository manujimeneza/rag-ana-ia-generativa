"""
Módulo de Captura de Datos - Wilfer
Descarga datos de la API pública EVA (datos.gov.co)
Evaluaciones Agropecuarias Municipales de Colombia
"""

import pandas as pd
import os


def capturar_datos_eva(departamento: str = "ANTIOQUIA", limite: int = 5000) -> pd.DataFrame:
    """
    Captura datos de la API pública EVA de datos.gov.co.

    Args:
        departamento: Nombre del departamento a filtrar (mayúsculas)
        limite: Número máximo de registros a traer

    Returns:
        DataFrame con los datos filtrados del departamento
    """
    url = f"https://www.datos.gov.co/resource/2pnw-mmge.csv?$limit={limite}"

    print(f"[CAPTURA] Descargando datos de EVA para {departamento}...")
    print(f"[CAPTURA] URL: {url}")

    try:
        df = pd.read_csv(url)
        print(f"[CAPTURA] Total registros descargados: {len(df)}")

        # Normalizar nombres de columnas (pueden variar)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # Mostrar columnas disponibles para debug
        print(f"[CAPTURA] Columnas disponibles: {list(df.columns)}")

        # Filtrar por departamento si la columna existe
        col_depto = None
        for col in df.columns:
            if "depart" in col.lower() or "depto" in col.lower():
                col_depto = col
                break

        if col_depto:
            df_filtrado = df[df[col_depto].str.upper().str.contains(departamento, na=False)]
            print(f"[CAPTURA] Registros para {departamento}: {len(df_filtrado)}")
        else:
            print(f"[CAPTURA] No se encontró columna de departamento, usando todos los datos")
            df_filtrado = df

        return df_filtrado

    except Exception as e:
        print(f"[CAPTURA] Error al descargar datos: {e}")
        print("[CAPTURA] Usando datos de ejemplo...")
        return _datos_ejemplo()


def _datos_ejemplo() -> pd.DataFrame:
    """
    Datos de ejemplo en caso de que la API no esté disponible.
    Basados en datos reales de EVA para Antioquia.
    """
    datos = {
        "departamento": ["ANTIOQUIA"] * 12,
        "municipio": ["ANDES", "ANDES", "ANDES", "JARDIN", "JARDIN", "JARDIN",
                       "FREDONIA", "FREDONIA", "FREDONIA", "SALGAR", "SALGAR", "SALGAR"],
        "cultivo": ["CAFÉ", "CAFÉ", "CAFÉ", "CAFÉ", "CAFÉ", "CAFÉ",
                     "MAÍZ", "MAÍZ", "MAÍZ", "MAÍZ", "MAÍZ", "MAÍZ"],
        "año": [2020, 2021, 2022, 2020, 2021, 2022, 2020, 2021, 2022, 2020, 2021, 2022],
        "area_sembrada_ha": [3500, 3600, 3400, 1200, 1250, 1180,
                              800, 850, 780, 600, 620, 590],
        "area_cosechada_ha": [3200, 3300, 3100, 1100, 1150, 1080,
                               720, 780, 700, 540, 560, 530],
        "produccion_t": [5760, 6270, 5580, 1980, 2185, 1944,
                          2880, 3276, 2660, 2160, 2352, 2014],
        "rendimiento_t_ha": [1.8, 1.9, 1.8, 1.8, 1.9, 1.8,
                              4.0, 4.2, 3.8, 4.0, 4.2, 3.8]
    }
    return pd.DataFrame(datos)


def guardar_datos(df: pd.DataFrame, nombre: str = "eva_datos.csv"):
    """Guarda los datos capturados en la carpeta data/"""
    ruta = os.path.join(os.path.dirname(__file__), "..", "data", nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    df.to_csv(ruta, index=False)
    print(f"[CAPTURA] Datos guardados en: {ruta}")
    return ruta


# --- Ejecución directa ---
if __name__ == "__main__":
    df = capturar_datos_eva("ANTIOQUIA")
    guardar_datos(df)
    print("\n[CAPTURA] Primeros 5 registros:")
    print(df.head())
