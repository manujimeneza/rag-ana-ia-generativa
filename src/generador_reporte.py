"""
Módulo Generador de Reporte - Manuela
Llama a un LLM para generar el reporte narrativo.
Soporta dos proveedores:
  - Groq (GRATIS, usa Llama 3.3 70B) ← RECOMENDADO
  - Claude/Anthropic (de pago)
 
Representa el paso de GENERATION en la arquitectura RAG.
Genera reporte en HTML y lo abre automáticamente en el navegador.
"""
 
import os
import webbrowser
import re
from datetime import datetime
 
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
 
 
# ══════════════════════════════════════════════════════════════════════
# PROVEEDORES DE LLM
# ══════════════════════════════════════════════════════════════════════
 
def _llamar_groq(system_prompt: str, user_prompt: str) -> str:
    """
    Versión optimizada para el Módulo ANA usando Groq.
    """
    try:
        from groq import Groq
    except ImportError:
        print("[GENERATION] Instalando SDK de Groq...")
        os.system("pip install groq --quiet")
        from groq import Groq

    # Obtener la key del archivo .env
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key or not api_key.startswith("gsk_"):
        print("[GENERATION] ⚠️ Error: GROQ_API_KEY no encontrada o inválida en .env")
        return None

    try:
        client = Groq(api_key=api_key)

        print(f"[GENERATION] Conectando con Groq (Modelo: llama-3.3-70b-versatile)")
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6, # Un poco más bajo para reportes técnicos precisos
            max_tokens=2000, # Ampliamos un poco para reportes más detallados
            top_p=1,
            stream=False,
        )

        reporte = completion.choices[0].message.content
        
        # Métricas para el equipo (Wilfer y Manuela)
        print(f"[GENERATION] ✅ Reporte generado exitosamente")
        print(f"[GENERATION] Tokens usados: {completion.usage.total_tokens}")
        
        return reporte

    except Exception as e:
        print(f"[GENERATION] ❌ Error crítico en la llamada a Groq: {e}")
        return None
 
 
def _llamar_anthropic(system_prompt: str, user_prompt: str) -> str:
    """
    Llama a la API de Claude/Anthropic (de pago).
    """
    try:
        import anthropic
    except ImportError:
        print("[GENERATION] Instalando SDK de Anthropic...")
        os.system("pip install anthropic --quiet")
        import anthropic
 
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
 
    client = anthropic.Anthropic(api_key=api_key)
 
    print("[GENERATION] Proveedor: Claude (Anthropic)")
    print("[GENERATION] Modelo: claude-sonnet-4-20250514")
    print("[GENERATION] Esperando respuesta...")
 
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
 
    reporte = message.content[0].text
    print(f"[GENERATION] Reporte generado exitosamente via Claude")
    print(f"[GENERATION] Longitud: {len(reporte)} caracteres, ~{len(reporte.split())} palabras")
    print(f"[GENERATION] Tokens: {message.usage.input_tokens} entrada + {message.usage.output_tokens} salida")
 
    return reporte
 
 
def _llamar_openai_compatible(system_prompt: str, user_prompt: str) -> str:
    """
    Llama a cualquier API compatible con OpenAI (Together, Mistral, etc).
    Configura OPENAI_BASE_URL y OPENAI_API_KEY en .env
    """
    try:
        from openai import OpenAI
    except ImportError:
        return None
 
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
 
    if not api_key:
        return None
 
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
 
    print(f"[GENERATION] Proveedor: OpenAI-compatible ({base_url or 'api.openai.com'})")
    print(f"[GENERATION] Modelo: {model}")
 
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1500,
    )
 
    return response.choices[0].message.content
 
 
# ══════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════
 
