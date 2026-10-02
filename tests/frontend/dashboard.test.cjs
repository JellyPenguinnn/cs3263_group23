const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

// Exercise request ordering and recovery without a browser or network.
async function dashboard() {
  const elements = new Map();
  const element = (id) => {
    if (!elements.has(id))
      elements.set(id, {
        innerHTML: "",
        textContent: "",
        value: "",
        hidden: false,
        open: false,
        showModal() { this.open = true; },
        close() { this.open = false; },
        replaceChildren() {
          this.innerHTML = "";
        },
      });
    return elements.get(id);
  };
  const data = {
    revision: "unchanged",
    active: false,
    activity: [],
    slices: [],
    progress: {
      completed: 0,
      planned: 0,
      pending_attempt_ids: [],
      not_started: 0,
      evidence: "offline",
    },
    summary: { subsets: [], paired: [] },
    manifest: {
      created_utc: "2026-09-29T00:00:00Z",
      contract: {
        config: {
          model: { model: "synthetic" },
          max_requests: 0,
          max_requested_output_tokens: 0,
          solver: { time_limit_seconds: 1, num_workers: 1, random_seed: 0 },
        },
      },
    },
  };
  const reply = (body) => ({ ok: true, json: async () => body });
  const pending = [];
  const details = [];
  let failRun = false;
  const context = vm.createContext({
    document: { querySelector: element, querySelectorAll: () => [] },
    URLSearchParams,
    setInterval: () => {},
    clearTimeout,
    setTimeout,
    fetch: async (url) => {
      if (url === "/api/session")
        return reply({
          runs: [{ id: "run", name: "Test run" }],
          selected: "run",
        });
      if (url.startsWith("/api/cases?"))
        return new Promise((resolve, reject) =>
          pending.push({ resolve: (body) => resolve(reply(body)), reject }),
        );
      if (url.startsWith("/api/case?"))
        return new Promise((resolve, reject) =>
          details.push({ resolve: (body) => resolve(reply(body)), reject }),
        );
      if (failRun) throw new Error("Temporarily unavailable");
      return reply(data);
    },
  });
  await vm.runInContext(
    readFileSync(
      resolve(__dirname, "../../src/scheduling/dashboard/static/app.js"),
      "utf8",
    ),
    context,
  );
  return {
    element,
    pending,
    details,
    fail: (value) => {
      failRun = value;
    },
    call: (script) => vm.runInContext(script, context),
  };
}

function cases(name) {
  return {
    total: 1,
    items: [
      {
        id: 0,
        case_id: name,
        sweep: "tiny",
        task_type: "generation",
        activity_count: 1,
        rows: {},
      },
    ],
  };
}

test("refresh restores the same revision after a temporary failure", async () => {
  const ui = await dashboard();
  const original = ui.element("#monitor-content").innerHTML;
  ui.fail(true);
  await ui.call("refresh()");
  assert.match(ui.element("#monitor-content").innerHTML, /unavailable/);
  assert.match(ui.element("#sync-label").textContent, /Update failed/);
  ui.fail(false);
  await ui.call("refresh()");
  assert.equal(ui.element("#monitor-content").innerHTML, original);
  assert.equal(ui.element("#notice").hidden, true);
  assert.equal(ui.element("#evidence-label").textContent, "offline");
});

test("an older filter response cannot replace the current results", async () => {
  const ui = await dashboard();
  const older = ui.call("loadCases()");
  const newer = ui.call("loadCases()");
  ui.pending[1].resolve(cases("current-case"));
  await newer;
  ui.pending[0].resolve(cases("stale-case"));
  await older;
  assert.match(ui.element("#case-rows").innerHTML, /current-case/);
  assert.doesNotMatch(ui.element("#case-rows").innerHTML, /stale-case/);
});

test("an obsolete filter failure does not report an error for current results", async () => {
  const ui = await dashboard();
  const older = ui.call("loadCases()");
  const newer = ui.call("loadCases()");
  ui.pending[1].resolve(cases("current-case"));
  await newer;
  ui.pending[0].reject(new Error("Obsolete request failed"));
  await older;
  assert.equal(ui.element("#notice").textContent, "");
  assert.match(ui.element("#case-rows").innerHTML, /current-case/);
});


