"""
Módulo de Vector DB - Gestión de Pinecone Serverless
Inicializa, maneja y consulta el índice vectorial en Pinecone.
"""

import os
import time

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("[VECTOR_DB] Instalando pinecone...")
    os.system("pip install pinecone --quiet")
    from pinecone import Pinecone, ServerlessSpec

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Configuración
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
NOMBRE_INDICE = os.getenv("PINECONE_INDEX_NAME", "rag-ana-evergreen")
REGION = os.getenv("PINECONE_REGION", "us-east-1")
DIMENSIONES = 384
METRICA = "cosine"
NAMESPACE = "knowledge_base"

# Variable global para cachear cliente
_cliente_pinecone = None
_indice_pinecone = None


def inicializar_pinecone() -> Pinecone:
    """
    Inicializa el cliente de Pinecone.

    Returns:
        Cliente de Pinecone conectado
    """
    global _cliente_pinecone

    if _cliente_pinecone is not None:
        return _cliente_pinecone

    if not PINECONE_API_KEY or not PINECONE_API_KEY.startswith("pcsk_"):
        print(f"[VECTOR_DB] ⚠️ PINECONE_API_KEY no configurada o inválida en .env")
        return None

    try:
        print(f"[VECTOR_DB] Inicializando Pinecone...")
        _cliente_pinecone = Pinecone(api_key=PINECONE_API_KEY)
        print(f"[VECTOR_DB] ✅ Cliente Pinecone conectado")
        return _cliente_pinecone
    except Exception as e:
        print(f"[VECTOR_DB] ❌ Error al conectar con Pinecone: {e}")
        return None


def obtener_o_crear_indice(pc: Pinecone = None) -> object:
    """
    Obtiene el índice Pinecone o lo crea si no existe.

    Args:
        pc: Cliente Pinecone (si None, llama a inicializar_pinecone)

    Returns:
        Índice de Pinecone
    """
    global _indice_pinecone

    if _indice_pinecone is not None:
        return _indice_pinecone

    if pc is None:
        pc = inicializar_pinecone()
        if pc is None:
            return None

    try:
        # Listar índices existentes
        indices_existentes = pc.list_indexes()
        nombres_indice = [idx.name for idx in indices_existentes]

        if NOMBRE_INDICE in nombres_indice:
            print(f"[VECTOR_DB] Usando índice existente: {NOMBRE_INDICE}")
            _indice_pinecone = pc.Index(NOMBRE_INDICE)
        else:
            print(f"[VECTOR_DB] Creando nuevo índice: {NOMBRE_INDICE}")
            print(f"[VECTOR_DB]   - Dimensiones: {DIMENSIONES}")
            print(f"[VECTOR_DB]   - Métrica: {METRICA}")
            print(f"[VECTOR_DB]   - Región: {REGION}")

            pc.create_index(
                name=NOMBRE_INDICE,
                dimension=DIMENSIONES,
                metric=METRICA,
                spec=ServerlessSpec(cloud="aws", region=REGION)
            )

            # Esperar a que el índice se cree
            time.sleep(10)
            _indice_pinecone = pc.Index(NOMBRE_INDICE)
            print(f"[VECTOR_DB] ✅ Índice creado exitosamente")

        return _indice_pinecone

    except Exception as e:
        print(f"[VECTOR_DB] ❌ Error al obtener/crear índice: {e}")
        return None


