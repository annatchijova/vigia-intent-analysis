# VIGIA FORENSIC INTENT ANALYSIS REPORT

| Campo | Valor |
|-------|-------|
| **Case ID** | VIGIA-MAGNET-2022-WINDOWS-FULL |
| **Investigator** | VIGÍA Autonomous Agent (Claude Code / Anthropic) |
| **Evidence** | `evidence/magnet-2022-windows-full/` |
| **Mode** | Claude Code + MCP (Mode 2) — Claude Opus 4.6 |
| **Timestamp** | 2026-07-04T00:30:00Z (UTC) |
| **SANS Phase** | PICERL — Eradication / Recovery |

---

## CHAIN OF CUSTODY

| Artifact | SHA-256 |
|----------|---------|
| Security.evtx | `b050682f7fe96938aca2fc19a96d24641173b4f31a4f3837119ea916663344c1` |
| System.evtx | `962edaf7f38dbb4f81e7e8e586af56ae063a5caaa40d1c8a68165b3ef8f66129` |
| Amcache.hve | `ba7b37b02c209e8237cc1c4bfa8497b44b8f98ac65fa1dd0a6ac45a98ab8a9aa` |
| SYSTEM hive | `545ac21ca335836d97f20580a97603b777284751358f5a97bff60d90f9230db2` |
| SAM hive | `4aec3ac88863e8f6a57dce79006f41d4b99adc519b160aabb5c418400c9e521e` |
| Browser History | `59641e2f78e28983b16beedfb883cafa26d25adfad0397d7e7ac14814d2f9919` |

All hashes generated **before** content was read. Chain of custody intact.

---

## HOST PROFILE

| Campo | Valor |
|-------|-------|
| Hostname | DESKTOP-SKPTDIO |
| Workgroup | WORKGROUP |
| OS | Windows 10/11 (Build 22543) |
| Hardware | HP laptop, Intel Kaby Lake |
| User | Patrick (pbentley0107@gmail.com) |
| User SID | S-1-5-21-3341181097-1059518978-806882922-1001 |
| Groups | Administrators |
| Gamertag | DreadGlitter366 (Xbox/Minecraft) |

---

## EXECUTIVE SUMMARY

Host **DESKTOP-SKPTDIO** fue comprometido entre el 6 y el 12 de febrero de 2022 en una campaña de ataque progresiva. El atacante instaló **ZeroTier One** (VPN P2P cifrada) el 6 de febrero como canal de acceso persistente, deshabilitó Windows Defender Real-Time Protection 6 veces, ejecutó **AMSI bypass** (VirtualProtect patch de AmsiScanBuffer), desplegó **Meterpreter x64 shellcode** (10 ejecuciones, C2: `192.168.191.253:443/4443`), intentó **Powercat** backdoor, instaló **TrojanDropper:VBS/Ploty.A** con Run-key persistence, creó la cuenta backdoor **`minecraftsteve`** (Administrators + Remote Management Users), habilitó RDP, y reseteó la password del Built-in Administrator. Todo ejecutado como LOCAL SYSTEM (S-1-5-18) sin sesión interactiva.

**Veredicto general: MALICE.**

**Mode 1 emitió NOISE (falso negativo).** Las señales individuales no excedieron z>2 porque cada evento es un evento Windows legítimo bien formateado. El MALICE emerge del patrón compuesto temporal y del actor (S-1-5-18 sin sesión interactiva).

---

## C2 INFRASTRUCTURE

| IP | Puerto | Protocolo | Herramienta |
|----|--------|-----------|-------------|
| 192.168.191.253 | 4443 | TCP | PowerShell reverse shell |
| 192.168.191.253 | 443 | TCP | Meterpreter x64 shellcode |

IP privada — atacante en el mismo segmento LAN o accesible via ZeroTier overlay.

---

## ATTACK TIMELINE

