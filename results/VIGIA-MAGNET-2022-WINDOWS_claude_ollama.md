# VIGIA FORENSIC INTENT ANALYSIS REPORT

| Campo | Valor |
|-------|-------|
| **Case ID** | VIGIA-MAGNET-2022-WINDOWS |
| **Investigator** | VIGÍA Autonomous Agent (Claude Code / Anthropic) |
| **Evidence** | `/evidence/magnet-2022-windows-artifacts/` |
| **Mode** | Claude Code + MCP (Mode 2) |
| **Timestamp** | 2026-06-29T02:09:30Z (UTC) |
| **SANS Phase** | PICERL — Containment / Eradication |

---

## CHAIN OF CUSTODY

| Artifact | SHA-256 |
|----------|---------|
| Security.evtx | `b050682f7fe96938aca2fc19a96d24641173b4f31a4f3837119ea916663344c1` |
| System.evtx | `962edaf7f38dbb4f81e7e8e586af56ae063a5caaa40d1c8a68165b3ef8f66129` |
| Application.evtx | `aee1375bce80a55466be951352332c639b2b9191fefa88609a35bcb9a0363ce5` |
| SAM | `4aec3ac88863e8f6a57dce79006f41d4b99adc519b160aabb5c418400c9e521e` |
| SECURITY | `987c6b547632140553727f1c60f97a75f33f2dec79a28295ab1c85f9aef3059a` |
| SOFTWARE | `2e9fb43409ef7c6e90c2e88622b3fe21cd202b5899de2a1b330764ff6296a875` |
| SYSTEM | `545ac21ca335836d97f20580a97603b777284751358f5a97bff60d90f9230db2` |
| sam.txt | `92c791dd45b8002572e9886d18f1959a4c2f6b4ae9da0fb0d6da80607904e688` |
| software.txt | `bb09d4c6e65152a420b995cecfe53a77b52b9e55c1b827508d36fed9e5de093e` |
| system.txt | `2d29ef7fa1b63b7297cb45860efd30b37a5613505f192b3044a3878bd9cb9bbe` |

Todos los hashes fueron generados **antes** de leer el contenido de los artefactos (`generate_forensic_hash` → `read_evidence`). Cadena de custodia íntegra.

---

## HOST PROFILE

| Campo | Valor |
|-------|-------|
| Hostname | DESKTOP-SKPTDIO |
| Workgroup | WORKGROUP |
| Hardware | HP laptop, Intel Core Kaby Lake |
| OS | Windows 10/11 |
| Usuario legítimo | Patrick [RID 1001, SID `S-1-5-21-3341181097-1059518978-806882922-1001`] |
| Email | pbentley0107@gmail.com |
| Grupos (Patrick) | Administrators |
| Último login legítimo | 2022-01-21 02:59:12Z (21 días antes del ataque) |

---

## EXECUTIVE SUMMARY

El host **DESKTOP-SKPTDIO** fue comprometido entre el 6 y el 12 de febrero de 2022. El atacante instaló **ZeroTier One** (VPN P2P cifrada que elude firewalls de perímetro) el 6 de febrero, estableciendo un canal de acceso persistente. El 12 de febrero, entre las 01:01 y las 02:17 UTC, sin ninguna sesión interactiva del usuario Patrick, el atacante ejecutó una secuencia de persistencia completa como `LOCAL SYSTEM (S-1-5-18)`: habilitó RDP, creó la cuenta backdoor `minecraftsteve`, la agregó a **Administrators** y **Remote Management Users**, y tomó control de las credenciales tanto del backdoor como de la cuenta Built-in Administrator.

Todos los eventos de gestión de cuentas (4720/4722/4724/4728/4732) tienen `SubjectUserSid: S-1-5-18` — estructuralmente imposible para operaciones iniciadas por un usuario interactivo. **Veredicto general: MALICE.**

---

## TIMELINE DE EVENTOS

