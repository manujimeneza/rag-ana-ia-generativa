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
# IMPORTANTE: Aquí agregamos guardar_reporte_html y abrir_en_navegador
from generador_reporte import generar_reporte, guardar_reporte, guardar_reporte_html, abrir_en_navegador


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

    # ── PASO 3: RETRIEVAL - Base de conocimiento (Manuela) ────────────
    print("─" * 50)
    print("  PASO 3: Retrieval - Base de conocimiento (Manuela)")
    print("─" * 50)
    cultivos_detectados = cultivos or resumen.get("cultivos_analizados", [])
    contexto = cargar_base_conocimiento(cultivos=cultivos_detectados)

    # ── PASO 4: AUGMENTATION - Construcción del prompt (Manuela) ──────
    print("─" * 50)
    print("  PASO 4: Augmentation - Prompt RAG (Manuela)")
    print("─" * 50)
    system_prompt, user_prompt = construir_prompt(resumen, contexto)

    # ── PASO 5: GENERATION - Llamada al LLM (Manuela) ────────────────
    print("─" * 50)
    print("  PASO 5: Generation - LLM API (Manuela)")
    print("─" * 50)
    reporte = generar_reporte(system_prompt, user_prompt)

    # ── GUARDAR Y MOSTRAR RESULTADO ──────────────────────────────────
    if reporte:
        # Guardamos en TXT
        ruta_txt = guardar_reporte(reporte)
        
        # 🟢 NUEVO: Guardamos en HTML pasando el 'resumen' generado en el paso 2
        ruta_html = guardar_reporte_html(reporte, resumen_analisis=resumen)

        print("\n" + "█" * 70)
        print("  REPORTE GENERADO:")
        print("█" * 70)
        print(reporte)
        print("█" * 70)
        print(f"\n  Archivo TXT guardado en: {ruta_txt}")
        print(f"  Archivo HTML guardado en: {ruta_html}")
        print(f"  Pipeline completado exitosamente ✓")
        print("█" * 70 + "\n")

        # 🟢 NUEVO: Abrimos el HTML generado
        abrir_en_navegador(ruta_html)
    else:
        print("\n[GENERATION] ❌ Error: No se pudo generar el reporte.")

    return reporte


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