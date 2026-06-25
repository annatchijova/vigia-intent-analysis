# -*- coding: utf-8 -*-
"""
vigia/tools/vigia_adversarial_nlp.py — COMPATIBILITY STUB

Este módulo re-exporta desde los módulos equivalentes del repo flat.
Existe para resolver el import:
    from vigia.tools.vigia_adversarial_nlp import ForensicDatabaseManager, LanguageDetector
en temporal_forensics.py, que asume estructura de package.

El código real está en:
    adversarial_nlp.py  → LanguageDetector, VigiaAdversarialNLP, etc.
    forensic_db.py      → ForensicDatabaseManager

NO modificar este archivo directamente — modificar los originales.
"""
from vigia.tools.forensic_db import ForensicDatabaseManager
from vigia.tools.adversarial_nlp import (
    LanguageDetector,
    ConfigLoader,
    SDA_NominalizationAnalyzer,
    CLI_Analyzer,
    ACP_Protocol,
    ROI_Analyzer,
    ZipfImperfectionAnalyzer,
    ForensicVerdict,
    InstitutionalEmitter,
    ForensicEngine,
    VigiaAdversarialNLP,
    calculate_entropy_profile,
)

__all__ = [
    "ForensicDatabaseManager",
    "LanguageDetector",
    "ConfigLoader",
    "SDA_NominalizationAnalyzer",
    "CLI_Analyzer",
    "ACP_Protocol",
    "ROI_Analyzer",
    "ZipfImperfectionAnalyzer",
    "ForensicVerdict",
    "InstitutionalEmitter",
    "ForensicEngine",
    "VigiaAdversarialNLP",
    "calculate_entropy_profile",
]