```
2022-02-06 07:15:35Z  [7045] ZeroTier One service instalado (auto start, LocalSystem)
                             Path: C:\ProgramData\ZeroTier\One\zerotier-one_x64.exe
2022-02-06 07:22:40Z  [7045] ZeroTier Virtual Port driver instalado (zttap300.sys)
2022-02-06 07:38:39Z  [MSI]  Java 8 Update 181 (64-bit) + JDK instalados
                             (versión 2018, múltiples CVEs conocidos)
[Feb 6–11]                   ZeroTier activo: acceso cifrado persistente disponible
2022-02-12 01:01:32Z  [7040] TermService (RDP): demand start → AUTO START
2022-02-12 01:29:43Z  [4720] Cuenta 'minecraftsteve' creada — por SYSTEM (S-1-5-18)
2022-02-12 01:29:43Z  [4722] minecraftsteve habilitada
2022-02-12 01:29:43Z  [4724] Password inicial establecida — por SYSTEM
2022-02-12 01:29:43Z  [4728] minecraftsteve agregada a Domain Users — por SYSTEM
2022-02-12 01:37:07Z  [4732] minecraftsteve agregada a Administrators (S-1-5-32-544)
2022-02-12 01:37:18Z  [4732] minecraftsteve agregada a Remote Management Users (S-1-5-32-580)
2022-02-12 02:06:06Z  [4724] Password de minecraftsteve reseteada nuevamente (estabilización)
2022-02-12 02:17:18Z  [4724] Password de Built-in Administrator reseteada — por SYSTEM
2022-02-12 23:17:11Z  [REG]  LSA Policy\Secrets LastWrite (actividad de credenciales LSA)
```

**Duración de la sesión de ataque activo:** ~76 minutos (01:01 → 02:17 UTC).

---

## FINDINGS

### F-001 — Cuenta backdoor "minecraftsteve" creada por LOCAL SYSTEM

| Campo | Valor |
|-------|-------|
| **Verdict** | **MALICE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | `hives/SAM` + `evtx/Security.evtx` |
| **Tools** | `generate_forensic_hash`, `read_evidence`, `detect_habit_incongruence`, Python/Evtx parser |
| **MITRE TTPs** | T1136.001 · T1078.003 · T1098 |

**Firstness (observación):**
Usuario `minecraftsteve` [RID 1002, SID `S-1-5-21-...-1002`] creado el 2022-02-12 01:29:43Z. Full Name = username. Login Count: **0** (nunca logueado interactivamente). Miembro de **Administrators** Y **Remote Management Users**. Password reseteada dos veces en 37 minutos. `SubjectUserSid` en todos los eventos: `S-1-5-18` (LOCAL SYSTEM).

Secuencia de eventos confirmada en Security.evtx:

```
01:29:43Z  [4720] ACCOUNT CREATED    — minecraftsteve — SubjectUserSid: S-1-5-18
01:29:43Z  [4722] ACCOUNT ENABLED    — minecraftsteve — SubjectUserSid: S-1-5-18
01:29:43Z  [4724] PASSWORD RESET     — minecraftsteve — SubjectUserSid: S-1-5-18
01:29:43Z  [4728] ADDED GLOBAL GROUP — minecraftsteve — SubjectUserSid: S-1-5-18
01:37:07Z  [4732] ADDED LOCAL GROUP  — Administrators       — SubjectUserSid: S-1-5-18
01:37:18Z  [4732] ADDED LOCAL GROUP  — Remote Management Users — SubjectUserSid: S-1-5-18
02:06:06Z  [4724] PASSWORD RESET     — minecraftsteve — SubjectUserSid: S-1-5-18
```

**Secondness (anomalía estructural):**
La creación interactiva de cuentas (GUI, `net user`, PowerShell) registra **siempre** el SID del usuario creador como `SubjectUserSid`. `S-1-5-18` (LOCAL SYSTEM) aparece como sujeto únicamente cuando la operación es ejecutada desde un servicio, tarea programada, o shell remota con privilegios SYSTEM. Patrick (SID `-1001`) no tiene ninguna sesión activa en la ventana de ataque. La membresía simultánea en Administrators + Remote Management Users garantiza acceso redundante por RDP y WinRM/WMI.

**Thirdness (patrón deliberado):**
Patrón Living-off-the-Land + persistencia (T1136.001). El nombre "minecraftsteve" es una transferencia de familiaridad (Carnegie): imita una cuenta que Patrick podría crear en un hogar gamer (tiene Discord, Gaming Services instalados), suprimiendo el escrutinio inicial del analista. La doble operación de reset de password es estabilización de credenciales — el atacante garantiza que su credencial es la vigente, no un artefacto del proceso de creación.

