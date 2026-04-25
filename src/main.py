"""
Pipeline Principal - RAG Módulo ANA Evergreen
Conecta los 3 pasos del RAG: Retrieval → Augmentation → Generation

Uso:
    python src/main.py
    python src/main.py --departamento ANTIOQUIA --cultivos CAFÉ MAÍZ

Autores:
    - Wilfer: captura_datos.py, analisis_datos.py
    - Manuela: base_conocimiento.py, prompt_builder.py, generador_reporte.py
    - Carolina: documentación y presentación
"""

import sys
import os
import argparse

# Agregar src al path
sys.path.insert(0, os.path.dirname(__file__))

from captura_datos import capturar_datos_eva, guardar_datos
from analisis_datos import analizar_datos
from base_conocimiento import cargar_base_conocimiento
from prompt_builder import construir_prompt
from generador_reporte import (
    generar_reporte,
    generar_reportes_comparacion,
    guardar_reporte,
    guardar_reporte_html,
    guardar_reporte_comparacion_html,
    abrir_en_navegador
)


def ejecutar_pipeline(departamento: str = "ANTIOQUIA", cultivos: list = None):
    """
    Ejecuta el pipeline RAG completo para el módulo ANA.

    Pipeline:
    1. CAPTURA (Wilfer)      → Datos de EVA API
    2. ANÁLISIS (Wilfer)     → Métricas del modelo ANA
    3. RETRIEVAL (Manuela)   → Contexto del dominio agrícola
    4. AUGMENTATION (Manuela)→ Prompt RAG ensamblado
    5. GENERATION (Manuela)  → Reporte narrativo vía LLM
    """

    print("\n" + "█" * 70)
    print("  RAG - MÓDULO DE ANALÍTICA [ANA] - EVERGREEN")
    print("  Generación Automática de Reportes Analíticos Agrícolas")
    print("█" * 70 + "\n")

    # ── PASO 1: CAPTURA DE DATOS (Wilfer) ─────────────────────────────
    print("─" * 50)
    print("  PASO 1: Captura de datos (Wilfer)")
    print("─" * 50)
    df = capturar_datos_eva(departamento)
    guardar_datos(df)

    # ── PASO 2: ANÁLISIS DE DATOS (Wilfer) ────────────────────────────
    print("─" * 50)
    print("  PASO 2: Análisis de datos - Modelo ANA (Wilfer)")
    print("─" * 50)
    resumen = analizar_datos(df)

    # ── PASO 3: RETRIEVAL SEMÁNTICO - Base de conocimiento (Manuela) ────────────
    print("─" * 50)
    print("  PASO 3: Retrieval Semántico - Pinecone (Manuela)")
    print("─" * 50)
    # NOTA: Si Pinecone está vacío, se indexa AUTOMÁTICAMENTE en este paso
    cultivos_detectados = cultivos or resumen.get("cultivos_analizados", [])
    # Construir query semántica para buscar en Pinecone
    query_semantica = f"rendimiento producción características {' '.join(cultivos_detectados).lower()}"
    contexto = cargar_base_conocimiento(cultivos=cultivos_detectados, query=query_semantica)

    # ── PASO 4: AUGMENTATION - Construcción del prompt (Manuela) ──────
    print("─" * 50)
    print("  PASO 4: Augmentation - Prompt RAG (Manuela)")
    print("─" * 50)
    system_prompt, user_prompt = construir_prompt(resumen, contexto)

    # ── PASO 5: GENERATION - Comparación de 3 modelos Groq (Manuela) ────────────
    print("─" * 50)
    print("  PASO 5: Generation - Comparación 3 Modelos Groq (Manuela)")
    print("─" * 50)
    # EL MISMO prompt se usa para todos los modelos → Comparación justa
    reportes = generar_reportes_comparacion(system_prompt, user_prompt)

    # ── GUARDAR Y MOSTRAR RESULTADOS ──────────────────────────────────
    if reportes:
        # Guardar reporte comparativo HTML (tab view)
        ruta_html_comparacion = guardar_reporte_comparacion_html(reportes, resumen_analisis=resumen)

        # También guardar el primer reporte exitoso como TXT individual
        primer_reporte = None
        for modelo_key, resultado in reportes.items():
            if resultado.get("reporte") and not resultado.get("error"):
                primer_reporte = resultado.get("reporte")
                break

        if primer_reporte:
            ruta_txt = guardar_reporte(primer_reporte)
            print(f"\n  Archivo TXT guardado en: {ruta_txt}")

        print("\n" + "█" * 70)
        print("  REPORTES GENERADOS (3 MODELOS):")
        print("█" * 70)
        for modelo_key, resultado in reportes.items():
            if resultado.get("error"):
                print(f"\n  ❌ {modelo_key}: {resultado['error']}")
            else:
                tokens = resultado.get("tokens", 0)
                tiempo = resultado.get("tiempo_ms", 0)
                print(f"\n  ✅ {modelo_key}: {tokens} tokens ({tiempo}ms)")
                print(f"     {resultado['reporte'][:200]}...")
        print("█" * 70)
        print(f"\n  Archivo HTML COMPARATIVO guardado en: {ruta_html_comparacion}")
        print(f"  Pipeline completado exitosamente ✓")
        print("█" * 70 + "\n")

        # Abrir el HTML comparativo en el navegador
        abrir_en_navegador(ruta_html_comparacion)
    else:
        print("\n[GENERATION] ❌ Error: No se pudieron generar los reportes.")

    return reportes


# ── CLI ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RAG - Módulo ANA Evergreen: Generación de reportes agrícolas"
    )
    parser.add_argument(
        "--departamento", "-d",
        default="ANTIOQUIA",
        help="Departamento a analizar (default: ANTIOQUIA)"
    )
    parser.add_argument(
        "--cultivos", "-c",
        nargs="+",
        default=None,
        help="Cultivos a filtrar (ej: CAFÉ MAÍZ)"
    )

    args = parser.parse_args()
    ejecutar_pipeline(
        departamento=args.departamento,
        cultivos=args.cultivos
    )