test("invalid large slots stay inspectable without calendar conversion errors", async () => {
  const ui = await dashboard();
  const c = {problem: {horizon_slots: 4, slot_minutes: 30,
    horizon_start: "2026-10-05T09:00:00+08:00", timezone: "+08:00",
    activities: [{id: "A", duration_slots: 1}]}};
  for (const start of [5, 1e30]) {
    const html = ui.call(`schedule(${JSON.stringify(c)}, [{activity_id: "A", start_slot: ${start}}], true)`);
    assert.ok(html.includes(start > Number.MAX_SAFE_INTEGER ? "Outside supported range" : `slot ${start} (outside horizon)`));
    assert.doesNotMatch(html, /Invalid Date|NaN/);
    assert.match(html, /invalid/);
  }
});

function detail(name) {
  return {case: {case_id: name}, responses: {}, rows: [], reference: null};
}

test("older case details cannot overwrite a newer selection", async () => {
  const ui = await dashboard();
  const older = ui.call("showDetail(0)");
  const newer = ui.call("showDetail(1)");
  ui.details[1].resolve(detail("current-case"));
  await newer;
  ui.details[0].resolve(detail("stale-case"));
  await older;
  assert.equal(ui.element("#detail-title").textContent, "current-case");
});

test("obsolete detail errors do not obscure the current case", async () => {
  const ui = await dashboard();
  const older = ui.call("showDetail(0)");
  const newer = ui.call("showDetail(1)");
  ui.details[1].resolve(detail("current-case"));
  await newer;
  ui.details[0].reject(new Error("Obsolete detail error"));
  await older;
  assert.equal(ui.element("#notice").textContent, "");
});

test("dismissed or switched-context requests cannot reopen case details", async () => {
  for (const action of [
    "document.querySelector('#close-detail').onclick()",
    "document.querySelector('#case-dialog').oncancel()",
    "runId = 'different-run'",
    "slice = ['controlled', 'paraphrase', 0]",
  ]) {
    const ui = await dashboard();
    const pending = ui.call("showDetail(0)");
    ui.call(action);
    ui.details[0].resolve(detail("stale-case"));
    await pending;
    assert.equal(ui.element("#case-dialog").open, false, action);
    assert.equal(ui.element("#detail-title").textContent, "", action);
  }
});

test("monitor distinguishes confirmed liveness, stale locks and unknown legacy activity", async () => {
  const ui = await dashboard();
  ui.call('run.progress = {completed:1, planned:2, pending_attempt_ids:["pending"], not_started:0}; run.active=true; run.liveness="active"; renderMonitor()');
  assert.match(ui.element("#monitor-content").innerHTML, />running</);
  ui.call('run.active=false; run.liveness="inactive"; renderMonitor()');
  assert.match(ui.element("#monitor-content").innerHTML, />incomplete</);
  assert.doesNotMatch(ui.element("#monitor-content").innerHTML, />running</);
  assert.match(ui.element("#monitor-content").innerHTML, /Requires reconciliation/);
  ui.call('run.liveness="unknown_legacy"; renderMonitor()');
  assert.match(ui.element("#monitor-content").innerHTML, />activity unknown</);
  assert.match(ui.element("#monitor-content").innerHTML, /check the original runner/);
  assert.match(ui.call('outcome({category:"interrupted_or_uncertain"})'), /pending \/ uncertain/);
});

test("shared-service runs disclose their evidence scope without changing strict run labels", async () => {
  const ui = await dashboard();
  ui.call('run.progress.evidence="live_development"; run.manifest.contract.config.qualification_policy="strict_model_observe_backend_v1"');
  await ui.call("refresh()");
  assert.match(ui.element("#evidence-label").textContent, /Shared-service development/);
  ui.call('run.manifest.contract.config.qualification_policy="strict_model_backend_v1"');
  await ui.call("refresh()");
  assert.doesNotMatch(ui.element("#evidence-label").textContent, /Shared-service/);
});
