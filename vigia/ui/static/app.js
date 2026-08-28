/* VIGIA Web UI — vanilla JS SPA. No build step, no external requests.
   All bundle content is untrusted data: everything is rendered through esc()
   or textContent, never as HTML. Verdicts are displayed verbatim.

   i18n: UI chrome strings come from window.VIGIA_I18N (static/i18n.js),
   EN/ES, toggled by the header button and persisted in localStorage.
   Sealed vocabulary (verdict values, schema names, bundle field content)
   is deliberately NOT translated. */

"use strict";

const app = document.getElementById("app");
const KNOWN_VERDICTS = ["NOISE", "SUSPICION", "INTENT", "MALICE", "ABSTAIN"];
const EXIT_LABELS = {0: "NOISE", 1: "MALICE", 2: "ERROR", 3: "INTENT",
                     4: "ABSTAIN", 5: "SUSPICION"};

/* ---------- i18n ---------- */

let LANG = (function () {
  try {
    const stored = localStorage.getItem("vigia-lang");
    if (stored === "en" || stored === "es") return stored;
  } catch (e) {}
  return (navigator.language || "en").toLowerCase().startsWith("es") ? "es" : "en";
})();

function t(key, vars) {
  const table = (window.VIGIA_I18N && window.VIGIA_I18N[LANG]) || {};
  const fallback = (window.VIGIA_I18N && window.VIGIA_I18N.en) || {};
  let s = table[key] !== undefined ? table[key] : (fallback[key] !== undefined ? fallback[key] : key);
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      s = s.split("{" + k + "}").join(String(v));
    }
  }
  return s;
}

function applyChrome() {
  document.documentElement.lang = LANG;
  const set = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  };
  set("chrome-eyebrow", t("header.eyebrow"));
  set("chrome-title", t("header.title"));
  set("chrome-sub", t("header.sub"));
  set("chrome-footer", t("footer.text"));
  set("theme-toggle", t("theme.toggle"));
  const nav = {bundles: "nav.bundles", investigate: "nav.investigate", jobs: "nav.jobs"};
  document.querySelectorAll("#nav a").forEach(a => {
    if (nav[a.dataset.nav]) a.textContent = t(nav[a.dataset.nav]);
  });
  const lt = document.getElementById("lang-toggle");
  if (lt) lt.textContent = LANG === "es" ? "EN" : "ES";
}

(function initLang() {
  const lt = document.getElementById("lang-toggle");
  if (lt) lt.addEventListener("click", () => {
    LANG = LANG === "es" ? "en" : "es";
    try { localStorage.setItem("vigia-lang", LANG); } catch (e) {}
    applyChrome();
    route();
  });
})();

/* ---------- utilities ---------- */

function esc(v) {
  if (v === null || v === undefined) return "";
  return String(v).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function chip(verdict) {
  if (verdict === null || verdict === undefined) return '<span class="chip other">—</span>';
  const cls = KNOWN_VERDICTS.includes(verdict) || verdict === "ERROR" ? verdict : "other";
  return `<span class="chip ${cls}">${esc(verdict)}</span>`;
}

function confDisplay(c) {
  if (c === null || c === undefined) return "";
  if (typeof c === "object" && c.is_fraction) return c.display;
  return String(c);
}

async function api(path, opts) {
  const res = await fetch(path, opts);
  let body = null;
  try { body = await res.json(); } catch (e) { /* raw endpoints */ }
  if (!res.ok) {
    const msg = body && body.detail ? JSON.stringify(body.detail) : res.statusText;
    throw new Error(`${res.status}: ${msg}`);
  }
  return body;
}

function post(path, payload) {
  return api(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload || {}),
  });
}

function setNav(name) {
  document.querySelectorAll("#nav a").forEach(a => {
    a.classList.toggle("active", a.dataset.nav === name);
  });
}

function errorView(err) {
  app.innerHTML = `<div class="banner error">${esc(t("err.request"))} ${esc(err.message)}</div>`;
}