```
2022-01-20 06:56  Patrick compra Minecraft Java Edition (minecraft.net) — LEGÍTIMO
2022-01-20 07:26  MinecraftInstaller.exe descargado de launcher.mojang.com — LEGÍTIMO
2022-02-04 07:02  Boot, Patrick login (Type 11 CachedInteractive)
2022-02-06 06:26  Patrick login
2022-02-06 07:15  ZeroTier One service instalado (auto start, LocalSystem)
2022-02-06 07:22  ZeroTier TAP driver (zttap300.sys) instalado
2022-02-06 07:51  Defender RTP DISABLED (1ª vez)
2022-02-09 22:44  Defender detecta CapfetoxLDAP.E (LDAP enum) — Remove
                  Defender detecta BypassAMSI — Quarantine
2022-02-09 23:33  Defender RTP DISABLED (2ª vez)
2022-02-09 23:34  AMSI bypass ejecutado (VirtualProtect patch AmsiScanBuffer)
                  PS reverse shell → 192.168.191.253:4443
2022-02-11 01:18  Patrick busca "how to know if you've been hacked"
2022-02-11 01:21  Patrick busca "how to report a hacker?" — VÍCTIMA CONSCIENTE
2022-02-11 23:00  Powercat (Backdoor:PowerShell/Powercat.A) × 4 — Quarantine
2022-02-11 23:04  Defender RTP DISABLED (3ª vez)
2022-02-11 23:19  Primer Meterpreter x64 shellcode (C2: 192.168.191.253:443)
2022-02-11 23:26  Segundo shellcode
2022-02-11 23:29  Tercero
2022-02-11 23:47  Cuarto
2022-02-11 23:53  Quinto
2022-02-12 00:04  Sexto
2022-02-12 00:17  Staged payload: GzipStream+B64 + reflective DLL injection
2022-02-12 01:01  TermService (RDP) → AUTO START
2022-02-12 01:29  Cuenta 'minecraftsteve' CREADA por S-1-5-18
2022-02-12 01:29  minecraftsteve HABILITADA + password SET
2022-02-12 01:37  minecraftsteve → Administrators (S-1-5-32-544)
2022-02-12 01:37  minecraftsteve → Remote Management Users (S-1-5-32-580)
2022-02-12 01:45  TrojanDropper:VBS/Ploty.A + HKCU Run key — Quarantine
2022-02-12 02:06  minecraftsteve password RESET (estabilización)
2022-02-12 02:17  Built-in Administrator password RESET por S-1-5-18
2022-02-12 04:30  Defender detecta Meterpreter.gen!A en PIDs 6384,13664,11964,14296
2022-02-12 22:40  Defender RTP DISABLED (4ª vez)
2022-02-12 22:48  Defender RTP DISABLED (5ª vez)
2022-02-12 22:53  Meterpreter shellcode ejecución 7-9
2022-02-12 23:18  Defender RTP DISABLED (6ª vez)
2022-02-12 23:19  Meterpreter shellcode ejecución 10
```

Duración total del compromiso: **6 días** (Feb 6 → Feb 12).
Sesión de ataque activa principal: **~3 horas** (Feb 12, 01:01 → 04:30 UTC).

---

## FINDINGS

### F-001 — ZeroTier One VPN como canal C2 persistente

| Campo | Valor |
|-------|-------|
| **Verdict** | **INTENT** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | System.evtx, SYSTEM hive, Amcache.hve |
| **MITRE TTPs** | T1133, T1571, T1573.002 |

**Firstness:** Service 'ZeroTier One' instalado 2022-02-06 07:15:35 UTC. ImagePath: `C:\ProgramData\ZeroTier\One\zerotier-one_x64.exe`. Auto start, LocalSystem. TAP driver `zttap300.sys` instalado 7 min después.

**Secondness:** ZeroTier crea redes overlay cifradas P2P que evaden firewalls perimetrales. Instalación durante sesión de Patrick (06:26). Sin embargo, ZeroTier también se usa para jugar Minecraft LAN — Patrick es jugador documentado.

**Thirdness:** La combinación ZeroTier + posterior gestión de cuentas por SYSTEM sin sesión interactiva indica que ZeroTier fue el canal de ingreso C2. 8 ejecuciones confirmadas en prefetch. El C2 Meterpreter usa IP privada `192.168.191.253` — posiblemente accesible via overlay ZeroTier.

**Devil Advocate:** ZeroTier es comúnmente instalado por jugadores de Minecraft Java para LAN-over-internet. Patrick compró Minecraft el 20 de enero y tiene artefactos legítimos de juego. Sin embargo, esto no explica la actividad maliciosa posterior.

---

### F-002 — AMSI Bypass (VirtualProtect patch de AmsiScanBuffer)

| Campo | Valor |
|-------|-------|
| **Verdict** | **MALICE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | PowerShell Operational (4104), Defender Operational (1116/1117) |
| **MITRE TTPs** | T1562.001 (Disable/Modify Tools), T1059.001 (PowerShell) |

