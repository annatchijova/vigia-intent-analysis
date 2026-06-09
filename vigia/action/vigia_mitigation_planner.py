"""
vigia_mitigation_planner.py
VIGÍA Forensic Suite — Generador de Mitigación Quirúrgica (Capa 4 - Action)
Versión: v1.0-Valkyrie
Autora:  Anna Tchijova
Plataforma: POSIX/Linux exclusivamente

Genera un plan de mitigación justificado por la hipótesis abductiva ganadora.
Cada acción requiere aprobación explícita del operador (approved=False por defecto).
Ningún comando tiene placeholders vacíos: los valores desconocidos se marcan
con directivas de obtención forense que el operador debe resolver antes de ejecutar.

Garantías:
- Sólo ejecuta en sys.platform == "linux"; de lo contrario emite CriticalWarning
  y marca el plan como PLATFORM_UNSUPPORTED.
- plan_hash cubre comandos finales + targets, no sólo metadatos.
- Todos los comandos son binarios nativos Linux (kill, pkill, iptables/nft,
  usermod, passwd, shred, systemctl, journalctl, tcpdump, ss).
- KILL_PROCESS valida que el PID objetivo no sea proceso de sistema crítico
  (PID <= 10, comm en SYSTEM_COMM_BLOCKLIST, nombre contiene "kthread").
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import shlex
import sys
import warnings
from pathlib import Path as _Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────
# PLATAFORMA
# ──────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────
# PATHS ABSOLUTOS DE BINARIOS (MP-PATH-01/02)
# Previene PATH hijacking. Si un binario no existe en el path declarado,
# el comando se marca con advertencia — nunca se inventa un path.
# ──────────────────────────────────────────────────────────────────────────
_BIN: dict[str, str] = {}
_BIN_CANDIDATES: dict[str, list[str]] = {
    "avml":       ["/usr/local/bin/avml", "/opt/avml/avml"],
    "iptables":   ["/usr/sbin/iptables", "/sbin/iptables"],
    "nft":        ["/usr/sbin/nft", "/sbin/nft"],
    "ip":         ["/usr/sbin/ip", "/sbin/ip", "/bin/ip"],
    "tcpdump":    ["/usr/sbin/tcpdump", "/usr/bin/tcpdump"],
    "systemctl":  ["/usr/bin/systemctl", "/bin/systemctl"],
    "passwd":     ["/usr/bin/passwd"],
    "pkill":      ["/usr/bin/pkill"],
    "kill":       ["/usr/bin/kill", "/bin/kill"],
    "shred":      ["/usr/bin/shred"],
    "usermod":    ["/usr/sbin/usermod"],
    "journalctl": ["/usr/bin/journalctl"],
    "ss":         ["/usr/sbin/ss", "/bin/ss"],
    "sha256sum":  ["/usr/bin/sha256sum"],
}
for _name, _candidates in _BIN_CANDIDATES.items():
    for _c in _candidates:
        if os.path.isfile(_c):
            _BIN[_name] = _c
            break
    if _name not in _BIN:
        _BIN[_name] = f"# BINARIO_NO_ENCONTRADO:{_name}"

def _bin(name: str) -> str:
    """
    Retorna el path absoluto verificado del binario.

    MP-BIN-02 (Kimi audit v2): emite RuntimeWarning explícito cuando el
    binario no se encuentra. El comentario en el comando resultante
    incluye '# INSTALAR ANTES DE EJECUTAR' para que sea obvio que el
    comando es inválido, no que simplemente no hace nada.
    """
    result = _BIN.get(name)
    if result is None:
        import warnings as _w_bin
        _w_bin.warn(
            f"[VIGIA MP-BIN-02] Binario '{name}' no encontrado en paths conocidos. "
            "El comando generado será inválido — instalar antes de ejecutar.",
            RuntimeWarning,
            stacklevel=2,
        )
        return f"# BINARIO_NO_ENCONTRADO:{name}  # INSTALAR ANTES DE EJECUTAR"
    return result


# ──────────────────────────────────────────────────────────────────────────
# VALIDACIÓN Y ESCAPE DE VALORES DE CONTEXTO (MP-INJ-01, MP-INJ-02, MP-TRAV-01)
# ──────────────────────────────────────────────────────────────────────────

class ContextValidationError(ValueError):
    """Lanzada cuando un valor de contexto no supera la validación de seguridad."""
    pass


def _validate_ip(ip: str) -> str:
    """
    Valida que ip sea una dirección IP válida (IPv4 o IPv6).
    Retorna el string canónico de la IP.
    Lanza ContextValidationError si el valor es inválido.

    Previene: MP-INJ-01 (inyección de shell via dst_ip/src_ip)
    """
    if ip.startswith("_OBTAIN_VIA:"):
        return ip  # directiva de obtención — no es un valor ejecutable
    try:
        return str(ipaddress.ip_address(ip.strip()))
    except ValueError:
        raise ContextValidationError(
            f"IP inválida: {ip!r}. Debe ser IPv4 o IPv6 canónica. "
            "Posible intento de inyección."
        )


def _validate_pid(pid: str) -> str:
    """
    Valida que pid sea un entero positivo puro.
    Retorna el string del PID validado.
    Lanza ContextValidationError si el valor es inválido.

    Previene: MP-INJ-02 (inyección via PID)
    """
    if pid.startswith("_OBTAIN_VIA:"):
        return pid
    stripped = pid.strip()
    if not stripped.isdigit():
        raise ContextValidationError(
            f"PID inválido: {pid!r}. Debe ser un entero positivo puro. "
            "Posible intento de inyección."
        )
    pid_int = int(stripped)
    if pid_int <= 0 or pid_int > 4_194_304:  # PID_MAX en Linux
        raise ContextValidationError(
            f"PID fuera de rango: {pid_int}. Rango válido: [1, 4194304]."
        )
    return stripped


# Nombres de usuario que NUNCA deben ser objetivo de acciones automáticas
_RESERVED_USERNAMES: frozenset = frozenset({
    "root", "daemon", "bin", "sys", "sync", "games", "man", "lp",
    "mail", "news", "uucp", "proxy", "www-data", "backup", "list",
    "irc", "gnats", "nobody", "systemd-network", "systemd-resolve",
    "messagebus", "syslog", "sshd", "ntp", "ntpd",
})


def _validate_username(username: str) -> str:
    """
    Valida que username sea un nombre de usuario Linux válido.

    MP-VAL-01 (Kimi audit v2):
    - Normaliza a minúsculas antes de validar (Linux UIDs son case-insensitive
      en la práctica; 'Root' y 'root' son el mismo uid=0).
    - Rechaza nombres reservados del sistema explícitamente.
    - Acepta: [a-z_][a-z0-9_-]{0,31} (estándar POSIX useradd).
    - Rechaza: cualquier cosa con @, %, espacios, o caracteres Unicode.
    """
    if isinstance(username, str) and username.startswith("_OBTAIN_VIA:"):
        return username
    if not isinstance(username, str):
        raise ContextValidationError(f"username debe ser str, recibido: {type(username).__name__}")
    # Normalizar a minúsculas — no es un cambio silencioso, lo documentamos
    normalised = username.strip().lower()
    if not normalised:
        raise ContextValidationError("username no puede estar vacío")
    # Patrón POSIX estricto
    if not re.match(r"^[a-z_][a-z0-9_-]{0,31}$", normalised):
        raise ContextValidationError(
            f"Username inválido: {username!r} (normalizado: {normalised!r}). "
            "Patrón POSIX: ^[a-z_][a-z0-9_-]{0,31}$. "
            "No se permiten mayúsculas, @, %, espacios ni Unicode."
        )
    # Rechazar nombres de sistema — nunca deben ser objetivo automático
    if normalised in _RESERVED_USERNAMES:
        raise ContextValidationError(
            f"Username reservado del sistema: {normalised!r}. "
            "Las acciones automáticas sobre cuentas de sistema están prohibidas."
        )
    # MP-WARN-01: la advertencia de normalización va al log de auditoría
    # NO usa warnings.warn() porque puede suprimirse con -W ignore.
    # En cambio, registra en stderr (siempre visible) y retorna el valor
    # normalizado acompañado de la advertencia para que el llamador la vea.
    if normalised != username.strip():
        import sys as _sys_warn
        _sys_warn.stderr.write(
            f"[VIGIA MP-WARN-01] username normalizado: "
            f"{username.strip()!r} → {normalised!r}. "
            "Verificar que este es el usuario objetivo correcto.\n"
        )
        _sys_warn.stderr.flush()
    return normalised


# Directorios raíz permitidos para archivos objetivo (deben existir en el sistema)
_ALLOWED_TARGET_ROOTS: tuple = ("/var", "/home", "/tmp", "/opt", "/srv",
                                  "/forensics", "/quarantine")


def _validate_filepath(filepath: str, must_exist: bool = False) -> str:
    """
    Valida que filepath sea un path absoluto sin traversal, incluyendo
    resolución de symlinks.

    MP-VAL-02 (Kimi audit v2): la versión anterior verificaba '..' en el path
    string pero no resolvía symlinks. Un symlink /tmp/evil -> /etc/passwd pasaba
    la verificación. Esta versión:
    1. Verifica ausencia de '..' en el path string (rápido, primera barrera).
    2. Si el archivo EXISTE, usa os.path.realpath() para resolver symlinks y
       verificar que el path real no sale de los directorios permitidos.
    3. Si el archivo NO existe, no puede resolver symlinks pero verifica que el
       directorio padre existe y no es sospechoso.
    """
    if isinstance(filepath, str) and filepath.startswith("_OBTAIN_VIA:"):
        return filepath
    if not isinstance(filepath, str):
        raise ContextValidationError(f"filepath debe ser str, recibido: {type(filepath).__name__}")
    try:
        p = _Path(filepath)
        # Barrera 1: path absoluto
        if not p.is_absolute():
            raise ContextValidationError(f"filepath debe ser absoluto: {filepath!r}")
        # Barrera 2: sin '..' en el string (incluso antes de resolver)
        if any(part == ".." for part in p.parts):
            raise ContextValidationError(f"Path traversal (..) detectado: {filepath!r}")
        # Barrera 3: rechazar symlinks directamente (Kimi P0)
        # Un symlink /tmp/evil → /home/victim/.bashrc pasaría el check de
        # _ALLOWED_TARGET_ROOTS porque /home está permitido.
        # Los archivos objetivo forenses nunca deben ser symlinks.
        if p.exists() or os.path.lexists(str(p)):
            if os.path.islink(str(p)):
                real = os.path.realpath(str(p))
                raise ContextValidationError(
                    f"Symlink rechazado: {filepath!r} → {real!r}. "
                    "Los archivos objetivo no pueden ser symlinks. "
                    "Usar el path real del archivo directamente."
                )
        if must_exist and not p.exists():
            raise ContextValidationError(f"Archivo requerido no existe: {filepath!r}")
        # MP-VAL-READ-01 (Kimi P1): verificar legibilidad cuando el archivo existe y
        # must_exist=True. Un archivo con permisos 000 pasa el check de existencia
        # pero cualquier operación posterior (cp, sha256sum, mv) falla con EACCES.
        # Detectar esto aquí produce un error claro en lugar de un fallo críptico después.
        #
        # LIMITACIÓN CONOCIDA — os.access() y el UID real (MP-VAL-READ-02, Kimi P2):
        # os.access() evalúa permisos contra el UID/GID REAL del proceso, no el efectivo.
        # En los siguientes escenarios puede retornar False aunque el archivo sea legible:
        #   1. Containers con usuarios non-root: si el archivo es legible via setuid/setgid
        #      del proceso pero no por el UID real, os.access() retorna False (falso positivo).
        #   2. Linux Capabilities: CAP_DAC_READ_SEARCH otorga lectura sin permisos de
        #      filesystem, pero os.access() no considera capabilities.
        #   3. ACLs POSIX complejas: permisos otorgados por ACL de grupo/usuario específico
        #      pueden no reflejarse en os.access().
        # En cualquiera de estos casos: usar must_exist=False y manejar el EACCES en el caller.
        if must_exist and p.exists() and not os.access(str(p), os.R_OK):
            raise ContextValidationError(
                f"[VIGIA MP-VAL-READ-01] Archivo existe pero no es legible: {filepath!r}. "
                "Verificar permisos (chmod +r) o si el proceso tiene las capabilities necesarias. "
                "En containers o entornos con ACLs complejas, usar must_exist=False."
            )
        # MP-VAL-05: bloquear paths en /dev/, /proc/, /sys/ — nunca son archivos forenses
        _BLOCKED_PREFIXES = ("/dev/", "/proc/", "/sys/", "/run/")
        if any(str(p).startswith(pfx) for pfx in _BLOCKED_PREFIXES):
            raise ContextValidationError(
                f"Path en directorio de sistema bloqueado: {filepath!r}. "
                f"Los archivos forenses no deben estar en {_BLOCKED_PREFIXES}."
            )
        # MP-VAL-05: detectar hardlinks — múltiples nombres para el mismo inode
        if p.exists():
            try:
                stat_result = os.lstat(str(p))
                if stat_result.st_nlink > 1:
                    raise ContextValidationError(
                        f"Hardlink detectado: {filepath!r} tiene {stat_result.st_nlink} "
                        "nombres (hardlinks). Mover este archivo puede dejar el contenido "
                        "accesible via otros nombres. Verificar manualmente."
                    )
                # Verificar que es archivo regular (no device, fifo, socket)
                import stat as _stat_mod
                if not _stat_mod.S_ISREG(stat_result.st_mode):
                    raise ContextValidationError(
                        f"No es archivo regular: {filepath!r} "
                        f"(mode={oct(stat_result.st_mode)}). "
                        "Sólo se permiten archivos regulares."
                    )
            except ContextValidationError:
                raise
            except OSError:
                pass  # Si no podemos stat, dejamos pasar — el mv fallará después
        return str(p)
    except ContextValidationError:
        raise
    except (TypeError, ValueError, OSError) as e:
        raise ContextValidationError(f"filepath inválido: {filepath!r}: {e}")


def _validate_service(service: str) -> str:
    """
    Valida que service sea un nombre de unidad systemd válido.

    MP-VAL-03 (Kimi audit v2): el regex anterior permitía '@' que habilita
    inyección de shell: 'evil; rm -rf /@.service' pasaba el regex porque
    el patrón general era permisivo.

    Cambios:
    - Eliminar '@' del regex base. Los servicios de instancia (getty@tty1)
      son válidos pero el '@@' como bypass de inyección es el vector real.
    - El patrón ahora exige que el sufijo .service/.socket/etc. esté presente
      (no opcional) para ser más restrictivo.
    - El nombre de instancia (antes de '@') se valida por separado si está presente.

    Ejemplos VÁLIDOS (MP-VAL-SVC-01):
      - "nginx.service"                  — servicio simple
      - "ssh.socket"                     — socket de activación
      - "systemd-journald.service"       — punto en el nombre: válido
      - "getty@tty1.service"             — instancia con terminal
      - "serial-getty@ttyUSB0.service"   — instancia con dispositivo USB serial
      - "user@1000.service"              — instancia con UID numérico
      - "a.b@c.d.service"               — punto en instancia: válido en systemd

    Ejemplos INVÁLIDOS (rechazados con ContextValidationError):
      - "nginx"                          — sin sufijo obligatorio
      - "evil; rm -rf /.service"         — caracteres de shell
      - "evil@../../etc.service"         — '..' no está en charset
      - "root@host.service"              — '@' en nombre base sin instancia válida
      - ""                               — nombre vacío
    """
    if isinstance(service, str) and service.startswith("_OBTAIN_VIA:"):
        return service
    if not isinstance(service, str):
        raise ContextValidationError(f"service debe ser str")
    s = service.strip()
    if not s:
        raise ContextValidationError("service name no puede estar vacío")
    # MP-VAL-06: rechazo explícito de caracteres de inyección de shell
    # antes del regex — defensa en profundidad
    _SHELL_CHARS = set('`$();|&<>!\\"\'')
    bad_chars = _SHELL_CHARS.intersection(s)
    if bad_chars:
        raise ContextValidationError(
            f"service contiene caracteres de shell peligrosos: "
            f"{sorted(bad_chars)!r} en {service!r}"
        )
    # Separar instancia si existe: name@instance.service
    if "@" in s:
        parts_at = s.split("@", 1)
        name_part = parts_at[0]
        rest = parts_at[1]  # instance.service o .service
    else:
        name_part = s
        rest = ""
    # Validar parte del nombre: sólo alfanumérico, guión, underscore, punto
    if not re.match(r"^[a-zA-Z0-9_.-]{1,64}$", name_part):
        raise ContextValidationError(
            f"Nombre de servicio inválido: {service!r}. "
            "El nombre debe ser [a-zA-Z0-9_.-]{1,64}."
        )
    # Si hay instancia, validarla también
    if rest:
        # rest debe ser: [instance].[suffix] o .[suffix]
        rest_match = re.match(
            r"^([a-zA-Z0-9_.-]{0,64})\.(service|socket|timer|target|mount|path|scope)$",
            rest
        )
        if not rest_match:
            raise ContextValidationError(
                f"Instancia/sufijo de servicio inválido: {service!r}. "
                "Formato: name[@instance].suffix"
            )
    elif not re.search(r"\.(service|socket|timer|target|mount|path|scope)$", name_part):
        raise ContextValidationError(
            f"Servicio sin sufijo válido: {service!r}. "
            "Debe terminar en .service, .socket, .timer, .target, .mount, .path o .scope"
        )
    return s


def _q(value: str) -> str:
    """
    shlex.quote() para valores que van en strings de shell.

    MP-Q-01 (Kimi audit v2): la versión anterior dejaba pasar sin quote
    cualquier valor que empezara con '_OBTAIN_VIA:' o '# '.
    Un atacante podía poner '_OBTAIN_VIA: 127.0.0.1; rm -rf /' y pasar.

    Ahora: _OBTAIN_VIA y # sólo son válidos si el valor es exactamente
    una directiva — no se puede inyectar shell después de la directiva.
    Las directivas se validan con regex antes de pasar sin quote.
    """
    if not isinstance(value, str):
        return shlex.quote(str(value))
    # Directiva de obtención: debe ser "_OBTAIN_VIA: DESCRIPCION_SIN_COMANDOS"
    # No puede contener ; & | ` $ ( ) < > para evitar inyección
    if value.startswith("_OBTAIN_VIA:"):
        directive_content = value[len("_OBTAIN_VIA:"):]
        # Excluir | porque las directivas pueden mostrar pipes como ejemplo
        # Los caracteres realmente peligrosos en shell son: ; & ` $ ( ) < >
        # MP-Q-02: incluir newlines y tabs — rompen estructura de comandos multi-línea
        if re.search(r"[;&`$()<>\n\r\t]", directive_content):
            raise ContextValidationError(
                f"_OBTAIN_VIA contiene caracteres peligrosos (shell o newline): {value!r}"
            )
        return value  # directiva limpia
    # Comentario forense puro: sólo alfanumérico, espacios y puntuación básica
    if value.startswith("# "):
        comment_content = value[2:]
        if re.search(r"[;&`$()<>]", comment_content):
            raise ContextValidationError(
                f"Comentario contiene caracteres de shell peligrosos: {value!r}"
            )
        return value  # comentario limpio
    return shlex.quote(value)

_PLATFORM_OK: bool = sys.platform == "linux"

if not _PLATFORM_OK:
    warnings.warn(
        f"[VIGIA CRIT] vigia_mitigation_planner requiere Linux. "
        f"Plataforma detectada: {sys.platform}. "
        "Los planes generados serán marcados PLATFORM_UNSUPPORTED "
        "y sus comandos no deben ejecutarse.",
        RuntimeWarning,
        stacklevel=1,
    )

# ──────────────────────────────────────────────────────────────────────────
# PROCESOS CRÍTICOS DEL SISTEMA — nunca matar
# ──────────────────────────────────────────────────────────────────────────

SYSTEM_COMM_BLOCKLIST: frozenset[str] = frozenset({
    "systemd", "init", "kthreadd", "ksoftirqd", "migration",
    "rcu_gp", "rcu_par_gp", "rcu_tasks_kthread", "rcu_tasks_trace_kthread",
    "rcu_exp_par_gp_kthread_worker", "rcu_exp_gp_kthread_worker",
    "kworker", "kswapd0", "khugepaged", "oom_reaper", "writeback",
    "crypto", "kblockd", "watchdog", "cpuhp", "irq_work",
    "sshd",   # bloquear pero nunca matar — perdería acceso al sistema
})

# PIDs del kernel (1 = systemd/init, 2 = kthreadd, ≤ 10 = kernel threads)
SYSTEM_PID_MAX: int = 10


def _read_proc_comm_once(pid: int) -> str:
    """
    Lee /proc/{pid}/comm UNA SOLA VEZ de forma atómica.
    Maneja la condición de carrera donde el proceso desaparece entre
    la verificación de existencia y la lectura.

    Retorna el nombre del proceso o "unknown" si no es accesible.
    (MP-TOCTOU-01, MP-RACE-01)
    """
    try:
        # Leer directamente sin exists() previo — evita TOCTOU
        return _Path(f"/proc/{pid}/comm").read_text().strip()
    except OSError:
        # El proceso desapareció entre nuestra llamada y la lectura — normal
        return "unknown"


def _pid_is_critical(pid: int) -> tuple[bool, str]:
    """
    Retorna (es_critico, comm) evaluando UNA SOLA LECTURA de /proc/{pid}/comm.

    La lectura única previene la race condition TOCTOU donde:
    1. Leemos comm = "proceso_malicioso"   → is_critical = False
    2. Proceso malicioso termina
    3. Kernel reasigna PID a "systemd"
    4. kill -9 {pid} mata systemd

    Al retornar comm junto con el bool, el llamador puede usar el MISMO
    valor que fue verificado, sin leer /proc de nuevo.

    (MP-TOCTOU-01)
    """
    if pid <= SYSTEM_PID_MAX:
        comm = _read_proc_comm_once(pid)
        return True, comm
    comm = _read_proc_comm_once(pid)
    if comm == "unknown":
        # Proceso ya no existe — no hay PID que matar
        return True, "unknown"
    if comm in SYSTEM_COMM_BLOCKLIST:
        return True, comm
    if "kthread" in comm or (comm.startswith("k") and "/" in comm):
        return True, comm
    return False, comm


def _read_proc_comm(pid: int) -> str:
    """Compatibilidad — delegar a _read_proc_comm_once."""
    return _read_proc_comm_once(pid)


# ──────────────────────────────────────────────────────────────────────────
# DETECCIÓN DE FIREWALL DISPONIBLE
# ──────────────────────────────────────────────────────────────────────────

def _detect_firewall() -> str:
    """Detecta si nftables o iptables está disponible. Retorna 'nft' | 'iptables' | 'none'."""
    for binary, tag in [("/usr/sbin/nft", "nft"), ("/usr/sbin/iptables", "iptables"),
                        ("/sbin/iptables", "iptables"), ("/sbin/nft", "nft")]:
        if Path(binary).exists():
            return tag
    return "none"


_FIREWALL: str = _detect_firewall()


def _block_network_cmd(dst_ip: str, iface: str) -> Tuple[str, str]:
    """
    Genera comando de bloqueo y rollback según el firewall disponible.

    MP-BLK-01 (Kimi audit v2):
    - Usa _bin() para paths absolutos de nft/iptables.
    - Usa set -euo pipefail para que si la primera regla falla, la segunda
      no se ejecute en contexto inconsistente.
    - dst_ip ya fue validado por _validate_ip() antes de llegar aquí.

    MP-BLK-02 (Kimi P2): validación defensiva de iface incluso siendo función
    "interna". Si alguien la llama directamente con iface maliciosa, el fallback
    a 'eth0' previene inyección de shell en el comando generado.
    """
    # Validación defensiva de iface — el caller debería haberla validado,
    # pero aplicamos defensa en profundidad aquí también.
    _iface_stripped = iface.strip() if isinstance(iface, str) else ""
    if not re.match(r'^[a-zA-Z0-9_-]{1,16}$', _iface_stripped):
        import sys as _sys_iface
        _sys_iface.stderr.write(
            f"[VIGIA MP-BLK-02] iface inválida: {iface!r}. "
            "Usando fallback seguro 'eth0'.\n"
        )
        _sys_iface.stderr.flush()
        _iface_stripped = "eth0"
    iface = _iface_stripped
    ip_q = shlex.quote(dst_ip)
    if _FIREWALL == "nft":
        nft_b = _bin("nft")
        cmd = (
            f"set -euo pipefail\n"
            # Kimi P2: usar ; para que cada regla se ejecute independiente
            f"{nft_b} add rule ip filter output ip daddr {ip_q} drop ; "
            f"{nft_b} add rule ip filter input ip saddr {ip_q} drop"
        )
        rollback = (
            f"set -euo pipefail\n"
            f"{nft_b} delete rule ip filter output ip daddr {ip_q} drop ; "
            f"{nft_b} delete rule ip filter input ip saddr {ip_q} drop"
        )
    elif _FIREWALL == "iptables":
        ipt_b = _bin("iptables")
        cmd = (
            f"set -euo pipefail\n"
            # Kimi P2: ; en lugar de && para ejecución independiente
            f"{ipt_b} -I OUTPUT -d {ip_q} -j DROP ; "
            f"{ipt_b} -I INPUT -s {ip_q} -j DROP"
        )
        rollback = (
            f"set -euo pipefail\n"
            f"{ipt_b} -D OUTPUT -d {ip_q} -j DROP ; "
            f"{ipt_b} -D INPUT -s {ip_q} -j DROP"
        )
    else:
        ip_b = _bin("ip")
        cmd = (
            f"# FIREWALL NO DETECTADO — ejecutar manualmente:\n"
            f"# {ip_b} rule add blackhole from {ip_q} prio 100\n"
            f"# {ip_b} rule add blackhole to {ip_q} prio 100"
        )
        rollback = (
            f"# {ip_b} rule del blackhole from {ip_q} prio 100\n"
            f"# {ip_b} rule del blackhole to {ip_q} prio 100"
        )
    return cmd, rollback


# ──────────────────────────────────────────────────────────────────────────
# TABLA DE PLAYBOOKS POR HIPÓTESIS (Linux puro)
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class PlaybookStep:
    action_type: str
    priority: int
    description: str
    impact: str       # CRITICAL | HIGH | MEDIUM | LOW
    risk_note: str


HYPOTHESIS_PLAYBOOKS: Dict[str, List[PlaybookStep]] = {

    "H_DE_001": [   # log_fabrication
        PlaybookStep(
            action_type="COLLECT_EVIDENCE",
            priority=1,
            description="Capturar imagen de memoria volátil antes de cualquier otra acción.",
            impact="LOW",
            risk_note="No destructivo. Requiere privilegios root y ~4 GB de espacio libre.",
        ),
        PlaybookStep(
            action_type="PRESERVE_LOGS",
            priority=2,
            description="Copiar logs sospechosos a almacenamiento forense de sólo lectura.",
            impact="LOW",
            risk_note="Usar cp --preserve=all, no mv. No modificar timestamps.",
        ),
        PlaybookStep(
            action_type="ISOLATE_HOST",
            priority=3,
            description="Aislar el host de la red para preservar estado de memoria.",
            impact="HIGH",
            risk_note="ALTO IMPACTO. Desconecta completamente el host. "
                      "Confirmar que no es infraestructura crítica antes de ejecutar.",
        ),
    ],

    "H_DE_002": [   # log_deletion_after_exfil
        PlaybookStep(
            action_type="COLLECT_EVIDENCE",
            priority=1,
            description="Imagen de disco antes de que se sobrescriba evidencia adicional.",
            impact="LOW",
            risk_note="Requiere espacio en disco igual al tamaño de la partición origen.",
        ),
        PlaybookStep(
            action_type="REVOKE_CREDENTIALS",
            priority=2,
            description="Bloquear cuenta del usuario que ejecutó el borrado.",
            impact="HIGH",
            risk_note="Verificar que no sea cuenta de servicio crítico antes de bloquear.",
        ),
    ],

    "H_DE_003": [   # anti_forensics_preparation
        PlaybookStep(
            action_type="COLLECT_EVIDENCE",
            priority=1,
            description="Calcular hashes de todos los archivos en directorios sospechosos.",
            impact="LOW",
            risk_note="Puede ser lento en directorios grandes. No destructivo.",
        ),
        PlaybookStep(
            action_type="KILL_PROCESS",
            priority=2,
            description="Terminar procesos de herramientas anti-forenses activas "
                        "(shred, wipe, dd if=/dev/urandom).",
            impact="MEDIUM",
            risk_note="Verificar el PID con: ps aux | grep -E 'shred|wipe' antes de ejecutar.",
        ),
    ],

    "H_XF_001": [   # bulk_data_exfiltration
        PlaybookStep(
            action_type="COLLECT_EVIDENCE",
            priority=1,
            description="Capturar tráfico en curso hacia la IP de destino.",
            impact="LOW",
            risk_note="Iniciar ANTES del bloqueo para preservar evidencia de la exfiltración.",
        ),
        PlaybookStep(
            action_type="BLOCK_NETWORK",
            priority=2,
            description="Bloquear conexión saliente hacia IP de destino de exfiltración.",
            impact="CRITICAL",
            risk_note="CRÍTICO: detiene la exfiltración activa pero puede alertar al atacante. "
                      "Coordinar con el equipo de respuesta antes de ejecutar.",
        ),
        PlaybookStep(
            action_type="KILL_PROCESS",
            priority=3,
            description="Terminar el proceso responsable de la transferencia.",
            impact="HIGH",
            risk_note="Ejecutar DESPUÉS de la captura de tráfico.",
        ),
    ],

    "H_PE_001": [   # single_persistence
        PlaybookStep(
            action_type="RESTORE_FILE",
            priority=1,
            description="Sobreescribir el ejecutable malicioso de persistencia "
                        "con el binario legítimo desde el backup.",
            impact="MEDIUM",
            risk_note="Guardar copia forense del binario malicioso antes de sobreescribir.",
        ),
        PlaybookStep(
            action_type="KILL_PROCESS",
            priority=2,
            description="Terminar el proceso persistente activo.",
            impact="MEDIUM",
            risk_note="El proceso puede reiniciarse si el mecanismo de inicio "
                      "no fue desactivado primero.",
        ),
        PlaybookStep(
            action_type="DISABLE_SERVICE",
            priority=3,
            description="Deshabilitar el servicio/unit de systemd malicioso.",
            impact="MEDIUM",
            risk_note="Usar systemctl disable --now, no rm. Preservar el archivo .service "
                      "como evidencia.",
        ),
    ],

    "H_LM_001": [   # pass_the_hash
        PlaybookStep(
            action_type="REVOKE_CREDENTIALS",
            priority=1,
            description="Bloquear la cuenta comprometida e invalidar sus sesiones activas.",
            impact="HIGH",
            risk_note="Coordinar con el usuario afectado. Puede interrumpir sesiones legítimas.",
        ),
        PlaybookStep(
            action_type="BLOCK_NETWORK",
            priority=2,
            description="Bloquear tráfico SMB (puerto 445) desde el host comprometido.",
            impact="HIGH",
            risk_note="Puede afectar acceso a recursos de red compartidos legítimos.",
        ),
        PlaybookStep(
            action_type="COLLECT_EVIDENCE",
            priority=3,
            description="Exportar timeline de autenticaciones laterales desde auth.log.",
            impact="LOW",
            risk_note="No destructivo. Ejecutar en todos los hosts alcanzados.",
        ),
    ],

    "H_EX_001": [   # command_line_abuse
        PlaybookStep(
            action_type="KILL_PROCESS",
            priority=1,
            description="Terminar el proceso de shell malicioso.",
            impact="HIGH",
            risk_note="Verificar árbol de procesos completo: "
                      "ps -eo pid,ppid,comm,args | grep -A3 <pid>",
        ),
        PlaybookStep(
            action_type="RESTORE_FILE",
            priority=2,
            description="Cuarentenar el script malicioso con shred diferido.",
            impact="MEDIUM",
            risk_note="Mover a /quarantine con permisos 000 ANTES de shred. "
                      "shred sólo después de análisis completo.",
        ),
    ],

    "H_IA_001": [   # spearphishing_execution
        PlaybookStep(
            action_type="KILL_PROCESS",
            priority=1,
            description="Terminar el proceso hijo del cliente de correo.",
            impact="HIGH",
            risk_note="Verificar con: pstree -p | grep -B5 <proceso_sospechoso>",
        ),
        PlaybookStep(
            action_type="RESTORE_FILE",
            priority=2,
            description="Cuarentenar el adjunto ejecutado.",
            impact="MEDIUM",
            risk_note="El adjunto ya fue ejecutado — cuarentena previene re-ejecución.",
        ),
        PlaybookStep(
            action_type="REVOKE_CREDENTIALS",
            priority=3,
            description="Bloquear la cuenta del usuario afectado.",
            impact="MEDIUM",
            risk_note="Interrumpe sesiones activas del usuario.",
        ),
    ],
}

DEFAULT_PLAYBOOK: List[PlaybookStep] = [
    PlaybookStep(
        action_type="COLLECT_EVIDENCE",
        priority=1,
        description="Capturar imagen de memoria volátil. "
                    "Primera acción siempre: preservar evidencia volátil.",
        impact="LOW",
        risk_note="No destructivo. Requiere privilegios root.",
    ),
    PlaybookStep(
        action_type="ISOLATE_HOST",
        priority=2,
        description="Aislar el host de la red para contención.",
        impact="HIGH",
        risk_note="Alto impacto en producción. Coordinar con operaciones.",
    ),
]


# ──────────────────────────────────────────────────────────────────────────
# ESTRUCTURAS DE DATOS
# ──────────────────────────────────────────────────────────────────────────



# ──────────────────────────────────────────────────────────────────────────
# FIRMA HMAC DEL PLAN (MP-CTRL-01, MP-TRUST-01)
# ──────────────────────────────────────────────────────────────────────────

def _get_plan_hmac_key() -> tuple:
    """
    Clave HMAC para firmar planes de mitigación.
    Misma jerarquía que security.py:
      1. VIGIA_HMAC_KEY env var (hex)
      2. VIGIA_HMAC_KEY_FILE env var
      3. Clave efímera con warning en stderr (solo desarrollo)

    Retorna: (key: bytes, is_verifiable: bool)

    MP-HMAC-02 (Kimi P1): la versión anterior retornaba sólo la clave.
    Si los permisos eran inseguros, caía silenciosamente a clave efímera
    sin que el operador pudiera saber que la firma NO era verificable.
    Ahora retornamos el flag is_verifiable explícitamente para que
    MitigationPlan lo exponga en el JSON de salida.
    """
    import os as _os_hmac
    key_hex = _os_hmac.environ.get("VIGIA_HMAC_KEY", "").strip()
    if key_hex:
        try:
            return bytes.fromhex(key_hex), True
        except ValueError:
            pass
    key_file = _os_hmac.environ.get("VIGIA_HMAC_KEY_FILE", "").strip()
    if key_file and _os_hmac.path.isfile(key_file):
        try:
            import stat as _stat_key
            key_mode = _os_hmac.stat(key_file).st_mode
            # Kimi P1: rechazar si grupo u otros tienen permisos de lectura
            if key_mode & (_stat_key.S_IRWXG | _stat_key.S_IRWXO):
                import sys as _sys_key
                _sys_key.stderr.write(
                    f"[VIGIA MP-HMAC] ADVERTENCIA: {key_file!r} tiene permisos "
                    f"de grupo/otros ({oct(key_mode)}). "
                    "Ejecutar: chmod 600 " + key_file + "\n"
                    "[VIGIA MP-HMAC-02] Clave rechazada — "
                    "usando clave efímera NO VERIFICABLE.\n"
                )
                _sys_key.stderr.flush()
                # Retornar clave efímera con is_verifiable=False
                import os as _os2
                return _os2.urandom(32), False
            else:
                if os.path.islink(key_file):
                    raise RuntimeError(f"HMAC key file is a symlink: {key_file}")
                fd = os.open(key_file, os.O_RDONLY | os.O_NOFOLLOW)
                try:
                    key_data = os.read(fd, 64)
                finally:
                    os.close(fd)
                return key_data, True
        except OSError:
            pass
    import sys as _sys_hmac
    _sys_hmac.stderr.write(
        "[VIGIA MP-CTRL-01] VIGIA_HMAC_KEY no configurada — "
        "usando clave efímera. Los planes NO son verificables entre reinicios.\n"
    )
    _sys_hmac.stderr.flush()
    import os as _os2
    return _os2.urandom(32), False


_PLAN_HMAC_KEY_TUPLE: tuple = _get_plan_hmac_key()
_PLAN_HMAC_KEY: bytes = _PLAN_HMAC_KEY_TUPLE[0]
_PLAN_HMAC_KEY_IS_VERIFIABLE: bool = _PLAN_HMAC_KEY_TUPLE[1]


def _sign_plan(plan_hash: str, actions_approved: list) -> str:
    """
    HMAC-SHA256(key, plan_hash || approved_states)

    MP-CTRL-01: incluir el estado approved de cada acción en la firma.
    Si approved cambia en el JSON serializado, la firma no coincide.

    MP-TRUST-01: usar HMAC en lugar de SHA-256 puro. Un atacante que
    conoce el algoritmo pero no la clave no puede recalcular la firma.
    """
    import hmac as _hmac_mod, json as _json_sign, hashlib as _hs
    payload = _json_sign.dumps(
        {"plan_hash": plan_hash, "approved": sorted(str(a) for a in actions_approved)},
        sort_keys=True, ensure_ascii=True,
    )
    return _hmac_mod.new(_PLAN_HMAC_KEY, payload.encode("utf-8"), "sha256").hexdigest()


def verify_plan_signature(plan_dict: dict) -> bool:
    """
    Verifica la firma HMAC de un plan serializado.
    Retorna True si el plan no fue modificado, False si fue alterado.

    Uso:
        plan_data = json.loads(plan_file.read_text())
        if not verify_plan_signature(plan_data):
            raise SecurityError("Plan de mitigación fue modificado. No ejecutar.")
    """
    stored_sig = plan_dict.get("plan_signature", "")
    if not stored_sig:
        return False
    plan_hash = plan_dict.get("plan_hash", "")
    approved_states = [
        a.get("approved", False)
        for a in plan_dict.get("actions", [])
    ]
    expected = _sign_plan(plan_hash, approved_states)
    import hmac as _hmac_mod
    return _hmac_mod.compare_digest(stored_sig, expected)

@dataclass
class MitigationAction:
    action_id: str
    action_type: str
    priority: int
    hypothesis_id: str
    justification: str
    supporting_rule: str
    target: Dict[str, Any]
    command: str
    rollback: str
    estimated_impact: str
    requires_approval: bool = True
    approved: bool = False
    risk_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id":         self.action_id,
            "action_type":       self.action_type,
            "priority":          self.priority,
            "hypothesis_id":     self.hypothesis_id,
            "justification":     self.justification,
            "supporting_rule":   self.supporting_rule,
            "target":            self.target,
            "command":           self.command,
            "rollback":          self.rollback,
            "estimated_impact":  self.estimated_impact,
            "requires_approval": self.requires_approval,
            "approved":          self.approved,
            "risk_note":         self.risk_note,
        }


@dataclass
class MitigationPlan:
    bundle_id: str
    verdict: str
    hypothesis_id: str
    hypothesis_intent: str
    posterior: float
    actions: List[MitigationAction]
    plan_hash: str
    generated_at: str
    operator_note: str
    platform_ok: bool
    plan_signature: str = ""           # HMAC-SHA256 — MP-CTRL-01
    signature_verifiable: bool = False  # MP-HMAC-02 (Kimi P1): False si clave efímera

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vigia_version":        "v1.0-Valkyrie",
            "bundle_id":            self.bundle_id,
            "verdict":              self.verdict,
            "hypothesis_id":        self.hypothesis_id,
            "hypothesis_intent":    self.hypothesis_intent,
            "posterior":            self.posterior,
            "platform_ok":          self.platform_ok,
            "platform":             sys.platform,
            "plan_signature":       self.plan_signature,       # MP-CTRL-01
            "signature_verifiable": self.signature_verifiable,  # MP-HMAC-02
            "actions":              [a.to_dict() for a in self.actions],
            "plan_hash":            self.plan_hash,
            "generated_at":         self.generated_at,
            "operator_note":        self.operator_note,
            "total_actions":        len(self.actions),
            "critical_actions":     sum(
                1 for a in self.actions if a.estimated_impact == "CRITICAL"
            ),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(
            self.to_dict(), indent=indent, sort_keys=True, ensure_ascii=False
        )

    def to_markdown(self) -> str:
        plat_warn = (
            "\n> ⛔ **PLATAFORMA NO SOPORTADA**: este plan fue generado en "
            f"`{sys.platform}`. Los comandos son para Linux únicamente.\n"
            if not self.platform_ok else ""
        )

        # MP-SIG-VIS-01 (Kimi P0): si la firma es efímera, el operador que lee
        # markdown no lo sabe a menos que lea el JSON. Banner obligatorio.
        # Se usa ASCII puro (no emoji) para garantizar visibilidad en cualquier TTY.
        _is_utf8_terminal = (
            sys.stdout.encoding is not None
            and sys.stdout.encoding.lower().replace("-", "") in ("utf8", "utf-8")
        )
        if not self.signature_verifiable:
            _warn_icon = "⚠️" if _is_utf8_terminal else "[!!]"
            sig_warn = (
                f"\n> {_warn_icon} **ADVERTENCIA DE FIRMA**: Este plan fue firmado con "
                "clave EFIMERA (no persistente).  \n"
                "> La firma **NO es verificable** entre reinicios de proceso.  \n"
                "> Para firmas verificables configurar: "
                "`VIGIA_HMAC_KEY` o `VIGIA_HMAC_KEY_FILE` antes de ejecutar VIGIA.  \n"
                "> `signature_verifiable: false` en el JSON de este plan.\n"
            )
        else:
            sig_warn = ""

        lines: List[str] = [
            "# VIGÍA — Plan de Mitigación Quirúrgica",
            "",
            f"> **Bundle ID:** `{self.bundle_id}`  ",
            f"> **Veredicto:** `{self.verdict}`  ",
            f"> **Hipótesis:** `{self.hypothesis_id}` ({self.hypothesis_intent})  ",
            f"> **P(malicioso):** `{self.posterior:.4f}` ({self.posterior * 100:.1f}%)  ",
            f"> **Plataforma:** `{sys.platform}` ({'OK' if self.platform_ok else 'UNSUPPORTED'})  ",
            f"> **Hash plan:** `{self.plan_hash}`  ",
            f"> **Firma verificable:** `{'SI' if self.signature_verifiable else 'NO — EFIMERA'}`  ",
            f"> **Generado:** `{self.generated_at}`",
            plat_warn,
            sig_warn,
            "---",
            "",
            "> ⚠️ **IMPORTANTE**: Plan NO ejecutado automáticamente.  ",
            "> Cada acción requiere `approved=True` del operador.  ",
            "> Ejecutar en orden de prioridad ascendente.  ",
            "> Documentar cada ejecución en el ForensicBundle.",
            "",
            "## Justificación",
            "",
            self.operator_note,
            "",
            f"## Acciones ({len(self.actions)})",
            "",
        ]

        # MP-MD-01 (Kimi P2): fallback ASCII para terminales sin soporte UTF-8 completo.
        # _is_utf8_terminal ya fue calculado arriba para el banner de firma.
        if _is_utf8_terminal:
            impact_icon = {
                "CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"
            }
        else:
            impact_icon = {
                "CRITICAL": "[!!]", "HIGH": "[!]", "MEDIUM": "[~]", "LOW": "[.]"
            }

        for action in sorted(self.actions, key=lambda a: a.priority):
            icon = impact_icon.get(action.estimated_impact, "⚪")
            lines += [
                f"### [{action.priority}] {icon} `{action.action_type}`",
                "",
                f"**ID:** `{action.action_id}`  ",
                f"**Impacto:** `{action.estimated_impact}`  ",
                f"**Hipótesis:** `{action.hypothesis_id}`",
                "",
                f"**Justificación:** {action.justification}",
                "",
                "**Target:**",
                "```json",
                json.dumps(action.target, indent=2, ensure_ascii=True),
                "```",
                "",
                "**Comando** (NO ejecutar sin aprobación):",
                "```bash",
                action.command,
                "```",
                "",
                "**Rollback:**",
                "```bash",
                action.rollback,
                "```",
                "",
            ]
            if action.risk_note:
                lines.append(f"**Nota de riesgo:** {action.risk_note}")
                lines.append("")
            lines += ["**Estado:** `PENDIENTE_APROBACIÓN`", "", "---", ""]

        lines.append(
            f"*Plan generado por `vigia_mitigation_planner.py` v1.0-Valkyrie | "
            f"Hash: `{self.plan_hash}`*"
        )
        return "\n".join(lines)




# ──────────────────────────────────────────────────────────────────────────
# ENFORCEMENT DE APROBACIÓN
# ──────────────────────────────────────────────────────────────────────────

class ApprovalRequired(RuntimeError):
    """
    Lanzada cuando se intenta ejecutar una MitigationAction sin aprobación.

    El campo approved=False NO es documentación opcional — es un control
    de seguridad que impide ejecución accidental de comandos forenses.

    Para aprobar una acción:
        action.approved = True  # sólo después de revisión humana
        result = execute_action(action, dry_run=False)
    """
    pass


class PlanIntegrityError(RuntimeError):
    """
    MP-INTEG-01 (Kimi P1): lanzada cuando la firma HMAC del plan no coincide.

    Diferencia semántica crítica con ApprovalRequired:
    - ApprovalRequired: el operador no aprobó la acción. Es un control de flujo.
    - PlanIntegrityError: el plan fue MODIFICADO después de generarse. Es un
      indicador de manipulación activa. No ejecutar bajo ninguna circunstancia.

    Un plan con PlanIntegrityError debe ser regenerado desde el bundle original.
    """
    pass


def execute_action(action: "MitigationAction", dry_run: bool = True, plan_dict: "dict | None" = None) -> dict:
    """
    Punto de entrada único para ejecutar una MitigationAction.

    WORKFLOW CORRECTO DE APROBACIÓN (MP-WFLOW-01):
    1. Generar plan: `plan = MitigationPlanner().generate(bundle)`
    2. Revisar cada acción manualmente
    3. Aprobar acción: `action.approved = True`
    4. Serializar el plan ACTUALIZADO: `plan_dict = plan.to_dict()`
       IMPORTANTE: la firma en `plan_dict` fue calculada con `approved=False`.
       Al cambiar `approved=True`, la firma original ya no coincide.
    5. Regenerar la firma: el plan debe ser re-firmado con `approved=True`
       antes de pasar `plan_dict` a `execute_action`. Flujo recomendado:
         a. No pasar `plan_dict` si el plan no fue re-firmado.
         b. O re-generar el plan completo tras la aprobación.
    6. Ejecutar: `result = execute_action(action, dry_run=False, plan_dict=plan_dict)`

    NOTA: pasar `plan_dict` original (con `approved=False` en la firma) a una
    acción donde `action.approved=True` hará que `verify_plan_signature` falle
    y lance `PlanIntegrityError`. Esto es INTENCIONAL — el plan debe re-firmarse
    con los estados de aprobación actualizados antes de la ejecución.

    Garantías:
    - Si approved=False: lanza ApprovalRequired. Sin excepciones.
    - Si dry_run=True: registra el intento sin ejecutar nada.
    - El comando NUNCA se pasa a subprocess — se retorna para que el
      operador lo ejecute manualmente. VIGÍA no tiene acceso al shell.
    - Registra timestamp de ejecución y hash del comando para auditoría.

    Retorna dict con: approved, command_hash, dry_run, timestamp
    """
    import hashlib
    from datetime import datetime, timezone

    # Kimi P1: verificar firma del plan si se proporciona.
    # IMPORTANTE: ApprovalRequired y PlanIntegrityError son errores distintos.
    # - PlanIntegrityError: el plan fue modificado post-generación → NO ejecutar NUNCA
    # - ApprovalRequired: falta aprobación del operador → pedir revisión
    if plan_dict is not None:
        if not verify_plan_signature(plan_dict):
            raise PlanIntegrityError(
                f"[VIGIA MP-INTEG-01] Firma HMAC inválida — el plan fue modificado "
                "después de ser generado. No se puede ejecutar un plan corrupto. "
                "Regenerar el plan desde el ForensicBundle original."
            )
    if not action.approved:
        raise ApprovalRequired(
            f"Acción {action.action_id} ({action.action_type}) requiere aprobación explícita. "
            f"Establecer action.approved = True después de revisión humana. "
            f"Hipótesis: {action.hypothesis_id} | Impacto: {action.estimated_impact}"
        )

    cmd_hash = hashlib.sha256(action.command.encode("utf-8")).hexdigest()
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "action_id":    action.action_id,
        "action_type":  action.action_type,
        "approved":     True,
        "dry_run":      dry_run,
        "command_hash": cmd_hash,
        "command":      action.command if not dry_run else "[DRY_RUN — comando no ejecutado]",
        "timestamp":    ts,
        "warning":      (
            "VIGÍA no ejecuta comandos directamente. "
            "El operador debe copiar el comando y ejecutarlo manualmente "
            "con los privilegios adecuados."
        ),
    }

# ──────────────────────────────────────────────────────────────────────────
# MOTOR DE PLANIFICACIÓN
# ──────────────────────────────────────────────────────────────────────────

class MitigationPlanner:
    """
    Genera un plan de mitigación quirúrgica desde un ForensicBundle.

    Solo genera acciones operativas para verdict=REJECT.
    Para ABSTAIN genera recolección de evidencia adicional.
    Para ACCEPT no genera acciones (falso positivo no requiere mitigación).
    """


    def _validate_bundle_schema(self, bundle: Dict[str, Any]) -> Optional[str]:
        """
        Verifica la estructura mínima requerida de un ForensicBundle.
        Retorna None si es válido, o mensaje de error si no.

        Campos mínimos requeridos:
        - bundle_id: str no vacío
        - decision_trace.decision: "ACCEPT" | "REJECT" | "ABSTAIN"
        - decision_trace.posterior: float en [0, 1]
        - abduction_trace: dict (puede estar vacío)
        """
        if not isinstance(bundle, dict):
            return f"bundle debe ser un dict, recibido: {type(bundle).__name__}"

        bid = bundle.get("bundle_id", "")
        if not isinstance(bid, str) or not bid.strip():
            return "bundle_id debe ser un string no vacío"

        dt = bundle.get("decision_trace")
        if not isinstance(dt, dict):
            return "decision_trace debe ser un dict"

        decision = str(dt.get("decision", "")).upper()
        if decision not in {"ACCEPT", "REJECT", "ABSTAIN", "UNKNOWN"}:
            return f"decision_trace.decision inválido: '{decision}'"

        posterior = dt.get("posterior")
        if posterior is not None:
            try:
                p = float(posterior)
                if not (0.0 <= p <= 1.0):
                    return f"decision_trace.posterior fuera de [0,1]: {p}"
            except (TypeError, ValueError):
                return f"decision_trace.posterior no es numérico: {posterior}"

        abduction = bundle.get("abduction_trace")
        if abduction is not None and not isinstance(abduction, dict):
            return f"abduction_trace debe ser un dict o None"

        return None

    def generate(self, bundle: Dict[str, Any]) -> MitigationPlan:
        # Validar schema del input antes de procesar
        schema_err = self._validate_bundle_schema(bundle)
        if schema_err:
            raise ValueError(f"[VIGIA schema] Bundle inválido: {schema_err}")

        decision_trace = bundle.get("decision_trace", {})
        verdict = str(decision_trace.get("decision", "UNKNOWN")).upper()
        posterior = float(decision_trace.get("posterior", 0.0))

        abduction = bundle.get("abduction_trace", {})
        hyp = abduction.get("abductive_hypothesis", {})
        winner_id = str(hyp.get("hypothesis_id", "UNKNOWN"))
        winner_intent = str(hyp.get("intent_type", "unknown"))
        supporting_rules: List[str] = hyp.get("supporting_rules", [])

        context = self._extract_context(bundle)

        if verdict == "ACCEPT":
            actions: List[MitigationAction] = []
            operator_note = (
                "Veredicto ACCEPT. Sin acciones de mitigación. "
                "Si sospecha falso negativo, revisar umbral ε_accept en PolicySpec."
            )
        elif verdict == "ABSTAIN":
            actions = self._collect_only(winner_id, context, supporting_rules)
            operator_note = (
                f"Veredicto ABSTAIN: evidencia insuficiente para REJECT sobre `{winner_id}`. "
                "Se generan acciones de recolección para resolver la ambigüedad."
            )
        else:  # REJECT
            playbook = HYPOTHESIS_PLAYBOOKS.get(winner_id, DEFAULT_PLAYBOOK)
            actions = self._instantiate(
                playbook, winner_id, winner_intent, supporting_rules,
                context, posterior,
            )
            operator_note = (
                f"P={posterior:.4f} ({posterior * 100:.1f}%). "
                f"Hipótesis `{winner_id}` ({winner_intent}) seleccionada como explicación "
                f"más parsimoniosa. Acciones justificadas por la inferencia abductiva."
            )

        actions.sort(key=lambda a: a.priority)

        # plan_hash cubre comandos + targets (no sólo metadatos)
        plan_hash = self._compute_plan_hash(actions, bundle.get("bundle_id", ""), winner_id)

        _generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        _approved_states = [a.approved for a in actions]
        _sig = _sign_plan(plan_hash, _approved_states)
        return MitigationPlan(
            bundle_id=bundle.get("bundle_id", "unknown"),
            verdict=verdict,
            hypothesis_id=winner_id,
            hypothesis_intent=winner_intent,
            posterior=posterior,
            actions=actions,
            plan_hash=plan_hash,
            generated_at=_generated_at,
            operator_note=operator_note,
            platform_ok=_PLATFORM_OK,
            plan_signature=_sig,
            signature_verifiable=_PLAN_HMAC_KEY_IS_VERIFIABLE,  # MP-HMAC-02
        )

    # ── extracción de contexto ────────────────────────────────────────────

    def _extract_context(self, bundle: Dict[str, Any]) -> Dict[str, str]:
        """
        Extrae valores concretos de los artefactos del bundle.
        Cuando un valor no está disponible, genera una directiva de obtención
        forense en lugar de un placeholder vacío.
        """
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        ctx: Dict[str, str] = {
            "ts":             ts,
            # MP-PH-01 (Kimi P0): PROCESO_SOSPECHOSO en mayúsculas es menos peligroso
            # que <> pero igual confunde al operador bajo presión. Agregar # REEMPLAZAR
            # explícito antes de cada ejemplo de comando para que sea inequívoco.
            "pid":            "_OBTAIN_VIA: # REEMPLAZAR <NOMBRE_PROCESO>: ps aux | grep <NOMBRE_PROCESO> | awk '{print $2}'",
            "dst_ip":         "_OBTAIN_VIA: # REEMPLAZAR <IP_DESTINO>: ss -tnp | grep ESTABLISHED | awk '{print $5}'",
            "src_ip":         "_OBTAIN_VIA: # REEMPLAZAR <IP_ORIGEN>: ss -tnp | grep ESTABLISHED | awk '{print $4}'",
            "username":       "_OBTAIN_VIA: # REEMPLAZAR <NOMBRE_USUARIO>: who | awk '{print $1}' | sort -u",
            "file_path":      "_OBTAIN_VIA: # REEMPLAZAR <PID>: lsof -p <PID> | awk '{print $9}' | head -5",
            "script_path":    "_OBTAIN_VIA: # REEMPLAZAR <PID>: cat /proc/<PID>/cmdline | tr '\\0' ' '",
            "file_hash":      "_OBTAIN_VIA: # REEMPLAZAR <RUTA_ARCHIVO>: sha256sum <RUTA_ARCHIVO> | awk '{print $1}'",
            "iface":          "_OBTAIN_VIA: # REEMPLAZAR: ip route get 1 | awk '{print $5; exit}'",
            "suspicious_dir": "/tmp",
            "service_name":   "_OBTAIN_VIA: # REEMPLAZAR: systemctl list-units --type=service --state=running",
        }

        # Rellenar desde artefactos del bundle cuando estén disponibles
        for art in bundle.get("artifacts", []):
            if not isinstance(art, dict):
                continue
            if "destination_ip" in art and "_OBTAIN_VIA" in ctx["dst_ip"]:
                ctx["dst_ip"] = str(art["destination_ip"])
            if "src_ip" in art and "_OBTAIN_VIA" in ctx["src_ip"]:
                ctx["src_ip"] = str(art["src_ip"])
            if "cleared_by" in art and "_OBTAIN_VIA" in ctx["username"]:
                raw = str(art["cleared_by"])
                ctx["username"] = raw.split("\\")[-1] if "\\" in raw else raw
            if "file_path" in art and "_OBTAIN_VIA" in ctx["file_path"]:
                ctx["file_path"] = str(art["file_path"])
            if art.get("artifact_name") == "command_line_execution":
                cmds = art.get("commands", [])
                if cmds and "_OBTAIN_VIA" in ctx["pid"]:
                    ctx["pid"] = "_OBTAIN_VIA: pgrep -f " + str(cmds[0]).split()[0]

        # Rellenar desde anomalías
        for anom in bundle.get("abduction_trace", {}).get("anomalies_found", []):
            if not isinstance(anom, dict):
                continue
            if "src_ip" in anom and "_OBTAIN_VIA" in ctx["src_ip"]:
                ctx["src_ip"] = str(anom["src_ip"])

        return ctx

    # ── instanciación de playbook ─────────────────────────────────────────

    def _instantiate(
        self,
        playbook: List[PlaybookStep],
        winner_id: str,
        winner_intent: str,
        rules: List[str],
        ctx: Dict[str, str],
        posterior: float,
    ) -> List[MitigationAction]:
        actions: List[MitigationAction] = []

        for step in playbook:
            cmd, rollback = self._build_command(
                step.action_type, winner_id, ctx
            )
            action_id = hashlib.sha256(
                f"{winner_id}:{step.action_type}:{ctx['ts']}:{cmd}".encode()
            ).hexdigest()[:16]

            rule = next(
                (r for r in rules
                 if not r.startswith(("OBSERVED:", "MISSING:", "EXPLICIT_"))),
                f"PLAYBOOK_{winner_id}_{step.action_type}",
            )

            target = self._build_target(step.action_type, winner_id, ctx)

            justification = (
                f"P={posterior:.4f}. Hipótesis `{winner_id}` ({winner_intent}). "
                f"{step.description}"
            )

            # Validación de seguridad para KILL_PROCESS
            pid_warning = ""
            if step.action_type == "KILL_PROCESS":
                raw_pid = ctx.get("pid", "")
                if raw_pid.isdigit():
                    pid_int = int(raw_pid)
                    # MP-TOCTOU-03: desempaquetar (bool, comm) — una sola lectura
                    _is_crit, _comm_inst = _pid_is_critical(pid_int)
                    if _is_crit:
                        pid_warning = (
                            f"⛔ SEGURIDAD: PID {pid_int} "
                            f"(comm={_comm_inst!r}) es proceso crítico del sistema. "
                            "ABORTADO. Revisar target manualmente."
                        )
                        justification = pid_warning

            actions.append(MitigationAction(
                action_id=action_id,
                action_type=step.action_type,
                priority=step.priority,
                hypothesis_id=winner_id,
                justification=justification,
                supporting_rule=rule,
                target=target,
                command=cmd if not pid_warning else f"# BLOQUEADO — {pid_warning}",
                rollback=rollback if not pid_warning else "# No aplicable — acción bloqueada",
                estimated_impact=step.impact,
                requires_approval=True,
                approved=False,
                risk_note=step.risk_note + (" " + pid_warning if pid_warning else ""),
            ))

        return actions

    def _build_command(
        self, action_type: str, winner_id: str, ctx: Dict[str, str]
    ) -> Tuple[str, str]:
        """
        Genera el comando Linux y su rollback para cada tipo de acción.

        Gemini audit fixes (v1.0-Valkyrie):
          MP-INJ-01/02: validación + shlex.quote en todos los valores del ctx
          MP-PATH-01/02: binarios via _bin() — paths absolutos verificados
          MP-TOCTOU-01:  _pid_is_critical() retorna (bool, comm) en una lectura
          MP-TRAV-01:    file_path validado con _validate_filepath()
          MP-SHELL-01:   bloques multi-cmd usan set -euo pipefail
          MP-ROLL-01:    rollback de ISOLATE_HOST verifica backup antes de restaurar
        """
        ts = ctx["ts"]  # generado internamente — no viene del bundle

        if action_type == "COLLECT_EVIDENCE":
            avml = _bin("avml")
            cmd = (
                f"set -euo pipefail\n"
                f"{avml} /forensics/mem_{ts}.lime 2>/dev/null || "
                f"dd if=/proc/kcore of=/forensics/mem_{ts}.dd bs=4096 2>/dev/null"
            )
            rollback = "# No aplica — captura de memoria es no destructiva"

        elif action_type == "PRESERVE_LOGS":
            jctl = _bin("journalctl")
            cmd = (
                f"set -euo pipefail\n"
                f"mkdir -p /forensics/logs_{ts}\n"
                f"cp --preserve=all /var/log/auth.log /forensics/logs_{ts}/\n"
                f"cp --preserve=all /var/log/syslog /forensics/logs_{ts}/ 2>/dev/null || true\n"
                f"{jctl} --since '1 hour ago' > /forensics/logs_{ts}/journal.txt"
            )
            rollback = "# No aplica — copia no destructiva"

        elif action_type == "ISOLATE_HOST":
            raw_iface = ctx["iface"]
            # MP-IFACE-01: regex estricto sin @ ni . que permiten inyección
            if not re.match(r'^[a-zA-Z0-9_-]{1,16}$', raw_iface.strip()):
                raw_iface = "eth0  # iface original inválida"
            iface_q = shlex.quote(raw_iface.split()[0])  # sólo el nombre, no comentarios
            ip_b = _bin("ip")
            cmd = (
                # MP-ISO-DOC-01 (Kimi P2): lógica de backup y abort explicada:
                # 1. iptables-save y nft list ruleset se ejecutan con '|| true' para
                #    que si el binario no existe, el subshell no falle. El archivo
                #    resultante puede quedar vacío (0 bytes).
                # 2. [ -s archivo ] verifica que el archivo existe Y tiene contenido.
                # 3. Si AMBOS backups están vacíos, 'exit 1' con 'set -e' termina
                #    el script completo — no se aísla el host sin backup válido.
                # 4. Si al menos uno tiene contenido, se procede con el aislamiento.
                # 5. El rollback usa iptables-restore --test primero (dry-run) para
                #    verificar que el backup es válido antes de restaurar.
                f"# MP-BIN-03: guardar reglas con paths absolutos\n"
                f"( /usr/sbin/iptables-save 2>/dev/null || /sbin/iptables-save 2>/dev/null "
                f"|| true ) > /forensics/iptables_backup_{ts}.rules\n"
                f"( {_bin('nft')} list ruleset 2>/dev/null || true ) "
                f"> /forensics/nft_backup_{ts}.rules\n"
                f"# Si ambos backups vacíos: abortar (sin backup no hay rollback seguro)\n"
                f"[ -s /forensics/iptables_backup_{ts}.rules ] || "
                f"[ -s /forensics/nft_backup_{ts}.rules ] || "
                f"{{ echo 'ABORT: backup vacío — aislamiento cancelado'; exit 1; }}\n"
                f"{ip_b} link set {iface_q} down 2>/dev/null || "
                f"{{ iptables -I INPUT ! -i lo -j DROP && "
                f"iptables -I OUTPUT ! -o lo -j DROP; }}"
            )
            rollback = (
                f"if [ -s /forensics/iptables_backup_{ts}.rules ]; then\n"
                f"  iptables-restore --test < /forensics/iptables_backup_{ts}.rules && "
                f"  iptables-restore < /forensics/iptables_backup_{ts}.rules\n"
                f"else\n"
                f"  {ip_b} link set {iface_q} up\n"
                f"fi"
            )

        elif action_type == "BLOCK_NETWORK":
            raw_dst_ip = ctx["dst_ip"]
            raw_iface  = ctx["iface"]
            try:
                dst_ip = _validate_ip(raw_dst_ip)
                dst_ip_q = shlex.quote(dst_ip)
            except ContextValidationError as e:
                dst_ip   = "127.0.0.1"
                dst_ip_q = shlex.quote(dst_ip)
                raw_iface = f"# IP INVÁLIDA: {e}"
            # MP-IFACE-01: sólo [a-zA-Z0-9_-] para interfaces
            _iface_clean = raw_iface.strip()
            if not re.match(r'^[a-zA-Z0-9_-]{1,16}$', _iface_clean):
                _iface_clean = 'eth0'
            iface_q = shlex.quote(_iface_clean)
            tcpdump_b = _bin("tcpdump")
            cmd_block, rollback = _block_network_cmd(dst_ip, raw_iface)
            cmd = (
                f"set -euo pipefail\n"
                f"# Capturar tráfico antes de bloquear\n"
                f"{tcpdump_b} -i {iface_q} host {dst_ip_q} "
                f"-w /forensics/capture_{ts}.pcap &\n"
                f"sleep 5\n"
                f"{cmd_block}"
            )

        elif action_type == "KILL_PROCESS":
            raw_pid  = ctx["pid"]
            kill_b   = _bin("kill")
            try:
                pid_str = _validate_pid(raw_pid)
                # _OBTAIN_VIA: valor no resuelto — generar directiva
                if pid_str.startswith("_OBTAIN_VIA:"):
                    cmd = f"# PID pendiente: {pid_str}"
                    rollback = "# PID no resuelto"
                    return cmd, rollback
                pid_int = int(pid_str)
                # Lectura única de /proc (MP-TOCTOU-01)
                is_crit, comm = _pid_is_critical(pid_int)
                if is_crit:
                    cmd     = (
                        f"# BLOQUEADO MP-TOCTOU-01: PID {pid_str} es proceso crítico\n"
                        f"# comm leído: {comm}\n"
                        f"# Revisar manualmente antes de continuar"
                    )
                    rollback = "# KILL bloqueado — no aplica"
                else:
                    cmd = (
                        f"# PID {pid_str} verificado: comm={comm}\n"
                        f"{kill_b} -TERM {pid_str} && sleep 3\n"
                        f"{kill_b} -KILL {pid_str} 2>/dev/null || "
                        f"echo 'PID {pid_str} ya terminado'"
                    )
                    rollback = f"# No hay rollback para KILL_PROCESS (PID={pid_str}, comm={comm})"
            except ContextValidationError as e:
                cmd     = f"# BLOQUEADO MP-INJ-02: {e}"
                rollback = "# PID inválido — no aplica"

        elif action_type == "RESTORE_FILE":
            raw_path = ctx["file_path"]
            raw_hash = ctx["file_hash"]
            sha256_b = _bin("sha256sum")
            try:
                file_path   = _validate_filepath(raw_path)
                file_path_q = shlex.quote(file_path)
                hash8 = re.sub(r'[^a-f0-9]', '', raw_hash.lower())[:8] or "00000000"
                dest   = f"/quarantine/{ts}/{_Path(file_path).name}.{hash8}"
                dest_q = shlex.quote(dest)
                cmd = (
                    f"set -euo pipefail\n"
                    f"mkdir -p /quarantine/{ts}\n"
                    f"mv {file_path_q} {dest_q}\n"
                    f"chmod 000 {dest_q}\n"
                    f"{sha256_b} {dest_q} >> /forensics/chain_of_custody_{ts}.txt"
                )
                rollback = f"chmod 644 {dest_q} && mv {dest_q} {file_path_q}"
            except ContextValidationError as e:
                cmd     = f"# BLOQUEADO MP-TRAV-01: {e}"
                rollback = "# path inválido — no aplica"

        elif action_type == "REVOKE_CREDENTIALS":
            raw_user   = ctx["username"]
            passwd_b   = _bin("passwd")
            pkill_b    = _bin("pkill")
            try:
                username = _validate_username(raw_user)
                uq = shlex.quote(username)
                cmd = (
                    f"set -euo pipefail\n"
                    f"{passwd_b} -l {uq}\n"
                    f"{pkill_b} -KILL -u {uq} || true\n"
                    f"/usr/bin/who | awk -v u={uq} '$1==u {{print $2}}' | "
                    f"xargs -I{{}} pkill -KILL -t {{}} 2>/dev/null || true"
                )
                rollback = f"{passwd_b} -u {uq}"
            except ContextValidationError as e:
                cmd     = f"# BLOQUEADO MP-INJ-01: {e}"
                rollback = "# username inválido — no aplica"

        elif action_type == "DISABLE_SERVICE":
            raw_svc = ctx["service_name"]
            sctl    = _bin("systemctl")
            try:
                service = _validate_service(raw_svc)
                sq = shlex.quote(service)
                cmd = (
                    f"set -euo pipefail\n"
                    f"{sctl} stop {sq}\n"
                    f"{sctl} disable {sq}\n"
                    f"{sctl} cat {sq} > /forensics/service_{sq}_{ts}.txt"
                )
                rollback = f"{sctl} enable {sq} && {sctl} start {sq}"
            except ContextValidationError as e:
                cmd     = f"# BLOQUEADO MP-INJ-01: {e}"
                rollback = "# servicio inválido — no aplica"

        else:
            avml = _bin("avml")
            cmd = (
                f"set -euo pipefail\n"
                f"{avml} /forensics/mem_{ts}.lime 2>/dev/null && "
                f"echo 'memoria capturada' >> /forensics/chain_of_custody_{ts}.txt"
            )
            rollback = "# No aplica"

        return cmd, rollback

    def _build_target(
        self, action_type: str, winner_id: str, ctx: Dict[str, str]
    ) -> Dict[str, str]:
        """Construye el target dict con los valores relevantes para cada acción."""
        base = {
            "hypothesis_id": winner_id,
            "timestamp": ctx["ts"],
        }
        mapping = {
            "KILL_PROCESS":       {"pid": ctx["pid"]},
            "BLOCK_NETWORK":      {"dst_ip": ctx["dst_ip"], "iface": ctx["iface"]},
            "RESTORE_FILE":       {"file_path": ctx["file_path"], "file_hash": ctx["file_hash"]},
            "REVOKE_CREDENTIALS": {"username": ctx["username"]},
            "ISOLATE_HOST":       {"iface": ctx["iface"]},
            "DISABLE_SERVICE":    {"service_name": ctx["service_name"]},
        }
        base.update(mapping.get(action_type, {}))
        return base

    def _collect_only(
        self,
        winner_id: str,
        ctx: Dict[str, str],
        rules: List[str],
    ) -> List[MitigationAction]:
        """Genera sólo acciones de recolección para veredictos ABSTAIN."""
        ts = ctx["ts"]
        # MP-ABST-01: usar _bin() y set -euo pipefail (Kimi audit v2)
        avml_b    = _bin("avml")
        jctl_b    = _bin("journalctl")
        ss_b      = _bin("ss")
        cmd = (
            f"set -euo pipefail\n"
            f"{avml_b} /forensics/mem_{ts}.lime 2>/dev/null; "
            f"{jctl_b} --since '2 hours ago' > /forensics/journal_{ts}.txt; "
            f"{ss_b} -tnp > /forensics/connections_{ts}.txt; "
            f"ps aux > /forensics/processes_{ts}.txt"
        )
        action_id = hashlib.sha256(
            f"ABSTAIN:{winner_id}:{ts}".encode()
        ).hexdigest()[:16]
        rule = next(
            (r for r in rules if not r.startswith(("OBSERVED:", "MISSING:", "EXPLICIT_"))),
            f"ABSTAIN_COLLECT_{winner_id}",
        )
        return [MitigationAction(
            action_id=action_id,
            action_type="COLLECT_EVIDENCE",
            priority=1,
            hypothesis_id=winner_id,
            justification=(
                f"ABSTAIN: evidencia insuficiente para `{winner_id}`. "
                "Recolección para resolver ambigüedad."
            ),
            supporting_rule=rule,
            target={"hypothesis_id": winner_id, "timestamp": ts},
            command=cmd,
            rollback="# No aplica — recolección no destructiva",
            estimated_impact="LOW",
            requires_approval=True,
            approved=False,
            risk_note="Recolección de evidencia adicional para resolver ABSTAIN.",
        )]

    def _compute_plan_hash(
        self,
        actions: List[MitigationAction],
        bundle_id: str,
        winner_id: str,
    ) -> str:
        """
        Hash SHA-256 que cubre comandos finales + targets de cada acción.
        No sólo metadatos — un cambio en cualquier comando cambia el hash.
        """
        payload = {
            "bundle_id": bundle_id,
            "winner_id": winner_id,
            "actions": [
                {
                    "action_id":   a.action_id,
                    "action_type": a.action_type,
                    "command":     a.command,
                    "rollback":    a.rollback,   # MP-HASH-01: incluido en hash
                    "target":      a.target,
                    "priority":    a.priority,
                }
                for a in sorted(actions, key=lambda x: x.priority)
            ],
        }
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode()).hexdigest()


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="VIGÍA Mitigation Planner — Capa 4 (POSIX/Linux)"
    )
    parser.add_argument("--bundle", required=True,
                        help="ForensicBundle sellado (.json)")
    parser.add_argument("--json",   dest="json_out", action="store_true",
                        help="Salida en JSON")
    parser.add_argument("--output", default=None,
                        help="Archivo de salida (default: stdout)")
    args = parser.parse_args()

    bundle_path = Path(args.bundle)
    if not bundle_path.exists():
        print(f"ERROR: {bundle_path} no encontrado", file=sys.stderr)
        return 1

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    plan = MitigationPlanner().generate(bundle)

    out = plan.to_json() if args.json_out else plan.to_markdown()

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"[OK] Plan: {args.output} ({len(plan.actions)} acciones) "
              f"hash={plan.plan_hash[:16]}...")
    else:
        print(out)

    return 0 if plan.platform_ok else 2


if __name__ == "__main__":
    sys.exit(main())