/* Pretty-print raw JSON, highlighting serialized Fractions as N/D. */
function rawJsonHtml(obj) {
  const frag = (o) => {
    if (o && typeof o === "object" && o.__fraction__ === true &&
        Number.isInteger(o.num) && Number.isInteger(o.den)) {
      return `<span class="fraction" title='{"__fraction__":true,"num":${o.num},"den":${o.den}}'>` +
             `${o.num}/${o.den}</span>`;
    }
    if (Array.isArray(o)) return "[" + o.map(frag).join(", ") + "]";
    if (o && typeof o === "object") {
      const inner = Object.entries(o)
        .map(([k, v]) => `\n${'"' + esc(k) + '"'}: ${frag(v)}`).join(",");
      return "{" + inner + "\n}";
    }
    return esc(JSON.stringify(o));
  };
  return frag(obj);
}

/* ---------- theme ---------- */

(function initTheme() {
  let stored = null;
  try { stored = localStorage.getItem("vigia-theme"); } catch (e) {}
  if (stored) document.documentElement.dataset.theme = stored;
  document.getElementById("theme-toggle").addEventListener("click", () => {
    const cur = document.documentElement.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("vigia-theme", next); } catch (e) {}
  });
})();

/* ---------- bundles list ---------- */

const listState = {verdict: "", schema: "", q: "", offset: 0, limit: 50};

async function viewBundles() {
  setNav("bundles");
  const params = new URLSearchParams();
  for (const k of ["verdict", "schema", "q"]) if (listState[k]) params.set(k, listState[k]);
  params.set("limit", listState.limit);
  params.set("offset", listState.offset);
  const data = await api("/api/bundles?" + params);

  const rows = data.items.map(b => {
    const verdicts = (b.verdicts || []).map(v => chip(v.verdict)).join(" ") ||
                     '<span class="chip other">—</span>';
    const flags = [
      b.verdict_disagreement ? `<span class="stamp warn" title="${esc(t("flag.disagree"))}">≠</span>` : "",
      b.has_sha256_sidecar ? `<span class="badge" title="${esc(t("flag.sidecar"))}">sha256</span>` : "",
      b.has_reasoning_trace ? `<span class="badge" title="${esc(t("flag.trace"))}">trace</span>` : "",
    ].join(" ");
    return `<tr class="rowlink" data-id="${esc(b.id)}">
      <td><div>${esc(b.case_id || t("list.no_case_id"))}</div>
          <div class="path">${esc(b.rel_path)}</div></td>
      <td><span class="badge">${esc(b.schema)}</span></td>
      <td>${verdicts}</td>
      <td class="mono">${esc((b.sealed_at || "").slice(0, 19))}</td>
      <td>${flags}</td>
    </tr>`;
  }).join("");

  const schemas = ["", "ebs_v1", "agent_audit", "mcp_investigation", "unknown", "unparseable"];
  app.innerHTML = `
    <div class="filters">
      <select id="f-verdict">
        <option value="">${esc(t("filters.verdict_all"))}</option>
        ${KNOWN_VERDICTS.map(v => `<option ${listState.verdict === v ? "selected" : ""}>${v}</option>`).join("")}
      </select>
      <select id="f-schema">
        ${schemas.map(s => `<option value="${s}" ${listState.schema === s ? "selected" : ""}>` +
                           `${s ? esc(t("filters.schema_prefix")) + s : esc(t("filters.schema_all"))}</option>`).join("")}
      </select>
      <input id="f-q" placeholder="${esc(t("filters.search_ph"))}" value="${esc(listState.q)}">
      <button id="f-refresh">${esc(t("filters.rescan"))}</button>
      <span class="count">${esc(t("list.count", {total: data.total, n: data.items.length, offset: data.offset}))}</span>
    </div>
    <table>
      <thead><tr><th>${esc(t("th.case"))}</th><th>${esc(t("th.schema"))}</th>
        <th>${esc(t("th.verdicts"))}</th><th>${esc(t("th.sealed"))}</th><th></th></tr></thead>
      <tbody>${rows || `<tr><td colspan="5" class="muted">${esc(t("list.empty"))}</td></tr>`}</tbody>
    </table>
    <div class="filters" style="margin-top:12px">
      <button id="pg-prev" ${data.offset === 0 ? "disabled" : ""}>${esc(t("pg.prev"))}</button>
      <button id="pg-next" ${data.offset + data.items.length >= data.total ? "disabled" : ""}>${esc(t("pg.next"))}</button>
    </div>`;

  document.getElementById("f-verdict").onchange = e => { listState.verdict = e.target.value; listState.offset = 0; viewBundles(); };
  document.getElementById("f-schema").onchange = e => { listState.schema = e.target.value; listState.offset = 0; viewBundles(); };
  let qTimer = null;
  document.getElementById("f-q").oninput = e => {
    clearTimeout(qTimer);
    qTimer = setTimeout(() => { listState.q = e.target.value; listState.offset = 0; viewBundles(); }, 300);
  };
  document.getElementById("f-refresh").onclick = async () => {
    await api("/api/bundles?refresh=1&limit=1"); viewBundles();
  };
  document.getElementById("pg-prev").onclick = () => { listState.offset = Math.max(0, listState.offset - listState.limit); viewBundles(); };
  document.getElementById("pg-next").onclick = () => { listState.offset += listState.limit; viewBundles(); };
  app.querySelectorAll("tr.rowlink").forEach(tr => {
    tr.onclick = () => { location.hash = `#/bundle/${tr.dataset.id}`; };
  });
}

