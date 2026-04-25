"""
Script de Indexación - DEPRECATED (No es necesario ejecutar)

⚠️  NOTA: Este script ya NO es necesario.

La indexación ahora es COMPLETAMENTE AUTOMÁTICA:
- Cuando ejecutas: python src/main.py
- Si Pinecone está vacío, automáticamente indexa la KB
- No requiere intervención del usuario

Este archivo se mantiene como RESPALDO/REFERENCIA para:
1. Reindexar manualmente si lo necesitas
2. Entender el proceso de indexación
3. Referencia para debugging

Uso (solo si quieres reindexar manualmente):
    python src/indexar_conocimiento.py
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.dirname(__file__))

from chunking import chunkear_knowledge_base
from embeddings import cargar_modelo, generar_embeddings_batch
from vector_db import inicializar_pinecone, obtener_o_crear_indice, subir_chunks, obtener_estadisticas_indice


def indexar_knowledge_base():
    """
    Pipeline completo de indexación:
    1. Chunkea la knowledge_base
    2. Genera embeddings con HuggingFace
    3. Sube a Pinecone
    4. Muestra estadísticas
    """

    print("\n" + "█" * 70)
    print("  INDEXACIÓN DE KNOWLEDGE BASE EN PINECONE")
    print("  Script: Carga la base de conocimiento en la DB vectorial")
    print("█" * 70 + "\n")

    # ── PASO 1: CHUNKING ──────────────────────────────────────────────────
    print("─" * 50)
    print("  PASO 1: Chunking de knowledge_base")
    print("─" * 50)
    chunks = chunkear_knowledge_base()

    if not chunks:
        print("\n❌ Error: No se generaron chunks. Verifica knowledge_base/")
        return

    # ── PASO 2: EMBEDDINGS ────────────────────────────────────────────────
    print("\n" + "─" * 50)
    print("  PASO 2: Generación de embeddings")
    print("─" * 50)

    modelo = cargar_modelo()

    # Extraer textos para embedding
    textos = [chunk["texto"] for chunk in chunks]

    # Generar embeddings en batch
    print(f"\n[INDEXACIÓN] Generando {len(textos)} embeddings...")
    embeddings = generar_embeddings_batch(textos, modelo)

    if not embeddings:
        print("\n❌ Error: No se generaron embeddings")
        return

    # Agregar embeddings a los chunks
    chunks_con_embeddings = []
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
        chunks_con_embeddings.append(chunk)

    print(f"[INDEXACIÓN] ✅ {len(chunks_con_embeddings)} chunks con embeddings generados")

    # ── PASO 3: INICIALIZAR PINECONE ──────────────────────────────────────
    print("\n" + "─" * 50)
    print("  PASO 3: Conexión a Pinecone")
    print("─" * 50)

    pc = inicializar_pinecone()
    if not pc:
        print("\n❌ Error: No se pudo conectar a Pinecone")
        print("    Verifica PINECONE_API_KEY en .env")
        return

    # ── PASO 4: OBTENER O CREAR ÍNDICE ───────────────────────────────────
    print("\n" + "─" * 50)
    print("  PASO 4: Obtener o crear índice")
    print("─" * 50)

    indice = obtener_o_crear_indice(pc)
    if not indice:
        print("\n❌ Error: No se pudo obtener o crear el índice")
        return

    # ── PASO 5: VERIFICAR SI YA ESTÁ INDEXADO ────────────────────────────
    print("\n" + "─" * 50)
    print("  PASO 5: Verificación de indexación previa")
    print("─" * 50)

    stats = obtener_estadisticas_indice(indice)
    total_vectores = stats.get("total_vectores", 0)

    if total_vectores > 0:
        print(f"\n[INDEXACIÓN] ⚠️  Índice ya contiene {total_vectores} vectores")
        respuesta = input("¿Reindexar completamente? (s/n): ").strip().lower()

        if respuesta != 's':
            print("\n✅ Indexación abortada. El índice ya tiene vectores.")
            print(f"   Total de vectores: {total_vectores}")
            return

    # ── PASO 6: SUBIR CHUNKS A PINECONE ───────────────────────────────────
    print("\n" + "─" * 50)
    print("  PASO 6: Subir chunks a Pinecone")
    print("─" * 50)

    resultado = subir_chunks(chunks_con_embeddings, indice)

    # ── PASO 7: ESTADÍSTICAS FINALES ──────────────────────────────────────
    print("\n" + "─" * 50)
    print("  PASO 7: Estadísticas finales")
    print("─" * 50)

    stats_finales = obtener_estadisticas_indice(indice)

    print("\n✅ INDEXACIÓN COMPLETADA")
    print("─" * 50)
    print(f"  Chunks procesados:  {resultado['total']}")
    print(f"  Upload exitoso:     {resultado['exitosos']}")
    print(f"  Upload con errores: {resultado['errores']}")
    print(f"  Total en Pinecone:  {stats_finales.get('total_vectores', 0)} vectores")
    print(f"  Dimensión:          {stats_finales.get('dimension', '?')}")
    print("─" * 50 + "\n")

    # ── INFORMACIÓN PARA VERIFICAR ────────────────────────────────────────
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Verifica en https://app.pinecone.io que los vectores se subieron")
    print("   2. Ejecuta: python src/base_conocimiento.py")
    print("   3. Ejecuta: python src/main.py")
    print("\n" + "█" * 70 + "\n")


if __name__ == "__main__":
    indexar_knowledge_base()
