# RAG - Módulo de Analítica [ANA] - Evergreen
## Informe Técnico Completo

**Proyecto Académico:** Arquitectura y Desarrollo para IA Generativa  
**Universidad:** Universidad de Medellín, 2025  
**Fecha:** Abril 2026  
**Equipo:** Wilfer, Manuela, Carolina

---

## 1. Resumen Ejecutivo

Este proyecto implementa una solución **RAG (Retrieval-Augmented Generation)** que genera automáticamente reportes analíticos agrícolas ejecutivos. 

El sistema captura datos reales del sector agropecuario colombiano desde la API pública EVA (datos.gov.co), realiza análisis estadísticos con pandas, recupera contexto del dominio agrícola, y utiliza Claude (Anthropic) para generar reportes narrativos que interpretan los resultados de forma comprensible para agricultores y gerentes.

**Pipeline de extremo a extremo:**
```
Datos EVA → Captura → Análisis ANA → Retrieval → Augmentation → Claude API → Reporte
```

**Resultado:** Reportes ejecutivos que traducen métricas de producción en recomendaciones accionables.

---

## 2. Arquitectura del Proyecto

### 2.1 Estructura de Directorios

```
rag-ana-ia-generativa/
├── src/                           # Código fuente (módulos del pipeline)
│   ├── captura_datos.py          # [Wilfer] Descarga datos EVA
│   ├── analisis_datos.py         # [Wilfer] Calcula métricas ANA
│   ├── base_conocimiento.py      # [Manuela] Retrieval de contexto
│   ├── prompt_builder.py         # [Manuela] Construcción prompt RAG
│   ├── generador_reporte.py      # [Manuela] Llamada API Claude + salida
│   └── main.py                   # Pipeline completo (orquestación)
│
├── data/                          # Datos descargados de EVA (CSV)
├── knowledge_base/                # Base de conocimiento agrícola
│   └── manual_cultivos.txt        # Contexto técnico de cultivos
├── output/                        # Reportes generados (TXT + HTML)
├── tests/                         # Suite de pruebas
│   └── test_pipeline.py
├── CLAUDE.md                      # Documentación de arquitectura
├── README.md                      # Guía de instalación y uso
├── requirements.txt               # Dependencias Python
└── informe_rag.md                 # Este documento
```

### 2.2 Módulos del Pipeline RAG

#### **PASO 1: CAPTURA (`captura_datos.py`) - Wilfer**

**Responsabilidad:** Obtener datos del sector agropecuario.

**Funciones principales:**
- `capturar_datos_eva(departamento, limite)`: Descarga CSV desde API pública EVA
  - URL: `https://www.datos.gov.co/resource/2pnw-mmge.csv`
  - Filtra por departamento (ej: ANTIOQUIA)
  - Normaliza nombres de columnas (lowercase, replace spaces)
  - Fallback: datos de ejemplo si la API no responde

- `guardar_datos(df, nombre)`: Persiste en `data/eva_datos.csv`

**Entrada:** Especificación de departamento (string)  
**Salida:** DataFrame de pandas con columnas normalizadas

---

#### **PASO 2: ANÁLISIS (`analisis_datos.py`) - Wilfer**

**Responsabilidad:** Calcular métricas del modelo ANA sobre los datos capturados.

**Funciones principales:**
- `analizar_datos(df)`: Calcula métricas descriptivas y predictivas
  - Detecta cultivos únicos en el dataset
  - **Por cultivo calcula:**
    - Rendimiento (ton/ha): promedio, mín, máx
    - Producción (ton): total, promedio
    - Área sembrada (ha): total
    - Municipios productores (count)
    - Tendencia: creciente/decreciente/estable (basada en cambio % anual)
  - **Alertas generadas:**
    - Rendimiento bajo (< 2.0 ton/ha)
    - Tendencia decreciente (cambio < -5%)
  
- Funciones auxiliares: `_buscar_columna()`, `_detectar_departamento()`, `_guardar_resumen()`