**Carnegie:** Transferencia de familiaridad — nombre diseñado para mimetizar el contexto del hogar de Patrick.

**Devil's Advocate:**
Patrick creó esta cuenta él mismo para un familiar o amigo que juega Minecraft, usando un script que casualmente elevó a SYSTEM.

**Refutación:**
Un usuario creando una cuenta por cualquier mecanismo Windows estándar registra su propio SID, no SYSTEM. Obtener contexto SYSTEM requiere escalación de privilegios deliberada. El último logon interactivo de Patrick fue el 21 de enero (21 días antes). No existe sesión de Patrick en la ventana 01:00–03:00 UTC. La hipótesis benigna no sobrevive la restricción `SubjectUserSid = S-1-5-18`.

---

### F-002 — RDP pre-habilitado 28 minutos antes de la cuenta backdoor

| Campo | Valor |
|-------|-------|
| **Verdict** | **INTENT** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | `evtx/System.evtx` (7040) + `hives/SYSTEM` (TermService LastWrite) |
| **Tools** | `generate_forensic_hash`, `read_evidence`, Python/Evtx parser |
| **MITRE TTPs** | T1021.001 · T1543.003 |

**Firstness:** System.evtx evento 7040 @ 2022-02-12 01:01:32Z: `TermService` cambiado de `demand start` → `auto start`. Corroborado en hive SYSTEM (LastWrite idéntico). Ocurre **28 minutos** antes de la creación de minecraftsteve.

**Secondness:** En laptops de uso personal, RDP no está habilitado por defecto. Habilitarlo como `auto start` garantiza que persista tras reinicios. La secuencia — RDP primero, luego cuenta — es el patrón operacional para establecer acceso remoto: el atacante necesitaba tanto un servicio escuchando como credenciales válidas antes de que RDP fuera útil.

**Thirdness:** La brecha de 28 minutos entre habilitación de RDP y creación de la cuenta es consistente con un atacante humano operando paso a paso a través de una shell remota, no con un script automatizado (que ejecutaría ambos en milisegundos). Sugiere una **sesión interactiva del atacante** a través del túnel ZeroTier.

**Devil's Advocate:** Patrick o un familiar habilitó RDP para acceso remoto legítimo; la cuenta minecraftsteve fue creada en coincidencia temporal.

**Refutación:** Ambas acciones ejecutadas como `S-1-5-18`. No hay sesión de Patrick en la ventana. La co-ocurrencia de dos acciones anómalas a nivel SYSTEM en la misma noche no tiene explicación benigna coherente.

**Corroboración:** F-001 (cuenta creada 28 min después, mismo actor/contexto), F-003 (ZeroTier provee el canal de acceso).

---

### F-003 — ZeroTier VPN P2P cifrada instalada como servicio persistente

| Campo | Valor |
|-------|-------|
| **Verdict** | SUSPICION → **INTENT** (en análisis combinado) |
| **Confidence** | MEDIUM |
| **Status** | INFERRED — instalación confirmada; vector de acceso inicial no verificable con artefactos disponibles |
| **Artifacts** | `evtx/System.evtx` (7045) + `evtx/Application.evtx` (MSI success) + `hives/SYSTEM` |
| **Tools** | `generate_forensic_hash`, `read_evidence`, `detect_habit_incongruence` |
| **MITRE TTPs** | T1572 · T1133 · T1543.003 |

**Firstness:**
- System.evtx [7045] @ 2022-02-06 07:15:35Z: `ZeroTier One` service instalado. Path: `C:\ProgramData\ZeroTier\One\zerotier-one_x64.exe`. StartType: **auto start**. AccountName: **LocalSystem**.
- System.evtx [7045] @ 07:22:40Z: driver `zttap300.sys` (ZeroTier Virtual Port) instalado.
- Application.evtx: MSI "Installation completed successfully" para ZeroTier One y ZeroTier One Virtual Network Port.
- System.evtx [7040] @ 07:53:08Z: IKEEXT (IKE/AuthIP IPsec) cambiado a auto start — compatibilidad VPN.

