/*
 * Red Team Round 10 — barrido de tipos sobre los renderizadores de la web UI.
 *
 * La UI existe para inspeccionar bundles que pueden venir de un tercero (otra
 * pericia, la contraparte), asi que el contenido de un bundle es entrada no
 * confiable. Este script mete cada tipo hostil en cada campo que los
 * renderizadores tocan y reporta cual de ellos LANZA.
 *
 * Uso:
 *     node scripts/redteam_round10_render_types.mjs
 *     # desde un checkout con el app.js pre-R10 -> 6 campos lanzan
 *
 * Exit 0 si ningun campo lanza; 1 si alguno lo hace.
 */
import fs from "node:fs";
const src = fs.readFileSync("vigia/ui/static/app.js", "utf8");
const fn = (name, arg, extra = []) => {
  const m = src.match(new RegExp(`function ${name}\\(${arg}\\) \\{([\\s\\S]*?)\\n\\}\\n`));
  if (!m) throw new Error("no encontrado: " + name);
  return new Function(arg, ...extra, m[1]);
};
const esc = fn("esc", "v");
const txt = src.includes("function txt(") ? fn("txt", "v") : (v) => (v ?? "");
const arr = src.includes("function arr(") ? fn("arr", "v") : (v) => (v || []);
const t = (k) => k;
const KNOWN_VERDICTS = ["MALICE","INTENT","SUSPICION","NOISE","ABSTAIN"];
const chip = fn("chip", "verdict", ["esc", "KNOWN_VERDICTS"]);
const cdm = src.match(/function confDisplay\((\w+)\) \{([\s\S]*?)\n\}\n/);
const confDisplay = new Function(cdm[1], "esc", cdm[2]);

const tl = fn("toolLogTab", "norm", ["esc", "t", "txt"]);
const ft = fn("findingsTab", "norm", ["esc","t","chip","confDisplay","KNOWN_VERDICTS","arr"]);

const HOSTILE = {numero: 42, dict: {a:1}, lista: [1], bool: true, string: "abc"};
let fallos = 0;
const probe = (label, run) => {
  const bad = [];
  for (const [kind, v] of Object.entries(HOSTILE)) {
    try { run(v); } catch (e) { bad.push(`${kind}: ${e.message}`); }
  }
  if (bad.length) { fallos++; console.log(`  ${label.padEnd(34)} LANZA -> ${bad[0]}`); }
  return bad.length === 0;
};

const be = {seq:1, tool:"t", target:"x", result_summary:"r",
            timestamp:"2026-01-01T00:00:00.000000+00:00",
            entry_hash:"a".repeat(64), prev_hash:"b".repeat(64)};
for (const f of Object.keys(be))
  probe(`toolLogTab / entry.${f}`, v =>
    tl({tool_log:{present:true, entries:[{...be,[f]:v}]}, audit_trail:{}}, esc, t, txt));
const ba = {seq:1, action:"a", tool:"t", note:"n", timestamp:"2026-01-01T00:00:00.000000+00:00"};
for (const f of Object.keys(ba))
  probe(`toolLogTab / audit.${f}`, v =>
    tl({tool_log:{}, audit_trail:{present:true, entry_count:1,
        entries_preview:[{...ba,[f]:v}]}}, esc, t, txt));
const bf = {id:"F-001", title:"x", verdict:"NOISE", status:"C", confidence:"HIGH",
            firstness:"a", secondness:"b", thirdness:"c", carnegie:"n",
            mitre_ttps:["T1070"], artifacts:["/a"], tools_used:["t"],
            devil_advocate:"d", corroboration:"c", kind:"finding"};
for (const f of Object.keys(bf))
  probe(`findingsTab / ${f}`, v =>
    ft({findings:[{...bf,[f]:v}]}, esc, t, x => chip(x, esc, KNOWN_VERDICTS),
       x => confDisplay(x, esc), KNOWN_VERDICTS, arr));

console.log(fallos ? `\n${fallos} campos LANZAN` : "\nningun campo lanza — los 3 renderizadores sobreviven a todos los tipos");
process.exit(fallos ? 1 : 0);
