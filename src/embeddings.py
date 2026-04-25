"""
Módulo de Embeddings - Generación de vectores con HuggingFace
Utiliza sentence-transformers para generar embeddings en español.
"""

import os

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("[EMBEDDINGS] Instalando sentence-transformers...")
    os.system("pip install sentence-transformers --quiet")
    from sentence_transformers import SentenceTransformer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Configuración
MODELO_DEFAULT = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
DIMENSIONES_DEFAULT = int(os.getenv("EMBEDDING_DIMENSION", "384"))

# Variable global para cachear el modelo
_modelo_cacheado = None


def cargar_modelo(nombre_modelo: str = None) -> SentenceTransformer:
    """
    Carga el modelo de embeddings.
    Se cachea en memoria para no recargar en múltiples llamadas.

    Args:
        nombre_modelo: Nombre del modelo HuggingFace (ej: 'paraphrase-multilingual-MiniLM-L12-v2')
                      Si None, usa el de la env o el default.

    Returns:
        Modelo SentenceTransformer cargado
    """
    global _modelo_cacheado

    if _modelo_cacheado is not None:
        return _modelo_cacheado

    nombre = nombre_modelo or MODELO_DEFAULT

    print(f"[EMBEDDINGS] Cargando modelo: {nombre}")
    print(f"[EMBEDDINGS] (Primera ejecución descargará ~130MB del modelo)")

    modelo = SentenceTransformer(nombre)
    _modelo_cacheado = modelo

    print(f"[EMBEDDINGS] ✅ Modelo cargado. Dimensión: {modelo.get_sentence_embedding_dimension()}")

    return modelo


def generar_embedding(texto: str, modelo: SentenceTransformer = None) -> list[float]:
    """
    Genera un embedding (vector) para un texto.

    Args:
        texto: Texto a vectorizar
        modelo: Modelo SentenceTransformer (si None, carga el default)

    Returns:
        Lista de floats (vector de 384 dimensiones)
    """
    if modelo is None:
        modelo = cargar_modelo()

    # SentenceTransformer.encode retorna numpy array, convertir a lista
    vector = modelo.encode(texto, convert_to_tensor=False)
    return vector.tolist() if hasattr(vector, 'tolist') else list(vector)


def generar_embeddings_batch(textos: list[str], modelo: SentenceTransformer = None) -> list[list[float]]:
    """
    Genera embeddings para una lista de textos (más eficiente en batch).

    Args:
        textos: Lista de textos a vectorizar
        modelo: Modelo SentenceTransformer (si None, carga el default)

    Returns:
        Lista de vectores (cada uno lista de 384 floats)
    """
    if modelo is None:
        modelo = cargar_modelo()

    if not textos:
        return []

    print(f"[EMBEDDINGS] Generando embeddings para {len(textos)} textos...")

    # SentenceTransformer.encode con lista retorna matriz
    vectores = modelo.encode(textos, convert_to_tensor=False, show_progress_bar=True)

    # Convertir a lista de listas
    return [v.tolist() if hasattr(v, 'tolist') else list(v) for v in vectores]


def obtener_dimension_modelo(modelo: SentenceTransformer = None) -> int:
    """
    Obtiene la dimensión del modelo de embeddings.

    Returns:
        Número de dimensiones (normalmente 384)
    """
    if modelo is None:
        modelo = cargar_modelo()

    return modelo.get_sentence_embedding_dimension()


# ─────────────────────────────────────────────────────────────────────────────
# Pruebas directas
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("MÓDULO DE EMBEDDINGS - PRUEBA DIRECTA")
    print("=" * 70 + "\n")

    # Prueba 1: Cargar modelo
    print("[PRUEBA 1] Cargando modelo...")
    modelo = cargar_modelo()
    print(f"Modelo cargado: {modelo}")
    print(f"Dimensión: {obtener_dimension_modelo(modelo)}\n")

    # Prueba 2: Un embedding individual
    print("[PRUEBA 2] Generando embedding individual...")
    texto_prueba = "El rendimiento óptimo del café en Colombia es de 1.8-2.2 ton/ha"
    embedding = generar_embedding(texto_prueba, modelo)
    print(f"Texto: {texto_prueba}")
    print(f"Vector (primeros 5 valores): {embedding[:5]}")
    print(f"Longitud del vector: {len(embedding)}\n")

    # Prueba 3: Batch de embeddings
    print("[PRUEBA 3] Generando batch de embeddings...")
    textos = [
        "Rendimiento del maíz tecnificado",
        "Plagas del café",
        "Ciclo de producción de la papa"
    ]
    embeddings = generar_embeddings_batch(textos, modelo)
    print(f"Textos procesados: {len(embeddings)}")
    for i, (texto, emb) in enumerate(zip(textos, embeddings)):
        print(f"  [{i}] {texto} → vector de {len(emb)} dims")
