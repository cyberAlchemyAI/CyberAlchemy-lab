# Product–research definitions and connection review

Status: **candidate route approved by the user on 2026-10-26; Lab owner admission and graph standing remain absent**. Prepared against the project's [78 local candidate meanings](../../model/definitions.json), [product–research trace](../../model/PRODUCT-RESEARCH-TRACE.md) and the Lab's selected [definition](../../../CyberAlchemy-lab/docs/lab/reference/definitions.md), [endpoint](../../../CyberAlchemy-lab/docs/lab/reference/endpoint-kinds.md) and [relation](../../../CyberAlchemy-lab/docs/lab/reference/relation-kinds.md) catalogs. The [preparation receipt](PRODUCT-RESEARCH-CONNECTION-RESULT.md) records the exact Define Pack and candidate carriers. This packet describes the **smallest governed connection** needed to trace the product hypothesis through studies, evidence, findings and product decisions. It does not approve recruitment, scores, employment use or claims.

## Decision requested

Approve the following **candidate model and preparation scope** for semantic/ontology work:

1. Keep Product, Product Thesis, Product Capability, Project, Goal, Research Inquiry, Experiment Design/Run, Evidence Set, Measurement Result, Finding and Decision separate. Use existing Lab endpoint kinds and the 26 **ordered endpoint pairs** in the relation table below. Do not admit the project's 105 local edge labels as Lab relation kinds by name.
2. Select the seven additional **existing Lab meanings** in the definition table below for a fresh exact Define v2 preparation. The original historical binding of other Lab meanings remains historical.
3. Review `ea.feedback-metric` and `ea.product-success-metric` as **task-local candidate meanings** with the exact statements below. Keep `FM-*` participant displays and `PS-*` aggregate product measures distinct. No new generic “Product Research Connection” definition is proposed.
4. Prepare candidate Product Thesis and seven Product Capability carrier instances, then the missing Research Inquiry/Experiment Design instances as their scope is selected. Create typed-relation instances only against exact eligible, versioned endpoints after the relevant carrier and source reviews.
5. Keep the three possible **new Lab extensions** in the final section deferred. They are unnecessary for the first trace and are not included in this approval scope.

This approval would select a modeling route and authorize preparation/review work only. The Lab's separate semantic owner, carrier, relation, current-host and effect decisions remain necessary before any graph standing or external use.

## A. Canonical meanings

### A1. Existing Lab meanings to select for this product

These meanings already exist in the Lab catalog. They need exact-version selection in a **new** source capture; the project does not redefine them.

| ID | Exact Lab meaning | Why the chain needs it | Current project state |
| --- | --- | --- | --- |
| `D-01` | [Experiment Run](../../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-experiment-run.md) `cal.definition.experiment-run@1.0.0-candidate.1` | An execution with deviations and receipts is distinct from E01–E08 designs. | Proposed external meaning; no run. |
| `D-02` | [Research Run](../../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-research-run.md) `cal.definition.research-run@1.0.0-candidate.1` | Literature/source investigation can produce evidence without being called an experiment. | No selected local binding or run. |
| `D-03` | [Evidence Set](../../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-evidence-set.md) `cal.definition.evidence-set@1.0.0-candidate.1` | Groups attributable supporting and contradictory run material before synthesis. | No selected local binding or instance. |
| `D-04` | [Hypothesis](../../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-hypothesis.md) `cal.definition.hypothesis@1.0.0-candidate.1` | E06 and the three session-transfer claims can name exact propositions an Experiment Design tests. | Six propositions embedded in thesis; no standalone Hypothesis instance because v1 carrier requires an evidence counterpart. |
| `D-05` | [Measurement Result](../../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-measurement-result.md) `cal.definition.measurement-result@1.0.0-candidate.1` | A value and its method/source/uncertainty are distinct from a Finding. | Proposed external meaning; no result. |
| `D-06` | [Finding](../../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-finding.md) `cal.definition.finding@1.0.0-candidate.1` | A bounded supported/contradicted/inconclusive interpretation is distinct from raw evidence. | Proposed external meaning; no finding. |
| `D-07` | [Decision](../../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-decision.md) `cal.definition.decision@1.0.0-candidate.1` | A product/claim/use choice is a separate owner act after a finding. | Proposed external meaning; no owner decision. |