/* ---------- bundle detail ---------- */

async function viewBundle(id, tab) {
  setNav("bundles");
  tab = tab || "overview";
  const norm = await api(`/api/bundles/${encodeURIComponent(id)}`);

  const tabs = ["overview", "findings", "toollog", "verify", "raw"];
  const tabBar = `<div class="tabs">${tabs.map(tb =>
    `<a href="#/bundle/${esc(id)}/${tb}" class="${tb === tab ? "active" : ""}">${esc(t("tab." + tb))}</a>`).join("")}</div>`;

  const banner = norm.verdict_disagreement
    ? `<div class="banner">${esc(t("banner.disagree"))}</div>`
    : "";
  const warnings = (norm.warnings || []).length
    ? `<p class="warnlist">${norm.warnings.map(w => "⚠ " + esc(w)).join("<br>")}</p>` : "";

  let body = "";
  if (tab === "overview") body = overviewTab(norm);
  else if (tab === "findings") body = findingsTab(norm);
  else if (tab === "toollog") body = toolLogTab(norm);
  else if (tab === "verify") body = verifyTab(norm);
  else if (tab === "raw") body = `<pre class="raw" id="rawbox">${esc(t("raw.loading"))}</pre>`;

  app.innerHTML = `
    <p><a href="#/bundles">${esc(t("detail.back"))}</a></p>
    <div class="sec-head"><span class="n">BUNDLE</span>
      <h2>${esc(norm.case_id || t("list.no_case_id"))}</h2>
      <span class="badge">${esc(norm.schema)}</span>
      <span class="path">${esc(norm.rel_path || "")}</span></div>
    ${banner}${warnings}${tabBar}${body}`;

  if (tab === "raw") {
    const raw = await fetch(`/api/bundles/${encodeURIComponent(id)}/raw`);
    const box = document.getElementById("rawbox");
    if (!raw.ok) { box.textContent = `${t("raw.unavailable")} (${raw.status})`; return; }
    box.innerHTML = rawJsonHtml(await raw.json());
  }
  if (tab === "verify") wireVerify(id, norm);
}

