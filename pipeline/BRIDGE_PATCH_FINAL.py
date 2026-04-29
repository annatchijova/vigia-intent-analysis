"""
BRIDGE_PATCH_FINAL.py
=====================
VIGÍA — Instrucciones de integración para vigia_sift_bridge_final.py

Este archivo NO es ejecutable directamente.
Contiene los 3 bloques exactos a agregar/modificar en el bridge.

INSTRUCCIONES:
1. En vigia_sift_bridge_final.py, línea ~2292, reemplazar el bloque
   de registro de herramientas (REGISTRO DE HERRAMIENTAS FORENSES EXTERNAS)
   por el BLOQUE A de este archivo.

2. Verificar que los imports del bridge incluyen vigia.sandbox
   (ya está en línea 66 del bridge actual — NO modificar).

3. Agregar la variable de entorno VIGIA_CAIE_ENABLED=true para activar.

Diagnóstico y correcciones: 20-abr-2026 — Claude (Systems Integration Engineer)
"""

# ===========================================================================
# BLOQUE A — REEMPLAZA EL BLOQUE DE REGISTRO ACTUAL (línea ~2292 del bridge)
# ===========================================================================
#
# Reemplazar desde:
#   # Kimi: Cross-Artifact Incongruence Engine ...
# Hasta:
#   )
# (el try/except de cross_artifact_analysis)
#
# POR ESTO:

REGISTRO_BLOCK = """
# ─────────────────────────────────────────────────────────────────────────────
# REGISTRO DE HERRAMIENTAS FORENSES EXTERNAS
# ─────────────────────────────────────────────────────────────────────────────
# Estas tools viven en vigia/tools/ y se registran aquí explícitamente para
# que el servidor MCP las exponga al cliente (Claude Code, Ollama-MCP, etc.).

mcp.tool()(audit_document_integrity)   # PDF/DOCX: fonts, producer, gender/role coherence
mcp.tool()(analyze_image_layers)       # ELA: Error Level Analysis para detección de paste-in
mcp.tool()(detect_document_geometry)   # Márgenes, alineación, consistencia de folio
mcp.tool()(ocr_semantic_validator)     # OCR + validación semántica de campos obligatorios (AR)
mcp.tool()(vision_intent_audit)        # CLIP zero-shot: intencionalidad visual en imágenes

# ---------------------------------------------------------------------------
# CAIE — Cross-Artifact Incongruence Engine (Kimi P0)
# Registro condicional: falla silenciosamente si el módulo no está disponible.
# Activar con VIGIA_CAIE_ENABLED=true en producción.
# ---------------------------------------------------------------------------
if os.getenv("VIGIA_CAIE_ENABLED", "true").lower() == "true":
    try:
        from vigia.tools.caie import cross_artifact_analysis
        mcp.tool()(cross_artifact_analysis)
        audit_logger.log_info(
            event_type="CAIE_REGISTERED",
            tool="vigia_sift_bridge",
            message="cross_artifact_analysis registered as MCP tool.",
        )
    except ImportError as _caie_err:
        print(
            f"[VIGIA] WARNING: vigia.tools.caie unavailable ({_caie_err}). "
            "Cross-artifact analysis will not be registered.",
            file=sys.stderr, flush=True,
        )

# ---------------------------------------------------------------------------
# TRUST FUSION — Capa P2: Inferencia Consistente (Kimi roadmap)
# Cierra el ciclo Temporal → Provenance → Correlation.
# Activar con VIGIA_TRUST_FUSION_ENABLED=true en producción.
# ---------------------------------------------------------------------------
if os.getenv("VIGIA_TRUST_FUSION_ENABLED", "true").lower() == "true":
    try:
        from vigia.core.trust_fusion import trust_fusion_analysis
        mcp.tool()(trust_fusion_analysis)
        audit_logger.log_info(
            event_type="TRUST_FUSION_REGISTERED",
            tool="vigia_sift_bridge",
            message="trust_fusion_analysis registered as MCP tool.",
        )
    except ImportError as _tf_err:
        print(
            f"[VIGIA] WARNING: vigia.core.trust_fusion unavailable ({_tf_err}). "
            "Trust fusion analysis will not be registered.",
            file=sys.stderr, flush=True,
        )

# ---------------------------------------------------------------------------
# WHITELIST DEL PLANNER — actualizada con las nuevas tools forenses
# Previene ejecución arbitraria de métodos via getattr() dinámico en el planner.
# ---------------------------------------------------------------------------
_PLANNER_TOOL_WHITELIST: frozenset[str] = frozenset({
    # Core filesystem
    "list_files", "read_evidence", "search_pattern",
    # System analysis
    "list_processes", "audit_network", "mount_sift_evidence",
    # Integrity & entropy
    "generate_forensic_hash", "calculate_shannon_entropy", "audit_image_metadata",
    # Intentionality analysis
    "analyze_stylometry", "calculate_human_entropy", "infer_intent",
    "detect_habit_incongruence", "detect_human_jitter", "audit_grice_maxims",
    "detect_eco_overinterpretation",
    # Security tools
    "activate_honey_token", "reason_with_llm", "validate_and_correct_analysis",
    "reload_phonetic_dict", "get_phonetic_dict_stats",
    # Document forensics
    "audit_document_integrity", "analyze_image_layers", "detect_document_geometry",
    "ocr_semantic_validator", "vision_intent_audit",
    # P2 — nuevas tools forenses integradas
    "cross_artifact_analysis",     # CAIE
    "trust_fusion_analysis",       # TrustFusion
    # Planner internal
    "investigate", "plan_investigation", "search_for_absence",
})
"""

