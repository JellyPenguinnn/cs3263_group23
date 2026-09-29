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
