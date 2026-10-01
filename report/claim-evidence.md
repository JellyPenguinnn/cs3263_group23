# Report claim-to-evidence index

Applies to [study-draft.md](study-draft.md), updated 1 October 2026. All human reviews
below are pending. File/record links establish traceability, not sign-off.
Development run: `expanded-development-100-20260930-01`; configuration:
[expanded-development-100.json](../configs/development/expanded-development-100.json).
Reproduction uses the existing `scheduling evaluate-replay --run-dir ...` command;
raw run files require the separately supplied reviewed archive.

| ID | Claim and scope | Source / exact locator | Reviewer / limitation |
| --- | --- | --- | --- |
| C1 | Standalone solver proof binds to exact spec/context | [explanation tests](../tests/unit/test_explanations.py), `test_bound_result_cannot_transfer_optimality_to_weaker_same_id_spec` and repair-context regression | Yao Xiang, pending; correspondence is not authenticity |
| C2 | Coupled tiny repair has only A1/B2/C0 and objective (3,4,0) | [formal qualification](../tests/unit/test_formal_qualification.py), `test_coupled_repair_requires_moving_unaffected_activities` | Yao Xiang/Yong Qing, pending; exhaustive tiny case, not population evidence |
| C3 | Expanded design: 100 cases / 41 families, 25 per task/label stratum | [selection manifest](../benchmarks/manifests/expanded-development-100-20260930.json), `case_count`, `source_family_count`, `counts` | Yong Qing, pending; known procedural development |
| C4 | Development task/label table in Section 6 | [aggregate](../results/summary/expanded-development-100-20260930.json), `summary.subsets` filtered by approach/task, `accepted_answer`, `sat_validity`, `unsat_accuracy` | Yong Qing, pending; 50 cases/task, 25 per label; canonical repeat 0 only |
| C5 | Two omitted appointments plus malformed JSON; eight of ten mismatches equivalent | [failure analysis](expanded-development-100.md), [semantic certificate](../results/summary/expanded-development-100-semantics-20260930.json), [saved-failure regressions](../tests/integration/test_expanded_extraction_failures.py), [automated F1 review](yaoxiang-f1-review.md) | Yao Xiang human review pending; automated checks passed; preserve structural metric and all original responses |
| C6 | Tokens, coverage and conditional timing | [resource receipt](../results/summary/expanded-development-100-resources-20260930.json), `overall_resources`, `by_approach`, `execution` | Li Hao/Yong Qing, pending; 200 model calls / 99 solves; currency unavailable |
| C7 | Concentrated participant inconvenience | [recorded case discussion](lihao-development-followup.md#four-responsible-ai-cases-for-team-discussion), run `main-baseline-20260929-01`, case `dev-3263-interaction_density-1-repair`, B | All, pending; historical development case; no proof of an avoidable inequity |
| C8 | One move/four slots wins over two moves/two slots | [formal qualification](../tests/unit/test_formal_qualification.py), `test_movement_priority_beats_smaller_total_shift` | Yao Xiang, pending; tiny mathematical counterexample |
| C9 | Instruction-like text remains public data in prompt construction | [direct tests](../tests/unit/test_direct.py), `test_repair_prompt_preserves_original_and_priority` | Li Hao, pending; no live adversarial-resistance claim |
| C10 | Reference serving fingerprint varied in bounded identity diagnostic | [Diagnostic receipt](../configs/development/lihao-f2-diagnostic-20261001.json), `summary.models`, [handoff](lihao-f2-followup.md) | Li Hao/Yao Xiang, pending; three calls per model, not a scheduling comparison or proof of weights |
| C11 | F3–F5 controls implemented and offline-verified | [Preparation receipt](../configs/development/yongqing-f345-verification-20261001.json), [handoff](yongqing-study-preparation.md) | All, pending; canned outputs and automated portability checks only |
| C12 | Candidate-pilot witness/contradiction and bounded optimum cross-check | [Formal review](yaoxiang-f3-formal-review.md), [receipt](../configs/development/yaoxiang-f3-formal-review-20261001.json), [regressions](../tests/integration/test_candidate_formal_review.py) | Yao Xiang/Yong Qing human review pending; 48 cases / 24 families, only six optima independently enumerated |

Engineering follow-up (1 October): [F3–F5 receipt](../configs/development/yongqing-f345-verification-20261001.json) and [handoff](yongqing-study-preparation.md) link the 24-family construction pilot, 16-attempt synthetic frozen rehearsal, exact cross-platform archive replay and 332 unchanged historical attempts. These support construction/bookkeeping/reproducibility claims only. The synthetic 15/16 accepted outputs are deliberately canned and must never become a model-performance result. Actual source-policy, gold/text and independent teammate reviews remain pending.

Archive follow-up (1 October): [F5 export integrity](yongqing-archive-review.md) and
[receipt](../configs/development/yongqing-archive-verification-20261001.json) record
623 passing tests on both platforms and exact analysis replay from the corrected
archive in network-disabled Linux. This is automated reproduction evidence, not
human sign-off, final data or model-performance evidence.

Final-study canonical/difficulty, realistic, wording, repair and resource claims
remain absent until F4/F5 provides compatible frozen blocks. Their eventual index
must include block/run/config hashes, subsets and denominators, figure/table
commands, exclusions and actual independent review/replay receipts. Do not attach
development counts to an empty final-results table.
