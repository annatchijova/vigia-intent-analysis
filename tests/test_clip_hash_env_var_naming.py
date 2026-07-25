"""
vigia/forensics/vision_audit.py -- two small doc/code mismatches found while
updating .env.example (2026-07-25), both confirmed by execution before being
fixed, in the same "claim/mechanism mismatch" class this codebase's audit
trail has repeatedly found elsewhere:

1. The per-model CLIP hash override env var name. _load_clip_model_hashes()
   derives it as "VIGIA_CLIP_HASH_" + filename.upper() with "-"/"." replaced
   by "_" -- for "ViT-B-32.pt" that's VIGIA_CLIP_HASH_VIT_B_32_PT (the ".pt"
   extension folds into a trailing "_PT"). The module's own comments and the
   previous .env.example instead documented VIGIA_CLIP_HASH_VIT_B_32,
   missing the "_PT" -- an operator following that documented name would set
   a variable _load_clip_model_hashes() never reads, and the override would
   silently no-op (the model loads with whatever the hardcoded/file hash
   says instead, or refuses to load under VIGIA_STRICT_MODEL_CHECK, with no
   error pointing at the typo).

2. VIGIA_STRICT_MODEL_CHECK's own code default (when unset) is "true" --
   comment marks it "P1-7: default seguro" (safe default). The previous
   .env.example explicitly set it to "false", which is a silent downgrade
   the moment the file is copied to .env: a template meant to represent
   sane starting values instead turned off a safety check the code ships
   safe-by-default, contradicting the file's own "STRICT MODE... enable
   before forensic use" section header.

Neither is a runtime bug in vision_audit.py itself -- both are documentation
drift between the code's actual behavior and what operators were told to
set. This test locks in the actual behavior so a future refactor of the
naming scheme or the default is caught here instead of silently reintroducing
the mismatch into .env.example.
"""

from __future__ import annotations

import importlib


class TestClipHashEnvVarNaming:
    def test_derived_env_var_name_for_vit_b_32_includes_pt_suffix(self):
        from vigia.forensics import vision_audit

        filename = "ViT-B-32.pt"
        derived = "VIGIA_CLIP_HASH_" + filename.replace("-", "_").replace(".", "_").upper()

        assert derived == "VIGIA_CLIP_HASH_VIT_B_32_PT"
        assert filename in vision_audit._CLIP_MODEL_HASHES_BUILTIN

    def test_env_var_override_actually_uses_the_pt_suffixed_name(self, monkeypatch):
        monkeypatch.setenv("VIGIA_CLIP_HASH_VIT_B_32_PT", "deadbeef" * 8)
        from vigia.forensics import vision_audit
        importlib.reload(vision_audit)
        try:
            assert vision_audit.CLIP_MODEL_HASHES["ViT-B-32.pt"] == "deadbeef" * 8
        finally:
            importlib.reload(vision_audit)

    def test_env_var_without_pt_suffix_is_silently_ignored(self, monkeypatch):
        """Documents the failure mode the naming mismatch caused: the
        without-suffix name an operator might reasonably guess is never
        read, so setting it has zero effect -- no error, no warning."""
        monkeypatch.setenv("VIGIA_CLIP_HASH_VIT_B_32", "deadbeef" * 8)
        from vigia.forensics import vision_audit
        importlib.reload(vision_audit)
        try:
            assert vision_audit.CLIP_MODEL_HASHES["ViT-B-32.pt"] != "deadbeef" * 8
        finally:
            importlib.reload(vision_audit)


class TestStrictModelCheckDefault:
    def test_default_is_true_when_env_var_unset(self, monkeypatch):
        monkeypatch.delenv("VIGIA_STRICT_MODEL_CHECK", raising=False)
        from vigia.forensics import vision_audit
        importlib.reload(vision_audit)
        try:
            assert vision_audit._STRICT_MODEL_CHECK is True
        finally:
            importlib.reload(vision_audit)