Product, Product Thesis, Product Capability, Project, Goal, Research Inquiry, Experiment Design, Measurement Method, Evidence and Authority already have historical selection or task-local use described in [DEFINITIONS.md](../../model/DEFINITIONS.md). New capture must not imply that those historical Packs admitted today's revised project source.

### A2. Two local definitions awaiting semantic review

| ID | Exact candidate statement in [definitions.json](../../model/definitions.json) | Scope and hard boundary |
| --- | --- | --- |
| `L-01` `ea.feedback-metric` | “A Feedback Metric is one versioned participant-facing value or status in a Score Report, derived from pinned case, rubric, scoring and administration evidence by a declared calculation and display rule, with its unit, missingness, uncertainty, comparison scope and permitted interpretation recorded.” It describes one report purpose/case/session. Administrative coverage, transcript quality and completion cannot be presented as ability; an uncalibrated percentile is excluded. |
| `L-02` `ea.product-success-metric` | “A Product Success Metric is a versioned, decision-linked measure of whether a declared product value or risk condition is met in a specified population and phase, with its numerator, denominator or outcome scale, observation window, source, missing-data rule, uncertainty, comparison and owner-selected decision rule recorded before interpretation.” Pilot engagement cannot establish hiring validity; a metric value cannot authorize a claim or deployment. |

These are **two of 78** unadmitted local meanings. Approval of this packet would review their intended meanings, not silently approve the remaining 76 or turn them into Lab-global definitions. The [metric handoff](METRICS-DEFINE-REQUEST.md) is historical; the [new Define Pack](PRODUCT-RESEARCH-CONNECTION-RESULT.md) pins the approved candidate meaning cut.

## B. Endpoint kinds and concrete instances

The Lab already declares the endpoint kinds below. The table separates an endpoint **kind** from an actual admitted/selected **instance**. No new endpoint kind is required for the first trace.

| Lab endpoint kind / selected carrier | Exact project subject or planned instance | Present state |
| --- | --- | --- |
| `product` · Product identity v2 | `EA-PRODUCT-001@0.1.0-candidate.2` | Candidate [identity](../../product/product.json); no Lab admission. |
| `product-thesis` · v1 | `product-thesis:ea:compact-selection@candidate.1` | Candidate carrier instance; no Lab admission. |
| `product-capability` · v1 | `EA-CAP-01` through `EA-CAP-07` | Seven candidate carrier instances; no Lab admission. |
| `project` · Project identity v1 | `project:ea-research-001` | Candidate Lab-shaped record. |
| `goal` · v1 | `goal:ea:g01-meaning-ownership`, `goal:ea:g02-case-science`, `goal:ea:g03-reproducible-prototype`, `goal:ea:g04-measurement`, `goal:ea:g05-prediction`, `goal:ea:g06-product-decision` | Six candidate Lab-shaped records. |
| `research-inquiry` · v1 | `research-inquiry:ea:compact-selection@candidate.1`; later session/value inquiries as needed | Eight candidate Inquiry records; no Lab admission. |
| `hypothesis` · v1 | Strong `3×10` proposition; Session 1/2/3 transfer propositions; product-value proposition when registered | No carrier instance. Use one exact version per proposition rather than a generic “assessment works.” |
| `experiment-design` · v1 | `experiment-design:ea:e06-compact-selection`; E01–E05A/B/C, E07–E08 as bounded designs | Ten candidate design carrier instances; no Lab admission or run. |
| `experiment-run` · v1; `research-run` · v1 | One actual execution per registered design or inquiry | None. Do not create run instances from planned work. |
| `evidence-set` · v1; `measurement-result` · v1; `finding` · v1 | Source-bound evidence, exact values and bounded interpretation from future runs | None. Do not fill from proposal prose. |
| `decision` · v2 | Product/case/claim/use owner decision with exact subject and evidence refs | None; owner principals unassigned. |
| `implementation` · v1 | Future software realization of a Product Capability | No app implementation. This endpoint is needed only when claiming realization. |