**Entrada:** DataFrame de EVA  
**Salida:** Diccionario con estructura:
```python
{
  "departamento": "ANTIOQUIA",
  "tipo_analisis": "descriptivo y predictivo",
  "total_registros": 120,
  "cultivos_analizados": ["CAFÉ", "MAÍZ"],
  "tendencia_general": "mixta",
  "metricas_por_cultivo": {
    "CAFÉ": {"rendimiento_promedio": 1.83, "tendencia_produccion": "decreciente", ...},
    "MAÍZ": {"rendimiento_promedio": 4.0, "tendencia_produccion": "estable", ...}
  },
  "alertas": ["ALERTA: MAÍZ muestra tendencia decreciente (-6.9%)"]
}
```

---

#### **PASO 3: RETRIEVAL (`base_conocimiento.py`) - Manuela**

**Responsabilidad:** Recuperar contexto del dominio agrícola (knowledge base).

**Funciones principales:**
- `cargar_base_conocimiento(cultivos=None)`: Carga archivos de contexto
  - Busca todos los `.txt` en `knowledge_base/`
  - Combina contenidos en un string de contexto
  - **Filtrado opcional:** Si se especifican cultivos, filtra por secciones relevantes

- `_filtrar_por_cultivos(texto, cultivos)`: Simula búsqueda semántica
  - Detecta secciones delimitadas por `---` y `==`
  - Incluye solo secciones relevantes a cultivos especificados
  - Mantiene secciones generales siempre

- Fallback: Contexto mínimo por defecto si no hay archivos

**Entrada:** Lista opcional de cultivos (para filtrado)  
**Salida:** String con contexto del dominio

**Archivo de base de conocimiento:** `knowledge_base/manual_cultivos.txt`
- Contiene rendimientos óptimos de cultivos
- Normas técnicas agrícolas colombianas
- Buenas prácticas de cultivo

---

#### **PASO 4: AUGMENTATION (`prompt_builder.py`) - Manuela**

**Responsabilidad:** Ensamblar el prompt RAG completo para el LLM.

**Funciones principales:**
- `construir_prompt(resumen_analisis, contexto_dominio)`: Crea system + user prompt
  
  **System Prompt:** Define el rol del LLM
  ```
  "Eres un analista agrícola experto en cultivos colombianos..."
  ```
  - Restricción: no inventar datos
  - Tono: profesional pero accesible
  - Estructura esperada: Resumen, Hallazgos, Alertas, Recomendaciones

  **User Prompt:** Ensamblaje de contexto + datos + instrucción
  - Sección 1: Conocimiento del dominio (del PASO 3)
  - Sección 2: Resultados del análisis (del PASO 2)
  - Sección 3: Instrucción clara de generación
  - Restricción de longitud: 400-600 palabras

**Entrada:** 
- `resumen_analisis`: Dict del PASO 2
- `contexto_dominio`: String del PASO 3

**Salida:** Tupla `(system_prompt, user_prompt)`

**Tokens estimados:** ~500-1000 tokens aprox (según contenido)

---

#### **PASO 5: GENERATION (`generador_reporte.py`) - Manuela**

**Responsabilidad:** Llamar a Claude API y generar el reporte narrativo.

**Funciones principales:**
- `generar_reporte(system_prompt, user_prompt)`: Llama a Claude
  - Modelo: `claude-3-5-sonnet-20241022` (configurable)
  - Temperatura: 0.7 (balance creatividad/precisión)
  - Max tokens: 1500
  - Captura respuesta del LLM

- `guardar_reporte(reporte, formato="txt")`: Persiste en `output/reporte_ana_TIMESTAMP.txt`

- `guardar_reporte_html(reporte, resumen_analisis=None)`: Genera HTML renderizado
  - Incluye estilos CSS
  - Integra métricas del análisis
  - Abre automáticamente en navegador

- `abrir_en_navegador(ruta_html)`: Abre el HTML generado en el navegador default

