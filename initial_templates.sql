-- =============================================================================
-- VIGÍA — LIBRERÍA DE HÁBITOS v3.0
-- Schema + 20 Templates de Intencionalidad
-- Correcciones aplicadas: C1, C2, W1, W5, C4, P1-B, P2-C
-- =============================================================================

-- -----------------------------------------------------------------------------
-- SCHEMA DDL (W1)
-- -----------------------------------------------------------------------------
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS intent_templates (
    template_id         TEXT PRIMARY KEY,
    human_name          TEXT NOT NULL,
    ir_phase            TEXT NOT NULL,
    intent_type         TEXT NOT NULL,
    required_artifacts  TEXT NOT NULL,
    assumed_artifacts   TEXT NOT NULL,
    template_prior      TEXT NOT NULL,   -- P2-C: Decimal como TEXT para determinismo exacto
    -- Ejemplo: '0.78' se parsea como Decimal('0.78') en el loader
    lambda_drift        REAL NOT NULL DEFAULT 0.0,
    gamma_stability     REAL NOT NULL DEFAULT 0.0,
    omega_intention     REAL NOT NULL DEFAULT 0.0,
    max_coverage_score  INTEGER NOT NULL DEFAULT 100,
    falsifiable_by      TEXT NOT NULL,
    grice_violation     TEXT NOT NULL,
    carnegie_pattern    TEXT,
    peirce_firstness    TEXT NOT NULL,
    peirce_secondness   TEXT NOT NULL,
    peirce_thirdness    TEXT NOT NULL,
    mitre_ttps          TEXT,
    weight              REAL NOT NULL DEFAULT 1.0,
    prior_source        TEXT NOT NULL DEFAULT 'expert_elicitation_bootstrap_v1',
    -- P1-B CHECK: Campos DEPRECATED deben permanecer en 0.0
    -- El RiskBoundedDecisionLayer usa λγω globales del SelfAdaptiveRiskPolicy
    CHECK (lambda_drift = 0.0 AND gamma_stability = 0.0 AND omega_intention = 0.0)
);

