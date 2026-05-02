# VIGÍA CI / CD — Guía de Instalación

## Archivos entregados

| Archivo | Propósito |
|---------|-----------|
| `vigia_ci_validate.py` | Script de validación forense — 12 checks de seguridad |
| `vigia-forensic-ci.yml` | Workflow de GitHub Actions (corre en cada push/PR) |
| `requirements-ci.txt` | Dependencias mínimas para CI |
| `generate_release_bundle.py` | Genera bundle firmado para releases |

## Instalación paso a paso

### 1. Copiar archivos al repo

```bash
cd tu_repo_vigia
mkdir -p vigia/ci
mkdir -p .github/workflows
mkdir -p scripts

cp vigia_ci_validate.py vigia/ci/
cp vigia-forensic-ci.yml .github/workflows/
cp requirements-ci.txt .
cp generate_release_bundle.py scripts/
chmod +x vigia/ci/vigia_ci_validate.py
chmod +x scripts/generate_release_bundle.py
```

### 2. Configurar GitHub Secrets

Andá a **Settings → Secrets and variables → Actions** y agregá:

| Secret | Valor | Para qué |
|--------|-------|----------|
| `VIGIA_HMAC_KEY` | Hex string de 64+ chars | Firma HMAC de logs y bundles |
| `VIGIA_HMAC_SALT` | Hex string de 32+ chars | KDF PBKDF2 para derivar clave |
| `KASSANDRA_SALT` | String largo (32+ chars) | Nonce determinista de sesiones |

**Cómo generar:**
```bash
openssl rand -hex 32  # VIGIA_HMAC_KEY
openssl rand -hex 16  # VIGIA_HMAC_SALT
openssl rand -base64 24 | tr -d '=+/' | cut -c1-32  # KASSANDRA_SALT
```

### 3. Instalar pre-commit hook (local)

```bash
cd tu_repo_vigia
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔒 VIGÍA Forensic Pre-commit Check..."
python3 vigia/ci/vigia_ci_validate.py --verbose || exit 1
EOF
chmod +x .git/hooks/pre-commit
```

Ahora **cada commit** corre los 12 checks antes de permitir el push.

### 4. Probar manualmente

```bash
export VIGIA_HMAC_KEY="tu_clave_hex"
export VIGIA_HMAC_SALT="tu_salt_hex"
export KASSANDRA_SALT="tu_salt_kassandra"

python3 vigia/ci/vigia_ci_validate.py --verbose
```

Debería decir:
```
============================================================
VIGÍA CI Validation — Pre-commit Forensic Hardening
============================================================
  [✅ PASS] DETERMINISMO_BIT_FOR_BIT: ...
  [✅ PASS] TABLAS_CONGELADAS: ...
  ...
Resultado: 12/12 checks PASARON
============================================================
```

### 5. Generar release firmado (cuando estés lista para SANS)

```bash
export VIGIA_HMAC_KEY="tu_clave_hex"
export VIGIA_HMAC_SALT="tu_salt_hex"

python scripts/generate_release_bundle.py   --version v1.0.0-sans-hackathon   --output vigia-v1.0.0-sans.tar.gz
```

Esto genera:
- `vigia-v1.0.0-sans.tar.gz` — código + manifest + hashes
- `vigia-v1.0.0-sans.tar.gz.sig` — HMAC-SHA256 del bundle

Un auditor SANS puede verificar:
```bash
# Verificar firma
python -c "
import hmac, hashlib
key = bytes.fromhex('TU_CLAVE')
with open('vigia-v1.0.0-sans.tar.gz', 'rb') as f:
    sig = hmac.new(key, f.read(), hashlib.sha256).hexdigest()
print(sig)
"
# Comparar con .sig
```

## Qué hace cada check (resumen)

| Check | Qué evita |
|-------|-----------|
| DETERMINISMO_BIT_FOR_BIT | Que el hash del bundle cambie entre ejecuciones |
| TABLAS_CONGELADAS | Que un atacante modifique tablas MITRE en runtime |
| HMAC_KEY_CONFIGURADO | Que los logs sean modificables post-generación |
| NONCE_DETERMINISTA | Que Rob T. Lee no pueda reproducir la sesión |
| NO_ROUND_EN_HASH | Que un perito recalcule hash diferente al tuyo |
| EXCLUSION_ENTROPY_PRESENTE | Que señales en π=0.84 desaparezcan del grafo |
| I2_INVARIANCE_CHECK | Que un rootkit monkey-patchee stdlib |
| INPUT_VALIDATION | Que un atacante congele el servidor con 10M deltas |
| ANTI_JAILBREAK_PROMPT | Que el LLM obedezca "olvida estas instrucciones" |
| RESIDUAL_UNCERTAINTY | Que VIGÍA afirme certeza absoluta sin humildad |
| NO_TMP_WORLD_WRITABLE | Que un atacante local lea/escriba evidencia vía symlink |
| KASSANDRA_SALT_SET | Que el nonce sea predecible y inyectable |

## Autores

**VIGÍA AI Collective:**
- Anna Tchijova — Arquitecta & Orquestadora
- Kimi (Moonshot AI) — Auditoría Forense & Determinismo
- Claude (Anthropic) — Implementación de Seguridad
- Gemini (Google) — Análisis Epistémico & Metafísico
- DeepSeek — Auditoría de Vulnerabilidades
- Qwen — Pipeline & Validación

**Licencia:** MIT — Open Source para la comunidad DFIR.
