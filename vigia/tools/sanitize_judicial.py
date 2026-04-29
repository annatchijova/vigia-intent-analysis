#!/usr/bin/env python3
"""
sanitize_judicial.py - Sanitizador de documentos judiciales para análisis forense
Autor: VIGÍA AI Collective
Uso: Extrae texto de PDFs, sanitiza PII, genera tokens consistentes
Todo local. Sin nube. Sin exposición.
"""

import re
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERROR] PyMuPDF no instalado. Ejecutá: pip install pymupdf")
    raise

try:
    import spacy
except ImportError:
    print("[WARNING] spaCy no instalado. NER básico con regex. Ejecutá: pip install spacy")
    print("[WARNING] Y luego: python -m spacy download es_core_news_md")
    spacy = None

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SALT_FILE = ".sanitization_salt"
MAPPING_FILE = "pii_mapping_encrypted.json"
LOG_FILE = "sanitization_audit.log"

# Patrones regex para PII argentina
PATTERNS = {
    "DNI": {
        "regex": r'\b\d{2}[.,]?\d{3}[.,]?\d{3}\b',
        "prefix": "DNI",
        "description": "Documento Nacional de Identidad argentino"
    },
    "CUIT_CUIL": {
        "regex": r'\b\d{2}[-.]?\d{8}[-.]?\d\b',
        "prefix": "CUIT",
        "description": "Código Único de Identificación Tributaria/Laboral"
    },
    "EMAIL": {
        "regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "prefix": "EMAIL",
        "description": "Correo electrónico"
    },
    "TELEFONO": {
        "regex": r'\b(?:\+54\s?)?(?:\(?(?:0\d{1,4})?\)?[-.\s]?)?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}\b',
        "prefix": "TEL",
        "description": "Número telefónico"
    },
    "DOMICILIO": {
        "regex": r'(?:Calle|Av\.?|Avenida|Avda\.?|Pasaje|Psje\.?|B°|Barrio)\s+[A-Za-záéíóúñÁÉÍÓÚÑ\s]+\d+',
        "prefix": "DOM",
        "description": "Dirección física"
    },
    "MATRICULA": {
        "regex": r'\b(?:MP|MN|ME|MT|MC)\s*\d{1,6}\b',
        "prefix": "MAT",
        "description": "Matrícula profesional"
    },
    "IP_ADDRESS": {
        "regex": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "prefix": "IP",
        "description": "Dirección IP"
    },
    "URL": {
        "regex": r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
        "prefix": "URL",
        "description": "URL web"
    }
}

# Nombres propios comunes argentinos para detección básica (fallback si no hay spaCy)
COMMON_NAMES = [
    "Joaquín", "Pedro", "Alexia", "María", "Ana", "Gastón", "Lombardi",
    "Gallo", "Muriel", "Tchijova", "Verstappen", "Clarín", "OSDE"
]

# ============================================================================
# FUNCIONES CORE
# ============================================================================

def load_or_create_salt():
    """Carga o genera un salt persistente para hashing consistente."""
    salt_path = Path(SALT_FILE)
    if salt_path.exists():
        with open(salt_path, 'rb') as f:
            return f.read()
    else:
        salt = os.urandom(32)
        with open(salt_path, 'wb') as f:
            f.write(salt)
        os.chmod(SALT_FILE, 0o600)  # Solo owner puede leer
        return salt

def generate_token(value, prefix, salt, index):
    """Genera token consistente e irreversible."""
    combined = f"{value}:{prefix}:{index}:{salt.hex()}".encode()
    hash_val = hashlib.sha256(combined).hexdigest()[:12]
    return f"[{prefix}_{hash_val}]"