**Secondness:** ZeroTier crea una interfaz TAP virtual y une el host a una red privada identificada por un Network ID. Una vez conectado, cualquier máquina en esa red ZeroTier puede alcanzar este host en puertos estándar (RDP/3389, WinRM/5985) sin atravesar el firewall de perímetro. El atacante's SYSTEM-level operations del 12 de febrero son consistentes con conexiones llegando por la interfaz ZeroTier.

**Thirdness:** Secuencia "beachhead + foothold": instalar ZeroTier (Feb 6) → esperar 6 días → operar a través de ZeroTier para instalar backdoor (Feb 12). ZeroTier es la cabeza de playa; la cuenta minecraftsteve es el foothold persistente para explotación posterior. Juntos conforman una arquitectura de persistencia completa.

**REFUTATION GATE LOG — F-003:**
```
Candidate verdict : INTENT (ZeroTier como canal de acceso — circunstancialmente fuerte)
Gate applied      : Daubert Corroboration Gate
Gate rule         : No se puede establecer ZeroTier como vector de ataque desde
                    artefactos disponibles; tráfico de red, ZeroTier Network ID
                    y logs locales de ZeroTier ausentes.
Gate result       : Corroboración INSUFICIENTE para atribución de vector.
                    ZeroTier escalado a INTENT solo en análisis combinado.
Forensic note     : La brecha temporal (Feb 6 → Feb 12) es sospechosa pero no
                    confirmable causalmente con los artefactos disponibles.
```

**Devil's Advocate:** Patrick instaló ZeroTier para gaming en LAN (uso común y legítimo). El atacante usó un vector de acceso inicial diferente.

---

### F-004 — Reset de password del Built-in Administrator — toma de control del recovery path

| Campo | Valor |
|-------|-------|
| **Verdict** | **MALICE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | `evtx/Security.evtx` (4724 @ 02:17:18Z) |
| **Tools** | Python/Evtx parser |
| **MITRE TTPs** | T1098 · T1078.003 |

**Firstness:** Security.evtx [4724] @ 2022-02-12 02:17:18Z: password del Administrator [RID 500] reseteada por `SubjectUserSid: S-1-5-18`. La cuenta Administrator está deshabilitada (Login Count: 0, Last Login: Never en SAM), pero su password fue actualizada 48 minutos después de la estabilización de minecraftsteve.

**Secondness:** Resetear la password del Administrator deshabilitado da al atacante una credencial de recuperación secundaria que puede habilitar a demanda. También impide que el propietario legítimo use la cuenta built-in para recuperación. Es una medida anti-recuperación deliberada.

**Thirdness:** Arquitectura de dos backdoors: `minecraftsteve` (activa, usable inmediatamente por RDP/WinRM) + `Administrator` (dormante, habilitável como segunda opción). Ambas passwords controladas por el atacante. Patrón "belt and suspenders" de un atacante preparando persistencia a largo plazo.

**Devil's Advocate:** Patrick resetó accidentalmente la password del Administrator con un script de automatización mal configurado.

**Refutación:** `SubjectUserSid = S-1-5-18` sin sesión de Patrick activa. Mismo actor, misma sesión de ~2 horas. La proximidad temporal con las operaciones de minecraftsteve elimina la coincidencia.

---

### F-005 — Gaps de auditoría (NOISE)

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | `hives/SECURITY` (auditpol plugin) |

Process Creation (4688) y Credential Validation (4776) no estaban auditados. LastWrite de `PolAdtEv`: **2022-02-04 07:02:36Z** — coincide con la fecha de instalación del OS. Configuración **por defecto**, no modificada por el atacante. El atacante se benefició de estos gaps pero con alta probabilidad no los creó.

---

## ARTEFACTOS EXAMINADOS

