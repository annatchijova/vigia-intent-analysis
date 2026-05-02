# VIGÍA Benign Cases — Dataset de Validación Anti-Alucinación

## Propósito

15 casos donde **todo parece sospechoso pero no hay ataque**. VIGÍA debe:
1. Detectar la anomalía (Firstness)
2. Buscar explicación benigna verificable (Secondness)
3. Concluir NOISE o ABSTAIN cuando la hipótesis benigna es más fuerte

Esto demuestra el criterio **"Hallucination Management"** del hackathon SANS.

---

## Distribución

| Veredicto | Cantidad | Casos |
|-----------|----------|-------|
| **NOISE** | 14 | BEN-001 al BEN-013, BEN-015 |
| **ABSTAIN** | 1 | BEN-014 (Periodista con Tor — contexto legal limita certeza) |

**Rango de confianza**: 75% - 93%  
**Nota**: Los casos benignos tienen confianza más baja que los maliciosos porque VIGÍA es honesto epistémicamente: reconoce que "no hay ataque" es más difícil de probar que "sí hay ataque".

---

## Casos Destacados

| ID | Nombre | Apariencia de ataque | Realidad | Por qué NOISE |
|---|---|---|---|---|
| BEN-001 | Admin de Moscú | Teclado ruso en logs | Empleado remoto legítimo | RRHH verifica empleado y hardware |
| BEN-002 | Backup 3AM | Exfiltración nocturna | Cron de backup aprobado | Documentado, auditado, IAM role de servicio |
| BEN-003 | Desastre real | "Soy un desastre" | Error real de junior | Secuencia: error→pánico→ayuda, no error→ocultamiento |
| BEN-004 | Script perfecto | Ejecución inhumana | Ansible Tower | Change board aprobó, Git commit firmado |
| BEN-005 | Teclado nuevo | Login fallidos | Adaptación táctil | Ticket IT verificable, 8h actividad normal post-login |
| BEN-006 | Sudo masivo | Escalada de privilegios | Mantenimiento programado | Calendario compartido, aprobado por CTO |
| BEN-007 | PDF confidencial | Exfiltración | Distribución RRHH | Email a 45 managers, política autoriza |
| BEN-008 | Ping periódico | Beaconing C2 | Monitor Nagios | Dashboard público, config firmada por NOC |
| BEN-009 | Permisos 777 | Backdoor | Legacy requerido | Deuda técnica documentada, plan migración 2025 |
| BEN-010 | Urgente CEO | Phishing | Deadline real | Junta en calendario, thread previo, DKIM pass |
| BEN-011 | USB en finanzas | Malware | Update drivers | Ticket soporte, escoltado, máquina air-gapped |
| BEN-012 | Kernel huérfano | Rootkit | kworker Linux | Documentado en kernel.org, parent en kernel space |
| BEN-013 | rm -rf logs | Anti-forense | Retención GDPR | Política de 30 días, aprobada por DPO, auditada |
| BEN-014 | Tor periodista | Exfiltración | Protección fuentes | Autorización editor+legal, pero VIGÍA no ve contenido → ABSTAIN |
| BEN-015 | Timestamps idénticos | Timestomping | Snapshot restaurado | Ticket infraestructura, 47 VMs, vendor confirmó fallo |

---

## Estructura de cada caso

Cada caso incluye:
- `why_not_malice`: Explicación explícita de por qué la hipótesis benigna gana
- `devil_advocate`: La hipótesis hostil más fuerte (para probar que VIGÍA la refuta)
- `devil_refutation`: Por qué el diablo pierde (Ockham cost)
- `abstention_risk`: bajo/medio/alto

---

## Uso en el Hackathon

1. **Accuracy Report**: Correr VIGÍA contra estos 15 casos + los 10 reales. Medir:
   - True Negatives (NOISE correcto): 14 esperados
   - False Positives (MALICE incorrecto): 0 tolerados
   - Abstentions correctos: 1 esperado (BEN-014)

2. **Demo Video**: Mostrar BEN-001 o BEN-014 para demostrar que VIGÍA no alucina.

3. **Documentación**: "VIGÍA detecta anomalías pero no confunde anomalía con ataque. Requiere evidencia de segunda anomalía para elevar a MALICE."

---

*Generado: 2026-04-28T06:50:11.502851+00:00*
*Schema: v1.0 | Standard: SANS_FIND_EVIL_2026*
*Propósito: Hallucination Management Validation*
