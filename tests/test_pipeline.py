"""
Tests básicos del pipeline RAG ANA
Ejecutar: python -m pytest tests/test_pipeline.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from captura_datos import capturar_datos_eva, _datos_ejemplo
from analisis_datos import analizar_datos
from base_conocimiento import cargar_base_conocimiento
from prompt_builder import construir_prompt


def test_datos_ejemplo():
    """Verifica que los datos de ejemplo se cargan correctamente."""
    df = _datos_ejemplo()
    assert len(df) > 0
    assert "cultivo" in df.columns
    assert "rendimiento_t_ha" in df.columns
    print("✓ test_datos_ejemplo pasó")


def test_analisis():
    """Verifica que el análisis genera métricas correctas."""
    df = _datos_ejemplo()
    resumen = analizar_datos(df)
    assert "cultivos_analizados" in resumen
    assert "metricas_por_cultivo" in resumen
    assert len(resumen["cultivos_analizados"]) > 0
    print("✓ test_analisis pasó")


def test_base_conocimiento():
    """Verifica que la base de conocimiento se carga."""
    contexto = cargar_base_conocimiento()
    assert len(contexto) > 0
    assert "café" in contexto.lower() or "rendimiento" in contexto.lower()
    print("✓ test_base_conocimiento pasó")


def test_prompt_builder():
    """Verifica que el prompt se construye correctamente."""
    resumen = {
        "departamento": "Antioquia",
        "tipo_analisis": "descriptivo",
        "total_registros": 10,
        "cultivos_analizados": ["CAFÉ"],
        "tendencia_general": "estable",
        "metricas_por_cultivo": {"CAFÉ": {"rendimiento_promedio": 1.8}},
        "alertas": ["Sin alertas"]
    }
    system, user = construir_prompt(resumen, "Contexto de prueba")
    assert "analista agrícola" in system.lower()
    assert "Antioquia" in user
    assert "CAFÉ" in user
    print("✓ test_prompt_builder pasó")


if __name__ == "__main__":
    test_datos_ejemplo()
    test_analisis()
    test_base_conocimiento()
    test_prompt_builder()
    print("\n✓ Todos los tests pasaron exitosamente")
