"""
Módulo de Base de Conocimiento - Manuela
Carga y gestiona el contexto del dominio agrícola para el RAG.
Representa el paso de RETRIEVAL en la arquitectura RAG.

AUTOMÁTICO: Detecta si la KB está indexada en Pinecone.
Si no, la indexa automáticamente sin intervención del usuario.
"""

import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from embeddings import generar_embedding, cargar_modelo, generar_embeddings_batch
    from vector_db import inicializar_pinecone, obtener_o_crear_indice, buscar_similares, obtener_estadisticas_indice, subir_chunks
    from chunking import chunkear_knowledge_base
    PINECONE_DISPONIBLE = True
except ImportError:
    PINECONE_DISPONIBLE = False


def cargar_base_conocimiento(cultivos: list = None, query: str = None) -> str:
    """
    Carga el contexto del dominio agrícola mediante búsqueda semántica en Pinecone.

    AUTOMÁTICO: Si Pinecone está vacío, indexa la KB automáticamente.

    Estrategia:
    1. Verifica si Pinecone ya tiene vectores indexados
    2. Si está vacío: chunkea KB → genera embeddings → sube a Pinecone (automático)
    3. Busca semánticamente en Pinecone
    4. Si Pinecone falla: fallback a carga de texto

    Args:
        cultivos: Lista de cultivos para filtrar (ej: ["CAFÉ", "MAÍZ"])
        query: Query de búsqueda semántica (ej: "rendimiento del café")
               Si None, se construye automáticamente

    Returns:
        String con el contexto del dominio relevante
    """
    print("[RETRIEVAL] Cargando base de conocimiento del dominio agrícola...")

    # Si query no se proporciona, construirla
    if query is None:
        if cultivos:
            query = f"rendimiento producción características {' '.join(cultivos).lower()}"
        else:
            query = "rendimiento producción cultivos agrícolas"

    # Intentar búsqueda semántica con Pinecone
    if PINECONE_DISPONIBLE:
        # AUTOMÁTICO: Verificar e indexar si es necesario
        _verificar_e_indexar_si_necesario()

        contexto = _buscar_con_pinecone(query, cultivos)
        if contexto:
            return contexto

    # Fallback a carga de texto
    print("[RETRIEVAL] ⚠️  Pinecone no disponible. Usando fallback (carga de texto)...")
    return _cargar_texto_completo(cultivos)


def _verificar_e_indexar_si_necesario():
    """
    Verifica si la KB ya está indexada en Pinecone.
    Si está vacía, la indexa automáticamente SIN intervención del usuario.
    """
    try:
        print("\n[RETRIEVAL] ⏳ Verificando estado de Pinecone...")

        pc = inicializar_pinecone()
        if not pc:
            print("[RETRIEVAL] ⚠️  No se pudo conectar a Pinecone")
            return

        indice = obtener_o_crear_indice(pc)
        if not indice:
            print("[RETRIEVAL] ⚠️  No se pudo obtener índice Pinecone")
            return

        # Obtener estadísticas
        stats = obtener_estadisticas_indice(indice)
        total_vectores = stats.get("total_vectores", 0)

        if total_vectores > 0:
            print(f"[RETRIEVAL] ✓ KB ya indexada en Pinecone ({total_vectores} vectores)")
            return

        # ────────────────────────────────────────────────────────────────────
        # INDEXACIÓN AUTOMÁTICA - El usuario NO necesita hacer nada
        # ────────────────────────────────────────────────────────────────────
        print("\n[RETRIEVAL] 📚 KB vacía. Iniciando indexación AUTOMÁTICA...")
        print("[RETRIEVAL] (Esto ocurre solo una sola vez)\n")

        # Paso 1: Chunking
        print("[RETRIEVAL] [1/3] Chunkendo knowledge_base...")
        chunks = chunkear_knowledge_base()

        if not chunks:
            print("[RETRIEVAL] ❌ Error: No se generaron chunks")
            return

        # Paso 2: Generar embeddings
        print(f"[RETRIEVAL] [2/3] Generando {len(chunks)} embeddings...")
        modelo = cargar_modelo()
        textos = [chunk["texto"] for chunk in chunks]
        embeddings = generar_embeddings_batch(textos, modelo)

        if not embeddings:
            print("[RETRIEVAL] ❌ Error: No se generaron embeddings")
            return

        # Agregar embeddings a los chunks
        chunks_con_embeddings = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
            chunks_con_embeddings.append(chunk)

        # Paso 3: Subir a Pinecone
        print(f"[RETRIEVAL] [3/3] Subiendo {len(chunks_con_embeddings)} vectores a Pinecone...")
        resultado = subir_chunks(chunks_con_embeddings, indice)

        print(f"\n[RETRIEVAL] ✅ INDEXACIÓN COMPLETADA AUTOMÁTICAMENTE")
        print(f"[RETRIEVAL]    Total: {resultado['exitosos']} vectores indexados")
        print(f"[RETRIEVAL]    Errores: {resultado['errores']}")
        print(f"[RETRIEVAL] 🎉 KB lista para búsqueda semántica\n")

    except Exception as e:
        print(f"[RETRIEVAL] ⚠️  Error en indexación automática: {e}")
        print(f"[RETRIEVAL] Continuando con fallback (texto plano)...")