function overviewTab(norm) {
  const cards = (norm.verdicts || []).map(v => {
    const cls = KNOWN_VERDICTS.includes(v.verdict) ? v.verdict : "";
    return `<div class="card ${cls}">
      <div class="src">${esc(v.source)}</div>
      <div class="verdict">${esc(v.verdict === null ? "—" : v.verdict)}</div>
      ${v.confidence ? `<div class="note mono">${esc(t("overview.confidence"))} ${esc(confDisplay(v.confidence))}</div>` : ""}
      <div class="note path">${esc(v.raw_pointer)}</div>
    </div>`;
  }).join("") || `<p class="muted">${esc(t("overview.no_verdicts"))}</p>`;

  const kv = [];
  if (norm.sealed_at) kv.push([t("kv.sealed_at"), norm.sealed_at]);
  const integ = norm.integrity || {};
  for (const [k, v] of Object.entries(integ)) if (v) kv.push([k.replace(/_/g, " "), v]);
  const side = norm.sidecar || {};
  kv.push([t("kv.sidecar"), side.has_sha256_sidecar ? t("kv.present") : t("kv.absent")]);
  kv.push([t("kv.trace"), side.has_reasoning_trace ? t("kv.present") : t("kv.absent")]);
  const extra = norm.extra || {};
  if (extra.mode) kv.push([t("kv.mode"), extra.mode]);
  if (extra.examiner) kv.push([t("kv.examiner"), extra.examiner]);
  if (extra.daubert_admissible !== undefined && extra.daubert_admissible !== null)
    kv.push([t("kv.daubert"), String(extra.daubert_admissible)]);
  if (extra.iterations_executed !== undefined && extra.iterations_executed !== null)
    kv.push([t("kv.iterations"), String(extra.iterations_executed)]);

  const rationale = extra.verdict_rationale || extra.caie_reason || null;
  const narrative = extra.narrative || null;
  return `
    <div class="cards">${cards}</div>
    <section class="panel"><div class="sec-head"><span class="n">§</span><h2>${esc(t("overview.seal"))}</h2></div>
      <dl class="kv">${kv.map(([k, v]) =>
        `<dt>${esc(k)}</dt><dd class="mono">${esc(v)}</dd>`).join("")}</dl>
    </section>
    ${rationale ? `<section class="panel"><div class="sec-head"><span class="n">§</span>
       <h2>${esc(t("overview.rationale"))}</h2></div><p>${esc(rationale)}</p></section>` : ""}
    ${narrative ? `<section class="panel"><div class="sec-head"><span class="n">§</span>
       <h2>${esc(t("overview.narrative"))}</h2></div><pre class="raw">${esc(narrative)}</pre></section>` : ""}`;
}

function findingsTab(norm) {
  const items = norm.findings || [];
  if (!items.length) {
    return `<p class="muted">${esc(t("findings.none"))}
      ${norm.schema === "ebs_v1" ? esc(t("findings.none_ebs")) : "."}</p>`;
  }
  return items.map(f => {
    const peirce = f.peirce ? `<div class="peirce">
        <div><b>${esc(t("peirce.first"))}</b><p>${esc(f.peirce.firstness)}</p></div>
        <div><b>${esc(t("peirce.second"))}</b><p>${esc(f.peirce.secondness)}</p></div>
        <div><b>${esc(t("peirce.third"))}</b><p>${esc(f.peirce.thirdness)}</p></div>
      </div>` : "";
    const mitre = (f.mitre_ttps || []).map(x => `<span class="badge">${esc(x)}</span>`).join(" ");
    const kv = [];
    if (f.status) kv.push([t("f.status"), f.status]);
    if (f.confidence) kv.push([t("f.confidence"), confDisplay(f.confidence)]);
    if (f.kind === "pipeline_signal") {
      if (f.evidence_type) kv.push([t("f.evidence_type"), f.evidence_type]);
      if (f.source) kv.push([t("f.source"), f.source]);
      if (f.z_score) kv.push([t("f.zscore"), f.z_score]);
    }
    if (f.carnegie) kv.push([t("f.carnegie"), f.carnegie]);
    if ((f.artifacts || []).length) kv.push([t("f.artifacts"), f.artifacts.join(", ")]);
    if ((f.tools_used || []).length) kv.push([t("f.tools"), f.tools_used.join(", ")]);
    return `<section class="panel">
      <div class="sec-head"><span class="n">${esc(f.id || "")}</span>
        <h2>${esc(f.title || t("findings.untitled"))}</h2>${chip(f.verdict)}</div>
      ${peirce}
      <dl class="kv">${kv.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
      ${f.devil_advocate ? `<p><b>${esc(t("f.devil"))}</b> ${esc(f.devil_advocate)}</p>` : ""}
      ${f.corroboration ? `<p><b>${esc(t("f.corr"))}</b> ${esc(f.corroboration)}</p>` : ""}
      ${mitre ? `<p>${mitre}</p>` : ""}
    </section>`;
  }).join("");
}