def subir_chunks(chunks_con_embeddings: list[dict], indice: object = None) -> dict:
    """
    Sube chunks con sus embeddings a Pinecone.

    Args:
        chunks_con_embeddings: Lista de dicts con estructura:
            {
                "id": "manual_cultivos_001",
                "texto": "contenido del chunk",
                "embedding": [lista de floats],
                "cultivo": "CAFÉ",
                "tipo": "cultivo_especifico",
                "archivo": "manual_cultivos.txt"
            }
        indice: Índice de Pinecone (si None, obtiene el default)

    Returns:
        Dict con estadísticas: {"total": int, "exitosos": int, "errores": int}
    """
    if indice is None:
        pc = inicializar_pinecone()
        indice = obtener_o_crear_indice(pc)
        if indice is None:
            return {"total": 0, "exitosos": 0, "errores": 0}

    print(f"[VECTOR_DB] Subiendo {len(chunks_con_embeddings)} chunks a Pinecone...")

    # Preparar vectores para upsert (formato: (id, vector, metadata))
    vectores_a_subir = []
    for chunk in chunks_con_embeddings:
        vector_tuple = (
            chunk["id"],
            chunk["embedding"],
            {
                "texto": chunk["texto"],
                "cultivo": chunk["cultivo"],
                "tipo": chunk["tipo"],
                "archivo": chunk["archivo"]
            }
        )
        vectores_a_subir.append(vector_tuple)

    # Subir en batches para evitar límites
    batch_size = 100
    total_exitosos = 0
    total_errores = 0

    for i in range(0, len(vectores_a_subir), batch_size):
        batch = vectores_a_subir[i:i+batch_size]
        try:
            indice.upsert(vectors=batch, namespace=NAMESPACE)
            total_exitosos += len(batch)
            print(f"[VECTOR_DB] ✓ Batch {i//batch_size + 1}: {len(batch)} vectores subidos")
        except Exception as e:
            print(f"[VECTOR_DB] ✗ Error en batch {i//batch_size + 1}: {e}")
            total_errores += len(batch)

    print(f"[VECTOR_DB] ✅ Upload completado: {total_exitosos} exitosos, {total_errores} errores")
    return {
        "total": len(chunks_con_embeddings),
        "exitosos": total_exitosos,
        "errores": total_errores
    }


def buscar_similares(
    query_embedding: list[float],
    indice: object = None,
    top_k: int = 5,
    filtro: dict = None
) -> list[dict]:
    """
    Busca chunks similares a un embedding de query.

    Args:
        query_embedding: Vector de la query (lista de 384 floats)
        indice: Índice de Pinecone (si None, obtiene el default)
        top_k: Número de resultados a retornar
        filtro: Filtro de metadatos, ej: {"cultivo": "CAFÉ"}

    Returns:
        Lista de chunks similares con scores, ej:
        [
            {
                "id": "manual_cultivos_001",
                "score": 0.95,
                "texto": "...",
                "cultivo": "CAFÉ",
                "tipo": "cultivo_especifico",
                "archivo": "manual_cultivos.txt"
            }
        ]
    """
    if indice is None:
        pc = inicializar_pinecone()
        indice = obtener_o_crear_indice(pc)
        if indice is None:
            return []

    try:
        # Buscar con filtro opcional
        resultados = indice.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=NAMESPACE,
            include_metadata=True,
            filter=filtro  # None si no hay filtro
        )

        # Procesar resultados
        chunks_recuperados = []
        for match in resultados.matches:
            chunk = {
                "id": match.id,
                "score": match.score,
                **match.metadata  # Expande los metadatos (texto, cultivo, tipo, archivo)
            }
            chunks_recuperados.append(chunk)

        print(f"[VECTOR_DB] ✅ Búsqueda completada: {len(chunks_recuperados)} chunks similares encontrados")
        return chunks_recuperados

    except Exception as e:
        print(f"[VECTOR_DB] ❌ Error en búsqueda: {e}")
        return []


def obtener_estadisticas_indice(indice: object = None) -> dict:
    """
    Obtiene estadísticas del índice (total de vectores, etc).

    Returns:
        Dict con estadísticas
    """
    if indice is None:
        pc = inicializar_pinecone()
        indice = obtener_o_crear_indice(pc)
        if indice is None:
            return {}

    try:
        stats = indice.describe_index_stats()
        return {
            "total_vectores": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespaces": stats.namespaces if hasattr(stats, 'namespaces') else {}
        }
    except Exception as e:
        print(f"[VECTOR_DB] Error obteniendo estadísticas: {e}")
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Pruebas directas
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("MÓDULO DE VECTOR DB - PRUEBA DIRECTA")
    print("=" * 70 + "\n")

    # Prueba 1: Inicializar Pinecone
    print("[PRUEBA 1] Inicializando Pinecone...")
    pc = inicializar_pinecone()
    if not pc:
        print("No se pudo conectar a Pinecone. Verifica PINECONE_API_KEY en .env")
    else:
        print("✅ Conectado\n")

        # Prueba 2: Obtener o crear índice
        print("[PRUEBA 2] Obteniendo o creando índice...")
        indice = obtener_o_crear_indice(pc)
        if indice:
            print("✅ Índice disponible\n")

            # Prueba 3: Estadísticas
            print("[PRUEBA 3] Estadísticas del índice:")
            stats = obtener_estadisticas_indice(indice)
            print(f"  Total vectores: {stats.get('total_vectores', '?')}")
            print(f"  Dimensión: {stats.get('dimension', '?')}\n")
