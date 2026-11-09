# Video rehearsal guide

The presentation is a recorded video of **at most 10 minutes**. The [deck](CS3263_Group23_Presentation_Slides.pptx) has 16 slides; its speaker notes and the [script](CS3263_Group23_Script.docx) contain the same narration (1,019 words, about 9:14 at a steady pace). Check the recorded length before uploading.

| Slide | Presenter | Target | Title |
| --- | --- | ---: | --- |
| 1 | Tham Yao Xiang | 0:38 | Scheduling with language models |
| 2 | Tham Yao Xiang | 0:53 | Scheduling is a coupled constraint problem |
| 3 | Tham Yao Xiang | 0:31 | Same request, two routes, one validator |
| 4 | Tham Yao Xiang | 0:38 | Both methods face the same certified cases |
| 5 | Tham Yao Xiang | 0:33 | Can eight activities share one room? |
| 6 | Woo Yong Qing | 0:25 | The same request exposes different errors |
| 7 | Woo Yong Qing | 0:30 | Solver assistance increases acceptance |
| 8 | Woo Yong Qing | 0:36 | The gap is in building schedules |
| 9 | Woo Yong Qing | 0:22 | Failures have different causes |
| 10 | Woo Yong Qing | 0:46 | A correct solver can solve the wrong problem |
| 11 | Tea Li Hao | 0:41 | Infrastructure failures and cost |
| 12 | Tea Li Hao | 0:46 | Earlier studies of the feedback scenarios |
| 13 | Tea Li Hao | 0:35 | Limits: one-day, template-based evidence |
| 14 | Tea Li Hao | 0:32 | Valid schedules still need responsible use |
| 15 | Tea Li Hao | 0:42 | Our answer to the project question |
| 16 | Tea Li Hao | 0:06 | References |

## Recording checklist

- Speak at a steady pace; if the take runs long, shorten slides 12 or 13 first.
- Keep the bottom and top-right areas clear if a webcam inset is used; slides 2–16 already show the presenter's name at top right.
- Each member should be able to explain both methods, one extraction failure and the study's limitations in their own words.
- Numbers on slides and in the narration match the [report](../docs/submission-report.md); do not present offline demo outputs as model results.

## Likely questions

| Question | Answer boundary |
| --- | --- |
| Why CP-SAT; is a new solver the contribution? | Integer domains and coupled constraints fit CP-SAT. The contribution is the formulation, comparable pipelines and evaluated trade-offs. |
| Why these models rather than frontier models? | Both are hosted on SoC's SoCLaaS and were agreed with our TA; stronger models may do better directly, which the report discusses. |
| Could the solver and reference share a bug? | Yes; arithmetic validation, independent certificates and exhaustive small-case checks reduce the risk, but optimality checks share the compiler. |
| Does 98.8% mean deployment reliability? | No. These are synthetic, template-generated cases from ten related families with one answer per condition. |
| Where do solver-assisted errors come from? | Extraction: given gold specifications, the compiler labels all 1,000 cases correctly. |
| Was the case text checked by people? | Yes, 24 cases across all families and both labels, with no mismatches; the rest rely on automated checks. |