function toolLogTab(norm) {
  const log = norm.tool_log || {};
  const audit = norm.audit_trail || {};
  let out = "";
  if (log.present) {
    const entries = log.entries || [];
    out += `<section class="panel"><div class="sec-head"><span class="n">§</span>
      <h2>${esc(t("toollog.title"))}</h2>
      <span class="badge">chain v${esc(log.chain_version || "1")}</span>
      <span class="muted">${esc(t("toollog.entries", {n: entries.length}))}</span></div>
      ${log.chain_tip_sha256 ? `<p class="mono muted">${esc(t("toollog.tip"))} ${esc(log.chain_tip_sha256)}</p>` : ""}
      <ol class="chainlist">${entries.map(e => `
        <li><span class="tool">#${esc(e.seq)} ${esc(e.tool)}</span>
          <span class="muted">→ ${esc(e.target)}</span><br>
          <span>${esc(e.result_summary)}</span><br>
          <span class="hash">${esc((e.timestamp || "").slice(0, 23))}
            ${e.entry_hash ? " · entry " + esc(e.entry_hash.slice(0, 16)) + "…" : ""}
            ${e.prev_hash ? " · prev " + esc(String(e.prev_hash).slice(0, 16)) + "…" : ""}</span>
        </li>`).join("")}</ol></section>`;
  }
  if (audit.present) {
    out += `<section class="panel"><div class="sec-head"><span class="n">§</span>
      <h2>${esc(t("toollog.audit"))}</h2><span class="muted">${esc(t("toollog.first_shown",
        {total: audit.entry_count, n: (audit.entries_preview || []).length}))}</span></div>
      <ol class="chainlist">${(audit.entries_preview || []).map(e => `
        <li><span class="tool">#${esc(e.seq)} ${esc(e.action)}</span>
          <span class="muted">${esc(e.tool || "")}</span><br>
          <span>${esc(e.note || "")}</span><br>
          <span class="hash">${esc((e.timestamp || "").slice(0, 23))}</span></li>`).join("")}
      </ol></section>`;
  }
  return out || `<p class="muted">${esc(t("toollog.none"))}</p>`;
}

/* ---------- verify tab ---------- */

function verifyTab(norm) {
  const applicable = {
    ebs_v1: ["ebs_v1", "sidecar"],
    mcp_investigation: ["tool_log", "sidecar"],
    agent_audit: ["tool_log", "sidecar"],
  }[norm.schema] || ["sidecar"];
  const all = ["ebs_v1", "tool_log", "sidecar"];
  return `<section class="panel">
    <div class="sec-head"><span class="n">§</span><h2>${esc(t("verify.title"))}</h2></div>
    <p class="muted">${esc(t("verify.note"))}</p>
    <label class="mono" style="font-size:12px">
      <input type="checkbox" id="v-anyway"> ${esc(t("verify.anyway"))}</label>
    ${all.map(v => `
      <div style="margin:14px 0" data-verifier-row="${v}"
           class="${applicable.includes(v) ? "" : "v-extra"}">
        <button data-verifier="${v}">${esc(t("verify.name." + v))}</button>
        ${v === "tool_log" ? `<input id="v-hmac" placeholder="${esc(t("verify.hmac_ph"))}"
            style="margin-left:8px;max-width:280px">` : ""}
        <div data-result="${v}" style="margin-top:8px"></div>
      </div>`).join("")}
  </section>
  <style>.v-extra{display:none} .v-show .v-extra{display:block;opacity:.75}</style>`;
}