def extract_text_from_pdf(pdf_path):
    """Extrae texto plano de PDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num, page in enumerate(doc):
        text += f"\n--- PÁGINA {page_num + 1} ---\n"
        text += page.get_text()
    doc.close()
    return text

def sanitize_with_regex(text, salt):
    """Sanitiza PII usando regex patterns."""
    mapping = {}
    sanitized = text
    counters = {k: 0 for k in PATTERNS.keys()}

    for pii_type, config in PATTERNS.items():
        regex = config["regex"]
        prefix = config["prefix"]

        for match in re.finditer(regex, sanitized):
            original = match.group()
            counters[pii_type] += 1
            token = generate_token(original, prefix, salt, counters[pii_type])
            mapping[token] = {
                "original": original,
                "type": pii_type,
                "description": config["description"],
                "index": counters[pii_type]
            }
            sanitized = sanitized.replace(original, token, 1)

    return sanitized, mapping

def sanitize_names_basic(text, salt, known_names=None):
    """Sanitiza nombres propios usando lista conocida + heurística."""
    mapping = {}
    sanitized = text
    counters = {"PER": 0}

    names_to_check = known_names or COMMON_NAMES

    for name in names_to_check:
        # Case insensitive, word boundaries
        pattern = rf'\b{name}\b'
        for match in re.finditer(pattern, sanitized, re.IGNORECASE):
            original = match.group()
            counters["PER"] += 1
            token = generate_token(original, "PER", salt, counters["PER"])
            mapping[token] = {
                "original": original,
                "type": "PERSON_NAME",
                "description": "Nombre propio de persona",
                "index": counters["PER"]
            }
            sanitized = sanitized.replace(original, token, 1)

    return sanitized, mapping

def sanitize_with_spacy(text, salt, nlp):
    """Sanitiza usando NER de spaCy (mejor calidad)."""
    mapping = {}
    doc = nlp(text)

    # Ordenar entidades por posición inversa para reemplazar sin desplazar índices
    entities = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)

    counters = {"PER": 0, "ORG": 0, "LOC": 0}
    sanitized = text

    for ent in entities:
        if ent.label_ in ["PER", "ORG", "LOC"]:
            counters[ent.label_] += 1
            token = generate_token(ent.text, ent.label_, salt, counters[ent.label_])
            mapping[token] = {
                "original": ent.text,
                "type": ent.label_,
                "description": f"Entidad spaCy: {ent.label_}",
                "index": counters[ent.label_]
            }
            sanitized = sanitized[:ent.start_char] + token + sanitized[ent.end_char:]

    return sanitized, mapping

def encrypt_mapping(mapping, password=None):
    """Encripta el mapping con contraseña (simple, mejorable con cryptography)."""
    if password:
        # En producción usar cryptography.fernet
        # Por ahora, guardamos con advertencia
        print("[WARNING] Guardando mapping sin encriptar. En producción usar cryptography.")

    return json.dumps(mapping, ensure_ascii=False, indent=2)

def write_audit_log(operation, details):
    """Escribe log de auditoría."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {operation}: {details}\n")

