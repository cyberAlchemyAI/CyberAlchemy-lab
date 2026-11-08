# UX research basis and test questions

Status: source-backed design input, not evidence from this product's users. Sources checked 2026-10-26. The first pilot is invited adult mixed software developers; any applicant or employer experience needs a separate study and authorization.

| Source card | Supported design use | Claim class and limit |
| --- | --- | --- |
| [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Text contrast, visible focus, status messages, timing, keyboard and reflow inform component and screen acceptance. | Standards-backed **hard gate** for applicable success criteria after implementation. A passing automation check is not whole-page conformance. The 10-minute answer limit requires an explicit timing/accessibility analysis and alternate path before release; an arbitrary exception is not presumed. |
| [WAI-ARIA disclosure pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) and [modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | Adjacent purpose details and exceptional dialogs must expose expanded state, keyboard operation and focus behavior. | **Hard gate** for observable semantics; comprehension of the words is a **human study**. Prefer native controls where suitable. |
| [DTCG 2025.10 format](https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/) | Token names, types and values support portable design/development handoff. | **Structural check** only. This is a W3C Community Group report, not a W3C Recommendation; it does not establish brand quality or accessibility. |
| [GOV.UK measuring service success](https://www.gov.uk/service-manual/measuring-success/measuring-the-success-of-your-service) and [usability benchmarking](https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service) | Pair transaction and completion data with observed task performance. | **Research method**. Funnels identify where to investigate; event analytics alone cannot explain a person's understanding or prove hiring validity. |
| [ICO cookies and similar technologies guidance](https://ico.org.uk/media/for-organisations/guide-to-pecr/guidance-on-the-use-of-cookies-and-similar-technologies-1-0.pdf) | Illustrates why third-party/cookie analytics need purpose and jurisdiction review before integration. | **Governance flag**, not a legal determination for the pilot jurisdiction. No optional analytics SDK is selected by this package. |

## Questions to register for the first UX study

1. Can participants accurately explain the three purposes, permitted help and the provisional nature of feedback after reading the invitation and report? Measure `PS-04` with fixed comprehension tasks and count nonresponses.
2. Can participants complete practice, recording, upload recovery, transcript correction and data controls across keyboard, screen reader, mobile/zoom and reduced-motion paths? Record task completion, support route, error, burden and mode; investigate gaps under `PS-02/03/06/16`.
3. Does visible blur/camera and recording state make capture status understandable without giving a false assurance about what is stored? Ask participants to explain what the system records and retains.
4. Can reviewers independently locate evidence and choose `0–4/NA/UNK` without seeing peer ratings? Test missing-source and disagreement tasks; preserve independent rating evidence.
5. Can research staff interpret denominators, missingness and purpose filters before export? Test a synthetic withdrawal and small-cell scenario.

Predeclare tasks, cohort, accommodation routes, success thresholds, uncertainty, researcher scripts and stop rules in the E08 protocol before recruitment. Screen and copy variants are hypotheses. Subjective trust, creativity of the brand and perceived fairness remain human-study findings, never automated pass/fail scores.