def _buscar_con_pinecone(query: str, cultivos: list = None) -> str:
    """
    Busca chunks similares en Pinecone usando embeddings.

    Args:
        query: String con la búsqueda
        cultivos: Lista de cultivos para filtro de metadatos

    Returns:
        Contexto concatenado de chunks similares, o None si falla
    """
    try:
        print("[RETRIEVAL] Conectando a Pinecone...")
        pc = inicializar_pinecone()
        if not pc:
            print("[RETRIEVAL] ❌ No se pudo inicializar Pinecone")
            return None

        indice = obtener_o_crear_indice(pc)
        if not indice:
            print("[RETRIEVAL] ❌ No se pudo obtener índice Pinecone")
            return None

        # Generar embedding de la query
        print(f"[RETRIEVAL] Generando embedding para query: '{query}'")
        modelo = cargar_modelo()
        query_embedding = generar_embedding(query, modelo)

        # Construir filtro de metadatos si se especificaron cultivos
        filtro = None
        if cultivos:
            # Pinecone permite filtrar por metadatos
            # Buscamos chunks cuyo cultivo esté en la lista
            filtro = {
                "$or": [{"cultivo": {"$eq": c.upper()}} for c in cultivos] + [{"cultivo": {"$eq": "general"}}]
            }

        # Buscar chunks similares
        top_k = int(os.getenv("RETRIEVAL_TOP_K", "5"))
        print(f"[RETRIEVAL] Buscando {top_k} chunks similares en Pinecone...")
        chunks = buscar_similares(query_embedding, indice, top_k, filtro)

        if not chunks:
            print("[RETRIEVAL] ⚠️  No se encontraron chunks similares en Pinecone")
            return None

        # Concatenar chunks con separadores
        contexto = _formatear_contexto_chunks(chunks)

        print(f"[RETRIEVAL] ✅ Contexto recuperado: {len(contexto)} caracteres")
        print(f"[RETRIEVAL] Chunks recuperados:")
        for chunk in chunks:
            print(f"  - {chunk['id']}: {chunk['cultivo']} (score: {chunk['score']:.3f})")

        return contexto

    except Exception as e:
        print(f"[RETRIEVAL] ❌ Error en búsqueda Pinecone: {e}")
        return None


def _formatear_contexto_chunks(chunks: list[dict]) -> str:
    """
    Formatea los chunks recuperados como un contexto coherente.

    Args:
        chunks: Lista de chunks con metadatos

    Returns:
        String formateado
    """
    lineas = []
    lineas.append("═" * 70)
    lineas.append("CONTEXTO DEL DOMINIO AGRÍCOLA (recuperado de la base vectorial)")
    lineas.append("═" * 70 + "\n")

    for i, chunk in enumerate(chunks, 1):
        lineas.append(f"[Chunk {i} - {chunk['cultivo']}] (relevancia: {chunk['score']:.1%})")
        lineas.append("-" * 50)
        lineas.append(chunk['texto'])
        lineas.append("")

    return "\n".join(lineas)


def _cargar_texto_completo(cultivos: list = None) -> str:
    """
    Fallback: carga texto plano de la knowledge_base (método antiguo).

    Args:
        cultivos: Lista de cultivos para filtrar

    Returns:
        String con el contexto
    """
    ruta_kb = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
    contexto_completo = ""

    if os.path.exists(ruta_kb):
        for archivo in sorted(os.listdir(ruta_kb)):
            if archivo.endswith(".txt"):
                ruta_archivo = os.path.join(ruta_kb, archivo)
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    contexto_completo += contenido + "\n\n"
                print(f"[RETRIEVAL] Cargado: {archivo} ({len(contenido)} caracteres)")
    else:
        print(f"[RETRIEVAL] No se encontró la carpeta: {ruta_kb}")
        contexto_completo = _contexto_por_defecto()

    if cultivos:
        contexto_filtrado = _filtrar_por_cultivos(contexto_completo, cultivos)
        print(f"[RETRIEVAL] Contexto filtrado para: {', '.join(cultivos)}")
        print(f"[RETRIEVAL] Tamaño del contexto: {len(contexto_filtrado)} caracteres")
        return contexto_filtrado

    print(f"[RETRIEVAL] Tamaño total del contexto: {len(contexto_completo)} caracteres")
    return contexto_completo


def _filtrar_por_cultivos(texto: str, cultivos: list) -> str:
    """Filtra el contexto para secciones relevantes a los cultivos dados."""
    lineas = texto.split("\n")
    resultado = []
    incluir = False
    seccion_general = True

    for linea in lineas:
        if linea.strip().startswith("---") and any(c.upper() in linea.upper() for c in cultivos):
            incluir = True
            seccion_general = False
        elif linea.strip().startswith("---") and not any(c.upper() in linea.upper() for c in cultivos):
            incluir = False
            seccion_general = False
        elif linea.strip().startswith("=="):
            incluir = True
            seccion_general = True

        if incluir or seccion_general:
            resultado.append(linea)

    return "\n".join(resultado)


def _contexto_por_defecto() -> str:
    """Contexto mínimo si no hay archivos en knowledge_base/"""
    return """
    Contexto agrícola general:
    - El rendimiento óptimo del café en Colombia es de 1.8-2.2 ton/ha
    - El rendimiento óptimo del maíz tecnificado es de 4.0-6.5 ton/ha
    - Rendimientos por debajo de estos umbrales indican posibles problemas
    - Un reporte debe ser comprensible para un agricultor sin formación técnica en datos
    """


# --- Ejecución directa ---
if __name__ == "__main__":
    # Cargar todo
    print("=== Carga completa ===")
    contexto = cargar_base_conocimiento()
    print(f"\nPrimeros 500 caracteres:\n{contexto[:500]}...")

    # Cargar filtrado por cultivo
    print("\n=== Carga filtrada (CAFÉ) ===")
    contexto_cafe = cargar_base_conocimiento(cultivos=["CAFÉ"])
    print(f"\nPrimeros 500 caracteres:\n{contexto_cafe[:500]}...")
