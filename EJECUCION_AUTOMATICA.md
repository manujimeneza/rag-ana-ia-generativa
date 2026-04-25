# Ejecución Automática del RAG - Guía Simplificada

## ✅ Ahora es completamente automático

Ya **NO necesitas** ejecutar scripts de indexación manualmente. Todo ocurre automáticamente.

---

## 🚀 Flujo completamente automatizado

```
python src/main.py
     ↓
[PASO 1] Captura datos EVA
     ↓
[PASO 2] Análisis con pandas
     ↓
[PASO 3] RETRIEVAL SEMÁNTICO
     │
     └─→ ¿Pinecone vacío?
         ├─ SÍ  → Indexa automáticamente:
         │       ├─ Chunkea KB
         │       ├─ Genera embeddings
         │       └─ Sube a Pinecone
         │       (Primera ejecución: ~2-3 min)
         │
         └─ NO  → Usa índice existente
                  (Ejecuciones siguientes: ~10-20 seg)
     ↓
[PASO 4] Construye prompt
     ↓
[PASO 5] Ejecuta 3 modelos Groq
     ↓
Genera HTML comparativo
```

---

## 💻 Instrucciones de uso

### Requisito previo (una sola vez)

1. **Configura el `.env`:**
   ```bash
   cp .env.example .env
   # Edita .env con:
   # - GROQ_API_KEY (obtén en https://console.groq.com)
   # - PINECONE_API_KEY (obtén en https://app.pinecone.io)
   # - PINECONE_INDEX_NAME=rag-ana-evergreen
   ```

### Ejecución

**Primera vez (indexa automáticamente):**
```bash
python src/main.py
```

Verás:
```
[RETRIEVAL] ⏳ Verificando estado de Pinecone...
[RETRIEVAL] 📚 KB vacía. Iniciando indexación AUTOMÁTICA...
[RETRIEVAL] [1/3] Chunkendo knowledge_base...
[RETRIEVAL] [2/3] Generando 15 embeddings...
[RETRIEVAL] [3/3] Subiendo 15 vectores a Pinecone...
[RETRIEVAL] ✅ INDEXACIÓN COMPLETADA AUTOMÁTICAMENTE
[RETRIEVAL] 🎉 KB lista para búsqueda semántica
```

**Veces siguientes (usa índice existente):**
```bash
python src/main.py
```

Verás:
```
[RETRIEVAL] ✓ KB ya indexada en Pinecone (15 vectores)
```

### Con parámetros
```bash
python src/main.py --departamento ANTIOQUIA --cultivos CAFÉ MAÍZ
```

---

## 📊 Resultado final

El script generará:
- **Reporte comparativo HTML** con 3 tabs (GPT-OSS 120B, Llama 3.3, Qwen 3)
- **Reporte TXT** con el primer modelo exitoso
- Se abre automáticamente en tu navegador

---

## 🔄 Si necesitas reindexar

Si cambias los archivos en `knowledge_base/`, puedes reindexar manualmente:

```bash
python src/indexar_conocimiento.py
```

Pero **normalmente no es necesario** — simplemente ejecuta `main.py` de nuevo.

---

## 🐛 Troubleshooting

### Error: "PyTorch >= 2.4 is required"
```bash
pip install --upgrade torch
```

### Error: "PINECONE_API_KEY no configurada"
- Verifica que `.env` existe y tiene `PINECONE_API_KEY=...`
- No uses la key vieja (la del chat está comprometida)

### Error: "No se pudo conectar a Pinecone"
- Verifica tu conexión a internet
- Verifica que la API key es válida
- Intenta recargar la página de Pinecone console

---

## ✨ Características automatizadas

| Tarea | Antes | Ahora |
|-------|-------|-------|
| Indexar KB | `python indexar_conocimiento.py` | Automático en `main.py` |
| Buscar | Manual en Pinecone | Automático con query |
| Generar reportes | Un modelo | 3 modelos en paralelo |
| Visualizar resultados | Necesitaba procesar manualmente | HTML comparativo automático |

---

## 📝 Notas

- La indexación ocurre **solo una vez** (en la primera ejecución)
- Las ejecuciones siguientes son mucho más rápidas
- No hay efectos secundarios — es seguro ejecutar `main.py` múltiples veces
- El índice se mantiene en Pinecone (no se elimina entre ejecuciones)

---

**¡Listo para usar!** Ejecuta:
```bash
python src/main.py
```