CREATE TABLE IF NOT EXISTS required_evidences (
    evidence_keyword    TEXT NOT NULL,
    template_id         TEXT NOT NULL,
    FOREIGN KEY (template_id) REFERENCES intent_templates(template_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_templates_phase ON intent_templates(ir_phase);
CREATE INDEX IF NOT EXISTS idx_templates_intent ON intent_templates(intent_type);
CREATE INDEX IF NOT EXISTS idx_evidence_keyword ON required_evidences(evidence_keyword);
CREATE INDEX IF NOT EXISTS idx_template_lookup ON required_evidences(template_id);

-- -----------------------------------------------------------------------------
-- BLOQUE 1: DEFENSE_EVASION (7 templates)
-- -----------------------------------------------------------------------------

INSERT INTO intent_templates VALUES (
    'H_DE_001_WEAPONIZED_INCOMPETENCE_VSS',
    'Incompetencia Fingida con Herramientas Avanzadas de Destrucción',
    'DEFENSE_EVASION',
    'insider_threat',
    '["comando_destruccion_vss", "ticket_incompetencia_explicito", "horario_no_laboral", "secuencia_accion_tecnica_seguida_de_negacion"]',
    '["attacker_conocía_forense_de_memoria", "attacker_acceso_admin_al_sistema", "attacker_planificó_coartada"]',
    '0.78', 0.0, 0.0, 0.0, 100,
    'Verificar si el empleado tenía formación en forensia o buscó "vssadmin" antes del incidente. Si no hay evidencia, la hipótesis benigna gana.',
    'Manner', 'Weaponized Incompetence',
    'Comando vssadmin ejecutado seguido de declaración de ignorancia. La acción es precisa; la narrativa es de torpeza.',
    'Un usuario incompetente no conoce herramientas de ocultación de evidencia en memoria. La combinación contradice el perfil declarado.',
    'Atacante con conocimiento técnico fingió incompetencia para desviar atribución y eliminar evidencia antes del análisis forense.',
    '["T1070","T1562.001","T1204"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_DE_002_CANVA_METADATA_SPOOF',
    'Documento Oficial con Metadatos de Herramienta No Profesional',
    'DEFENSE_EVASION',
    'false_flag',
    '["metadata_author_no_coincide", "tool_producer_no_oficial", "company_metadata_inconsistente", "fecha_creacion_posterior_a_fecha_declarada"]',
    '["attacker_acceso_a_plantilla_interna", "attacker_conocía_formato_documental", "attacker_no_anticipó_analisis_de_metadatos"]',
    '0.89', 0.0, 0.0, 0.0, 100,
    'Verificar si el autor declarado usa Canva legítimamente para otros documentos. Si existe historial de uso legítimo, la anomalía se atenúa.',
    'Quality', 'Borrowed Credibility',
    'PDF con metadatos de Canva y autor interno en lugar del tribunal declarado.',
    'Un tribunal usa sistemas de gestión procesal, no herramientas de diseño gráfico. Canva es una firma de fabricación amateur.',
    'Atacante con acceso a plantillas internas fabricó documento falso explotando confianza institucional en el formato judicial.',
    '["T1036","T1564","T1204"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_DE_003_MULTILINGUAL_FALSE_FLAG',
    'Malware con Strings Multilingües y Comentarios Monolingües',
    'DEFENSE_EVASION',
    'false_flag',
    '["strings_malware_multilingues", "comentarios_codigo_idioma_especifico", "error_articulo_sintaxis_l1"]',
    '["attacker_quiso_simular_operacion_multinacional", "attacker_conoce_linguistica_forense", "attacker_subestimo_analisis_de_comentarios"]',
    '0.88', 0.0, 0.0, 0.0, 100,
    'Verificar si el malware es de un APT multilingüe conocido. Si existe APT documentado que opera en 6 idiomas, la hipótesis de false flag se debilita.',
    'Quality', 'False Flag',
    'Malware con strings en 6 idiomas, pero comentarios en inglés con errores de artículo típicos de hablante nativo de ruso.',
    'Un APT monolítico no incluye mensajes de error en idiomas que no domina. El esfuerzo multinacional es una cortina de humo.',
    'Atacante solitario plantó strings multilingües para desviar atribución, pero los comentarios revelan su lengua materna.',
    '["T1036","T1027","T1585"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_DE_004_IMPOSSIBLE_EMAIL_ROUTE',
    'Email con Latencia de Enrutamiento Físicamente Imposible',
    'DEFENSE_EVASION',
    'false_flag',
    '["email_headers_inconsistentes", "hops_intercontinentales_imposibles", "latencia_total_inferior_a_latencia_minima_fisica"]',
    '["attacker_controla_servidor_smtp_local", "attacker_forjo_encabezados_received", "attacker_subestimo_fisica_de_redes"]',
    '0.96', 0.0, 0.0, 0.0, 100,
    'Verificar si los 4 saltos pueden ser dentro de la misma región. Si todos los servidores están en un mismo datacenter, la latencia es explicable.',
    'Quality', 'False Flag',
    'Email pasó por 4 servidores en 3 continentes en 3 segundos. La velocidad de la luz prohíbe este tiempo de tránsito.',
    'La latencia entre continentes tiene un piso físico. Un email que lo viola tiene encabezados falsificados.',
    'Atacante forjó encabezados Received para simular origen externo, pero el email se originó dentro de la red local.',
    '["T1036","T1566","T1585"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_DE_005_TOO_FAST_RANSOMWARE_BLOG',
    'Publicación de Ransomware Prematura como Cortina de Humo',
    'DEFENSE_EVASION',
    'false_flag',
    '["ransomware_blog_publicado_menos_de_2h_post_cifrado", "datos_filtrados_ya_exfiltrados_antes", "evidencia_acceso_previo_a_datos"]',
    '["attacker_ya_tenia_los_datos", "ransomware_fue_cortina_de_humo", "attacker_quiere_atribucion_inmediata"]',
    '0.92', 0.0, 0.0, 0.0, 100,
    'Verificar si los datos ya estaban en la dark web antes del cifrado. Si la publicación fue simultánea, la hipótesis de cortina de humo se debilita.',
    'Manner', 'False Flag',
    'Grupo ransomware publica muestra 1 hora después del cifrado. Datos ya estaban exfiltrados días antes.',
    'Un atacante real analiza los datos antes de publicarlos. La velocidad implica conocimiento previo del contenido.',
    'El ransomware fue distracción para ocultar exfiltración anterior. El atacante quería atribución inmediata y ruidosa.',
    '["T1486","T1567","T1585"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_DE_006_FAKE_LEGAL_CITATION',
    'Documento Legal con Referencia a Legislación Ficticia',
    'DEFENSE_EVASION',
    'insider_threat',
    '["documento_legal_con_cita", "ley_no_existe_en_base_juridica", "formato_juridico_correcto", "autor_con_acceso_a_plantillas"]',
    '["falsificador_acceso_a_plantillas_legales", "falsificador_sin_conocimiento_juridico", "documento_creado_para_respaldar_fraude"]',
    '0.95', 0.0, 0.0, 0.0, 100,
    'Verificar si la ley existió y fue derogada. Si la ley existió en algún momento, la cita puede ser un error genuino de actualización.',
    'Quality', 'Borrowed Credibility',
    'Contrato legal cita decreto inexistente. El formato es perfecto; la referencia es falsa.',
    'Un documento genuino cita legislación real. La falsificación domina el formato pero falla en verificación jurídica.',
    'Falsificador con acceso a plantillas creó documento para respaldar fraude, apelando a autoridad de ley inventada.',
    '["T1036","T1565.001","T1204"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_DE_007_BROADCAST_SOURCE_IP',
    'Evidencia de Red con Dirección IP de Origen Imposible',
    'DEFENSE_EVASION',
    'insider_threat',
    '["paquete_tcp_con_ip_broadcast", "captura_de_red_como_evidencia", "error_tecnico_elemental", "origen_de_evidencia_es_interno"]',
    '["fabricante_sin_conocimiento_de_redes", "evidencia_fue_plantada", "fabricante_es_interno"]',
    '0.88', 0.0, 0.0, 0.0, 100,
    'Verificar si un escáner de red mal configurado generó el paquete. Si existe escáner legítimo, la hipótesis benigna gana.',
    'Quality', 'Quality',
    'PCAP con paquete TCP usando 255.255.255.255 como IP de origen. Técnicamente imposible.',
    'Ningún host legítimo usa la dirección de broadcast como IP de origen. El error es tan burdo que delata fabricación amateur.',
    'Fabricante sin conocimientos de redes intentó generar evidencia de exfiltración con error técnico elemental.',
    '["T1036","T1565.001"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_DE_008_FIREWALL_LOG_PLANTING',
    'Logs de Firewall Plantados como Cortina de Humo',
    'DEFENSE_EVASION',
    'false_flag',
    '["firewall_muestra_ataque_bloqueado", "servidor_destino_sin_intentos", "discrepancia_firewall_vs_host", "volumen_alto_eventos_bloqueados"]',
    '["logs_firewall_fueron_generados", "atacante_acceso_al_firewall", "ataque_real_está_en_otra_parte"]',
    '0.91', 0.0, 0.0, 0.0, 100,
    'Verificar si el firewall tiene bug conocido de falsos positivos. Si el modelo tiene historial de eventos falsos, la hipótesis benigna se fortalece.',
    'Quality', 'False Flag',
    'Firewall muestra 10,000 intentos bloqueados. El servidor no registra ninguna conexión en el mismo período.',
    'Si el firewall bloqueó, el servidor no vería las conexiones. Pero un atacante no enviaría 10,000 intentos sabiendo que serán bloqueados.',
    'Logs del firewall fueron generados para desviar atención hacia ataque externo falso, mientras el incidente real ocurre en otra parte.',
    '["T1565.001","T1036","T1585"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

-- -----------------------------------------------------------------------------
-- BLOQUE 2: EXECUTION (5 templates)
-- -----------------------------------------------------------------------------

INSERT INTO intent_templates VALUES (
    'H_EX_001_ZERO_RETRANSMISSION',
    'Captura de Red con Cero Retransmisiones TCP',
    'EXECUTION',
    'fabricacion',
    '["captura_de_red_sin_retransmisiones", "cero_colisiones_tcp", "trafico_simulado", "ausencia_de_errores_de_red"]',
    '["atacante_genero_trafico_sintetico", "atacante_no_sabe_simular_ruido_de_red", "herramienta_de_simulacion_demasiado_perfecta"]',
    '0.95', 0.0, 0.0, 0.0, 100,
    'Verificar si la captura fue tomada en entorno de laboratorio controlado. Si es un lab aislado con cable directo, la ausencia de colisiones es esperable.',
    'Quality', 'Quality',
    'Archivo PCAP con 10,000 paquetes y cero retransmisiones TCP. Físicamente imposible en cualquier red real con más de un salto.',
    'Las colisiones y retransmisiones son inevitables por la física del medio. La perfección delata simulación de laboratorio.',
    'El atacante generó tráfico sintético para fabricar evidencia de exfiltración, pero olvidó incluir el ruido natural de una red real.',
    '["T1036","T1565.001"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_EX_002_IMPOSSIBLE_TYPING_SPEED',
    'Velocidad de Tipeo Fisiológicamente Imposible',
    'EXECUTION',
    'fabricacion',
    '["mensaje_enviado_en_menos_de_2_segundos", "longitud_mensaje_mayor_a_200_caracteres", "puntuacion_precisa", "sin_errores_de_tipeo"]',
    '["mensaje_fue_generado_por_bot", "no_hay_humano_detras_de_la_sesion", "atacante_uso_automation_o_paste"]',
    '0.91', 0.0, 0.0, 0.0, 100,
    'Verificar si el mensaje fue pegado desde portapapeles. Si hay historial de Ctrl+V o botón derecho, la velocidad no implica generación artificial.',
    'Manner', 'Artificial Urgency',
    'Mensaje de 500 caracteres enviado 1.2 segundos después del prompt. Velocidad equivalente a 25,000 caracteres por minuto.',
    'Un humano profesional tipea 200-400 caracteres por minuto. Esta velocidad es 100 veces superior al máximo humano registrado.',
    'Un bot generó y envió el mensaje. La velocidad delata automatización. El atacante usa urgencia artificial para forzar decisiones del analista.',
    '["T1497","T1498"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_EX_003_POSTMORTEM_LOG_ENTRY',
    'Entrada de Log con Fecha Posterior a la Muerte del Host',
    'EXECUTION',
    'fabricacion',
    '["timestamp_log_posterior_a_apagado", "servidor_fue_migrado_o_destruido", "entrada_de_log_imposible_fisicamente"]',
    '["log_fue_alterado_posteriormente", "timestamp_fue_manipulado", "evidencia_fue_plantada"]',
    '0.98', 0.0, 0.0, 0.0, 100,
    'Verificar si hubo una restauración de backup que explique la entrada. Si el sistema fue restaurado desde snapshot con logs incluidos, la entrada es legítima.',
    'Quality', 'Quality',
    'Entrada de sudo en auth.log fechada 5 días después de que el servidor fuera apagado, migrado y destruido.',
    'La causalidad física prohíbe eventos en un sistema que ya no existe. El timestamp contradice la línea de tiempo del hardware.',
    'Alguien alteró el archivo de log después de la migración para fabricar una coartada o plantar evidencia retroactiva.',
    '["T1070.006","T1565.001"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_EX_004_PERFECT_24H_CYCLE',
    'Ciclo de Reinicio sin Deriva de Reloj en VM',
    'EXECUTION',
    'fabricacion',
    '["reinicios_de_servicio_cada_24h_exactas", "desviacion_estandar_de_intervalos_cero", "uptime_largo_sin_deriva_de_reloj", "vm_con_excesiva_precision_temporal"]',
    '["sistema_es_una_simulacion", "script_determinista_sin_deriva", "no_hay_hardware_real", "logs_fueron_generados_no_capturados"]',
    '0.89', 0.0, 0.0, 0.0, 100,
    'Verificar si el reloj del sistema está sincronizado con NTP cada 60 segundos. Si hay servicio NTP agresivo, la precisión puede ser inusualmente alta.',
    'Quality', 'Quality',
    'VM con 847 días de uptime y reinicios cada 86,400.000 segundos exactos. Desviación estándar de intervalos: 0 ms.',
    'Los osciladores de cuarzo derivan con temperatura y envejecimiento. Una VM real tiene variaciones de milisegundos. La perfección es una firma de simulación determinista.',
    'El entorno no es una VM real sino una simulación en motor determinista. Los logs fueron generados algorítmicamente, no capturados de hardware.',
    '["T1497","T1036"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_EX_005_BACKUP_OLDER_THAN_ORIGINAL',
    'Archivo de Backup con Fecha de Creación Anterior al Original',
    'EXECUTION',
    'insider_threat',
    '["backup_timestamp_anterior_a_original", "causalidad_temporal_violada", "archivos_creados_en_orden_imposible"]',
    '["timestamps_fueron_manipulados", "backup_creado_posteriormente_y_retrofechedo", "atacante_intento_simular_restauracion_previa"]',
    '0.97', 0.0, 0.0, 0.0, 100,
    'Verificar si el reloj del sistema fue ajustado manualmente. Si hay evidencia de cambio de hora del sistema, los timestamps pueden ser incorrectos sin intención maliciosa.',
    'Quality', 'Quality',
    'Archivo database_backup.sql con timestamp de creación 72 horas anterior al archivo database.sql que supuestamente respalda.',
    'Un backup es una copia de un original ya existente. No puede ser creado antes que su fuente. La causalidad temporal es inviolable.',
    'Alguien manipuló las fechas con timestomping para simular que el backup existía antes de un incidente, cuando en realidad fue creado después para fabricar coartada.',
    '["T1070.006"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

-- -----------------------------------------------------------------------------
-- BLOQUE 3: INITIAL_ACCESS (2 templates)
-- -----------------------------------------------------------------------------

INSERT INTO intent_templates VALUES (
    'H_IA_001_EXACT_BITCOIN_PAYMENT',
    'Pago en Bitcoin con Valor Exactamente Igual al Volumen de Datos Exfiltrados',
    'INITIAL_ACCESS',
    'insider_threat',
    '["exfiltracion_de_datos_cuantificable", "pago_en_btc_por_monto_exacto_en_satoshis", "coincidencia_numerica_improbable", "exchange_no_kyc"]',
    '["pago_fue_por_los_datos_robados", "comprador_y_vendedor_coordinaron", "monto_es_una_firma_operacional"]',
    '0.82', 0.0, 0.0, 0.0, 100,
    'Verificar si el monto en BTC es una cantidad redonda que casualmente coincide. Si es 0.01, 0.1 o 1.0 BTC exactos, la coincidencia es probablemente espuria.',
    'Relation', NULL,
    'Empleado recibe transferencia de exactamente 0.847 BTC (847,000,000 satoshis) desde exchange no KYC, una semana después de que 847 registros fueran exfiltrados.',
    'La coincidencia exacta entre volumen de datos robados y valor del pago es estadísticamente improbable. Los pagos ilícitos no suelen ser literales.',
    'El pago fue una transacción por los datos robados. El monto exacto es una firma operacional que vincula la exfiltración con la compensación económica.',
    '["T1567","T1586"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_IA_002_SELECTIVE_HONEYPOT_EVASION',
    'Infección que Afecta Producción pero Evade Honeypots Selectivamente',
    'INITIAL_ACCESS',
    'insider_threat',
    '["malware_ejecutado_en_honeypots_sin_exfiltracion", "servidor_real_sufrio_exfiltracion", "mismo_hash_malware_en_todos", "atacante_conocio_arquitectura_de_defensa"]',
    '["attacker_tenia_informacion_privilegiada", "insider_proporciono_topologia_de_red", "attacker_es_o_fue_empleado"]',
    '0.90', 0.0, 0.0, 0.0, 100,
    'Verificar si la topología era deducible desde fuera. Si la diferencia entre honeypots y producción era visible externamente, la selectividad no implica insider.',
    'Manner', 'False Flag',
    'Tres servidores infectados con malware de hash idéntico. Los dos honeypots solo registraron ejecución. El servidor real sufrió exfiltración completa.',
    'Un malware real sin lista de exclusión no distingue producción de honeypot. La selectividad implica conocimiento detallado de la topología de defensa.',
    'El atacante conocía la ubicación exacta de los honeypots y los evitó. Esto implica información privilegiada de un insider con acceso a documentación de seguridad.',
    '["T1078","T1585"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

-- -----------------------------------------------------------------------------
-- BLOQUE 4: IMPACT (4 templates)
-- -----------------------------------------------------------------------------

INSERT INTO intent_templates VALUES (
    'H_IM_001_TIMING_RESIGNATION_CLEANUP',
    'Renuncia con Limpieza de Historial de Bash Previo a Exfiltración',
    'IMPACT',
    'insider_threat',
    '["historial_de_bash_eliminado", "renuncia_menos_de_24h_despues_de_exfiltracion", "exfiltracion_previa_a_la_renuncia", "comandos_de_limpieza_ejecutados"]',
    '["empleado_actuo_con_intencion", "empleado_sabia_que_seria_auditado", "exfiltracion_fue_preparacion_para_salida"]',
    '0.87', 0.0, 0.0, 0.0, 100,
    'Verificar si la limpieza fue parte de un script de salida estándar corporativo. Si la empresa tiene política de wipe al terminar contrato, la acción es rutinaria.',
    'Quality', 'Preemptive Confession',
    'Administrador ejecuta history -c && rm -rf ~/.bash_history la noche del domingo. El lunes a las 09:00 presenta su renuncia. Exfiltración masiva detectada el domingo a las 23:47.',
    'Un empleado que renuncia voluntariamente no borra su historial de comandos si su trabajo fue legítimo. La limpieza pre-renuncia es preparación para auditoría post-empleo.',
    'El empleado exfiltró datos el domingo, limpió su rastro, y renunció el lunes. La secuencia temporal revela intención de ocultación y planificación.',
    '["T1070","T1048"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_IM_002_3AM_PRINT_JOB',
    'Impresión de Documento Confidencial en Horario No Laboral sin Presencia Física',
    'IMPACT',
    'insider_threat',
    '["trabajo_de_impresion_en_horario_nocturno", "usuario_de_vacaciones_o_fin_de_semana", "token_de_acceso_fisico_no_utilizado", "documento_confidencial_impreso"]',
    '["credenciales_comprometidas", "atacante_uso_impresora_remotamente", "atacante_conocio_documentos_de_la_victima"]',
    '0.79', 0.0, 0.0, 0.0, 100,
    'Verificar si el usuario tiene historial de impresión remota desde VPN. Si el usuario imprime regularmente desde casa los fines de semana, la anomalía se atenúa.',
    'Quality', 'Circadian Breach',
    'Documento confidencial de fusión impreso a las 03:17 AM del domingo desde impresora de Finanzas. Usuario de vacaciones. Sin acceso físico al edificio.',
    'Un usuario legítimo imprime durante horario laboral con presencia física. La hora, la ausencia y la falta de acceso físico contradicen el hábito documentado.',
    'Las credenciales del usuario fueron comprometidas y usadas remotamente para imprimir documento confidencial fuera del horario laboral.',
    '["T1078","T1530"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_IM_003_SELF_KEYLOGGER',
    'Auto-Instalación de Keylogger para Simular Compromiso Externo',
    'IMPACT',
    'insider_threat',
    '["keylogger_instalado_en_propia_maquina", "no_hay_señales_de_explotacion_externa", "instalacion_desde_cuenta_con_privilegios", "credenciales_capturadas_enviadas_a_servidor_externo"]',
    '["empleado_instalo_keylogger_deliberadamente", "empleado_quiere_coartada_de_compromiso", "empleado_justifica_perdida_de_credenciales"]',
    '0.91', 0.0, 0.0, 0.0, 100,
    'Verificar si hay evidencia de phishing dirigido al empleado en los 7 días previos. Si recibió email con enlace malicioso, la infección puede ser externa genuina.',
    'Quality', 'Self-Victimization for Cover',
    'Keylogger instalado en estación de trabajo del empleado desde su propia cuenta de administrador. Sin señales de explotación remota. Capturó sus credenciales de admin de dominio.',
    'Un atacante externo compromete la máquina de la víctima. Aquí, la víctima y el perpetrador son la misma persona, creando coartada de "a mí también me hackearon".',
    'El empleado instaló el keylogger para justificar la pérdida de credenciales ante investigación forense, encubriendo su propia actividad maliciosa.',
    '["T1056.004","T1078"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_IM_004_EXCESSIVE_INCIDENT_KNOWLEDGE',
    'Empleado con Conocimiento Detallado que Solo el Atacante Debería Tener',
    'IMPACT',
    'insider_threat',
    '["empleado_describe_detalles_tecnicos_no_publicados", "conocimiento_de_procesos_y_rutas_de_archivos_temporales", "informacion_no_incluida_en_reportes_preliminares_al_equipo"]',
    '["empleado_es_el_atacante_o_complice", "empleado_tiene_acceso_a_informacion_privilegiada_del_ataque", "empleado_participo_en_el_incidente"]',
    '0.93', 0.0, 0.0, 0.0, 100,
    'Verificar si otro miembro del equipo compartió detalles informalmente antes de la entrevista. Si hubo briefing técnico no documentado, el conocimiento puede ser de segunda mano.',
    'Quantity', 'Over-Cooperation',
    'En entrevista post-incidente, empleado describe nombres de procesos maliciosos, rutas de archivos temporales y métodos de persistencia que no aparecen en reportes preliminares.',
    'Un empleado afectado legítimamente no conoce detalles técnicos del ataque. El conocimiento granular implica participación directa o acceso a información del atacante.',
    'El empleado es el atacante o su cómplice. Su conocimiento detallado del incidente lo delata: sabe lo que solo quien ejecutó el ataque podría saber.',
    '["T1078","T1204"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

-- -----------------------------------------------------------------------------
-- BLOQUE 5: COLLECTION (2 templates)
-- -----------------------------------------------------------------------------

INSERT INTO intent_templates VALUES (
    'H_CO_001_PERFECT_DATABASE_COMPACTNESS',
    'Base de Datos sin Fragmentación Interna con Tamaño Inusualmente Alto',
    'COLLECTION',
    'fabricacion',
    '["base_de_datos_sin_fragmentacion", "cero_paginas_libres", "sqlite_perfectamente_compacta", "tamaño_alto_para_datos_sin_historial"]',
    '["base_de_datos_fue_generada_desde_cero", "datos_fueron_fabricados", "no_hay_historial_de_operacion_real"]',
    '0.86', 0.0, 0.0, 0.0, 100,
    'Verificar si la base de datos fue exportada y re-importada como parte de una migración documentada. Si hay registro de migración en changelog, la compacidad es explicable.',
    'Quality', 'Quality',
    'Archivo SQLite de 2 GB con cero páginas libres y cero fragmentación interna. Distribución de páginas perfectamente secuencial.',
    'Las bases de datos reales acumulan espacio libre no reclamado y fragmentación con inserciones y eliminaciones. Una base perfecta solo existe si fue creada desde cero justo antes del análisis.',
    'La base de datos fue generada artificialmente para simular meses de operación. Los datos son probablemente fabricados y la estructura es sintética.',
    '["T1036","T1565.001"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

INSERT INTO intent_templates VALUES (
    'H_CO_002_METADATA_CANVA_COLLECTION',
    'Documento de Recolección con Metadatos de Herramienta No Profesional',
    'COLLECTION',
    'false_flag',
    '["documento_coleccion_con_metadatos_canva", "autor_interno_en_documento_externo", "fecha_creacion_inconsistente"]',
    '["atacante_uso_plantilla_disponible", "atacante_no_tenia_acceso_a_sistema_oficial", "documento_fue_creado_para_sustentar_narrativa"]',
    '0.85', 0.0, 0.0, 0.0, 100,
    'Verificar si el documento fue creado por un contractor externo sin acceso al sistema oficial. Si es un externo, el uso de Canva es plausible.',
    'Quality', 'Borrowed Credibility',
    'Documento presentado como evidencia de recolección tiene metadatos de Canva y autor que no corresponde al sistema oficial.',
    'La recolección de evidencia institucional requiere herramientas oficiales. El uso de software de diseño personal delata falta de acceso al sistema real.',
    'Atacante sin acceso al sistema de gestión documental oficial usó herramientas personales para crear evidencia de recolección falsa.',
    '["T1036","T1565.001"]', 1.0,
    'expert_elicitation_bootstrap_v1'
);

-- -----------------------------------------------------------------------------
-- ÍNDICES DE EVIDENCIAS REQUERIDAS (C2 fix: solo template_ids existentes)
-- -----------------------------------------------------------------------------

INSERT INTO required_evidences VALUES ('vssadmin', 'H_DE_001_WEAPONIZED_INCOMPETENCE_VSS');
INSERT INTO required_evidences VALUES ('shadow', 'H_DE_001_WEAPONIZED_INCOMPETENCE_VSS');
INSERT INTO required_evidences VALUES ('history_c', 'H_IM_001_TIMING_RESIGNATION_CLEANUP');
INSERT INTO required_evidences VALUES ('shred', 'H_IM_001_TIMING_RESIGNATION_CLEANUP');
INSERT INTO required_evidences VALUES ('Canva', 'H_DE_002_CANVA_METADATA_SPOOF');
INSERT INTO required_evidences VALUES ('metadata', 'H_DE_002_CANVA_METADATA_SPOOF');
INSERT INTO required_evidences VALUES ('Producer', 'H_DE_002_CANVA_METADATA_SPOOF');
INSERT INTO required_evidences VALUES ('retransmisión', 'H_EX_001_ZERO_RETRANSMISSION');
INSERT INTO required_evidences VALUES ('TCP', 'H_EX_001_ZERO_RETRANSMISSION');
INSERT INTO required_evidences VALUES ('PCAP', 'H_EX_001_ZERO_RETRANSMISSION');
INSERT INTO required_evidences VALUES ('broadcast', 'H_DE_007_BROADCAST_SOURCE_IP');
INSERT INTO required_evidences VALUES ('255_255_255_255', 'H_DE_007_BROADCAST_SOURCE_IP');
INSERT INTO required_evidences VALUES ('timestomp', 'H_EX_003_POSTMORTEM_LOG_ENTRY');
INSERT INTO required_evidences VALUES ('timestamp', 'H_EX_003_POSTMORTEM_LOG_ENTRY');
INSERT INTO required_evidences VALUES ('backup', 'H_EX_005_BACKUP_OLDER_THAN_ORIGINAL');
INSERT INTO required_evidences VALUES ('creación', 'H_EX_005_BACKUP_OLDER_THAN_ORIGINAL');
INSERT INTO required_evidences VALUES ('velocidad_tipeo', 'H_EX_002_IMPOSSIBLE_TYPING_SPEED');
INSERT INTO required_evidences VALUES ('caracteres_por_minuto', 'H_EX_002_IMPOSSIBLE_TYPING_SPEED');
INSERT INTO required_evidences VALUES ('impresión', 'H_IM_002_3AM_PRINT_JOB');
INSERT INTO required_evidences VALUES ('3_AM', 'H_IM_002_3AM_PRINT_JOB');
INSERT INTO required_evidences VALUES ('fuera_de_horario', 'H_IM_002_3AM_PRINT_JOB');
INSERT INTO required_evidences VALUES ('malware', 'H_DE_003_MULTILINGUAL_FALSE_FLAG');
INSERT INTO required_evidences VALUES ('keylogger', 'H_IM_003_SELF_KEYLOGGER');
INSERT INTO required_evidences VALUES ('ransomware', 'H_DE_005_TOO_FAST_RANSOMWARE_BLOG');
INSERT INTO required_evidences VALUES ('ley', 'H_DE_006_FAKE_LEGAL_CITATION');
INSERT INTO required_evidences VALUES ('decreto', 'H_DE_006_FAKE_LEGAL_CITATION');
INSERT INTO required_evidences VALUES ('artículo', 'H_DE_006_FAKE_LEGAL_CITATION');
INSERT INTO required_evidences VALUES ('SQLite', 'H_CO_001_PERFECT_DATABASE_COMPACTNESS');
INSERT INTO required_evidences VALUES ('fragmentación', 'H_CO_001_PERFECT_DATABASE_COMPACTNESS');
INSERT INTO required_evidences VALUES ('email', 'H_DE_004_IMPOSSIBLE_EMAIL_ROUTE');
INSERT INTO required_evidences VALUES ('Received', 'H_DE_004_IMPOSSIBLE_EMAIL_ROUTE');
INSERT INTO required_evidences VALUES ('SMTP', 'H_DE_004_IMPOSSIBLE_EMAIL_ROUTE');
INSERT INTO required_evidences VALUES ('Bitcoin', 'H_IA_001_EXACT_BITCOIN_PAYMENT');
INSERT INTO required_evidences VALUES ('BTC', 'H_IA_001_EXACT_BITCOIN_PAYMENT');
INSERT INTO required_evidences VALUES ('satoshis', 'H_IA_001_EXACT_BITCOIN_PAYMENT');
INSERT INTO required_evidences VALUES ('honeypot', 'H_IA_002_SELECTIVE_HONEYPOT_EVASION');
INSERT INTO required_evidences VALUES ('entrevista', 'H_IM_004_EXCESSIVE_INCIDENT_KNOWLEDGE');
INSERT INTO required_evidences VALUES ('testimonio', 'H_IM_004_EXCESSIVE_INCIDENT_KNOWLEDGE');
INSERT INTO required_evidences VALUES ('Canva', 'H_CO_002_METADATA_CANVA_COLLECTION');
INSERT INTO required_evidences VALUES ('metadata', 'H_CO_002_METADATA_CANVA_COLLECTION');

-- -----------------------------------------------------------------------------
-- VERIFICACIÓN DE INTEGRIDAD
-- -----------------------------------------------------------------------------
-- SELECT 'SQL_V3_HASH', hex(sha3sum(readfile('initial_templates_v3.sql')));
-- =============================================================================
