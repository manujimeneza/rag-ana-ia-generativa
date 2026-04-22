# RAG - Módulo de Analítica [ANA] - Evergreen

## Generación Automática de Reportes Analíticos Agrícolas

Proyecto universitario del curso **Arquitectura y Desarrollo para IA Generativa**.  
Implementación de una funcionalidad RAG (Retrieval-Augmented Generation) para el módulo de Analítica de Evergreen.

### Integrantes
- **Carolina** — Documentación y Presentación
- **Wilfer** — Captura de datos, análisis y GitHub
- **Manuela** — Implementación RAG, prompt engineering y arquitectura

---

## ¿Qué hace este proyecto?

Toma datos reales del sector agropecuario colombiano (EVA - datos.gov.co), los analiza con pandas, y usa un LLM (Claude de Anthropic) para generar automáticamente un reporte narrativo ejecutivo que interpreta los resultados del análisis.

```
EVA API → Captura datos → Análisis pandas → Prompt RAG → Claude API → Reporte narrativo
```

## Estructura del Proyecto

```
rag-ana-evergreen/
├── src/
│   ├── captura_datos.py        # Wilfer: captura desde API EVA
│   ├── analisis_datos.py       # Wilfer: métricas con pandas
│   ├── base_conocimiento.py    # Manuela: carga del contexto del dominio
│   ├── prompt_builder.py       # Manuela: construcción del prompt RAG
│   ├── generador_reporte.py    # Manuela: llamada a Claude API
│   └── main.py                 # Pipeline completo
├── data/                       # Datos descargados de EVA
├── knowledge_base/             # Documentos del dominio agrícola
│   └── manual_cultivos.txt     # Manual técnico de referencia
├── output/                     # Reportes generados
├── tests/
│   └── test_pipeline.py        # Tests básicos
├── requirements.txt
├── .env.example
└── README.md
```

## Requisitos

- Python 3.10+
- PyCharm (IDE)
- Cuenta en Anthropic con API key

## Instalación

```bash
# 1. Clonar el repo
git clone https://github.com/<usuario>/rag-ana-evergreen.git
cd rag-ana-evergreen

# 2. Crear entorno virtual en PyCharm o por terminal
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key
cp .env.example .env
# Editar .env y agregar tu ANTHROPIC_API_KEY
```

## Uso

```bash
# Ejecutar el pipeline completo
python src/main.py

# O ejecutar cada paso individual:
python src/captura_datos.py       # Solo captura
python src/analisis_datos.py      # Solo análisis
python src/generador_reporte.py   # Solo generación del reporte
```

## Uso con Claude Code

Este proyecto se puede desarrollar y depurar con [Claude Code](https://docs.claude.com/en/docs/claude-code/overview):

```bash
# Instalar Claude Code
npm install -g @anthropic-ai/claude-code

# Abrir el proyecto
cd rag-ana-evergreen
claude

# Ejemplos de prompts para Claude Code:
# > "Ejecuta el pipeline completo y muéstrame el reporte generado"
# > "Mejora el prompt RAG para incluir alertas de producción"
# > "Agrega un nuevo cultivo al análisis"
```

## Fuentes de Datos

| Fuente | URL | Descripción |
|--------|-----|-------------|
| EVA - datos.gov.co | https://www.datos.gov.co/resource/2pnw-mmge.csv | Evaluaciones Agropecuarias Municipales |
| Agronet | https://www.agronet.gov.co/estadistica/ | Históricos de producción y rendimiento |

## Tecnologías

- **Python 3.10+** — Lenguaje principal
- **pandas** — Análisis de datos
- **anthropic** — SDK oficial de Claude
- **python-dotenv** — Manejo de variables de entorno
- **Claude (Anthropic)** — LLM para generación de reportes

## Licencia

Proyecto académico - Universidad de Medellín, 2025