function wireVerify(id, norm) {
  const anyway = document.getElementById("v-anyway");
  if (anyway) anyway.onchange = () => app.classList.toggle("v-show", anyway.checked);
  app.querySelectorAll("button[data-verifier]").forEach(btn => {
    btn.onclick = async () => {
      const v = btn.dataset.verifier;
      const box = app.querySelector(`[data-result="${v}"]`);
      box.innerHTML = `<span class="muted">${esc(t("verify.running"))}</span>`;
      const payload = {verifier: v};
      const hmac = document.getElementById("v-hmac");
      if (v === "tool_log" && hmac && hmac.value.trim()) payload.hmac_key_hex = hmac.value.trim();
      try {
        const r = await post(`/api/bundles/${encodeURIComponent(id)}/verify`, payload);
        const cls = {PASS: "pass", VERIFIED: "pass", MATCH: "pass",
                     FAIL: "fail", BROKEN: "fail", MISMATCH: "fail",
                     NO_LOG: "warn", ABSENT: "warn", ERROR: "fail", TIMEOUT: "fail"}[r.status] || "warn";
        box.innerHTML = `<span class="stamp ${cls}">${esc(r.status)}</span>
          ${r.conformity_label ? `<span class="badge">${esc(r.conformity_label)}</span>` : ""}
          ${r.exit_code !== undefined && r.exit_code !== null ? `<span class="badge">${esc(t("verify.exit"))} ${esc(r.exit_code)}</span>` : ""}
          ${r.checks ? `<dl class="kv" style="margin-top:8px">${r.checks.map(c =>
             `<dt>${esc(c.rule)}</dt><dd>${c.passed ? "✓" : "✗"} ${esc(c.message)}</dd>`).join("")}</dl>` : ""}
          ${r.detail ? `<pre class="raw" style="margin-top:8px;max-height:32vh">${esc(r.detail)}</pre>` : ""}`;
      } catch (err) {
        box.innerHTML = `<span class="stamp fail">ERROR</span> <span class="muted">${esc(err.message)}</span>`;
      }
    };
  });
}

/* ---------- investigate ---------- */

const CASE_ID_RE = /^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/;