**Firstness:** Script PowerShell capturado por Script Block Logging (EID 4104) a 2022-02-09 23:34:55. Define P/Invoke stubs para `GetProcAddress`, `LoadLibrary`, `VirtualProtect`. Carga `amsi.dll` con ofuscación de strings (`[cHAR]` + aritmética de bytes). Resuelve `AmsiScanBuffer` via normalización Unicode + regex. Parchea con `0xB8,0x57,0x00,0x07,0x80,0xC3` (`mov eax,0x80070057; ret`) — AMSI retorna `E_INVALIDARG`.

**Secondness:** Este es el bypass AMSI canónico documentado. Defender lo detectó inicialmente (22:44, VirTool:PowerShell/BypassAMSI, Quarantine). A las 23:33, Defender RTP fue DESHABILITADO. El script reaparece a las 23:34 — el atacante deshabilitó RTP para re-ejecutar.

**Thirdness:** Evasión deliberada de seguridad. El atacante: (1) intentó bypass AMSI, (2) fue detectado y puesto en cuarentena, (3) deshabilitó Defender, (4) re-ejecutó exitosamente. Esto es anti-forensics activo.

---

### F-003 — Meterpreter x64 Shellcode (10 ejecuciones)

| Campo | Valor |
|-------|-------|
| **Verdict** | **MALICE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | PowerShell Operational (4104), Defender Operational (1116/1117) |
| **MITRE TTPs** | T1055.001 (DLL Injection), T1059.001 (PowerShell), T1071.001 (Web C2) |

**Firstness:** Shellcode `fc4883e4f0e8cc000000...` — stub de alineación de stack x64 + PEB walk (Meterpreter/Cobalt Strike). Loader: VirtualAlloc → Marshal::Copy → CreateThread. C2 extraído de sockaddr_in (offset 0xe8): `192.168.191.253:443`.

**Secondness:** 10 ejecuciones entre 2022-02-11 23:19 y 2022-02-12 23:19. Defender detectó `Behavior:Win32/Meterpreter.gen!A` en PIDs 6384, 13664, 11964, 14296 — inyección reflectiva en múltiples procesos incluyendo `explorer.exe`.

**Thirdness:** Implant de post-explotación profesional. Múltiples ejecuciones + múltiples PIDs indican persistencia en memoria con re-inyección tras detección. El atacante mantuvo acceso durante >24 horas a pesar de detecciones de Defender.

---

### F-004 — Cuenta backdoor 'minecraftsteve' creada por LOCAL SYSTEM

| Campo | Valor |
|-------|-------|
| **Verdict** | **MALICE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | Security.evtx, SAM hive |
| **MITRE TTPs** | T1136.001, T1078.003, T1098 |

**Firstness:** User `minecraftsteve` (RID 1002) creado 2022-02-12 01:29:43 UTC. SubjectUserSid: S-1-5-18 (LOCAL SYSTEM). Login Count: 0.

**Secondness:** S-1-5-18 creando cuentas de usuario es estructuralmente imposible via operaciones interactivas normales. No hay sesión interactiva de Patrick entre Feb 11 22:46 y Feb 12 22:47.

**Thirdness:** Cuenta backdoor con naming Carnegie (authority transfer: nombre de juego en máquina de gamer). Secuencia completa: create → enable → set password → Administrators → Remote Management Users → password reset → Administrator password reset. 76 minutos de operación.

**Devil Advocate:** No hay servicio legítimo de Windows que cree cuentas admin llamadas 'minecraftsteve'. El Login Count=0 confirma que fue creada para uso futuro. Patrick buscó "how to report a hacker" el día anterior.

---

### F-005 — Defender RTP deshabilitado 6 veces

| Campo | Valor |
|-------|-------|
| **Verdict** | **MALICE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | Defender Operational (5001) |
| **MITRE TTPs** | T1562.001 (Disable/Modify Tools) |

RTP deshabilitado antes de cada fase de ataque: Feb 6 (post-ZeroTier), Feb 9 (pre-AMSI bypass), Feb 11 (pre-Meterpreter), Feb 12 × 3 (ejecuciones tardías). Patrón: disable → execute → RTP re-enables on reboot → disable again.

---

### F-006 — TrojanDropper:VBS/Ploty.A con Run-key persistence

| Campo | Valor |
|-------|-------|
| **Verdict** | **MALICE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | Defender Operational (1116/1117) |
| **MITRE TTPs** | T1547.001 (Run Key), T1059.005 (VBScript) |

