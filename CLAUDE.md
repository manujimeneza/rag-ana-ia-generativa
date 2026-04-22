# RAG - Módulo de Analítica [ANA] - Evergreen

## Contexto del proyecto
Este es un proyecto universitario del curso "Arquitectura y Desarrollo para IA Generativa" de la Universidad de Medellín, 2025. Implementa una funcionalidad RAG (Retrieval-Augmented Generation) para el módulo de Analítica (ANA) del sistema Evergreen.

## Qué hace
Genera automáticamente reportes analíticos agrícolas. Toma datos reales del sector agropecuario colombiano (API EVA de datos.gov.co), los analiza con pandas, y usa Claude (Anthropic) para generar un reporte narrativo ejecutivo.

## Pipeline RAG
1. **Captura** (`src/captura_datos.py`): Descarga datos de la API pública EVA
2. **Análisis** (`src/analisis_datos.py`): Calcula métricas con pandas (rendimiento, tendencias, alertas)
3. **Retrieval** (`src/base_conocimiento.py`): Carga contexto del dominio agrícola desde `knowledge_base/`
4. **Augmentation** (`src/prompt_builder.py`): Ensambla el prompt RAG (system + contexto + datos + instrucción)
5. **Generation** (`src/generador_reporte.py`): Llama a la API de Claude y captura el reporte

## Ejecutar
```bash
python src/main.py
python src/main.py --departamento ANTIOQUIA --cultivos CAFÉ MAÍZ
python tests/test_pipeline.py
```

## Entidades del módulo ANA
- **ProyectoDeAnalitica**: Contenedor del proyecto analítico
- **DataSet / Entrada**: Datos de EVA cargados
- **Modelo**: Análisis descriptivo/predictivo ejecutado
- **Salida**: Métricas calculadas
- **Reporte**: Reporte narrativo generado por el LLM
- **DashBoard**: Visualización de alertas
- **Etapa**: Fases del proyecto (Descriptivo, Diagnóstico, Predictivo, Prescriptivo)
- **AnalisisGeoespacial**: Análisis por zona geográfica

## Tecnologías
- Python 3.10+, pandas, requests
- anthropic SDK (Claude API)
- python-dotenv para manejo de API keys

## Equipo
- **Wilfer**: captura_datos.py, analisis_datos.py, GitHub
- **Manuela**: base_conocimiento.py, prompt_builder.py, generador_reporte.py, arquitectura
- **Carolina**: documentación Word y presentación PPTX

## Fuentes de datos
- EVA API: https://www.datos.gov.co/resource/2pnw-mmge.csv
- Agronet: https://www.agronet.gov.co/estadistica/

## Convenciones
- Todo el código está en español (nombres de funciones, variables, docstrings)
- Los prints de debug usan prefijos: [CAPTURA], [ANÁLISIS], [RETRIEVAL], [AUGMENTATION], [GENERATION]
- Los reportes se guardan en `output/` con timestamp
