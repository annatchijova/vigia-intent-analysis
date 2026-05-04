"""
vigia/patterns/adversarial_silence.py
=======================================
Detector de silencio adversarial para VIGÍA.

Principio: Para cada acción afirmada o inferida, verifica que los
artefactos secundarios esperados estén presentes. Su ausencia sistemática
= evidencia de borrado deliberado.

La clave: un atacante que borra selectivamente los artefactos difíciles
de borrar (Prefetch, $MFT) revela que CONOCE qué herramientas forenses
usarán los analistas. Eso en sí mismo es indicador de sofisticación.

Invariantes:
- Todo scoring usa Fraction
- SilenceRecord y ExpectedArtifact son frozen dataclasses
- audit_hash determinista
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional


# ─── Base de conocimiento de artefactos secundarios esperados ────────────────

@dataclass(frozen=True)
class ExpectedArtifact:
    artifact_type:      str
    erasure_difficulty: Fraction   # 0=fácil de borrar, 1=muy difícil
    forensic_value:     Fraction   # Valor como evidencia
    detection_command:  str


@dataclass(frozen=True)
class SilenceRecord:
    absence_confirmed:      bool
    expected_artifact:      ExpectedArtifact
    alternative_explanation: Optional[str]


# Base de conocimiento por OS
_WINDOWS_ARTIFACTS: dict[str, list[ExpectedArtifact]] = {
    "process_execution": [
        ExpectedArtifact("prefetch_entry",    Fraction(8, 10), Fraction(9, 10),
                         "dir C:\\Windows\\Prefetch\\*.pf"),
        ExpectedArtifact("shimcache_entry",   Fraction(7, 10), Fraction(8, 10),
                         "reg query HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\AppCompatCache"),
        ExpectedArtifact("amcache_entry",     Fraction(6, 10), Fraction(8, 10),
                         "C:\\Windows\\AppCompat\\Programs\\Amcache.hve"),
        ExpectedArtifact("event_4688",        Fraction(3, 10), Fraction(7, 10),
                         "Get-WinEvent -FilterHashtable @{LogName='Security';Id=4688}"),
    ],
    "network_connection": [
        ExpectedArtifact("dns_cache_entry",   Fraction(2, 10), Fraction(6, 10),
                         "ipconfig /displaydns"),
        ExpectedArtifact("firewall_log",      Fraction(4, 10), Fraction(7, 10),
                         "Get-WinEvent -FilterHashtable @{LogName='Security';Id=5156}"),
        ExpectedArtifact("netflow_record",    Fraction(5, 10), Fraction(8, 10),
                         "Get-NetTCPConnection"),
    ],
    "file_creation": [
        ExpectedArtifact("mft_entry",         Fraction(9, 10), Fraction(9, 10),
                         "MFTECmd.exe -f '$MFT'"),
        ExpectedArtifact("usnjrnl_entry",     Fraction(8, 10), Fraction(8, 10),
                         "MFTECmd.exe -f '$UsnJrnl:$J'"),
        ExpectedArtifact("lnk_file",          Fraction(3, 10), Fraction(5, 10),
                         "dir %APPDATA%\\Microsoft\\Windows\\Recent\\*.lnk"),
    ],
    "service_installation": [
        ExpectedArtifact("event_7045",        Fraction(4, 10), Fraction(9, 10),
                         "Get-WinEvent -FilterHashtable @{LogName='System';Id=7045}"),
        ExpectedArtifact("registry_service",  Fraction(6, 10), Fraction(8, 10),
                         "reg query HKLM\\SYSTEM\\CurrentControlSet\\Services"),
        ExpectedArtifact("prefetch_entry",    Fraction(8, 10), Fraction(7, 10),
                         "dir C:\\Windows\\Prefetch\\*.pf"),
    ],
    "user_login": [
        ExpectedArtifact("event_4624",        Fraction(3, 10), Fraction(8, 10),
                         "Get-WinEvent -FilterHashtable @{LogName='Security';Id=4624}"),
        ExpectedArtifact("event_4634",        Fraction(3, 10), Fraction(7, 10),
                         "Get-WinEvent -FilterHashtable @{LogName='Security';Id=4634}"),
        ExpectedArtifact("ntuser_dat",        Fraction(7, 10), Fraction(6, 10),
                         "dir C:\\Users\\*\\NTUSER.DAT /A:H"),
    ],
}

_LINUX_ARTIFACTS: dict[str, list[ExpectedArtifact]] = {
    "process_execution": [
        ExpectedArtifact("bash_history",      Fraction(2, 10), Fraction(6, 10),
                         "cat ~/.bash_history"),
        ExpectedArtifact("syslog_entry",      Fraction(4, 10), Fraction(7, 10),
                         "grep <pid> /var/log/syslog"),
        ExpectedArtifact("proc_accounting",   Fraction(5, 10), Fraction(7, 10),
                         "lastcomm"),
        ExpectedArtifact("audit_log",         Fraction(5, 10), Fraction(9, 10),
                         "ausearch -sc execve"),
    ],
    "network_connection": [
        ExpectedArtifact("netstat_entry",     Fraction(1, 10), Fraction(5, 10),
                         "netstat -antp"),
        ExpectedArtifact("iptables_log",      Fraction(4, 10), Fraction(7, 10),
                         "grep DROP /var/log/syslog"),
        ExpectedArtifact("pcap_fragment",     Fraction(6, 10), Fraction(9, 10),
                         "tcpdump -r capture.pcap"),
    ],
    "file_creation": [
        ExpectedArtifact("inode_entry",       Fraction(8, 10), Fraction(8, 10),
                         "stat <file>"),
        ExpectedArtifact("ext4_journal",      Fraction(9, 10), Fraction(9, 10),
                         "debugfs -R 'logdump' /dev/sda1"),
        ExpectedArtifact("fam_inotify_log",   Fraction(3, 10), Fraction(5, 10),
                         "inotifywait -m /path"),
    ],
}

_OS_PROFILES: dict[str, dict] = {
    "windows": _WINDOWS_ARTIFACTS,
    "linux":   _LINUX_ARTIFACTS,
}


@dataclass
class SilenceAnalysisResult:
    silence_score:          Fraction
    selectivity_score:      Fraction
    erasure_sophistication: Fraction
    fabrication_likelihood: Fraction
    audit_hash:             str
    silence_records:        list[SilenceRecord]
    top_investigation_hints: list[str]


class AdversarialSilenceDetector:
    """
    Para cada acción registrada, verifica que los artefactos secundarios
    esperados estén presentes. La ausencia sistemática de artefactos
    difíciles de borrar = evidencia de borrado deliberado.
    """

    def __init__(self, os_profile: str = "windows") -> None:
        self._os_profile = os_profile.lower()
        self._kb = _OS_PROFILES.get(self._os_profile, _WINDOWS_ARTIFACTS)
        self._primary_actions: list[str] = []
        self._confirmed_absent: set[str] = set()
        self._present_artifacts: set[str] = set()

    def register_primary_action(self, action: str) -> None:
        """Registra una acción primaria afirmada o inferida."""
        self._primary_actions.append(action)

    def register_confirmed_absent(self, artifact_type: str) -> None:
        """Registra un artefacto secundario confirmado como ausente."""
        self._confirmed_absent.add(artifact_type)

    def register_present_artifact(self, artifact_type: str) -> None:
        """Registra un artefacto secundario presente."""
        self._present_artifacts.add(artifact_type)

    def analyze(self) -> SilenceAnalysisResult:
        """
        Analiza el patrón de silencio y retorna scores forenses.
        """
        records: list[SilenceRecord] = []
        total_expected = 0
        total_absent = 0
        weighted_absent = Fraction(0)
        weighted_total = Fraction(0)
        hard_absent = 0
        hard_total = 0

        for action in self._primary_actions:
            expected = self._kb.get(action, [])
            for artifact in expected:
                total_expected += 1
                weighted_total += artifact.forensic_value

                if artifact.erasure_difficulty > Fraction(5, 10):
                    hard_total += 1

                is_absent = artifact.artifact_type in self._confirmed_absent
                is_present = artifact.artifact_type in self._present_artifacts

                if is_absent:
                    total_absent += 1
                    weighted_absent += artifact.forensic_value
                    if artifact.erasure_difficulty > Fraction(5, 10):
                        hard_absent += 1

                records.append(SilenceRecord(
                    absence_confirmed=is_absent,
                    expected_artifact=artifact,
                    alternative_explanation=(
                        None if is_absent else
                        "Artifact present — consistent with legitimate activity"
                        if is_present else
                        "Artifact status unknown"
                    ),
                ))

        # silence_score: fracción ponderada de artefactos ausentes
        silence_score = (
            weighted_absent / weighted_total
            if weighted_total > Fraction(0)
            else Fraction(0)
        )

        # selectivity_score: ¿se borraron preferentemente los difíciles?
        selectivity_score = Fraction(0)
        if hard_total > 0 and total_expected > hard_total:
            easy_total = total_expected - hard_total
            easy_absent = total_absent - hard_absent
            hard_ratio = Fraction(hard_absent, hard_total) if hard_total > 0 else Fraction(0)
            easy_ratio = Fraction(easy_absent, easy_total) if easy_total > 0 else Fraction(0)
            # Alta selectividad = difíciles borrados MÁS que fáciles
            selectivity_score = max(hard_ratio - easy_ratio, Fraction(0))

        # erasure_sophistication: promedio de dificultad de los artefactos borrados
        absent_records = [r for r in records if r.absence_confirmed]
        if absent_records:
            erasure_sophistication = sum(
                r.expected_artifact.erasure_difficulty for r in absent_records
            ) / len(absent_records)
        else:
            erasure_sophistication = Fraction(0)

        # fabrication_likelihood: combinación de los tres scores
        fabrication_likelihood = min(
            (silence_score * Fraction(4, 10)
             + selectivity_score * Fraction(4, 10)
             + erasure_sophistication * Fraction(2, 10)),
            Fraction(1),
        )

        # Investigation hints
        hints = _build_hints(absent_records, self._os_profile)
        audit_hash = _compute_silence_hash(records, silence_score, selectivity_score)

        return SilenceAnalysisResult(
            silence_score=silence_score,
            selectivity_score=selectivity_score,
            erasure_sophistication=erasure_sophistication,
            fabrication_likelihood=fabrication_likelihood,
            audit_hash=audit_hash,
            silence_records=records,
            top_investigation_hints=hints,
        )


def _build_hints(
    absent_records: list[SilenceRecord],
    os_profile: str,
) -> list[str]:
    """Genera hints de investigación para el analista SANS."""
    hints = []
    # Ordenar por valor forense descendente
    sorted_records = sorted(
        absent_records,
        key=lambda r: r.expected_artifact.forensic_value,
        reverse=True,
    )
    for record in sorted_records[:5]:
        art = record.expected_artifact
        hints.append(
            f"[{os_profile.upper()}] ABSENT: {art.artifact_type} "
            f"(forensic_value={int(art.forensic_value * 100)}%, "
            f"erasure_difficulty={int(art.erasure_difficulty * 100)}%). "
            f"Check: {art.detection_command}"
        )
    return hints


def _compute_silence_hash(
    records: list[SilenceRecord],
    silence_score: Fraction,
    selectivity_score: Fraction,
) -> str:
    content = json.dumps(
        {
            "silence_score":     str(silence_score),
            "selectivity_score": str(selectivity_score),
            "absent_artifacts": sorted(
                r.expected_artifact.artifact_type
                for r in records if r.absence_confirmed
            ),
        },
        sort_keys=True,
    )
    return hashlib.sha256(content.encode()).hexdigest()