async function viewInvestigate() {
  setNav("investigate");
  let roots;
  try { roots = await api("/api/evidence"); }
  catch (err) { return errorView(err); }

  const tree = roots.roots.map(r => `
    <div class="muted" style="cursor:default">${esc(r.root)}/</div>
    ${r.entries.map(e => `<div data-path="${esc(r.root)}/${esc(e.rel_path)}"
        style="padding-left:18px">${e.kind === "dir" ? "📁" : "·"} ${esc(e.rel_path)}</div>`).join("")}
  `).join("") || `<div class="muted">${esc(t("inv.no_roots"))}</div>`;

  const note = esc(t("inv.note", {cmd: "__CMD__", out: "__OUT__"}))
    .replace("__CMD__", '<span class="mono">python3 vigia_agent.py --evidence … --case-id …</span>')
    .replace("__OUT__", '<span class="mono">results/webui/</span>');

  app.innerHTML = `
    <div class="sec-head"><span class="n">MODE 1</span><h2>${esc(t("inv.title"))}</h2></div>
    <p class="muted">${note}</p>
    <form class="panel" id="inv-form">
      <label>${esc(t("inv.evidence"))}</label>
      <div class="evtree" id="evtree">${tree}</div>
      <input id="inv-evidence" placeholder="${esc(t("inv.evidence_ph"))}">
      <label>${esc(t("inv.case"))}</label>
      <input id="inv-case" placeholder="CASE-001" maxlength="64">
      <div class="hint mono">${esc(t("inv.case_hint"))}</div>
      <label>${esc(t("inv.examiner"))}</label><input id="inv-examiner" maxlength="128">
      <label>${esc(t("inv.acq"))}</label><input id="inv-acq" maxlength="128">
      <label>${esc(t("inv.wb"))}</label>
      <select id="inv-wb"><option value="">${esc(t("inv.wb_unspecified"))}</option>
        <option value="true">true</option><option value="false">false</option></select>
      <div style="margin-top:18px"><button type="submit">${esc(t("inv.submit"))}</button></div>
      <div id="inv-msg" style="margin-top:10px"></div>
    </form>`;

  const evInput = document.getElementById("inv-evidence");
  document.querySelectorAll("#evtree div[data-path]").forEach(d => {
    d.onclick = () => {
      document.querySelectorAll("#evtree .sel").forEach(x => x.classList.remove("sel"));
      d.classList.add("sel");
      evInput.value = d.dataset.path;
    };
  });
  const caseInput = document.getElementById("inv-case");
  caseInput.oninput = () => {
    caseInput.classList.toggle("invalid", !CASE_ID_RE.test(caseInput.value));
  };
  document.getElementById("inv-form").onsubmit = async (e) => {
    e.preventDefault();
    const msg = document.getElementById("inv-msg");
    if (!CASE_ID_RE.test(caseInput.value)) {
      msg.innerHTML = `<span class="stamp fail">${esc(t("inv.invalid_case"))}</span>`; return;
    }
    const payload = {
      evidence_path: evInput.value.trim(),
      case_id: caseInput.value.trim(),
    };
    const ex = document.getElementById("inv-examiner").value.trim();
    const acq = document.getElementById("inv-acq").value.trim();
    const wb = document.getElementById("inv-wb").value;
    if (ex) payload.examiner_id = ex;
    if (acq) payload.acquisition_tool = acq;
    if (wb) payload.write_blocker_used = wb === "true";
    msg.innerHTML = `<span class="muted">${esc(t("inv.submitting"))}</span>`;
    try {
      const r = await post("/api/investigations", payload);
      location.hash = `#/jobs/${r.job_id}`;
    } catch (err) {
      msg.innerHTML = `<span class="stamp fail">${esc(t("inv.rejected"))}</span> <span class="muted">${esc(err.message)}</span>`;
    }
  };
}

/* ---------- jobs ---------- */

async function viewJobs() {
  setNav("jobs");
  const jobs = await api("/api/investigations");
  const rows = jobs.map(j => `<tr class="rowlink" data-id="${esc(j.job_id)}">
      <td class="mono">${esc(j.job_id)}</td>
      <td>${esc(j.case_id)}</td>
      <td class="mono">${esc(j.state)}</td>
      <td>${j.exit_code !== null && j.exit_code !== undefined
            ? chip(EXIT_LABELS[j.exit_code] || String(j.exit_code)) : ""}</td>
      <td class="mono">${esc((j.created_at || "").slice(0, 19))}</td>
    </tr>`).join("");
  app.innerHTML = `
    <div class="sec-head"><span class="n">§</span><h2>${esc(t("jobs.title"))}</h2></div>
    <table><thead><tr><th>${esc(t("jobs.th_job"))}</th><th>${esc(t("jobs.th_case"))}</th>
      <th>${esc(t("jobs.th_state"))}</th><th>${esc(t("jobs.th_exit"))}</th>
      <th>${esc(t("jobs.th_created"))}</th></tr></thead>
    <tbody>${rows || `<tr><td colspan="5" class="muted">${esc(t("jobs.empty"))}</td></tr>`}</tbody></table>
    <p style="margin-top:14px"><a href="#/investigate">${esc(t("jobs.new"))}</a></p>`;
  app.querySelectorAll("tr.rowlink").forEach(tr => {
    tr.onclick = () => { location.hash = `#/jobs/${tr.dataset.id}`; };
  });
}

