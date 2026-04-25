"""
Módulo de Prompt Builder - Manuela
Construye el prompt RAG ensamblando contexto + datos + instrucciones.
Representa el paso de AUGMENTATION en la arquitectura RAG.

NOTA: Genera UN ÚNICO prompt que se usa para todos los modelos.
Esto permite comparar cómo responden los 3 modelos Groq a LA MISMA entrada.
"""

import json


def construir_prompt(resumen_analisis: dict, contexto_dominio: str) -> tuple:
    """
    Construye el prompt RAG completo para el LLM.

    UN ÚNICO prompt para todos los modelos → Comparación justa de respuestas.

    Ensamblaje:
    1. System prompt: define el rol del LLM como analista agrícola
    2. Contexto del dominio: chunks de Pinecone o KB texto plano
    3. Datos del análisis: métricas calculadas por el módulo ANA
    4. Instrucción: estructura del reporte esperado

    Args:
        resumen_analisis: Dict con métricas del análisis (output de Wilfer)
        contexto_dominio: String con el conocimiento del dominio (output de retrieval)

    Returns:
        Tupla (system_prompt, user_prompt) lista para enviar a LOS 3 MODELOS
    """
    print("[AUGMENTATION] Construyendo prompt RAG (igual para todos los modelos)...")

    # Detectar si el contexto viene de Pinecone (búsqueda semántica)
    es_pinecone = "[Chunk" in contexto_dominio or "recuperado de la base vectorial" in contexto_dominio

    if es_pinecone:
        print("[AUGMENTATION] ✓ Contexto recuperado de Pinecone (búsqueda semántica)")
    else:
        print("[AUGMENTATION] • Contexto cargado de archivo (texto plano)")

    print("[AUGMENTATION] Modelos a comparar: Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B")

    # ── 1. SYSTEM PROMPT (igual para todos) ──────────────────────────────
    system_prompt = """Eres un analista agrícola experto en cultivos colombianos, especializado en interpretar datos de las Evaluaciones Agropecuarias Municipales (EVA) del Ministerio de Agricultura de Colombia.

Tu tarea es generar reportes ejecutivos que sean:
- Claros y comprensibles para agricultores y gerentes sin formación técnica en datos
- Basados estrictamente en los datos y el contexto del dominio proporcionados
- Con recomendaciones concretas y accionables
- En español, con lenguaje profesional pero accesible
- Estructurados con: Resumen Ejecutivo, Hallazgos Clave, Alertas y Recomendaciones

IMPORTANTE: No inventes datos. Solo usa la información proporcionada en el contexto y en los resultados del análisis. Si no tienes información suficiente sobre algo, indícalo explícitamente."""

    # ── 2. USER PROMPT (igual para todos) ───────────────────────────────
    if es_pinecone:
        titulo_contexto = "CONOCIMIENTO AGRÍCOLA (Recuperado por búsqueda semántica - Pinecone)"
    else:
        titulo_contexto = "CONOCIMIENTO DEL DOMINIO AGRÍCOLA (Manual técnico)"

    user_prompt = f"""Genera un reporte analítico ejecutivo basándote en la siguiente información:

═══════════════════════════════════════════════
{titulo_contexto}:
═══════════════════════════════════════════════
{contexto_dominio}

═══════════════════════════════════════════════
RESULTADOS DEL ANÁLISIS - MÓDULO ANA EVERGREEN:
═══════════════════════════════════════════════
- Departamento: {resumen_analisis.get('departamento', 'No especificado')}
- Tipo de análisis: {resumen_analisis.get('tipo_analisis', 'descriptivo')}
- Total de registros analizados: {resumen_analisis.get('total_registros', 0)}
- Cultivos analizados: {', '.join(resumen_analisis.get('cultivos_analizados', []))}
- Tendencia general: {resumen_analisis.get('tendencia_general', 'No determinada')}

Métricas por cultivo:
{json.dumps(resumen_analisis.get('metricas_por_cultivo', {}), indent=2, ensure_ascii=False)}

Alertas detectadas:
{chr(10).join('- ' + a for a in resumen_analisis.get('alertas', ['Sin alertas críticas']))}

═══════════════════════════════════════════════
INSTRUCCIÓN DE GENERACIÓN:
═══════════════════════════════════════════════
Genera un REPORTE EJECUTIVO con la siguiente estructura:

1. **RESUMEN EJECUTIVO** (máximo 100 palabras)
   Panorama general de los hallazgos más importantes.

2. **HALLAZGOS CLAVE** (3-5 puntos)
   Para cada cultivo analizado, interpreta las métricas comparándolas
   con los estándares del manual técnico. Incluye:
   - Rendimiento actual vs rendimiento óptimo según el manual
   - Tendencia de producción (creciente/decreciente/estable)
   - Número de municipios productores

3. **ALERTAS DE PRODUCCIÓN** (si aplica)
   Cultivos o zonas con rendimiento por debajo del umbral óptimo,
   explicando las posibles causas según el contexto del dominio.

4. **RECOMENDACIONES** (3-5 puntos)
   Acciones concretas para el agricultor o gerente, basadas en
   los hallazgos y en las buenas prácticas del manual técnico.

El reporte debe tener entre 400 y 600 palabras."""

    # Estadísticas del prompt
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"[AUGMENTATION] System prompt: {len(system_prompt)} caracteres")
    print(f"[AUGMENTATION] User prompt:   {len(user_prompt)} caracteres")
    print(f"[AUGMENTATION] Total prompt:  {total_chars} caracteres (~{total_chars // 4} tokens aprox.)")
    print(f"[AUGMENTATION] ℹ️  Este MISMO prompt se usará para los 3 modelos Groq")

    return system_prompt, user_prompt


# --- Ejecución directa ---
if __name__ == "__main__":
    # Datos de prueba
    resumen_prueba = {
        "departamento": "Antioquia",
        "tipo_analisis": "descriptivo y predictivo",
        "total_registros": 120,
        "cultivos_analizados": ["CAFÉ", "MAÍZ"],
        "tendencia_general": "mixta",
        "metricas_por_cultivo": {
            "CAFÉ": {"rendimiento_promedio": 1.83, "tendencia_produccion": "decreciente", "cambio_porcentual": -3.1},
            "MAÍZ": {"rendimiento_promedio": 4.0, "tendencia_produccion": "estable", "cambio_porcentual": -6.9}
        },
        "alertas": ["ALERTA: MAÍZ muestra tendencia decreciente (-6.9%)"]
    }

    system, user = construir_prompt(resumen_prueba, "Contexto de prueba...")
    print("\n=== SYSTEM PROMPT ===")
    print(system[:300] + "...")
    print("\n=== USER PROMPT ===")
    print(user[:500] + "...")
