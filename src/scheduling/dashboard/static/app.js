"use strict";
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const esc = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const pretty = (v) => JSON.stringify(v, null, 2);
const human = (v) => String(v ?? "").replaceAll("_", " ");
const num = (v) =>
  v == null
    ? "—"
    : Number(v).toLocaleString(undefined, { maximumFractionDigits: 1 });
const pct = (r) => (r?.rate == null ? "—" : `${num(r.rate * 100)}%`);
const fraction = (r) => (r ? `${r.numerator} / ${r.denominator}` : "—");
const categoryLabel = (value) =>
  ({
    gold_invalid_schedule: "Constraint violations",
    invalid_output: "Invalid response format",
    false_unsat: "Incorrect infeasibility claim",
    provider_error: "Provider error",
    solver_limit: "Solver limit reached",
    model_unknown: "Model could not decide",
    unresolved_reference: "Unresolved reference",
    interrupted_or_uncertain: "Interrupted / uncertain",
  })[value] || human(value);
const names = { direct: "Direct LLM", solver_augmented: "LLM + CP-SAT" };
let session,
  runId = null,
  run = null,
  page = "monitor",
  offset = 0;
let slice = ["controlled", "canonical", 0],
  refreshing = false,
  refreshError = false,
  caseRequest = 0,
  detailRequest = 0;
