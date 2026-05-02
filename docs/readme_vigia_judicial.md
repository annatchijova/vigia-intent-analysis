# VIGÍA Judicial Sanitization Toolkit
## Para análisis forense de incoherencias procesales

### Archivos incluidos

1. **`sanitize_judicial.py`** — Script de sanitización de PII en documentos judiciales
2. **`vigia_procedural_prompt.md`** — Prompt de sistema para análisis de absurdo procesal

### Requisitos

```bash
pip install pymupdf
# Opcional para NER mejorado:
pip install spacy
python -m spacy download es_core_news_md
```

### Uso básico

```bash
# Sanitizar un solo PDF
python sanitize_judicial.py documento.pdf -o ./output

# Sanitizar directorio completo con spaCy NER
python sanitize_judicial.py ./pdfs/ -o ./output --spacy

# Agregar nombres personalizados a sanitizar
python sanitize_judicial.py documento.pdf --names "Joaquín" "Pedro" "Alexia"
```

### Pipeline completo

```bash
# 1. Extraer y sanitizar
python sanitize_judicial.py ./expediente/*.pdf -o ./sanitized --spacy

# 2. Analizar con VIGÍA (usando Ollama local)
# Copiar el prompt de vigia_procedural_prompt.md como system prompt
# Feedear el texto sanitizado como user input

# 3. Verificar que no quedó PII
# Revisar manualmente los archivos *_SANITIZED.txt
```

### Seguridad

- El script genera un **salt persistente** (`.sanitization_salt`) para hashing consistente
- Los mappings se guardan en JSON con permisos `0o600` (solo owner)
- Todo el procesamiento es **local**, sin llamadas a API externas
- El salt y el mapping son necesarios para revertir — guardalos seguros

### Advertencias

- Este toolkit es para **análisis forense interno**, no para presentación en tribunales
- Los tokens sanitizados permiten compartir documentos para análisis sin exponer PII
- La reversión requiere el salt + mapping original — sin ellos, la sanitización es irreversible
- **NO reemplaza asesoramiento legal**. Es herramienta de organización y análisis estructural.

### Modelos recomendados en Ollama (según tu lista)

Para análisis de razonamiento forense:
- `huihui_ai/acereason-nemotron-abliterated:14b` — razonamiento abductivo, bueno para VIGÍA
- `mirage335/Qwen-3-VL-30B-A3B-virtuoso` — Qwen 30B, excelente para análisis profundo
- `mirage335/Llama-3_3-Nemotron-Super-49B-v1_5-virtuoso` — 49B, el más potente de tu lista
- `deepseek-r1:8b` — razonamiento step-by-step, bueno para devil's advocate

Para sanitización NER (si no usás spaCy):
- Cualquiera de los Qwen o Llama funcionan para NER básico en español

### Comando ejemplo con Ollama

```bash
# Usar acereason-nemotron para análisis VIGÍA
cat sanitized_output/documento_SANITIZED.txt | ollama run huihui_ai/acereason-nemotron-abliterated:14b --system "$(cat vigia_procedural_prompt.md)"
```

---
**VIGÍA AI Collective** — Open Source Forensic Intelligence
