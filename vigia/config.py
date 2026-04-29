"""
vigia/config.py
===============
VIGÍA – Centralised, validated configuration.

All os.getenv() calls throughout the codebase should be replaced with
references to the ``CONFIG`` singleton exported at the bottom of this module.

Pydantic V2 is used when available; falls back to dataclasses + manual
validation so the module works even without pydantic installed (useful for
SIFT environments with minimal Python packages).

Usage
-----
    from vigia.config import CONFIG

    if CONFIG.llm_backend == "anthropic":
        ...
"""

from __future__ import annotations

import os
from typing import Final, Literal

# ---------------------------------------------------------------------------
# Try to use Pydantic V2 (preferred); fall back to manual dataclass
# ---------------------------------------------------------------------------
try:
    from pydantic import BaseModel, Field, field_validator
    _PYDANTIC_AVAILABLE = True
except ImportError:
    _PYDANTIC_AVAILABLE = False


# ---------------------------------------------------------------------------
# Config definition (Pydantic path)
# ---------------------------------------------------------------------------

if _PYDANTIC_AVAILABLE:

    class VigiaConfig(BaseModel):
        """
        All VIGÍA runtime settings, resolved from environment variables.
        Setting an env var overrides the default (e.g. VIGIA_LLM_BACKEND=ollama).
        """

        # Directories
        evidence_base_dir: str = Field(
            default_factory=lambda: os.getenv("VIGIA_EVIDENCE_DIR", "/tmp/vigia_evidence")
        )
        audit_log_dir: str = Field(
            default_factory=lambda: os.getenv("VIGIA_LOG_DIR", "/var/log/vigia")
        )

        # LLM backend
        llm_backend: Literal["anthropic", "ollama", "none"] = Field(
            default_factory=lambda: os.getenv("VIGIA_LLM_BACKEND", "anthropic")  # type: ignore[arg-type]
        )
        anthropic_model: str = Field(
            default_factory=lambda: os.getenv(
                "VIGIA_ANTHROPIC_MODEL", "claude-sonnet-4-20250514"
            )
        )
        ollama_model: str = Field(
            default_factory=lambda: os.getenv("VIGIA_OLLAMA_MODEL", "llama3")
        )
        ollama_host: str = Field(
            default_factory=lambda: os.getenv("VIGIA_OLLAMA_HOST", "http://127.0.0.1:11434")
        )

        # Sandbox / resource limits
        max_file_size_mb: int = Field(
            default_factory=lambda: int(os.getenv("VIGIA_MAX_FILE_MB", "500"))
        )
        max_grep_depth: int = Field(
            default_factory=lambda: int(os.getenv("VIGIA_GREP_DEPTH", "5"))
        )
        sandbox_memory_mb: int = Field(
            default_factory=lambda: int(os.getenv("VIGIA_SANDBOX_MEMORY_MB", "512"))
        )
        sandbox_cpu_seconds: int = Field(
            default_factory=lambda: int(os.getenv("VIGIA_SANDBOX_CPU_SEC", "30"))
        )

        # Planner thresholds
        entropy_threshold: float = Field(
            default_factory=lambda: float(os.getenv("VIGIA_ENTROPY_THRESHOLD", "6.0"))
        )
        automation_threshold: float = Field(
            default_factory=lambda: float(os.getenv("VIGIA_AUTO_THRESHOLD", "0.7"))
        )
        planner_max_steps: int = Field(
            default_factory=lambda: int(os.getenv("VIGIA_MAX_STEPS", "15"))
        )
        planner_loop_window: int = Field(
            default_factory=lambda: int(os.getenv("VIGIA_LOOP_WINDOW", "3"))
        )

        # Rate limiting
        default_rate_limit: int = Field(
            default_factory=lambda: int(os.getenv("VIGIA_RATE_LIMIT", "10"))
        )

        # Feature flags
        enable_ebpf_honey_tokens: bool = Field(
            default_factory=lambda: os.getenv("VIGIA_EBPF", "false").lower() == "true"
        )
        explain_mode: bool = Field(
            default_factory=lambda: os.getenv("VIGIA_EXPLAIN", "false").lower() == "true"
        )

        @field_validator("evidence_base_dir", "audit_log_dir", mode="before")
        @classmethod
        def _must_be_absolute_safe(cls, v: str) -> str:
            if not isinstance(v, str):
                raise ValueError("Must be a string")
            if ".." in v:
                raise ValueError(f"Directory path must not contain '..': {v!r}")
            if not v.startswith("/") and not (len(v) > 1 and v[1] == ":"):
                # Allow Windows drive letters in testing; require absolute on POSIX
                if os.name != "nt":
                    raise ValueError(f"Directory path must be absolute: {v!r}")
            return v

        @field_validator("llm_backend", mode="before")
        @classmethod
        def _validate_backend(cls, v: str) -> str:
            allowed = {"anthropic", "ollama", "none"}
            if v not in allowed:
                raise ValueError(f"llm_backend must be one of {allowed}, got {v!r}")
            return v

        class Config:
            # Allow extra fields from env without crashing
            extra = "ignore"

