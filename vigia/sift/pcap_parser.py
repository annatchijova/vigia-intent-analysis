"""
vigia/sift/pcap_parser.py

Parser de archivos .pcap a NetworkFlow usando tshark.
Convierte captura de red cruda en estructuras que NetworkForensicsEngine puede analizar.

Requiere: tshark (Wireshark CLI) instalado y accesible en PATH.
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import List

from vigia.sift.network_forensics import NetworkFlow

logger = logging.getLogger(__name__)

# Cap de seguridad: máximo de paquetes a parsear
MAX_PACKETS = 50_000

# Protocolo IP → nombre legible
_PROTO_MAP = {
    "6": "TCP",
    "17": "UDP",
    "1": "ICMP",
}


def parse_pcap_to_flows(pcap_path: str) -> List[NetworkFlow]:
    """
    Parsea un archivo .pcap con tshark y devuelve una lista de NetworkFlow.

    Cada paquete IP se convierte en un NetworkFlow individual.
    NetworkForensicsEngine agrupa internamente por (src, dst, port) para
    detección de beaconing/exfiltration.

    Args:
        pcap_path: Ruta al archivo .pcap/.pcapng.

    Returns:
        Lista de NetworkFlow, máximo MAX_PACKETS elementos.

    Raises:
        FileNotFoundError: Si tshark no está instalado.
        subprocess.CalledProcessError: Si tshark falla al procesar el archivo.
        RuntimeError: Si tshark produce salida no parseable.
    """
    cmd = [
        "tshark",
        "-r", pcap_path,
        "-T", "json",
        "-c", str(MAX_PACKETS),
        "-e", "ip.src",
        "-e", "ip.dst",
        "-e", "tcp.srcport",
        "-e", "tcp.dstport",
        "-e", "udp.srcport",
        "-e", "udp.dstport",
        "-e", "frame.time_epoch",
        "-e", "frame.len",
        "-e", "ip.proto",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "tshark no encontrado en PATH. Instalar wireshark-common: "
            "sudo apt install tshark"
        )

    if not result.stdout.strip():
        logger.warning("[PCAP_PARSER] tshark produjo salida vacía para %s", pcap_path)
        return []

    try:
        packets = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"tshark produjo JSON inválido para {pcap_path}: {e}"
        )

    flows: List[NetworkFlow] = []
    skipped = 0

    for pkt in packets:
        layers = pkt.get("_source", {}).get("layers", {})

        src_ip = _first(layers.get("ip.src"))
        dst_ip = _first(layers.get("ip.dst"))
        if not src_ip or not dst_ip:
            skipped += 1
            continue

        proto_num = _first(layers.get("ip.proto", []))
        protocol = _PROTO_MAP.get(proto_num, proto_num or "UNKNOWN")

        # Puertos: TCP tiene prioridad sobre UDP
        src_port = _int_first(layers.get("tcp.srcport")) or _int_first(layers.get("udp.srcport")) or 0
        dst_port = _int_first(layers.get("tcp.dstport")) or _int_first(layers.get("udp.dstport")) or 0

        epoch_str = _first(layers.get("frame.time_epoch"))
        if epoch_str:
            timestamp = int(float(epoch_str))
        else:
            timestamp = 0

        frame_len = _int_first(layers.get("frame.len")) or 0

        flows.append(NetworkFlow(
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            timestamp=timestamp,
            bytes_sent=frame_len,
            packets=1,
            duration_ms=0,
        ))

    if skipped:
        logger.info("[PCAP_PARSER] %d paquetes sin IP omitidos (ARP, LLC, etc.)", skipped)

    total_in_file = len(packets)
    if total_in_file >= MAX_PACKETS:
        logger.warning(
            "[PCAP_PARSER] Cap de seguridad alcanzado: %d paquetes parseados de %s. "
            "El archivo puede contener más paquetes.",
            MAX_PACKETS, pcap_path,
        )

    logger.info(
        "[PCAP_PARSER] %s: %d paquetes → %d NetworkFlows",
        pcap_path, total_in_file, len(flows),
    )

    return flows


def _first(lst: list | None) -> str | None:
    """Extrae el primer elemento de una lista tshark (cada campo es [valor])."""
    if lst and isinstance(lst, list) and len(lst) > 0:
        return str(lst[0])
    return None


def _int_first(lst: list | None) -> int:
    """Extrae el primer elemento como int, 0 si falla."""
    val = _first(lst)
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0