def generar_reporte(system_prompt: str, user_prompt: str) -> str:
    """
    Genera el reporte usando el primer proveedor LLM disponible.
 
    Orden de prioridad:
    1. Groq     → GROQ_API_KEY      (GRATIS, Llama 3.3 70B)
    2. Claude   → ANTHROPIC_API_KEY  (de pago)
    3. OpenAI   → OPENAI_API_KEY     (de pago o compatible)
    4. Demo     → sin API key         (reporte de ejemplo)
    """
    print("[GENERATION] Buscando proveedor LLM disponible...")
 
    # Intentar Groq primero (gratis)
    if os.environ.get("GROQ_API_KEY"):
        try:
            resultado = _llamar_groq(system_prompt, user_prompt)
            if resultado:
                return resultado
        except Exception as e:
            print(f"[GENERATION] Error con Groq: {e}")
 
    # Intentar Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            resultado = _llamar_anthropic(system_prompt, user_prompt)
            if resultado:
                return resultado
        except Exception as e:
            print(f"[GENERATION] Error con Claude: {e}")
 
    # Intentar OpenAI-compatible
    if os.environ.get("OPENAI_API_KEY"):
        try:
            resultado = _llamar_openai_compatible(system_prompt, user_prompt)
            if resultado:
                return resultado
        except Exception as e:
            print(f"[GENERATION] Error con OpenAI: {e}")
 
    # Sin API key disponible
    print("[GENERATION] No se encontro ninguna API key configurada")
    print("[GENERATION]")
    print("[GENERATION] OPCION GRATIS (recomendada):")
    print("[GENERATION]   1. Ve a https://console.groq.com (sin tarjeta de credito)")
    print("[GENERATION]   2. Crea una cuenta y genera una API key")
    print("[GENERATION]   3. Agrega al archivo .env: GROQ_API_KEY=gsk_XXXXXXXX")
    print("[GENERATION]")
    print("[GENERATION] Generando reporte de demostracion...")
    return _reporte_demo()
 
 
# ══════════════════════════════════════════════════════════════════════
# HTML GENERATION
# ══════════════════════════════════════════════════════════════════════
 
