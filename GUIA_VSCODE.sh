# ══════════════════════════════════════════════════════════════
#  GUÍA: Configurar el proyecto RAG ANA en VS Code + Claude Code
#  Módulo de Analítica [ANA] - Evergreen
#  Autores: Carolina, Wilfer, Manuela
# ══════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────
# PASO 1: REQUISITOS PREVIOS
# ──────────────────────────────────────────────────────────────

# 1.1 Instalar Node.js 18+ (necesario para Claude Code)
#     Descargar de: https://nodejs.org/
#     Verificar con:
#         node --version   (debe ser 18 o superior)

# 1.2 Instalar Python 3.10+
#     Descargar de: https://www.python.org/downloads/
#     Verificar con:
#         python --version

# 1.3 Tener VS Code actualizado
#     Descargar de: https://code.visualstudio.com/

# 1.4 Tener una API key de Anthropic
#     Obtenerla en: https://console.anthropic.com/
#     (Necesitan cuenta, hay créditos gratuitos al registrarse)


# ──────────────────────────────────────────────────────────────
# PASO 2: INSTALAR CLAUDE CODE
# ──────────────────────────────────────────────────────────────

# OPCIÓN A: Extensión de VS Code (RECOMENDADA)
#   1. Abrir VS Code
#   2. Presionar Ctrl+Shift+X (abrir extensiones)
#   3. Buscar "Claude Code" por Anthropic
#   4. Clic en "Install"
#   5. Aparece el ícono de Spark (✦) en la barra lateral
#   6. Clic en el ícono → iniciar sesión con cuenta Anthropic

# OPCIÓN B: CLI por terminal
#   npm install -g @anthropic-ai/claude-code
#   Verificar: claude --version


# ──────────────────────────────────────────────────────────────
# PASO 3: CONFIGURAR EL PROYECTO EN VS CODE
# ──────────────────────────────────────────────────────────────

# 3.1 Descomprimir el proyecto (o clonar de GitHub)
# 3.2 Abrir la carpeta en VS Code:
#     Archivo → Abrir carpeta → seleccionar "rag-ana-evergreen"

# 3.3 Crear entorno virtual Python (en la terminal de VS Code):
#     Ctrl+` para abrir terminal, luego:

python -m venv venv

# Activar el entorno:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3.4 Instalar dependencias:
pip install -r requirements.txt

# 3.5 Configurar API key:
cp .env.example .env
# Editar .env con tu API key real:
# ANTHROPIC_API_KEY=sk-ant-api03-TU_KEY_AQUI


# ──────────────────────────────────────────────────────────────
# PASO 4: EJECUTAR EL PIPELINE RAG
# ──────────────────────────────────────────────────────────────

# Ejecutar todo el pipeline:
python src/main.py

# Con parámetros específicos:
python src/main.py --departamento ANTIOQUIA --cultivos CAFÉ MAÍZ

# Ejecutar solo un módulo:
python src/captura_datos.py       # Solo captura de datos (Wilfer)
python src/analisis_datos.py      # Solo análisis (Wilfer)
python src/generador_reporte.py   # Solo generación LLM (Manuela)

# Ejecutar tests:
python tests/test_pipeline.py


# ──────────────────────────────────────────────────────────────
# PASO 5: USAR CLAUDE CODE DENTRO DE VS CODE
# ──────────────────────────────────────────────────────────────

# Clic en el ícono ✦ (Spark) en la barra lateral de VS Code
# o usar el atajo Ctrl+Shift+P → "Claude Code: Open"

# PROMPTS ÚTILES PARA CLAUDE CODE EN ESTE PROYECTO:

# Para entender el proyecto:
#   > "Explícame la estructura de este proyecto RAG"
#   > "¿Qué hace cada archivo en src/?"

# Para ejecutar:
#   > "Ejecuta el pipeline completo con python src/main.py"
#   > "Corre los tests y dime si pasan"

# Para mejorar (EVIDENCIA para la presentación):
#   > "Agrega un nuevo cultivo PAPA al análisis"
#   > "Mejora el prompt RAG para que incluya gráficos de tendencia"
#   > "Agrega manejo de errores al módulo de captura de datos"
#   > "Crea una función que exporte el reporte a PDF"

# Para depurar:
#   > "¿Por qué el rendimiento del café sale bajo?"
#   > "Revisa si hay errores en el análisis de datos"

# Para documentar:
#   > "Genera docstrings para todas las funciones"
#   > "Crea un diagrama de flujo del pipeline en mermaid"


# ──────────────────────────────────────────────────────────────
# PASO 6: SUBIR A GITHUB (Wilfer)
# ──────────────────────────────────────────────────────────────

# Desde la terminal de VS Code:
git init
git add .
git commit -m "feat: pipeline RAG módulo ANA Evergreen"
git remote add origin https://github.com/USUARIO/rag-ana-evergreen.git
git push -u origin main


# ──────────────────────────────────────────────────────────────
# ESTRUCTURA DE ARCHIVOS EXPLICADA
# ──────────────────────────────────────────────────────────────

# rag-ana-evergreen/
# │
# ├── src/
# │   ├── captura_datos.py        # WILFER - Descarga datos de API EVA
# │   ├── analisis_datos.py       # WILFER - Calcula métricas con pandas
# │   ├── base_conocimiento.py    # MANUELA - Carga contexto del dominio (RETRIEVAL)
# │   ├── prompt_builder.py       # MANUELA - Ensambla el prompt RAG (AUGMENTATION)
# │   ├── generador_reporte.py    # MANUELA - Llama a Claude API (GENERATION)
# │   └── main.py                 # Pipeline completo que conecta todo
# │
# ├── knowledge_base/
# │   └── manual_cultivos.txt     # Base de conocimiento agrícola
# │
# ├── data/                       # Datos descargados (se genera al ejecutar)
# ├── output/                     # Reportes generados (se genera al ejecutar)
# ├── tests/
# │   └── test_pipeline.py        # Tests del pipeline
# │
# ├── requirements.txt            # Dependencias Python
# ├── .env.example                # Template para API key
# ├── .gitignore                  # Archivos excluidos de Git
# ├── CLAUDE.md                   # Contexto para Claude Code
# └── README.md                   # Documentación del proyecto
