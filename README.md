# Dynamic Constraint-Aware Scheduling

**CS3263 Foundations of Artificial Intelligence · Group 23 · NUS AY2026/27 Semester 1**

A research project comparing direct language-model scheduling with language-model-to-constraint-solver scheduling. We study both generating a new schedule and repairing an existing schedule after requirements change, while minimizing unnecessary disruption.

**Status:** research plan, configuration templates, and empty directory scaffold only. Scheduling systems, benchmarks, and experiment results are not implemented yet. The four-week delivery window is **5–30 October 2026 (Week 11 completion; setup from 28 September)**. The plan also covers final review and course submission in November.

## Research questions

- When does direct LLM reasoning produce complete, feasible schedules?
- How does LLM-to-solver performance change with constraint interactions, resource contention, and available slack?
- How much error comes from translating language into constraints versus solving those constraints?
- Can either approach repair schedules with minimal changes, and remain reliable under equivalent paraphrases and constraint reorderings?

## Approaches

| Path | Input and output | Role |
| --- | --- | --- |
| Direct LLM | Natural-language problem → structured schedule or feasibility claim | Evaluated approach A |
| LLM-to-Solver | Same problem → structured specification → OR-Tools CP-SAT → schedule/status | Evaluated approach B |
| Gold-to-Solver | Human-checked specification → CP-SAT → reference status/objective | Evaluation reference; not a natural-language competitor |

Both approaches will be checked by an independent validator against the gold specification. A solver-valid answer to an incorrectly translated problem does not count as a correct answer to the original problem.

The core covers fixed-duration activities, availability, deadlines, fixed commitments, precedence, participant/resource non-overlap, preferences, and minimum-disruption repair. A small demo UI and verifier-feedback correction are stretch work. Live calendar integrations are outside project scope.

## Getting started

```bash
git clone git@github.com:JellyPenguinnn/cs3263_group23.git
cd cs3263_group23
```

1. Read [planning.md](planning.md) for scope, interfaces, ownership, experiments, and milestones.
2. Read [AGENTS.md](AGENTS.md) before changing files or using a coding agent.
3. Fetch and switch to your assigned branch from the table below. Each member should use a separate local clone.

The planned local runtime is CPU-only Python on macOS and Linux, with remote inference through SoCLaaS; portability remains to be verified during implementation. There is no install, test, or experiment command yet. Those commands will be added when their implementations exist; the planned stack is Python, OR-Tools CP-SAT, and NUS SoCLaaS through its OpenAI-compatible API.

### NUS SoCLaaS configuration

**Development uses SoCLaaS only; no frontier-model access is needed to begin implementation or development pilots.** Final evaluation model selection is a separate milestone by 18 October, before held-out experiments. The course requires a frontier-model comparison unless the teaching team accepts an alternative; SoCLaaS access alone does not establish that acceptance.

Configure access to the NUS SoCLaaS API:

```bash
cp .env.example .env
chmod 600 .env
```

Edit `.env` locally and supply your own authorized key. The file is ignored by Git. Do not paste keys into source files, commits, screenshots, issue descriptions, prompts, or logs.

For a POSIX shell, explicitly load the file before a connectivity check:

```bash
set -a
. ./.env
set +a
curl --fail --silent --show-error \
  -H "Authorization: Bearer ${SOCLAAS_API_KEY}" \
  "${SOCLAAS_BASE_URL}/models"
```

This lists models and does not run a scheduling experiment. Avoid shell tracing (`set -x`), verbose HTTP logs, and publishing raw provider responses. `SOCLAAS_MODEL=default` is a bootstrap alias; choose and record a verified development model ID before scheduling pilots. Keep development and final evaluation configurations and results separate. Available models, quotas, and advanced request features must be checked live. Environment files are not loaded automatically by this repository yet.

Connectivity verified on **28 September 2026**: authenticated model listing and one tiny chat completion succeeded; `default` returned `qwen3.6:35b`. This verifies access only, not scheduling performance or suitability for the course's frontier-model comparison. Final evaluation suitability or teaching-team approval must be established before the main experiment is frozen; this does not block SoCLaaS development.

## Team and branches

| Member | Primary responsibility | Branch |
| --- | --- | --- |
| Tea Li Hao | Direct LLM baseline, SoCLaaS adapter, setup/integration tooling, demo | `lihao-llm-baseline` |
| Tham Yao Xiang · team leader | Formal model, CP-SAT and repair, LLM-to-solver pipeline, coordination | `yaoxiang-formal-core` |
| Woo Yong Qing | Benchmark, independent validator, experiment runner, metrics | `yongqing-evaluation` |

All three members share experiment analysis, report writing, presentation, and cross-review. Detailed effort allocation and review rotation are in [planning.md](planning.md).

## Evaluation and responsible AI

We will report schedule validity, SAT/UNSAT claims, invalid outputs, formalization errors, objective quality, repair distance, language robustness, latency, and cost/accounting coverage. Feasible, optimal, infeasible, invalid, and unknown outcomes remain distinct.

Development begins with synthetic scenarios. We will examine privacy of routines, unequal inconvenience across participants, faithful explanations, and the consequences of objective choices. Hard requirements cannot be silently relaxed. Individual contributions and AI assistance will be recorded honestly.

## Repository contents

- `README.md` — project overview and entry points.
- `planning.md` — working plan, interface contract, experiment matrix, rubric evidence checklist, portability requirements, and submission schedule.
- `AGENTS.md` — contributor and coding-agent instructions.
- `.env.example` — configuration names without credentials.
- `.gitignore` — local secrets, environments, generated artifacts, and caches.

The directory backbone is ready for work on the assigned branches:

```text
.github/workflows/        # future offline CI
src/scheduling/
  providers/              # model access and response accounting
  pipelines/              # direct and solver-augmented paths
prompts/
  direct/
  extraction/
configs/
  development/            # SoCLaaS development settings
  experiments/            # frozen evaluation settings
benchmarks/
  fixtures/               # small reviewed synthetic cases
  manifests/              # split, seed, and provenance records
evaluation/               # experiment orchestration and analysis
tests/
  unit/
  integration/
results/summary/          # reviewed aggregate tables
report/figures/           # report sources and selected figures
presentation/             # slides and demo materials
```

These folders contain only empty `.gitkeep` placeholders. No Python modules, package manifest, CI workflow, tests, prompts, or experiment configurations are implemented yet. Planned module paths and ownership are in [planning.md](planning.md#4-team-responsibilities-and-workload). Ignored runtime folders such as `runs/`, `artifacts/`, and `data/private/` are created locally when needed; they are not part of the tracked scaffold.

## References

- [SCHEDBench](https://arxiv.org/abs/2608.00991), Sharma and Sharma, 2026.
- [NATURAL PLAN](https://arxiv.org/abs/2406.04520), Zheng et al., 2024.
- [Large Language Models Can Solve Real-World Planning Rigorously with Formal Verification Tools](https://aclanthology.org/2025.naacl-long.176/), Hao et al., NAACL 2025.
- [OR-Tools CP-SAT documentation](https://developers.google.com/optimization/cp/cp_solver).
- [NUS SoCLaaS documentation](https://dochub.comp.nus.edu.sg/cf/guides/soclaas/start) — institutional access may be required.

Project scope follows the Group 23 proposal and CS3263 project guidelines. A distribution license has not yet been selected.