Files: `C:\Users\Patrick\AppData\Local\Temp\flWNZUu.vbs`, `xPSPLcEr.vbs`. Registry: `HKCU\SOFTWARE\MICROSOFT\WINDOWS\CURRENTVERSION\RUN\gCxznIQLuQTUQn`. Defender detectó y puso en cuarentena.

---

### F-007 — MinecraftInstaller.exe de minecraft.net — FALSE POSITIVE

| Campo | Valor |
|-------|-------|
| **Verdict** | **NOISE** |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifacts** | Browser History |

MinecraftInstaller.exe (31.4 MB) descargado de `launcher.mojang.com` (CDN oficial de Mojang/Microsoft). Flujo de compra completo: minecraft.net → login → purchase → download. Confirmado FP legítimo.

---

### F-008 — CERTUTIL.EXE en path ZeroTier — bundled con TAP driver

| Campo | Valor |
|-------|-------|
| **Verdict** | **NOISE** |
| **Confidence** | MEDIUM |
| **Status** | CONFIRMED |
| **Artifacts** | Amcache.hve, Prefetch |

certutil.exe en `c:\program files\zerotier\zerotier one virtual network port\zttap300\`. Versión Windows 7 SP1 (2013). Ejecutado una vez (2022-02-06 10:16:05) para instalar `ZTTAP300.CER` (certificado del TAP driver). No LOLBin. Bundled con el instalador ZeroTier.

---

### F-009 — PS1 con nombres aleatorios en TEMP

| Campo | Valor |
|-------|-------|
| **Verdict** | **SUSPICION** |
| **Confidence** | MEDIUM |
| **Status** | INFERRED |
| **Artifacts** | Prefetch (POWERSHELL.EXE-CA1AE517.pf) |

`BMZBLBHU.PS1`, `GPQZTZGF.PS1`, `CIMMSKAC.PS1` — nombres de 8 caracteres consonantes aleatorios. Patrón consistente con staging scripts de malware. Contenido no disponible (solo referencia en prefetch).

---

## REFUTATION PROTOCOL (Eco's Razor)

**Hipótesis benigna:** Patrick es un usuario normal que juega Minecraft, usa Discord, mira videos de sellos en YouTube, juega ajedrez, e instaló ZeroTier para jugar Minecraft LAN. Los eventos de gestión de cuentas son de un proceso legítimo del sistema.

**Test contra evidencia completa:** **RECHAZADA.**

La hipótesis benigna explica: Minecraft, Discord, ZeroTier (parcialmente), Java JDK.

La hipótesis benigna **NO explica:**
1. AMSI bypass script (VirtualProtect patch de AmsiScanBuffer) — código ofensivo profesional
2. Meterpreter x64 shellcode × 10 con C2 a 192.168.191.253
3. Powercat backdoor (netcat PowerShell)
4. TrojanDropper:VBS/Ploty.A con Run-key persistence
5. Defender RTP deshabilitado 6 veces (anti-forensics)
6. Cuenta 'minecraftsteve' creada por S-1-5-18 sin sesión interactiva
7. minecraftsteve → Administrators + Remote Management Users
8. RDP habilitado 28 minutos antes de la creación de la cuenta backdoor
9. Built-in Administrator password reset
10. LDAP enumeration (CapfetoxLDAP.E)
11. Patrick buscando "how to report a hacker" (víctima consciente)

**Gate applied:** Daubert Corroboration Gate: ≥2 fuentes independientes para MALICE
**Gate passed:** Sí — 5+ fuentes independientes (Security.evtx, System.evtx, PowerShell Operational, Defender Operational, Browser History)

---

## MODE 1 FALSE NEGATIVE ANALYSIS

| Campo | Valor |
|-------|-------|
| **Root cause** | COMPOUND_PATTERN_BLINDNESS |
| **z-scores Mode 1** | REGISTRY_RTR=1.96, PREFETCH=1.75, EVENT_LOG=1.45 |
| **Threshold** | z>2 (ninguna señal lo excedió) |
| **CAIE result** | INCONCLUSIVE, 0 fractures |
| **Verdict emitido** | NOISE (falso negativo) |

**Diagnóstico:** Mode 1 evalúa cada señal de artefacto independientemente. Las z-scores individuales no excedieron z>2 porque cada evento es un evento Windows legítimo bien formateado. El MALICE emerge del **patrón compuesto temporal** (VPN + AMSI bypass + Meterpreter + account creation + privilege escalation + RDP + credential reset, todo por S-1-5-18 sin sesión interactiva) y del análisis semántico del Script Block Logging (que requiere LLM/human para interpretar).

**Recommended fix:** 
1. CAIE debería detectar "SYSTEM como actor para user management sin sesión interactiva" como fracture pattern
2. Agregar correlación temporal para secuencias service_enable + account_create + privilege_escalate
3. El pipeline debería integrar Defender Operational (5001 RTP disable + 1116/1117 detections) como señales de alta prioridad
4. PowerShell Script Block Logging (4104) con contenido ofensivo requiere análisis semántico — considerar heurísticas para VirtualAlloc+CreateThread, AMSI bypass patterns

---

## KNOWN LIMITATIONS

- **L-001:** No Sysmon instalado — EID 8 (CreateRemoteThread) no disponible. La señal "REMOTE_THREAD_INJECTION" del Mode 1 fue inferida, no de un evento real.
- **L-002:** Prefetch MAM-compressed (Xpress Huffman) — decompresión requiere APIs Windows. Paths de archivos accedidos por CERTUTIL/POWERSHELL no extraídos completamente.
- **L-003:** Command line auditing no habilitado — 4688 sin CommandLine.
- **L-004:** No memory dump ni disk image completa — no se puede verificar conexiones ZeroTier reales.
- **L-005:** Contenido de PS1 maliciosos (BMZBLBHU, GPQZTZGF, CIMMSKAC) no disponible — solo referencia en prefetch.
- **L-006:** ZeroTier `SAVED_NETWORKS.JSON` no examinado — requiere verificar qué redes overlay fueron configuradas.

---

## ARTIFACTS EXAMINED

| Tool/Source | Arguments | Result |
|-------------|-----------|--------|
| python-evtx | Security.evtx (29,465 records) | 4688 × 62, 4624 × 1337, 4720/4722/4724/4728/4732 × 8 |
| python-evtx | System.evtx (1,349 records) | 7045 × 53, 7040 × 117 |
| python-registry | Amcache.hve (361 entries) | certutil in ZeroTier path, Java JDK 8u181 |
| python-registry | SYSTEM hive | ZeroTier service (Start=2), TermService |
| sqlite3 | Browser History | 80+ URLs, 2 downloads (MinecraftInstaller.exe official) |
| PowerShell Operational | Script Block Logging | AMSI bypass, Meterpreter shellcode × 10 |
| Defender Operational | Detections + RTP events | 5 malware families detected, 6 RTP disables |
| Prefetch (MAM) | CERTUTIL, POWERSHELL × 2, CMD × 2, ZEROTIER | Partially extracted (compression limitation) |

---

## MITRE ATT&CK MAPPING

| Tactic | Technique | Evidence |
|--------|-----------|----------|
| Initial Access | T1133 External Remote Services | ZeroTier VPN |
| Execution | T1059.001 PowerShell | AMSI bypass, Meterpreter loader, reverse shell |
| Execution | T1059.005 VBScript | TrojanDropper:VBS/Ploty.A |
| Persistence | T1547.001 Registry Run Keys | HKCU Run key gCxznIQLuQTUQn |
| Persistence | T1136.001 Create Local Account | minecraftsteve |
| Persistence | T1543.003 Windows Service | ZeroTier auto-start |
| Privilege Escalation | T1098 Account Manipulation | Administrators + Remote Management Users |
| Defense Evasion | T1562.001 Disable/Modify Tools | Defender RTP × 6, AMSI bypass |
| Defense Evasion | T1055.001 DLL Injection | Reflective DLL injection via Meterpreter |
| Credential Access | T1078.003 Valid Accounts | Administrator password reset |
| Discovery | T1087 Account Discovery | CapfetoxLDAP.E |
| Lateral Movement | T1021.001 Remote Desktop | TermService enabled |
| Command & Control | T1573.002 Asymmetric Crypto | ZeroTier encrypted overlay |
| Command & Control | T1071.001 Web Protocols | Meterpreter C2 port 443 |

---

*VIGÍA — Making deception computationally expensive since 2026.*

*Bundle SHA-256: `aeb821275fd6855100376637a10b76c85d9ee811c037f462cd27bf3b60743c20`*
*Bundle: `cases/VIGIA-MAGNET-2022-WINDOWS-FULL_bundle_claude.json`*
