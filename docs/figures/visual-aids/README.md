# Statistical visual aids

Generated offline from saved development summaries. No model calls.

PNG: 300 dpi. SVG: vector, editable text. Place at 6.2 inches wide to preserve 11-point labels.

Choose figures that support the narrative; the report body is limited to ten pages. Inserting figures requires a fresh report render, page-count check and visual review.

Regenerate with the report plotting environment: `python scripts/render_report_visual_aids.py`.

## controlled-accepted

[PNG](controlled-accepted.png) · [SVG](controlled-accepted.svg)

Accepted-answer rates: 240 canonical cases per method, from 120 source families. Accepted means a gold-valid schedule or correct UNSAT, not necessarily an optimum. All failures remain in denominators. Qwen3.8 rejections are provider failures, not demonstrated reasoning or wording errors. Exploratory development data.

## realistic-accepted

[PNG](realistic-accepted.png) · [SVG](realistic-accepted.svg)

Accepted-answer rates: 12 AI-assisted fictional scenarios per method; human prose/gold review pending. Accepted means a gold-valid schedule or correct UNSAT, not necessarily an optimum. All failures remain in denominators. Qwen3.8 rejections are provider failures, not demonstrated reasoning or wording errors. Exploratory development data.

## language-accepted

[PNG](language-accepted.png) · [SVG](language-accepted.svg)

Accepted-answer rates: 48 additional wording conditions per method, reusing 24 controlled bases. Accepted means a gold-valid schedule or correct UNSAT, not necessarily an optimum. All failures remain in denominators. Qwen3.8 rejections are provider failures, not demonstrated reasoning or wording errors. Exploratory development data.

## optimality

[PNG](optimality.png) · [SVG](optimality.svg)

Controlled reference-optimum matching, conditional on gold-valid SAT schedules with proven reference objectives. Labels show matches/valid schedules. Successful subsets differ across methods; compare with failure-inclusive acceptance. Qwen3.8 Direct repair matches 59/60, despite all 60 schedules being valid.

## resources

[PNG](resources.png) · [SVG](resources.svg)

Controlled mean model-call time and provider-reported total tokens. Time covers all 240 attempts per row, including failures, and excludes subsequent local solving. Token coverage: Qwen3.8 Direct 239/240; all other rows 240/240. Missing usage is unknown. Shared hosted backends/defaults were uncontrolled; these are not monetary costs or causal speed comparisons.

## outcomes

[PNG](outcomes.png) · [SVG](outcomes.svg)

Controlled outcome counts, retaining all 240 attempts in each row. Invalid output denotes parser/schema-invalid output; invalid schedule denotes a gold-constraint violation. Small segments are explicitly noted. Acceptance includes correct UNSAT and does not guarantee optimality. Qwen3.8's controlled rejection is operational, not a demonstrated reasoning failure.

## activity-count

[PNG](activity-count.png) · [SVG](activity-count.svg)

Controlled SAT generation activity-count sweep: five cases per level and method. Labels show valid/attempted. Qwen3.6 Direct declines across these levels. Qwen3.8 Direct's 4/5 at 12 activities includes one provider failure, not a demonstrated reasoning error. This selected sweep is descriptive, not a causal threshold or a claim that all difficulty dimensions have monotonic effects. Lines connect tested levels only.