def _markdown_a_html(texto: str) -> str:
    """Convierte markdown basico a HTML."""
    lineas = texto.strip().split("\n")
    html_lineas = []
    en_lista = False
 
    for linea in lineas:
        stripped = linea.strip()
 
        if en_lista and not stripped.startswith(("- ", "* ")) and not re.match(r'^\d+\.', stripped):
            html_lineas.append("</ul>")
            en_lista = False
 
        if stripped.startswith("## "):
            html_lineas.append(f'<h2>{stripped[3:]}</h2>')
        elif stripped.startswith("### "):
            html_lineas.append(f'<h3>{stripped[4:]}</h3>')
        elif "ALERTA" in stripped.upper():
            texto_alerta = stripped.replace("⚠", "").strip()
            html_lineas.append(f'<div class="alerta">{texto_alerta}</div>')
        elif re.match(r'^\d+\.', stripped):
            if not en_lista:
                html_lineas.append("<ul>")
                en_lista = True
            contenido = re.sub(r'^\d+\.\s*', '', stripped)
            contenido = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', contenido)
            html_lineas.append(f"<li>{contenido}</li>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not en_lista:
                html_lineas.append("<ul>")
                en_lista = True
            contenido = stripped[2:]
            contenido = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', contenido)
            html_lineas.append(f"<li>{contenido}</li>")
        elif stripped == "---":
            html_lineas.append("<hr>")
        elif stripped == "":
            html_lineas.append("")
        elif stripped.startswith("[NOTA"):
            html_lineas.append(f'<div class="nota">{stripped}</div>')
        else:
            contenido = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            html_lineas.append(f"<p>{contenido}</p>")
 
    if en_lista:
        html_lineas.append("</ul>")
 
    return "\n".join(html_lineas)
 
 
def guardar_reporte_html(reporte: str, resumen_analisis: dict = None, nombre: str = None) -> str:
    """Genera un reporte HTML profesional y lo guarda."""
    if not nombre:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"reporte_ana_{timestamp}.html"
 
    ruta = os.path.join(os.path.dirname(__file__), "..", "output", nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
 
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    departamento = resumen_analisis.get("departamento", "N/A") if resumen_analisis else "N/A"
    total_registros = resumen_analisis.get("total_registros", 0) if resumen_analisis else 0
    cultivos = resumen_analisis.get("cultivos_analizados", []) if resumen_analisis else []
    tendencia = resumen_analisis.get("tendencia_general", "N/A") if resumen_analisis else "N/A"
    alertas = resumen_analisis.get("alertas", []) if resumen_analisis else []
    metricas = resumen_analisis.get("metricas_por_cultivo", {}) if resumen_analisis else {}
 
    # Detectar proveedor usado
    if os.environ.get("GROQ_API_KEY"):
        proveedor = "Groq (Llama 3.3 70B) — GRATIS"
    elif os.environ.get("ANTHROPIC_API_KEY"):
        proveedor = "Claude (Anthropic)"
    elif os.environ.get("OPENAI_API_KEY"):
        proveedor = "OpenAI-compatible"
    else:
        proveedor = "Demo (sin API key)"
 
    # Tarjetas de cultivos
    tarjetas = ""
    for cultivo, datos in list(metricas.items())[:6]:
        rend = datos.get("rendimiento_promedio", "N/A")
        tend = datos.get("tendencia_produccion", "N/A")
        cambio = datos.get("cambio_porcentual", "N/A")
        prod = datos.get("produccion_total", "N/A")
        area = datos.get("area_total_sembrada", "N/A")
        mun = datos.get("municipios_con_cultivo", "N/A")
        if tend == "creciente":
            col = "#10b981"; ico = "&#9650;"
        elif tend == "decreciente":
            col = "#ef4444"; ico = "&#9660;"
        else:
            col = "#f59e0b"; ico = "&#9654;"
        cambio_txt = f" ({cambio}%)" if cambio != "N/A" else ""
        tarjetas += f"""
        <div class="cc"><div class="ch"><h3>{cultivo}</h3>
        <span class="bt" style="background:{col}15;color:{col};border:1px solid {col}30">{ico} {tend}{cambio_txt}</span></div>
        <div class="mg">
            <div class="m"><span class="mv">{rend}</span><span class="ml">Rendimiento (ton/ha)</span></div>
            <div class="m"><span class="mv">{prod if prod != 'N/A' else '—'}</span><span class="ml">Produccion total (t)</span></div>
            <div class="m"><span class="mv">{area if area != 'N/A' else '—'}</span><span class="ml">Area sembrada (ha)</span></div>
            <div class="m"><span class="mv">{mun if mun != 'N/A' else '—'}</span><span class="ml">Municipios</span></div>
        </div></div>"""
 
    alertas_html = ""
    for a in alertas:
        if "sin alertas" in a.lower():
            alertas_html += f'<div class="al ok">&#10003; {a}</div>'
        else:
            alertas_html += f'<div class="al">&#9888; {a}</div>'
 
    reporte_html = _markdown_a_html(reporte)
    tcol = "#ef4444" if tendencia == "decreciente" else "#10b981" if tendencia == "creciente" else "#f59e0b"
 
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte ANA - Evergreen</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0fdf4;color:#1a1a1a;line-height:1.6}}
.hd{{background:linear-gradient(135deg,#166534,#15803d 50%,#22c55e);color:#fff;padding:40px 0;text-align:center}}
.hd h1{{font-size:28px;font-weight:700;margin-bottom:6px}}
.hd p{{font-size:14px;opacity:.85}}
.hd .b{{display:inline-block;background:rgba(255,255,255,.2);padding:4px 14px;border-radius:20px;font-size:12px;margin-top:8px}}
.hd .b2{{display:inline-block;background:rgba(255,255,255,.12);padding:3px 12px;border-radius:20px;font-size:11px;margin-top:6px}}
.c{{max-width:960px;margin:0 auto;padding:0 24px}}
.sb{{display:flex;gap:1px;margin:-24px auto 32px;max-width:720px;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)}}
.st{{flex:1;background:#fff;padding:16px 12px;text-align:center}}
.sv{{font-size:22px;font-weight:700;color:#166534}}
.sl{{font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;margin-top:2px}}
.se{{background:#fff;border-radius:12px;padding:28px 32px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,.04)}}
.tt{{font-size:13px;font-weight:600;color:#166534;text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #dcfce7}}
.cg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}
.cc{{border:1px solid #e5e7eb;border-radius:10px;padding:16px;transition:box-shadow .2s}}
.cc:hover{{box-shadow:0 4px 12px rgba(0,0,0,.06)}}
.ch{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}
.ch h3{{font-size:14px;font-weight:600}}
.bt{{font-size:11px;font-weight:500;padding:2px 10px;border-radius:20px;white-space:nowrap}}
.mg{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.m{{background:#f9fafb;border-radius:8px;padding:8px 10px}}
.mv{{display:block;font-size:16px;font-weight:700;color:#166534}}
.ml{{font-size:10px;color:#6b7280}}
.al{{background:#fef2f2;border-left:4px solid #ef4444;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:8px;font-size:13px;color:#991b1b}}
.al.ok{{background:#f0fdf4;border-left-color:#22c55e;color:#166534}}
.pp{{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin:16px 0}}
.ps{{display:flex;align-items:center;gap:6px;font-size:11px;color:#6b7280}}
.pd{{width:8px;height:8px;border-radius:50%;background:#22c55e}}
.pa{{color:#d1d5db;font-size:14px}}
.rc h2{{font-size:18px;font-weight:700;color:#166534;margin:24px 0 12px;padding-bottom:6px;border-bottom:1px solid #dcfce7}}
.rc h2:first-child{{margin-top:0}}
.rc h3{{font-size:15px;font-weight:600;color:#333;margin:16px 0 8px}}
.rc p{{margin-bottom:10px;font-size:14px;color:#374151}}
.rc ul{{margin:8px 0 16px 24px}}
.rc li{{margin-bottom:6px;font-size:14px;color:#374151}}
.rc strong{{color:#166534}}
.rc hr{{border:none;border-top:1px dashed #d1d5db;margin:20px 0}}
.nota{{background:#f0f9ff;border-left:4px solid #3b82f6;padding:12px 16px;border-radius:0 8px 8px 0;font-size:12px;color:#1e40af;margin-top:16px}}
.ft{{text-align:center;padding:32px 0;font-size:12px;color:#9ca3af}}
.ft a{{color:#22c55e;text-decoration:none}}
@media print{{body{{background:#fff}}.hd{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}.se{{box-shadow:none;border:1px solid #e5e7eb}}}}
</style>
</head>
<body>
<div class="hd"><div class="c">
    <h1>Reporte Analitico Agricola</h1>
    <p>Modulo de Analitica [ANA] — Evergreen</p>
    <span class="b">Generado por RAG — {fecha}</span><br>
    <span class="b2">LLM: {proveedor}</span>
</div></div>
<div class="c">
<div class="sb">
    <div class="st"><div class="sv">{departamento}</div><div class="sl">Departamento</div></div>
    <div class="st"><div class="sv">{total_registros:,}</div><div class="sl">Registros EVA</div></div>
    <div class="st"><div class="sv">{len(cultivos)}</div><div class="sl">Cultivos</div></div>
    <div class="st"><div class="sv" style="color:{tcol}">{tendencia.upper()}</div><div class="sl">Tendencia general</div></div>
</div>
<div class="se"><div class="tt">Pipeline RAG ejecutado</div>
    <div class="pp">
        <div class="ps"><div class="pd"></div> EVA API</div><div class="pa">&#8594;</div>
        <div class="ps"><div class="pd"></div> Captura datos</div><div class="pa">&#8594;</div>
        <div class="ps"><div class="pd"></div> Analisis pandas</div><div class="pa">&#8594;</div>
        <div class="ps"><div class="pd"></div> Retrieval KB</div><div class="pa">&#8594;</div>
        <div class="ps"><div class="pd"></div> Prompt RAG</div><div class="pa">&#8594;</div>
        <div class="ps"><div class="pd"></div> LLM ({proveedor.split('(')[0].strip()})</div><div class="pa">&#8594;</div>
        <div class="ps"><div class="pd" style="background:#166534"></div> <strong>Reporte</strong></div>
    </div>
</div>
<div class="se"><div class="tt">Alertas de produccion</div>
    {alertas_html if alertas_html else '<div class="al ok">&#10003; Sin alertas criticas</div>'}
</div>
<div class="se"><div class="tt">Metricas por cultivo — Modelo ANA</div>
    <div class="cg">{tarjetas}</div>
</div>
<div class="se"><div class="tt">Reporte narrativo generado por el LLM</div>
    <div class="rc">{reporte_html}</div>
</div>
<div class="ft">
    <p>Proyecto universitario — Arquitectura y Desarrollo para IA Generativa</p>
    <p>Equipo: Carolina &middot; Wilfer &middot; Manuela</p>
    <p>Fuente: <a href="https://www.datos.gov.co/resource/2pnw-mmge.csv" target="_blank">EVA — datos.gov.co</a></p>
</div>
</div>
</body></html>"""
 
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[GENERATION] Reporte HTML guardado en: {ruta}")
    return ruta
 
 
def guardar_reporte(reporte: str, nombre: str = None) -> str:
    """Guarda el reporte en texto plano."""
    if not nombre:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"reporte_ana_{timestamp}.txt"
    ruta = os.path.join(os.path.dirname(__file__), "..", "output", nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"{'='*70}\n  REPORTE ANALITICO - MODULO ANA EVERGREEN\n")
        f.write(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*70}\n\n")
        f.write(reporte)
    print(f"[GENERATION] Reporte TXT guardado en: {ruta}")
    return ruta
 
 
def abrir_en_navegador(ruta: str):
    """Abre el reporte HTML en el navegador por defecto."""
    ruta_absoluta = os.path.abspath(ruta)
    print(f"[GENERATION] Abriendo reporte en el navegador...")
    webbrowser.open(f"file://{ruta_absoluta}")
 
 
def _reporte_demo() -> str:
    """Reporte de demostracion cuando no hay API key."""
    return """## RESUMEN EJECUTIVO
 
El analisis de las Evaluaciones Agropecuarias Municipales (EVA) para el departamento de Antioquia revela un panorama mixto en la produccion agricola. Se identificaron cultivos con rendimientos cercanos al optimo y otros con tendencias decrecientes que requieren atencion inmediata.
 
## HALLAZGOS CLAVE
 
**Hortalizas:** Presentan rendimientos variables segun el municipio y la variedad cultivada. Los municipios del oriente antioqueno muestran los mejores indicadores de productividad.
 
**Tuberculos y platanos:** El rendimiento se mantiene estable en la mayoria de municipios analizados, con produccion concentrada en zonas de clima templado y frio.
 
**Plantas aromaticas:** Con un rendimiento promedio de 0.5 ton/ha, este grupo muestra los valores mas bajos del analisis. Sin embargo, esto es esperable dado el tipo de cultivo y su alto valor por kilogramo.
 
**Frutales:** Tendencia mixta con algunos municipios mostrando crecimiento sostenido y otros con caidas asociadas a factores climaticos.
 
## ALERTAS DE PRODUCCION
 
- Las plantas aromaticas, condimentarias y medicinales presentan rendimiento bajo (0.5 ton/ha), aunque esto puede ser normal dado su alto valor comercial.
- Se detectaron municipios con caida sostenida de produccion en los ultimos 3 periodos.
 
## RECOMENDACIONES
 
1. **Plantas aromaticas:** Evaluar si el rendimiento reportado corresponde al estandar del cultivo o si hay oportunidades de mejora en practicas de cosecha y postcosecha.
 
2. **Hortalizas:** Fortalecer la asistencia tecnica en municipios con rendimientos por debajo del promedio departamental.
 
3. **General:** Implementar un sistema de monitoreo continuo basado en los umbrales del manual tecnico para detectar caidas de rendimiento tempranamente.
 
4. **Datos:** Mejorar la calidad del reporte de datos en la EVA, ya que se detectaron registros con valores inconsistentes que dificultan el analisis.
 
---
[NOTA: Este es un reporte de demostracion. Configura GROQ_API_KEY en .env para generar reportes reales con Llama 3.3 70B (gratis).]"""