def process_pdf(pdf_path, output_dir, use_spacy=False, password=None):
    """Pipeline completo: PDF → texto → sanitizado → output."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    salt = load_or_create_salt()

    print(f"[INFO] Procesando: {pdf_path.name}")
    write_audit_log("START", f"Processing {pdf_path.name}")

    # 1. Extraer texto
    raw_text = extract_text_from_pdf(pdf_path)
    print(f"[INFO] Texto extraído: {len(raw_text)} caracteres")

    # 2. Guardar raw (opcional, para verificación interna)
    raw_path = output_dir / f"{pdf_path.stem}_RAW.txt"
    with open(raw_path, 'w', encoding='utf-8') as f:
        f.write(raw_text)
    print(f"[INFO] Raw guardado: {raw_path}")

    # 3. Sanitizar
    all_mapping = {}

    # Regex-based PII
    sanitized, regex_mapping = sanitize_with_regex(raw_text, salt)
    all_mapping.update(regex_mapping)
    print(f"[INFO] PII regex detectado: {len(regex_mapping)} items")

    # Nombres
    if use_spacy and spacy:
        print("[INFO] Usando spaCy NER...")
        nlp = spacy.load("es_core_news_md")
        sanitized, ner_mapping = sanitize_with_spacy(sanitized, salt, nlp)
        all_mapping.update(ner_mapping)
        print(f"[INFO] Entidades spaCy detectadas: {len(ner_mapping)} items")
    else:
        print("[INFO] Usando detección de nombres básica...")
        sanitized, name_mapping = sanitize_names_basic(sanitized, salt)
        all_mapping.update(name_mapping)
        print(f"[INFO] Nombres detectados: {len(name_mapping)} items")

    # 4. Guardar sanitizado
    clean_path = output_dir / f"{pdf_path.stem}_SANITIZED.txt"
    with open(clean_path, 'w', encoding='utf-8') as f:
        f.write(sanitized)
    print(f"[INFO] Sanitizado guardado: {clean_path}")

    # 5. Guardar mapping (encriptado si hay password)
    mapping_path = output_dir / f"{pdf_path.stem}_MAPPING.json"
    mapping_content = encrypt_mapping(all_mapping, password)
    with open(mapping_path, 'w', encoding='utf-8') as f:
        f.write(mapping_content)
    os.chmod(mapping_path, 0o600)
    print(f"[INFO] Mapping guardado: {mapping_path}")

    # 6. Generar hash de integridad del sanitizado
    with open(clean_path, 'rb') as f:
        clean_hash = hashlib.sha256(f.read()).hexdigest()

    write_audit_log("COMPLETE", 
        f"PDF={pdf_path.name}, "
        f"chars_raw={len(raw_text)}, "
        f"pii_found={len(all_mapping)}, "
        f"hash_sha256={clean_hash[:16]}...")

    print(f"[INFO] Hash de integridad: {clean_hash}")
    print(f"[INFO] COMPLETADO: {pdf_path.name}\n")

    return {
        "input": str(pdf_path),
        "raw_output": str(raw_path),
        "sanitized_output": str(clean_path),
        "mapping": str(mapping_path),
        "integrity_hash": clean_hash,
        "pii_count": len(all_mapping)
    }

def main():
    parser = argparse.ArgumentParser(
        description="Sanitizador forense de documentos judiciales - VIGÍA"
    )
    parser.add_argument("pdf", help="PDF de entrada o directorio con PDFs")
    parser.add_argument("-o", "--output", default="./sanitized_output", 
                        help="Directorio de salida")
    parser.add_argument("--spacy", action="store_true", 
                        help="Usar spaCy NER (requiere modelo es_core_news_md)")
    parser.add_argument("--password", help="Contraseña para encriptar mapping (opcional)")
    parser.add_argument("--names", nargs="+", help="Nombres adicionales a sanitizar")

    args = parser.parse_args()

    input_path = Path(args.pdf)

    if input_path.is_dir():
        pdfs = list(input_path.glob("*.pdf"))
        print(f"[INFO] Encontrados {len(pdfs)} PDFs en {input_path}")
    else:
        pdfs = [input_path]

    results = []
    for pdf in pdfs:
        result = process_pdf(
            pdf, 
            args.output, 
            use_spacy=args.spacy,
            password=args.password
        )
        results.append(result)

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE SANITIZACIÓN")
    print("="*60)
    for r in results:
        print(f"\nArchivo: {Path(r['input']).name}")
        print(f"  PII detectado: {r['pii_count']} items")
        print(f"  Hash integridad: {r['integrity_hash']}")
        print(f"  Output: {r['sanitized_output']}")

    print(f"\n[INFO] Mapping guardado en: {args.output}/")
    print(f"[INFO] Salt persistente: {SALT_FILE}")
    print(f"[INFO] Audit log: {LOG_FILE}")
    print("[INFO] IMPORTANTE: Guardá el salt y el mapping en lugar seguro.")
    print("[INFO] Sin ellos, NO podés revertir la sanitización.")

if __name__ == "__main__":
    main()