**Entrada:** 
- `system_prompt`: String con instrucciones del sistema
- `user_prompt`: String con datos + contexto + instrucción

**Salida:** 
- Reporte narrativo (String)
- Archivo TXT: `output/reporte_ana_20260422_HHMMSS.txt`
- Archivo HTML: `output/reporte_ana_20260422_HHMMSS.html`

---

#### **MAIN - Orquestación (`main.py`)**

**Responsabilidad:** Ejecutar el pipeline completo secuencialmente.

**Función principal:**
- `ejecutar_pipeline(departamento="ANTIOQUIA", cultivos=None)`: Encadena todos los pasos
  1. Captura datos de EVA
  2. Analiza datos (genera métricas)
  3. Carga base de conocimiento
  4. Construye prompt RAG
  5. Genera reporte vía Claude
  6. Guarda en TXT + HTML
  7. Abre en navegador

**CLI Arguments:**
```bash
python src/main.py --departamento ANTIOQUIA --cultivos CAFÉ MAÍZ
```

**Flujo visual en consola:**
```
█████ RAG - MÓDULO DE ANALÍTICA [ANA] - EVERGREEN █████
[CAPTURA] Descargando datos...
[ANÁLISIS] Procesando datos...
[RETRIEVAL] Cargando base de conocimiento...
[AUGMENTATION] Construyendo prompt RAG...
[GENERATION] Llamando a Claude API...
█████ REPORTE GENERADO █████
Archivo TXT guardado en: output/reporte_ana_20260422_102225.txt
Archivo HTML guardado en: output/reporte_ana_20260422_102225.html
```

---

## 3. Flujo de Datos Detallado

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CAPTURA (EVA API)                                            │
│    └─> DataFrame con columnas: departamento, cultivo, año,      │
│        area_sembrada_ha, produccion_t, rendimiento_t_ha          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. ANÁLISIS (Modelo ANA)                                        │
│    └─> Diccionario con métricas por cultivo + tendencias +      │
│        alertas de producción                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────────┐            ┌──────────────────────┐
│ 3. RETRIEVAL         │            │ knowledge_base/      │
│ (cargar contexto)    │<───────────│ manual_cultivos.txt  │
│                      │            │                      │
└──────────────┬───────┘            └──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. AUGMENTATION (Prompt RAG)                                    │
│                                                                 │
│    system_prompt: "Eres un analista agrícola..."               │
│    user_prompt:                                                 │
│    ├─ CONOCIMIENTO: [contenido knowledge_base]                 │
│    ├─ DATOS: [métricas del PASO 2]                             │
│    └─ INSTRUCCIÓN: "Genera reporte ejecutivo..."               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. GENERATION (Claude API)                                      │
│    └─> Reporte narrativo (400-600 palabras)                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
    output/                       output/
    reporte_*.txt                reporte_*.html
    (almacenamiento)             (visualización)
```

---

## 4. Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| **Python** | 3.10+ | Lenguaje principal |
| **pandas** | Latest | Análisis y transformación de datos |
| **requests** | Latest | Descargas HTTP (EVA API) |
| **anthropic** | Latest | SDK oficial de Claude |
| **python-dotenv** | Latest | Manejo de variables de entorno (.env) |
| **Claude API** | claude-3-5-sonnet | LLM para generación de reportes |

### Configuración de Claude API

```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1500,
    temperature=0.7,
    system=system_prompt,
    messages=[{"role": "user", "content": user_prompt}]
)
```

---

## 5. Ejecución del Proyecto

### 5.1 Instalación

```bash
# 1. Clonar repositorio
git clone <repo>
cd rag-ana-ia-generativa

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# o: venv\Scripts\activate      # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key
cp .env.example .env
# Editar .env y agregar ANTHROPIC_API_KEY
```

### 5.2 Ejecución

```bash
# Pipeline completo (default: ANTIOQUIA)
python src/main.py

# Con parámetros personalizados
python src/main.py --departamento BOLÍVAR --cultivos PLÁTANO ARROZ