`measurement-method` is an existing Lab kind, but its selected v1 carrier requires residuality-specific fields such as `entropy_register` and `residue_type_ref`. The broad definition can describe our metric methods; the **carrier fit for FM/PS scorecards is unverified**. For now their exact formulas and versions remain project-local and can be cited from Experiment Designs/Runs and Evidence Sets. Do not invent a Lab metric endpoint or put a dummy residue value in the accepted carrier. A new metric carrier/type request is a later choice if first-class Lab metric instances become necessary.

## C. Exact ordered relation pairs proposed for reuse

Every pair below was checked against the Lab's selected relation catalog. The displayed qualifier names are mandatory for a future typed-relation **instance**; no instance is asserted by this packet. Reuse the accepted relation meanings and directions. A local edge with similar English wording is not automatically the same relation.

| ID | Accepted relation | Allowed ordered endpoints (source → target) | Required qualifiers | What it records |
| --- | --- | --- | --- | --- |
| `R-01` | [`member-of`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-member-of.md) | `product-thesis → product`; `product-capability → product`; `goal → project`; `research-inquiry → project`; `experiment-design → project`; `experiment-run → project` | `membership_role` | Exact containment/scope, no authority transfer. |
| `R-02` | [`derives-from`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-derives-from.md) | `product-capability → product-thesis`; `evidence-set → experiment-run`; `evidence-set → research-run`; `measurement-result → experiment-run`; `finding → evidence-set` | `derivation_role` | Source lineage, not identity or acceptance. |
| `R-03` | [`contributes-to`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-contributes-to.md) | `project → product`; `research-inquiry → goal`; `experiment-design → goal` | `contribution_role`, `contribution_scope` | Intended advancement, not success. |
| `R-04` | [`engages-inquiry`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-engages-inquiry.md) | `experiment-design → research-inquiry`; `experiment-run → research-inquiry`; `finding → research-inquiry` | `inquiry_role` | Which question a design/run/finding addresses. |
| `R-05` | [`evaluates`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-evaluates.md) | `experiment-design → product`; `experiment-design → product-capability`; `experiment-design → product-thesis` | `evaluation_role`, `evaluation_purpose` | The exact product subject being tested, no result implied. |
| `R-06` | [`tests-hypothesis`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-tests-hypothesis.md) | `experiment-design → hypothesis` | `hypothesis_version_ref`, `test_role` | Exact falsifiable proposition. |
| `R-07` | [`realizes`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-realizes.md) | `experiment-run → experiment-design`; later `implementation → product-capability` | `realization_role`, `exact_target_version_ref` | Execution or implementation, not effectiveness. |
| `R-08` | [`evidence-bears-on`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-evidence-bears-on.md) | `evidence-set → hypothesis`; `measurement-result → hypothesis` | `polarity` | Support or contradiction, never automatic acceptance. |
| `R-09` | [`declares-effect-on`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-declares-effect-on.md) | `decision → product-capability` | `effect_kind`, `exact_target_version_ref` | Exact owner-declared capability effect; execution is separate. |
| `R-10` | [`successor-of`](../../../CyberAlchemy-lab/docs/lab/reference/records/rel-relation-successor-of.md) | Same-kind successor for product, thesis, capability, inquiry, design, run, evidence set, result, finding or decision as applicable | `succession_effect` | Version lineage, not automatic replacement. |

There are **26 specific ordered endpoint pairs** in `R-01`–`R-09`, plus the existing same-kind version pattern `R-10`. The first currently nameable instance candidates include: Project `contributes-to` Product; six Goals `member-of` Project; the central Inquiry `member-of` Project and `contributes-to` Goal 05; E06 Design `member-of` Project, `engages-inquiry` the central Inquiry, `contributes-to` Goal 05 and `evaluates` the Product. Their records remain candidate/unadmitted, so these are proposed links, not applied Lab graph edges. The [114-link proposal manifest](../../model/lab-records/relation-proposals.json) covers the broader current candidate set. Hypothesis links await a compatible standalone carrier route.