| Herramienta | Objetivo | Resultado |
|-------------|----------|-----------|
| `generate_forensic_hash` | 10 artefactos | INTEGRITY_VERIFIED (todos) |
| `list_files` | 3 directorios | 10 artefactos mapeados |
| `read_evidence` | sam.txt, security.txt | Contenido completo extraído |
| `read_evidence` | system.txt, software.txt | Parcial (50KB); grep complementario |
| `detect_habit_incongruence` | SAM account management | MALICE, 6/6 anomalías, 90% probabilidad |
| `detect_eco_overinterpretation` | 8 ítems de evidencia | NORMAL_DISTRIBUTION — no fabricado |
| `validate_and_correct_analysis` | Análisis completo | Sin correcciones requeridas |
| Python/Evtx (`python-evtx`) | Security.evtx | 4720/4722/4724/4728/4732 confirmados |
| Python/Evtx | System.evtx | 7040 TermService + 7045 ZeroTier/Java confirmados |
| Python/Evtx | Application.evtx | MSI ZeroTier+Java instalaciones confirmadas |
| Grep (rip_output) | *.txt | Run keys, ZeroTier, TermService localizados |

---

## LIMITACIONES CONOCIDAS

| ID | Limitación |
|----|-----------|
| L-1 | Process Creation (4688) no auditado durante el ataque. No se puede identificar el proceso exacto que ejecutó `net user`/`net localgroup` (cmd.exe, PowerShell, WMI, etc.). |
| L-2 | ZeroTier no puede confirmarse como vector de acceso inicial. No hay capturas de red, ZeroTier Network ID ni logs locales de ZeroTier en este set de evidencia. No se puede descartar un vector alternativo (explotación de CVE en Java, Discord malware, brute force RDP previo al 6 de febrero). |
| L-3 | Sin prefetch, MFT, shellbags ni artefactos de browser. No se puede determinar qué hizo Patrick entre el 21 de enero (último logon) y el 6 de febrero (instalación de ZeroTier). |
| L-4 | Java 8u181 (2018) tiene múltiples CVEs conocidos. No se puede confirmar explotación desde datos de registro/event log. |
| L-5 | Modo LLM: Claude Code (Anthropic API). `reason_with_llm` disponible pero no requerido — todos los hallazgos con veredicto se apoyan en evidencia dura (registro/EVTX). |

---

## VEREDICTO GENERAL: MALICE

**Dos cadenas de evidencia independientes confirmadas:**

- **Cadena A:** 4720 → 4722 → 4724 → 4732×2 → 4724×2 (cuenta + grupos + passwords — todo SYSTEM)
- **Cadena B:** 7040 TermService Auto Start (confirmado por SYSTEM hive + System.evtx)

Ambas cadenas: sin sesión interactiva de Patrick, actor SYSTEM, ventana de ataque 01:01–02:17 UTC.

| Verificación | Estado |
|-------------|--------|
| Mandatory Refutation Protocol | APPLIED — hipótesis benigna **refutada** |
| `devil_advocate` field | Poblado en F-001, F-002, F-004 — todos refutados |
| Eco overinterpretation test | NORMAL_DISTRIBUTION — evidencia no fabricada/plantada |
| `validate_and_correct_analysis` | Sin correcciones requeridas |
| Fuentes independientes (Daubert) | ≥2 para todos los hallazgos INTENT/MALICE |

---

## ACCIONES INMEDIATAS RECOMENDADAS

1. **AISLAR** el host de la red — desconectar interfaz ZeroTier (driver `zttap300.sys`) primero
2. **CAMBIAR** todas las credenciales — cuenta de Patrick, cuentas de servicio en este host
3. **ELIMINAR** la cuenta `minecraftsteve` y verificar que el Administrator vuelva a estar deshabilitado
4. **DESHABILITAR** `TermService` (RDP) si no es requerido legítimamente
5. **OBTENER** el ZeroTier Network ID desde `C:\ProgramData\ZeroTier\One\networks.d\` para identificar la red C2 del atacante
6. **ADQUIRIR** imagen forense completa del disco para análisis de MFT, prefetch y artefactos de browser
7. **BUSCAR** artefactos de explotación de Java en `%APPDATA%\Sun\Java\Deployment\cache\`

---

## TOKEN USAGE

```
Mode       : Claude Code + MCP (Mode 2)
LLM        : Claude Sonnet 4.6 (Anthropic API)
Session ID : 2026-06-29T02:00:00Z
Note       : Desglose completo disponible en usage.anthropic.com
```

---

*VIGÍA — Making deception computationally expensive since 2026.*
*"Si un sistema afirma MALICE sin explicarlo con matemáticas exactas, no es forense. Es adivinación."*