# Alias corto
python src/main.py -d CAUCA -c CAFÉ

# Módulos individuales (debugging)
python src/captura_datos.py      # Solo captura
python src/analisis_datos.py     # Solo análisis
python src/base_conocimiento.py  # Carga contexto
python src/prompt_builder.py     # Muestra prompts
python src/generador_reporte.py  # Solo generación
```

### 5.3 Pruebas

```bash
python tests/test_pipeline.py
```

---

## 6. Fuentes de Datos

### EVA (Evaluaciones Agropecuarias)

| Campo | Fuente | Tipo |
|-------|--------|------|
| **Datos brutos** | datos.gov.co - Recurso 2pnw-mmge | CSV público |
| **Columnas** | departamento, municipio, cultivo, año, area_sembrada_ha, area_cosechada_ha, produccion_t, rendimiento_t_ha | Numérica/Categórica |
| **Cobertura** | Municipios de Colombia | Nacional |
| **Frecuencia** | Anual | Histórico: 2015+ |
| **URL** | https://www.datos.gov.co/resource/2pnw-mmge.csv | API |

### Base de Conocimiento

| Documento | Contenido | Autor |
|-----------|----------|-------|
| **manual_cultivos.txt** | Rendimientos óptimos, normas técnicas, buenas prácticas | Manuela |
| **Contexto por defecto** | Fallback si no hay archivos | Sistema |

### Datos de Ejemplo (Fallback)

Si la API no responde, el sistema usa datos simulados de Antioquia:
- Municipios: Andes, Jardín, Fredonia, Salgar
- Cultivos: Café, Maíz
- Años: 2020-2022
- Métricas realistas basadas en EVA histórico

---

## 7. Responsabilidades del Equipo

### Wilfer
- **captura_datos.py:** Descarga y normalización de API EVA
- **analisis_datos.py:** Cálculo de métricas modelo ANA
- **GitHub:** Gestión del repositorio
- **Datos:** Fuentes y validación

### Manuela
- **base_conocimiento.py:** Retrieval de contexto del dominio
- **prompt_builder.py:** Ingeniería del prompt RAG
- **generador_reporte.py:** Integración Claude API + salida (TXT/HTML)
- **arquitectura.md / CLAUDE.md:** Documentación técnica
- **informe_rag.md:** Este documento

### Carolina
- **Documentación:** Especificación funcional en Word
- **Presentación:** PPTX para exposición
- **Reportes:** Resumenes ejecutivos

---

## 8. Ejemplos de Reportes Generados

### Muestra de Reporte Ejecutivo

```
═════════════════════════════════════════════════════════════════

                       REPORTE ANALÍTICO - MÓDULO ANA
                    Evaluación Agropecuaria - Antioquia
                              Abril 2026

═════════════════════════════════════════════════════════════════

RESUMEN EJECUTIVO
─────────────────
En Antioquia se analizaron 120 registros de cultivos (Café, Maíz) 
con tendencia mixta. El café muestra rendimiento estable (1.83 ton/ha)
pero con tendencia decreciente (-3.1% anual). El maíz mantiene 
rendimiento óptimo (4.0 ton/ha) pero con caída en producción (-6.9%).

HALLAZGOS CLAVE
───────────────
1. CAFÉ: Rendimiento de 1.83 ton/ha está por debajo del óptimo 
   (1.8-2.2). Producida en 3 municipios. Tendencia decreciente.

2. MAÍZ: Rendimiento de 4.0 ton/ha es óptimo (4.0-6.5). Producida 
   en 2 municipios. Producción en caída.

3. COBERTURA: 5 municipios analizados en total.

ALERTAS
───────
⚠️  CAFÉ muestra tendencia decreciente (-3.1% anual)
⚠️  MAÍZ muestra tendencia decreciente (-6.9% anual)