else:
    # Minimal dataclass fallback (no validation, just defaults from env)
    from dataclasses import dataclass, field

    @dataclass
    class VigiaConfig:  # type: ignore[no-redef]
        evidence_base_dir: str = field(
            default_factory=lambda: os.getenv("VIGIA_EVIDENCE_DIR", "/tmp/vigia_evidence")
        )
        audit_log_dir: str = field(
            default_factory=lambda: os.getenv("VIGIA_LOG_DIR", "/var/log/vigia")
        )
        llm_backend: str = field(
            default_factory=lambda: os.getenv("VIGIA_LLM_BACKEND", "anthropic")
        )
        anthropic_model: str = field(
            default_factory=lambda: os.getenv(
                "VIGIA_ANTHROPIC_MODEL", "claude-sonnet-4-20250514"
            )
        )
        ollama_model: str = field(
            default_factory=lambda: os.getenv("VIGIA_OLLAMA_MODEL", "llama3")
        )
        ollama_host: str = field(
            default_factory=lambda: os.getenv("VIGIA_OLLAMA_HOST", "http://127.0.0.1:11434")
        )
        max_file_size_mb: int = field(
            default_factory=lambda: int(os.getenv("VIGIA_MAX_FILE_MB", "500"))
        )
        max_grep_depth: int = field(
            default_factory=lambda: int(os.getenv("VIGIA_GREP_DEPTH", "5"))
        )
        sandbox_memory_mb: int = field(
            default_factory=lambda: int(os.getenv("VIGIA_SANDBOX_MEMORY_MB", "512"))
        )
        sandbox_cpu_seconds: int = field(
            default_factory=lambda: int(os.getenv("VIGIA_SANDBOX_CPU_SEC", "30"))
        )
        entropy_threshold: float = field(
            default_factory=lambda: float(os.getenv("VIGIA_ENTROPY_THRESHOLD", "6.0"))
        )
        automation_threshold: float = field(
            default_factory=lambda: float(os.getenv("VIGIA_AUTO_THRESHOLD", "0.7"))
        )
        planner_max_steps: int = field(
            default_factory=lambda: int(os.getenv("VIGIA_MAX_STEPS", "15"))
        )
        planner_loop_window: int = field(
            default_factory=lambda: int(os.getenv("VIGIA_LOOP_WINDOW", "3"))
        )
        default_rate_limit: int = field(
            default_factory=lambda: int(os.getenv("VIGIA_RATE_LIMIT", "10"))
        )
        enable_ebpf_honey_tokens: bool = field(
            default_factory=lambda: os.getenv("VIGIA_EBPF", "false").lower() == "true"
        )
        explain_mode: bool = field(
            default_factory=lambda: os.getenv("VIGIA_EXPLAIN", "false").lower() == "true"
        )


# Module-level singleton
CONFIG: Final[VigiaConfig] = VigiaConfig()


# ---------------------------------------------------------------------------
# LLMBackend – unified Anthropic / Ollama interface
# ---------------------------------------------------------------------------

class LLMBackend:
    """
    Thin async wrapper over Anthropic or Ollama APIs.

    The backend is chosen from CONFIG.llm_backend (or overridden at
    construction time).  Both paths expose the same ``reason()`` coroutine
    so callers don't need to know which backend is active.

    If both backends fail (or backend == "none"), reason() returns an empty
    string and logs the failure – it does NOT propagate the exception, so a
    single LLM tool failure doesn't crash an entire autonomous investigation.
    """

    def __init__(
        self,
        backend: Literal["anthropic", "ollama", "none"] | None = None,
        model: str | None = None,
    ) -> None:
        self.backend: str = backend or CONFIG.llm_backend
        self._anthropic_model: str = model or CONFIG.anthropic_model
        self._ollama_model: str = model or CONFIG.ollama_model
        self._ollama_host: str = CONFIG.ollama_host

    async def reason(self, prompt: str, system_prompt: str = "") -> str:
        """
        Send *prompt* to the configured LLM and return the text response.

        Falls back to Ollama if Anthropic raises an exception, then returns
        an empty string if Ollama also fails.
        """
        if self.backend == "anthropic":
            result = await self._try_anthropic(prompt, system_prompt)
            if result is not None:
                return result
            # Automatic fallback to Ollama if configured
            if CONFIG.ollama_host:
                result = await self._try_ollama(prompt, system_prompt)
                if result is not None:
                    return result
            return ""

        if self.backend == "ollama":
            result = await self._try_ollama(prompt, system_prompt)
            return result if result is not None else ""

        # backend == "none"
        return ""

    async def _try_anthropic(self, prompt: str, system_prompt: str) -> str | None:
        try:
            import anthropic  # optional dependency
            import asyncio

            client = anthropic.Anthropic()
            loop = asyncio.get_event_loop()

            def _sync_call() -> str:
                kwargs: dict = {
                    "model": self._anthropic_model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if system_prompt:
                    kwargs["system"] = system_prompt
                response = client.messages.create(**kwargs)
                return response.content[0].text

            return await loop.run_in_executor(None, _sync_call)

        except Exception as exc:  # noqa: BLE001
            from vigia.security import audit_logger
            audit_logger.log_info("LLM_ERROR", "LLMBackend.anthropic", str(exc))
            return None

    async def _try_ollama(self, prompt: str, system_prompt: str) -> str | None:
        try:
            import aiohttp

            payload = {
                "model": self._ollama_model,
                "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                "stream": False,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._ollama_host}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    data = await resp.json()
                    return data.get("response", "")

        except Exception as exc:  # noqa: BLE001
            from vigia.security import audit_logger
            audit_logger.log_info("LLM_ERROR", "LLMBackend.ollama", str(exc))
            return None