let jobPoll = null;

async function viewJob(id) {
  setNav("jobs");
  clearInterval(jobPoll);
  const render = async () => {
    let job;
    try { job = await api(`/api/investigations/${encodeURIComponent(id)}`); }
    catch (err) { clearInterval(jobPoll); return errorView(err); }

    const terminal = job.state === "done" || job.state === "error";
    let verdictPanel = "";
    if (terminal) {
      const exitLabel = job.exit_code !== null ? (EXIT_LABELS[job.exit_code] || "?") : "?";
      const agrees = job.verdict_from_bundle && exitLabel === job.verdict_from_bundle;
      verdictPanel = `
        ${job.verdict_from_bundle && !agrees && job.exit_code !== null
          ? `<div class="banner">${esc(t("job.disagree"))}</div>` : ""}
        <div class="cards">
          <div class="card ${KNOWN_VERDICTS.includes(exitLabel) ? exitLabel : ""}">
            <div class="src">${esc(t("job.exit_src"))}</div>
            <div class="verdict">${job.exit_code === null ? "—" : esc(job.exit_code)}</div>
            <div class="note mono">${esc(t("job.exit_label"))} ${esc(exitLabel)}</div></div>
          <div class="card ${KNOWN_VERDICTS.includes(job.verdict_from_bundle) ? job.verdict_from_bundle : ""}">
            <div class="src">${esc(t("job.bundle_src"))}</div>
            <div class="verdict">${esc(job.verdict_from_bundle || "—")}</div>
            ${job.bundle_id ? `<div class="note"><a href="#/bundle/${esc(job.bundle_id)}">${esc(t("job.open_bundle"))}</a></div>`
                            : `<div class="note muted">${esc(t("job.bundle_missing"))}</div>`}</div>
        </div>
        ${job.error ? `<div class="banner error">${esc(job.error)}</div>` : ""}`;
      clearInterval(jobPoll);
    }

    const logBox = document.getElementById("job-log");
    const prevScroll = logBox ? {top: logBox.scrollTop, atEnd:
      logBox.scrollTop + logBox.clientHeight >= logBox.scrollHeight - 8} : null;

    const log = await api(`/api/investigations/${encodeURIComponent(id)}/log?offset=0`);
    app.innerHTML = `
      <p><a href="#/jobs">${esc(t("job.back"))}</a></p>
      <div class="sec-head"><span class="n">JOB ${esc(id)}</span>
        <h2>${esc(job.case_id)}</h2>
        <span class="badge">${esc(job.state)}</span></div>
      ${verdictPanel}
      ${log.truncated ? `<p class="warnlist">${esc(t("job.truncated"))}</p>` : ""}
      <pre class="term" id="job-log">${esc(log.lines.join("\n"))}</pre>`;
    const newBox = document.getElementById("job-log");
    if (newBox) {
      if (!prevScroll || prevScroll.atEnd) newBox.scrollTop = newBox.scrollHeight;
      else newBox.scrollTop = prevScroll.top;
    }
  };
  await render();
  jobPoll = setInterval(render, 1000);
}

/* ---------- router ---------- */

async function route() {
  clearInterval(jobPoll);
  const hash = location.hash || "#/bundles";
  const parts = hash.slice(2).split("/");
  try {
    if (parts[0] === "bundles" || parts[0] === "") await viewBundles();
    else if (parts[0] === "bundle" && parts[1]) await viewBundle(parts[1], parts[2]);
    else if (parts[0] === "investigate") await viewInvestigate();
    else if (parts[0] === "jobs" && parts[1]) await viewJob(parts[1]);
    else if (parts[0] === "jobs") await viewJobs();
    else await viewBundles();
  } catch (err) {
    errorView(err);
  }
}

window.addEventListener("hashchange", route);
applyChrome();
route();
