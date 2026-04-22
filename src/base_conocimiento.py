"""
Módulo de Base de Conocimiento - Manuela
Carga y gestiona el contexto del dominio agrícola para el RAG.
Representa el paso de RETRIEVAL en la arquitectura RAG.
"""

import os


def cargar_base_conocimiento(cultivos: list = None) -> str:
    """
    Carga la base de conocimiento del dominio agrícola.
    En un RAG completo esto sería una búsqueda semántica en una vector DB.
    Para el alcance del curso, cargamos los archivos de texto relevantes.

    Args:
        cultivos: Lista de cultivos para filtrar el contexto (opcional)

    Returns:
        String con el contexto del dominio relevante
    """
    print("[RETRIEVAL] Cargando base de conocimiento del dominio agrícola...")

    ruta_kb = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
    contexto_completo = ""

    # Cargar todos los archivos .txt de la base de conocimiento
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

    # Filtrar por cultivos si se especifican (simulación de búsqueda semántica)
    if cultivos:
        contexto_filtrado = _filtrar_por_cultivos(contexto_completo, cultivos)
        print(f"[RETRIEVAL] Contexto filtrado para: {', '.join(cultivos)}")
        print(f"[RETRIEVAL] Tamaño del contexto: {len(contexto_filtrado)} caracteres")
        return contexto_filtrado

    print(f"[RETRIEVAL] Tamaño total del contexto: {len(contexto_completo)} caracteres")
    return contexto_completo


def _filtrar_por_cultivos(texto: str, cultivos: list) -> str:
    """
    Filtra el contexto para incluir solo secciones relevantes a los cultivos dados.
    Simula la búsqueda semántica de un RAG completo.
    """
    lineas = texto.split("\n")
    resultado = []
    incluir = False
    seccion_general = True

    for linea in lineas:
        # Detectar inicio de sección de cultivo
        if linea.strip().startswith("---") and any(c.upper() in linea.upper() for c in cultivos):
            incluir = True
            seccion_general = False
        elif linea.strip().startswith("---") and not any(c.upper() in linea.upper() for c in cultivos):
            incluir = False
            seccion_general = False
        elif linea.strip().startswith("=="):
            incluir = True  # Secciones generales siempre se incluyen
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
