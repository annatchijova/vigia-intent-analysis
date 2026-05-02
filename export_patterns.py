import sqlite3, json

DB = '/home/labestiadevigia/vigia-repo/vigia/tools/forensic_patterns.sqlite'
conn = sqlite3.connect(DB)
rows = conn.execute("""
    SELECT pattern_name, category, pattern_regex, weight, description, 
           source, case_origin, peirce_layer, confidence_boost 
    FROM nlp_patterns
    ORDER BY pattern_name, weight DESC
""").fetchall()
conn.close()

print(f"Total patrones a exportar: {len(rows)}")
for r in rows:
    print(r[0], r[7])  # nombre + layer