RECOMENDACIONES
────────────────
1. Investigar causas de decrecimiento: plagas, clima, prácticas
2. Implementar sistema de rotación de cultivos
3. Capacitación en nuevas técnicas agrícolas
4. Considerar cultivos complementarios para diversificar riesgo

═════════════════════════════════════════════════════════════════
Generado: 22/04/2026 10:22:25 | LLM: Claude 3.5 Sonnet
═════════════════════════════════════════════════════════════════
```

---

## 9. Variables de Entorno

### .env (requerido)

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
DEPARTAMENTO_DEFAULT=ANTIOQUIA
LOG_LEVEL=INFO
```

---

## 10. Convenciones del Código

### Nombres y Prefijos

- **Módulos:** snake_case en español (captura_datos.py, prompt_builder.py)
- **Funciones:** snake_case en español (construir_prompt, cargar_base_conocimiento)
- **Constantes:** UPPER_SNAKE_CASE
- **Print de debug:** Prefijos identificadores:
  - `[CAPTURA]` - datos de EVA
  - `[ANÁLISIS]` - métricas del modelo
  - `[RETRIEVAL]` - contexto del dominio
  - `[AUGMENTATION]` - construcción del prompt
  - `[GENERATION]` - llamada API Claude

### Estructura del Código

```python
"""
Módulo de Nombre - Autor
Descripción una línea del propósito.
Representa el paso X en la arquitectura RAG.
"""

# 1. Imports
# 2. Función principal
# 3. Funciones auxiliares (con prefijo _)
# 4. Fallbacks / valores por defecto
# 5. Bloque main: if __name__ == "__main__"
```

---

## 11. Limitaciones y Futuros Mejoras

### Limitaciones Actuales

1. **Retrieval simplificado:** Busca por texto literal, no semántica
2. **Base de conocimiento estática:** 100-200 cultivos máximo
3. **Sin chunking:** Contexto completo en un solo prompt
4. **Sin vector DB:** No hay embeddings ni búsqueda semántica real
5. **Ventana de contexto:** Limitada por max_tokens de Claude
6. **Sin caché:** Cada ejecución es una llamada nueva a API

### Mejoras Futuras

1. **Retrieval semántico:** Integrar Chroma o Pinecone con embeddings
2. **Chunking adaptativo:** Dividir documentos largos inteligentemente
3. **Caché de prompts:** Reutilizar prompts similares
4. **Feedback loop:** Validar reportes con expertos agrícolas
5. **Dashboard interactivo:** Visualización web de métricas
6. **Multi-idioma:** Soporte para reportes en inglés/portugués
7. **Pronósticos:** Predicciones de producción futura
8. **Análisis geoespacial:** Mapas de rendimiento por región

---

## 12. Conclusiones

Este proyecto implementa exitosamente un **pipeline RAG completo de extremo a extremo** que:

✅ **Integra múltiples fuentes:** API pública + knowledge base + LLM  
✅ **Automatiza reportes:** De datos crudos a narrativa ejecutiva  
✅ **Aplica contexto:** Utiliza conocimiento del dominio agrícola  
✅ **Genera valor:** Reportes accionables para agricultores  
✅ **Demuestra arquitectura:** Separación clara de responsabilidades RAG  

**Es un ejemplo educativo robusto de cómo combinar:**
- Web scraping / APIs públicas
- Data analytics con pandas
- Ingeniería de prompts
- Integración con LLMs
- Generación de documentos

---

## 13. Referencias y Recursos

### Documentación
- CLAUDE.md: Arquitectura del proyecto
- README.md: Guía de instalación rápida
- test_pipeline.py: Pruebas unitarias

### APIs
- [EVA - datos.gov.co](https://www.datos.gov.co/resource/2pnw-mmge.csv)
- [Anthropic Claude API](https://docs.anthropic.com/)

### Librerías
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [anthropic-python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [python-dotenv](https://python-dotenv.readthedocs.io/)

---

**Fin del informe técnico**  
*Generado: 22/04/2026*  
*Versión del proyecto: Feature RAG-ANA-Evergreen*
