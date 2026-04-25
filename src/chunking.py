"""
Módulo de Chunking - División inteligente de la knowledge base
Divide los documentos de conocimiento agrícola en fragmentos con metadatos.
"""

import os
import re


def chunkear_archivo(ruta_archivo: str) -> list[dict]:
    """
    Divide un archivo de texto en chunks respetando la estructura natural.

    Estructura reconocida:
    - == SECCIÓN == → secciones generales (estándares, glosario)
    - --- CULTIVO --- → secciones específicas de cultivos

    Args:
        ruta_archivo: Ruta al archivo .txt

    Returns:
        Lista de chunks con estructura: {
            "id": "archivo_001",
            "texto": "contenido del chunk",
            "cultivo": "CAFÉ" | "general",
            "tipo": "cultivo_especifico" | "estandares" | "glosario",
            "archivo": "manual_cultivos.txt"
        }
    """
    print(f"[CHUNKING] Leyendo archivo: {ruta_archivo}")

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    nombre_archivo = os.path.basename(ruta_archivo)
    chunks = []
    contador = 0

    # Dividir por separadores principales (== o ---)
    # Primero separamos por líneas para preservar estructura
    lineas = contenido.split("\n")
    chunk_actual = []
    encabezado_actual = None
    cultivo_actual = "general"
    tipo_actual = "general"

    for linea in lineas:
        stripped = linea.strip()

        # Detectar encabezados de sección general
        if stripped.startswith("==") and stripped.endswith("=="):
            # Guardar chunk anterior si existe
            if chunk_actual:
                texto_chunk = "\n".join(chunk_actual).strip()
                if len(texto_chunk) > 20:  # Evitar chunks vacíos
                    chunks.append({
                        "id": f"{nombre_archivo.replace('.txt', '')}_{contador:03d}",
                        "texto": texto_chunk,
                        "cultivo": cultivo_actual,
                        "tipo": tipo_actual,
                        "archivo": nombre_archivo
                    })
                    contador += 1
                chunk_actual = []

            encabezado_actual = stripped
            tipo_actual = _detectar_tipo_seccion(stripped)
            cultivo_actual = "general"

        # Detectar encabezados de cultivo específico
        elif stripped.startswith("---") and stripped.endswith("---"):
            # Guardar chunk anterior
            if chunk_actual:
                texto_chunk = "\n".join(chunk_actual).strip()
                if len(texto_chunk) > 20:
                    chunks.append({
                        "id": f"{nombre_archivo.replace('.txt', '')}_{contador:03d}",
                        "texto": texto_chunk,
                        "cultivo": cultivo_actual,
                        "tipo": tipo_actual,
                        "archivo": nombre_archivo
                    })
                    contador += 1
                chunk_actual = []

            encabezado_actual = stripped
            cultivo_actual = _extraer_cultivo(stripped)
            tipo_actual = "cultivo_especifico"

        # Acumular contenido en chunk
        if stripped:  # No agregar líneas completamente vacías
            chunk_actual.append(linea)
        elif chunk_actual and len(chunk_actual) > 0:  # Preservar saltos de párrafo
            chunk_actual.append("")

    # Guardar último chunk
    if chunk_actual:
        texto_chunk = "\n".join(chunk_actual).strip()
        if len(texto_chunk) > 20:
            chunks.append({
                "id": f"{nombre_archivo.replace('.txt', '')}_{contador:03d}",
                "texto": texto_chunk,
                "cultivo": cultivo_actual,
                "tipo": tipo_actual,
                "archivo": nombre_archivo
            })

    print(f"[CHUNKING] Total chunks generados: {len(chunks)}")
    for chunk in chunks[:3]:  # Mostrar primeros 3
        print(f"  - {chunk['id']}: {chunk['cultivo']} ({chunk['tipo']}) - {len(chunk['texto'])} caracteres")

    return chunks


def chunkear_knowledge_base(ruta_kb: str = None) -> list[dict]:
    """
    Chunkea todos los archivos .txt en la knowledge_base.

    Args:
        ruta_kb: Ruta a la carpeta knowledge_base (si None, usa ruta estándar)

    Returns:
        Lista acumulada de todos los chunks
    """
    if ruta_kb is None:
        ruta_kb = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

    if not os.path.exists(ruta_kb):
        print(f"[CHUNKING] ⚠️ Carpeta no encontrada: {ruta_kb}")
        return []

    print(f"[CHUNKING] Procesando knowledge_base: {ruta_kb}")

    chunks_totales = []
    archivos_procesados = 0

    for archivo in sorted(os.listdir(ruta_kb)):
        if archivo.endswith(".txt"):
            ruta_archivo = os.path.join(ruta_kb, archivo)
            chunks = chunkear_archivo(ruta_archivo)
            chunks_totales.extend(chunks)
            archivos_procesados += 1

    print(f"[CHUNKING] ✅ {archivos_procesados} archivo(s) procesados")
    print(f"[CHUNKING] Total chunks acumulados: {len(chunks_totales)}")

    return chunks_totales


def _detectar_tipo_seccion(encabezado: str) -> str:
    """Detecta el tipo de sección según el encabezado."""
    texto_lower = encabezado.lower()

    if "glosario" in texto_lower:
        return "glosario"
    elif "estándar" in texto_lower or "estandar" in texto_lower:
        return "estandares"
    elif "reporte" in texto_lower:
        return "estandares_reporte"
    else:
        return "general"


def _extraer_cultivo(encabezado: str) -> str:
    """Extrae el nombre del cultivo del encabezado --- CULTIVO ---."""
    # Remover los guiones y espacios
    cultivo = encabezado.strip("-").strip().upper()
    return cultivo if cultivo else "general"


# ─────────────────────────────────────────────────────────────────────────────
# Pruebas directas
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("MÓDULO DE CHUNKING - PRUEBA DIRECTA")
    print("=" * 70 + "\n")

    chunks = chunkear_knowledge_base()

    print("\n" + "─" * 70)
    print("Muestra de chunks generados:")
    print("─" * 70)

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n[Chunk {i}]")
        print(f"  ID: {chunk['id']}")
        print(f"  Cultivo: {chunk['cultivo']}")
        print(f"  Tipo: {chunk['tipo']}")
        print(f"  Archivo: {chunk['archivo']}")
        print(f"  Longitud: {len(chunk['texto'])} caracteres")
        print(f"  Vista previa: {chunk['texto'][:100]}...")