function notice(message, type = "") {
  $("#notice").textContent = message;
  $("#notice").className = `notice ${type}`;
  $("#notice").hidden = !message;
}
async function api(path) {
  const response = await fetch(path);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function status(value) {
  let label = human(value),
    cls = "neutral";
  if (["accepted", "OPTIMAL", "SAT", "completed"].includes(value)) cls = "good";
  if (
    [
      "rejected",
      "INVALID_OUTPUT",
      "ERROR",
      "failed",
      "stopped_provider",
    ].includes(value)
  )
    cls = "bad";
  if (
    [
      "UNKNOWN",
      "UNRESOLVED",
      "pending",
      "running",
      "starting",
      "stopped_by_user",
    ].includes(value)
  )
    cls = "warn";
  return `<span class="status ${cls}">${esc(label)}</span>`;
}
function outcome(row) {
  if (!row) return status("not started");
  if (row.category === "interrupted_or_uncertain")
    return status(run?.active ? "pending" : "interrupted");
  if (row.accepted == null) return status("UNRESOLVED");
  return status(row.accepted ? "accepted" : "rejected");
}
function objectives(obj) {
  if (!obj) return "";
  return `<div class="objective-row">${[
    ["moved_count", "Activities moved"],
    ["total_shift_slots", "Shift · slots"],
    ["preference_penalty", "Preference penalty"],
  ]
    .filter(([k]) => obj[k] != null)
    .map(
      ([k, l]) => `<div><strong>${num(obj[k])}</strong><span>${l}</span></div>`,
    )
    .join("")}</div>`;
}
function schedule(
  c,
  entries,
  invalid = false,
  original = false,
  approach = "reference",
) {
  if (!entries) return '<p class="comparison-note">No schedule returned.</p>';
  const p = c.problem,
    horizon = p.horizon_slots;
  const clock = (slot) => {
    // JSON numbers outside the safe range cannot preserve the model's exact slot.
    if (!Number.isFinite(slot) || Math.abs(slot) > Number.MAX_SAFE_INTEGER)
      return "Outside supported range · see raw response";
    if (slot < 0 || slot > horizon) return `slot ${slot} (outside horizon)`;
    const d = new Date(
      Date.parse(p.horizon_start) + slot * p.slot_minutes * 60000,
    );
    const offset = p.horizon_start.match(/([+-]\d\d:\d\d|Z)$/)?.[0] || "Z";
    const mins =
      offset === "Z"
        ? 0
        : (offset[0] === "-" ? -1 : 1) *
          (Number(offset.slice(1, 3)) * 60 + Number(offset.slice(4)));
    return new Date(d.getTime() + mins * 60000).toISOString().slice(11, 16);
  };
  const old = Object.fromEntries(
    (c.original_schedule || []).map((x) => [x.activity_id, x.start_slot]),
  );
  const rows = entries.map((e) => {
    const a = p.activities.find((x) => x.id === e.activity_id);
    return { ...e, duration: a?.duration_slots ?? 0, known: !!a };
  });
  return `<div class="timeline">${rows.map((e) => `<div class="timeline-row"><span>${esc(e.activity_id)}</span><div class="timeline-track"><div class="timeline-bar ${esc(approach)} ${invalid ? "invalid" : ""}" style="left:${Math.max(0, Math.min(100, (e.start_slot / horizon) * 100))}%;width:${Math.max(0, Math.min(100 - (e.start_slot / horizon) * 100, (e.duration / horizon) * 100))}%" title="${esc(e.activity_id)}: ${clock(e.start_slot)}–${clock(e.start_slot + e.duration)}"></div></div></div>`).join("")}<div class="timeline-axis"><span>${clock(0)}</span><span>${clock(horizon / 2)}</span><span>${clock(horizon)}</span></div></div><p class="muted">${esc(p.horizon_start.slice(0, 10))} · ${esc(p.timezone)} · ${p.slot_minutes}-minute slots</p><div class="table-scroll"><table class="schedule-list"><thead><tr><th>Activity</th><th>Start → end</th>${c.original_schedule && !original ? "<th>Change</th>" : ""}</tr></thead><tbody>${rows.map((e) => `<tr><td>${esc(e.activity_id)}</td><td title="Slots [${e.start_slot}, ${e.start_slot + e.duration})">${clock(e.start_slot)} → ${clock(e.start_slot + e.duration)}</td>${c.original_schedule && !original ? `<td>${old[e.activity_id] == null ? "—" : e.start_slot === old[e.activity_id] ? "Unchanged" : `${e.start_slot - old[e.activity_id] > 0 ? "+" : ""}${e.start_slot - old[e.activity_id]} ${Math.abs(e.start_slot - old[e.activity_id]) === 1 ? "slot" : "slots"}`}</td>` : ""}</tr>`).join("")}</tbody></table></div>`;
}
function switchPage(target) {
  page = target;
  $$(".page").forEach((e) => (e.hidden = e.id !== page));
  $$(".nav").forEach((e) => {
    e.classList.toggle("active", e.dataset.page === page);
    if (e.dataset.page === page) e.setAttribute("aria-current", "page");
    else e.removeAttribute("aria-current");
  });
  if (page === "cases" && run) loadCases();
  refresh();
}
$$(".nav").forEach((b) => (b.onclick = () => switchPage(b.dataset.page)));
async function loadSession() {
  session = await api("/api/session");
  const options = session.runs
    .map((r) => `<option value="${r.id}">${esc(r.name)}</option>`)
    .join("");
  const nextOptions = options || '<option value="">No saved runs</option>';
  if ($("#run-select").innerHTML !== nextOptions)
    $("#run-select").innerHTML = nextOptions;
  if (!runId) runId = session.selected || session.runs[0]?.id || null;
  $("#run-select").value = runId || "";
}
$("#run-select").onchange = async (e) => {
  runId = e.target.value;
  closeDetail();
  run = null;
  offset = 0;
  caseRequest++;
  $("#monitor-content").textContent = "Loading run…";
  $("#results-content").textContent = "Loading results…";
  $("#case-rows").replaceChildren();
  await refresh();
};
$("#refresh").onclick = () => refresh();
function kpi(label, value, foot) {
  return `<div class="card kpi"><div class="label">${label}</div><div class="value">${value}</div><div class="foot">${foot}</div></div>`;
}
function renderMonitor() {
  const p = run.progress,
    c = run.manifest.contract,
    cfg = c.config;
  const state = run.active
    ? "active / interrupted"
    : p.completed === p.planned
      ? "completed"
      : "incomplete";
  const totals = run.summary.subsets.reduce(
    (a, s) => {
      const t = s.tokens.total_tokens;
      a.sum += t.reported_sum || 0;
      a.reported += t.reported_attempts;
      a.calls += t.all_provider_attempts;
      return a;
    },
    { sum: 0, reported: 0, calls: 0 },
  );
  $("#monitor-content").innerHTML =
    `<div class="kpis">${kpi("Completed", `${p.completed}<span class="muted"> / ${p.planned}</span>`, "Includes rejected answers")}${kpi("Pending / uncertain", p.pending_attempt_ids.length, p.pending_attempt_ids.length ? (run.active ? "Requests reserved; awaiting results" : "Requires reconciliation before resume") : "No pending requests")}${kpi("Not started", p.not_started, "No request sent")}${kpi("Reported tokens", totals.reported ? num(totals.sum) : "—", `Usage available: ${totals.reported} / ${totals.calls}`)}</div><section class="card"><div class="progress-head"><h2>Progress</h2>${status(state)}</div><div class="progress-track" role="progressbar" aria-label="Completed attempts" aria-valuemin="0" aria-valuemax="${p.planned}" aria-valuenow="${p.completed}"><div class="progress-fill" style="width:${p.planned ? (100 * p.completed) / p.planned : 0}%"></div></div><div class="progress-meta"><span>${p.completed} of ${p.planned} attempts complete</span><span>Sequential · no retries</span></div></section><section class="card"><div class="card-heading"><h2>Latest activity</h2></div><div class="table-scroll"><table><thead><tr><th>Case</th><th>Approach</th><th>Result</th><th>Started · UTC</th></tr></thead><tbody>${run.activity.map((a) => `<tr><td>${esc(a.case_id)}</td><td>${names[a.approach]}</td><td>${a.state !== "completed" ? status("pending / uncertain") : outcome(a)}</td><td class="muted">${esc(a.started_utc ? a.started_utc.slice(11, 19) : "—")}</td></tr>`).join("") || '<tr><td colspan="4">No requests reserved yet.</td></tr>'}</tbody></table></div></section><section class="card"><h2>Run details</h2><dl class="facts"><dt>Model requested</dt><dd>${esc(cfg.model.model)}</dd><dt>Started</dt><dd>${esc(run.manifest.created_utc.replace("T", " ").slice(0, 19))} UTC</dd><dt>Budget</dt><dd>${cfg.max_requests} requests · ${num(cfg.max_requested_output_tokens)} requested output tokens · input tokens additional</dd><dt>Solver</dt><dd>${cfg.solver.time_limit_seconds}s / case · ${cfg.solver.num_workers} worker(s) · seed ${cfg.solver.random_seed}</dd></dl><details><summary>Configuration & provenance</summary><pre class="raw">${esc(pretty(run.manifest))}</pre></details></section>`;
}
function sliceControls() {
  const slices = run.slices.length
    ? run.slices
    : [["controlled", "canonical", 0]];
  if (!slices.some((s) => pretty(s) === pretty(slice))) slice = slices[0];
  $$(".slice-toolbar").forEach((el) => {
    if (slices.length === 1) {
      el.innerHTML = `<span class="muted">Subset: ${esc(human(slice[0]))} · ${esc(slice[1])} · repeat ${slice[2] + 1}</span>`;
      return;
    }
    el.innerHTML = `<label>Comparison subset<select class="slice-select">${slices.map((s) => `<option value="${esc(JSON.stringify(s))}" ${pretty(s) === pretty(slice) ? "selected" : ""}>${esc(human(s[0]))} · ${esc(s[1])} · repeat ${s[2] + 1}</option>`).join("")}</select></label>`;
    el.querySelector("select").onchange = (e) => {
      slice = JSON.parse(e.target.value);
      closeDetail();
      offset = 0;
      sliceControls();
      renderResults();
      loadCases();
    };
  });
}
function matches(s) {
  return (
    s.kind === slice[0] && s.variant_id === slice[1] && s.repeat === slice[2]
  );
}
function renderResults() {
  const subsets = run.summary.subsets.filter((s) => matches(s.subset));
  const comparison = run.summary.paired.filter((s) =>
    matches({
      kind: s.subset[0],
      variant_id: s.subset[2],
      repeat: s.subset[3],
    }),
  );
  if (!subsets.length) {
    $("#results-content").innerHTML =
      '<div class="card empty"><h2>No completed results yet</h2><p>Results appear after independent validation.</p></div>';
    return;
  }
  const cards = ["generation", "repair"]
    .map((task) => {
      const parts = ["direct", "solver_augmented"].map((a) =>
        subsets.find(
          (s) => s.subset.task_type === task && s.subset.approach === a,
        ),
      );
      const pair = comparison.find((s) => s.subset[1] === task);
      return `<section class="card"><div class="card-heading"><h2>${task === "repair" ? "Repair" : "Generation"}</h2><span class="tag">Accepted answers</span></div>${parts.map((s, i) => `<div class="bar-item"><div class="bar-label"><span><i class="key ${i ? "b" : "a"}"></i>${names[i ? "solver_augmented" : "direct"]}</span><span><strong>${pct(s?.accepted_answer)}</strong> <span class="muted">${fraction(s?.accepted_answer)}</span></span></div><div class="track"><div class="bar ${i ? "b" : "a"}" style="width:${100 * (s?.accepted_answer?.rate || 0)}%"></div></div></div>`).join("")}<table class="metric-table"><thead><tr><th>Gold checks</th><th>Direct</th><th>Solver</th></tr></thead><tbody>${[
        ["sat_validity", "Valid on feasible cases"],
        ["unsat_accuracy", "Correct infeasibility"],
      ]
        .map(
          ([k, l]) =>
            `<tr><td>${l}</td>${parts.map((s) => `<td>${fraction(s?.[k])}</td>`).join("")}</tr>`,
        )
        .join(
          "",
        )}</tbody></table><p class="comparison-note">${pair ? `Solver − direct: <strong>${num(pair.B_minus_A_percentage_points)} pp</strong> · ${pair.pair_count} pairs${pair.cluster_bootstrap_95 ? ` · 95% interval [${num(pair.cluster_bootstrap_95[0])}, ${num(pair.cluster_bootstrap_95[1])}] pp` : " · descriptive (small sample)"}${pair.incomplete_pairs ? ` · ${pair.incomplete_pairs} incomplete` : ""}${pair.unresolved_pairs ? ` · ${pair.unresolved_pairs} unresolved` : ""}.` : "No complete pairs yet."}</p></section>`;
    })
    .join("");
  const failureKeys = [
    ...new Set(subsets.flatMap((s) => Object.keys(s.category_counts))),
  ].filter((x) => x !== "accepted");
  $("#results-content").innerHTML =
    `<div class="compare-grid">${cards}</div><section class="card"><div class="card-heading"><h2>Failures & unresolved answers</h2></div><table class="metric-table"><thead><tr><th>Outcome</th><th>Direct</th><th>Solver</th></tr></thead><tbody>${failureKeys.length ? failureKeys.map((k) => `<tr><td>${esc(categoryLabel(k))}</td>${["direct", "solver_augmented"].map((a) => `<td>${subsets.filter((s) => s.subset.approach === a).reduce((n, s) => n + (s.category_counts[k] || 0), 0)}</td>`).join("")}</tr>`).join("") : '<tr><td colspan="3">No rejected answers in completed records.</td></tr>'}</tbody></table><details><summary>How to read these results</summary><p class="comparison-note">Accepted means a schedule passes all gold constraints, or correctly reports infeasibility. Chart fractions show accepted / evaluated cases; unresolved references are excluded from rates. ${run.active ? "Pending requests are excluded until completion. " : ""}Paired differences compare the same cases in percentage points (pp), with a 95% cluster-bootstrap interval when available. Subsets are reported separately. Development runs do not establish held-out performance.</p></details></section>`;
}
function query(extra = {}) {
  return new URLSearchParams({
    run: runId,
    kind: slice[0],
    variant: slice[1],
    repeat: slice[2],
    ...extra,
  });
}
async function loadCases() {
  if (!runId) return;
  const id = runId,
    request = ++caseRequest;
  try {
    const data = await api(
      "/api/cases?" +
        query({
          q: $("#search").value,
          task: $("#filter-task").value,
          outcome: $("#filter-outcome").value,
          offset,
        }),
    );
    if (id !== runId || request !== caseRequest) return;
    $("#case-rows").innerHTML =
      data.items
        .map(
          (c) =>
            `<tr><td><button class="case-link" data-detail="${c.id}">${esc(c.case_id)}</button><div class="case-sweep">${esc(human(c.sweep))}</div></td><td>${esc(c.task_type)}</td><td>${c.activity_count}</td><td>${outcome(c.rows.direct)}</td><td>${outcome(c.rows.solver_augmented)}</td></tr>`,
        )
        .join("") ||
      '<tr><td colspan="5">No cases match these filters.</td></tr>';
    $("#case-count").textContent = data.total
      ? `${offset + 1}–${Math.min(offset + 20, data.total)} of ${data.total} cases`
      : "0 cases";
    $("#previous").disabled = offset === 0;
    $("#next").disabled = offset + 20 >= data.total;
  } catch (e) {
    if (id !== runId || request !== caseRequest) return;
    notice(e.message, "error");
  }
}
for (const id of ["filter-task", "filter-outcome"])
  $("#" + id).onchange = () => {
    offset = 0;
    loadCases();
  };
let searchTimer;
$("#search").oninput = () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    offset = 0;
    loadCases();
  }, 200);
};
$("#previous").onclick = () => {
  offset = Math.max(0, offset - 20);
  loadCases();
};
$("#next").onclick = () => {
  offset += 20;
  loadCases();
};
$("#case-rows").onclick = (e) => {
  const b = e.target.closest("[data-detail]");
  if (b) showDetail(Number(b.dataset.detail));
};
async function showDetail(id) {
  const request = ++detailRequest,
    selection = query({ id }).toString();
  const current = () => request === detailRequest && selection === query({ id }).toString();
  try {
    const data = await api("/api/case?" + selection);
    if (!current()) return;
    const c = data.case;
    $("#detail-title").textContent = c.case_id;
    $("#detail-content").innerHTML = `<div class="detail-grid">${[
      "direct",
      "solver_augmented",
    ]
      .map((a) => {
        const payload = data.responses[a],
          row = data.rows.find((r) => r.approach === a),
          r = payload?.pipeline_result;
        return `<section class="card"><div class="card-heading"><h2><i class="key ${a === "direct" ? "a" : "b"}"></i>${names[a]}</h2>${outcome(row)}</div>${r ? `<p class="muted">Model: ${esc(row.returned_model || "Unavailable")} · Pipeline: ${esc(row.pipeline_status)}${row.solver_status ? ` · Solver: ${esc(row.solver_status)}` : ""}</p>${schedule(c, r.schedule, row.accepted === false, false, a)}${objectives(row.validation?.objectives)}${(row.validation?.violations || []).map((v) => `<div class="violation">${esc(v.message || human(v.category))}<br><span class="muted">${esc((v.activity_ids || []).join(", "))}</span></div>`).join("")}${row.accepted === false && (!row.validation?.violations?.length || r.diagnostics?.length) ? `<p class="violation">${esc(categoryLabel(row.category))}${r.diagnostics?.length ? `: ${esc(r.diagnostics.join("; "))}` : ""}</p>` : ""}${a === "solver_augmented" ? `<p class="comparison-note">Extraction: ${row.extraction_comparison ? (row.extraction_comparison.structurally_equivalent ? "structurally matches gold" : "differs from gold") : "not comparable"}.</p>` : ""}<details><summary>Response & diagnostics</summary>${a === "solver_augmented" ? '<p class="comparison-note">Structural agreement does not establish semantic fidelity. Solver status applies to the extracted model.</p>' : ""}<pre class="raw">${esc(r.model_response?.content || "No model response")}</pre><pre class="raw">${esc(pretty(row))}</pre></details>` : '<p class="comparison-note">No completed response for this approach.</p>'}</section>`;
      })
      .join(
        "",
      )}<section class="card full"><h2>Problem & reference</h2>${c.event ? `<p class="comparison-note">Change: ${esc(c.event)}</p>` : ""}${c.original_schedule ? `<details><summary>Original schedule</summary>${schedule(c, c.original_schedule, false, true)}</details>` : ""}<details><summary>Gold reference · ${esc(data.reference?.status || "not yet available")}</summary>${schedule(c, data.reference?.schedule)}${objectives(data.reference?.objectives)}<p class="muted">${data.reference?.optimality_proven ? "Optimum proven" : "Optimality not proven"}</p></details><details><summary>Source problem and constraints</summary><pre class="raw">${esc(pretty(c))}</pre></details></section></div>`;
    if (!$("#case-dialog").open) $("#case-dialog").showModal();
  } catch (e) {
    if (current()) notice(e.message, "error");
  }
}
function closeDetail() {
  detailRequest++;
  $("#case-dialog").close();
}
$("#close-detail").onclick = closeDetail;
$("#case-dialog").oncancel = () => { detailRequest++; };
async function refresh() {
  if (refreshing) return;
  refreshing = true;
  try {
    await loadSession();
    if (!runId) {
      const message =
        '<div class="card empty"><h2>No saved runs yet</h2><p>Start a run from the terminal under the configured runs directory. It will appear here automatically.</p></div>';
      $("#monitor-content").innerHTML = message;
      $("#results-content").innerHTML = message;
      $("#case-rows").innerHTML =
        '<tr><td colspan="5">No saved runs.</td></tr>';
      return;
    }
    const id = runId;
    const data = await api("/api/run?" + query());
    if (id !== runId) return;
    const changed = refreshError || run?.revision !== data.revision;
    run = data;
    $("#evidence-label").textContent = human(run.progress.evidence);
    if (refreshError) {
      notice("");
      refreshError = false;
    }
    if (changed) {
      renderMonitor();
      sliceControls();
      renderResults();
      if (page === "cases") await loadCases();
    }
    $("#sync-label").textContent =
      `Updated ${new Date().toLocaleTimeString()} · every 3s`;
  } catch (e) {
    refreshError = true;
    $("#sync-label").textContent = "Update failed · retrying";
    notice(e.message, "error");
    $("#monitor-content").innerHTML =
      '<div class="card">Run data is temporarily unavailable.</div>';
    $("#results-content").innerHTML =
      '<div class="card">Results unavailable until records pass verification.</div>';
    $("#case-rows").replaceChildren();
  } finally {
    refreshing = false;
  }
}
(async () => {
  await refresh();
  setInterval(() => {
    if (!document.hidden) refresh();
  }, 3000);
})();
