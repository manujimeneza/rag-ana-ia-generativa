"""
Módulo de Análisis de Datos - Wilfer
Calcula métricas analíticas sobre los datos capturados de EVA.
Representa la salida del Modelo en el módulo ANA de Evergreen.
"""

import pandas as pd
import os


def analizar_datos(df: pd.DataFrame) -> dict:
    """
    Realiza el análisis de datos agrícolas.
    Calcula métricas que representan el output del Modelo ANA.

    Args:
        df: DataFrame con datos de EVA

    Returns:
        Diccionario con las métricas del análisis
    """
    print("[ANÁLISIS] Procesando datos del módulo ANA...")

    # Detectar columnas relevantes dinámicamente
    cols = df.columns.str.lower()
    col_cultivo = _buscar_columna(df, ["cultivo", "crop", "nombre_cultivo"])
    col_produccion = _buscar_columna(df, ["produccion_t", "produccion", "production"])
    col_rendimiento = _buscar_columna(df, ["rendimiento_t_ha", "rendimiento", "yield"])
    col_area = _buscar_columna(df, ["area_sembrada_ha", "area_sembrada", "area"])
    col_año = _buscar_columna(df, ["año", "year", "periodo", "anio"])
    col_municipio = _buscar_columna(df, ["municipio", "municipality"])

    resumen = {
        "tipo_analisis": "descriptivo y predictivo",
        "departamento": _detectar_departamento(df),
        "total_registros": len(df),
        "cultivos_analizados": [],
        "metricas_por_cultivo": {},
        "alertas": [],
        "tendencia_general": "",
    }

    # --- Análisis por cultivo ---
    if col_cultivo:
        cultivos = df[col_cultivo].dropna().unique()
        resumen["cultivos_analizados"] = list(cultivos)[:10]

        for cultivo in resumen["cultivos_analizados"]:
            df_cultivo = df[df[col_cultivo] == cultivo]
            metricas = {}

            if col_rendimiento:
                rend = pd.to_numeric(df_cultivo[col_rendimiento], errors="coerce").dropna()
                if not rend.empty:
                    metricas["rendimiento_promedio"] = round(rend.mean(), 2)
                    metricas["rendimiento_min"] = round(rend.min(), 2)
                    metricas["rendimiento_max"] = round(rend.max(), 2)

            if col_produccion:
                prod = pd.to_numeric(df_cultivo[col_produccion], errors="coerce").dropna()
                if not prod.empty:
                    metricas["produccion_total"] = round(prod.sum(), 2)
                    metricas["produccion_promedio"] = round(prod.mean(), 2)

            if col_area:
                area = pd.to_numeric(df_cultivo[col_area], errors="coerce").dropna()
                if not area.empty:
                    metricas["area_total_sembrada"] = round(area.sum(), 2)

            if col_municipio:
                metricas["municipios_con_cultivo"] = int(df_cultivo[col_municipio].nunique())

            # Tendencia si hay datos por año
            if col_año and col_produccion:
                try:
                    df_num = df_cultivo.copy()
                    df_num[col_produccion] = pd.to_numeric(df_num[col_produccion], errors="coerce")
                    prod_por_año = df_num.groupby(col_año)[col_produccion].sum().sort_index()
                    if len(prod_por_año) >= 2:
                        cambio = ((prod_por_año.iloc[-1] - prod_por_año.iloc[0]) / prod_por_año.iloc[0]) * 100
                        metricas["tendencia_produccion"] = "creciente" if cambio > 5 else "decreciente" if cambio < -5 else "estable"
                        metricas["cambio_porcentual"] = round(cambio, 1)
                except Exception:
                    pass

            resumen["metricas_por_cultivo"][str(cultivo)] = metricas

            # Alertas
            if "rendimiento_promedio" in metricas and metricas["rendimiento_promedio"] < 2.0:
                resumen["alertas"].append(
                    f"ALERTA: {cultivo} tiene rendimiento bajo ({metricas['rendimiento_promedio']} ton/ha)"
                )
            if "tendencia_produccion" in metricas and metricas["tendencia_produccion"] == "decreciente":
                resumen["alertas"].append(
                    f"ALERTA: {cultivo} muestra tendencia decreciente ({metricas.get('cambio_porcentual', 'N/A')}%)"
                )

    # Tendencia general
    tendencias = [m.get("tendencia_produccion", "estable")
                  for m in resumen["metricas_por_cultivo"].values()]
    if tendencias.count("creciente") > tendencias.count("decreciente"):
        resumen["tendencia_general"] = "creciente"
    elif tendencias.count("decreciente") > tendencias.count("creciente"):
        resumen["tendencia_general"] = "decreciente"
    else:
        resumen["tendencia_general"] = "mixta"

    if not resumen["alertas"]:
        resumen["alertas"].append("Sin alertas críticas detectadas")

    _imprimir_resumen(resumen)
    return resumen


def _buscar_columna(df, candidatos):
    """Busca la primera columna que coincida con los nombres candidatos."""
    for c in candidatos:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None


def _detectar_departamento(df):
    """Intenta detectar el departamento de los datos."""
    for col in df.columns:
        if "depart" in col.lower() or "depto" in col.lower():
            vals = df[col].dropna().unique()
            if len(vals) > 0:
                return str(vals[0]).title()
    return "No especificado"


def _imprimir_resumen(resumen):
    """Imprime un resumen legible del análisis."""
    print(f"\n{'='*60}")
    print(f"  RESUMEN DEL ANÁLISIS - MÓDULO ANA")
    print(f"{'='*60}")
    print(f"  Departamento:     {resumen['departamento']}")
    print(f"  Tipo de análisis: {resumen['tipo_analisis']}")
    print(f"  Total registros:  {resumen['total_registros']}")
    print(f"  Cultivos:         {', '.join(resumen['cultivos_analizados'][:5])}")
    print(f"  Tendencia:        {resumen['tendencia_general']}")
    print(f"\n  Alertas:")
    for alerta in resumen["alertas"]:
        print(f"    ⚠ {alerta}")
    print(f"{'='*60}\n")


# --- Ejecución directa ---
if __name__ == "__main__":
    ruta = os.path.join(os.path.dirname(__file__), "..", "data", "eva_datos.csv")
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
    else:
        from captura_datos import capturar_datos_eva
        df = capturar_datos_eva("ANTIOQUIA")

    resumen = analizar_datos(df)

    import json
    print("\n[ANÁLISIS] Resumen JSON completo:")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