An owner Decision about Product or Product Thesis can cite exact subjects in the selected Decision v2 carrier's `payload.subject_refs` and its evidence in `payload.evidence_basis_refs`. The current `declares-effect-on` relation allows `decision → product-capability`, **not** `decision → product` or `decision → product-thesis`. Do not fabricate those typed edges. Likewise `Measurement Result` has `method_ref` in its carrier, while the selected `uses-method` relation pairs it with generic `method`, not directly with `measurement-method`; keep the exact field reference until carrier compatibility is resolved.

### Experiment Design → Product evaluation subjects

The `evaluates` pairs above should be instantiated for these exact **proposed** scopes when each design carrier is prepared. Metric IDs are method/output refs, not new graph endpoint kinds. All ten designs now have candidate Lab-shaped records; all rows remain unapplied plans.

| Design ID | Product Capability endpoints to evaluate | Primary product metrics and claim boundary |
| --- | --- | --- |
| `EA-E01` | `EA-CAP-03`, `EA-CAP-05` | Role-task link for E02/E05/E06; no numeric product success value by itself. |
| `EA-E02` | `EA-CAP-01`, `EA-CAP-03` | `PS-08`, case burden and exposure; release quality, not predictive validity. |
| `EA-E03` | `EA-CAP-02`, `EA-CAP-04` | `PS-07`, cited rating/calibration error; formative score quality. |
| `EA-E04` | `EA-CAP-04`, `EA-CAP-05` | `PS-09`, one-case precision; narrow C2 measurement claim only if supported. |
| `EA-E05A` | `EA-CAP-05` | `PS-10` creative-work transfer; Session 1 claim. |
| `EA-E05B` | `EA-CAP-05` | `PS-10` design-work transfer; Session 2 claim. |
| `EA-E05C` | `EA-CAP-05` | `PS-10` observed coordination transfer; Session 3 claim. |
| `EA-E06` | `EA-CAP-05`, `EA-CAP-07` | `PS-11/12`, with `PS-13` guardrail; strong named-role selection thesis, not employer use by itself. Current design names only `EA-CAP-05`; add `EA-CAP-07` in a successor design after employer-use scope is accepted. |
| `EA-E07` | `EA-CAP-01`, `EA-CAP-02`, `EA-CAP-04`, `EA-CAP-06`, `EA-CAP-07` | `PS-06/07/13/16`; access, mode and fairness guardrails across the journey. |
| `EA-E08` | `EA-CAP-01`, `EA-CAP-02`, `EA-CAP-07` | `PS-01–05/14/15/17`; pilot feedback and later employer/product value must remain separate study conditions. |

## D. Deferred extensions requiring a separate approval

| Candidate extension | Why someone may want it | Why it is deferred |
| --- | --- | --- |
| Add `decision → product` and `decision → product-thesis` to the accepted `declares-effect-on` allowed pairs. | Direct graph query for a product/thesis posture decision. | Decision v2 already has exact `subject_refs`; adding pairs changes a Lab relation contract and needs its own semantic/impact review. |
| Give `ea.product-success-metric` (and perhaps `ea.feedback-metric`) a Lab artifact type, endpoint and a typed `capability measured-by metric` relation. | First-class metric query, method/result lifecycle and dashboard trace in the Lab graph. | Current local scorecards and run evidence can carry the trace; the selected Measurement Method v1 carrier's residuality-specific fields need fit review before any new carrier or relation is justified. |
| Give local `ea.target-outcome` and Engineering Role Profile Lab endpoint kinds/relations. | Direct graph query from named role and independent job outcome to each validation study. | E06's exact design fields and registered work criteria can bind them now. Decide the carrier and privacy boundary for real employer outcomes before making a Lab-global endpoint. |

## Review outcome to record

The reviewer can accept, revise or reject `D-01`–`D-07`, `L-01`–`L-02`, and `R-01`–`R-10` **as the candidate route**, and can separately choose whether any item in D should be brought forward. Record the decision maker, scope, exact source cut, dissent and claim ceiling. Approval of the route does not imply that missing thesis/capability/design carriers, study runs, metric values, findings or owner effect records already exist.