# ===========================================================================
# BLOQUE B — NUEVAS VARIABLES DE ENTORNO (agregar a .env o docker-compose.yml)
# ===========================================================================

ENV_VARS = """
# VIGÍA — Variables de entorno para activar módulos P2
# Agregar a .env, docker-compose.yml, o exportar antes de ejecutar el bridge

VIGIA_CAIE_ENABLED=true           # Activar Cross-Artifact Incongruence Engine
VIGIA_TRUST_FUSION_ENABLED=true   # Activar Trust Fusion (P2)

# Umbrales del pipeline forense
VIGIA_TEMPORAL_WINDOW_SEC=300     # Ventana temporal para análisis de vecindad (default: 5min)
VIGIA_TRUST_AGGREGATION=noisy_or  # Método: noisy_or | bayesian_average | conservative_min
VIGIA_DAUBERT_MIN_TRUST=0.5       # Trust mínimo para admisibilidad Daubert

# Claves de integridad
VIGIA_HMAC_KEY=<64-char hex key>  # Generado con: python3 -c "import secrets; print(secrets.token_hex(32))"
"""

# ===========================================================================
# BLOQUE C — WORKFLOW DEL PLANNER (cómo usar los nuevos módulos)
# ===========================================================================
# Este es el orden correcto del pipeline completo según paraimplementar.md:
#
# 1. DATA INGESTION → artifacts (raw)
# 2. NORMALIZATION (P0) → evidence_type, spoofability profiling
# 3. TEMPORAL VALIDATION (P1) → TCV: EFFECT_BEFORE_CAUSE, TOO_FAST, etc.
# 4. PROVENANCE (P2) → ProvenanceChain: trust_score, chain_status
# 5. TRUST FUSION (P2) → TrustFusionEngine: effective_trust per artifact
#    • compute_effective_trust(artifact_id, prov_trust, temporal_violations)
#    • artifacts_for_caie = engine.export_to_caie()
# 6. CAIE → CrossArtifactIncongruenceEngine: fractures, composite_score
# 7. CORRELATION DECAY → CorrelationDecayEngine: adjusted_scores
# 8. DECISION → MALICE / SUSPICION / NOISE + Peirce chain
# 9. STIX EXPORT → create_stix_bundle(to_stix_sdo(artifact, technique_id))
#
# LLAMADA MCP TÍPICA DESDE CLAUDE CODE:
#
# # Paso 5: Trust Fusion
# trust_result = await trust_fusion_analysis(
#     artifacts=raw_artifacts,
#     temporal_violations=tcv_violations,
#     aggregation_method="noisy_or",
# )
# enriched_artifacts = trust_result["artifacts_for_caie"]
#
# # Paso 6: CAIE
# caie_result = await cross_artifact_analysis(
#     artifacts=enriched_artifacts,
# )
# fractures = caie_result["fractures"]
# composite_score = caie_result["composite_score"]
# verdict = caie_result["verdict"]

