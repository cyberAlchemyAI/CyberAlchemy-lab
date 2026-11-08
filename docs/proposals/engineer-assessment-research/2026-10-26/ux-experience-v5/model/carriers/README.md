# Artifact Type coverage for authored records

The [earlier Lab review result](../../integration/lab/CONCRETE-CARRIER-COVERAGE-RESULT.md) freezes the pre-recovery candidate cut. This [coverage index](coverage.json) maps the concrete records currently authored in this project to their carrier contracts. The [gap register](gaps.json) records source/control surfaces that require adaptation or later owner decisions. It does not invent participant responses, research runs, scores, findings, decisions or released cases.

| Existing record group | Count | Carrier posture |
| --- | ---: | --- |
| Product, Project, six Goals, Product Thesis, seven Capabilities, eight Inquiries, thirteen Designs | 37 | Selected Lab Product/Project/Goal/Thesis/Capability/Inquiry/Design carriers; all candidate-unadmitted. |
| Individual Definition records | 94 | Selected Lab Definition/v1 carrier; all project-scoped candidates. |
| Actor role IDs in the MVP policy | 27 | Selected Lab Role/v1 carrier, one draft record per role; no assignment or grant. |
| Feedback and product metric specifications | 25 | Local candidate [Feedback Metric](feedback-metric-spec/v1/artifact.json) and [Product Success Metric](product-success-metric-spec/v1/artifact.json) carriers and requests. They preserve exact authored rules; typed calculation/decision fields remain open. |
| Question rules, use cases, operations and workflow | 29 | Four separate local candidate carriers and requests under `question-*/v1`; source-bound and not executable. |
| Application permission entries | 36 | Local candidate [Access Permission carrier](access-permission/v1/artifact.json) and request; no active policy. |
| Draft case scripts | 3 | Local candidate [Case Candidate carrier](case-candidate/v1/artifact.json) and request; source scripts remain draft/unreleased. |
| Case-specific rubric blueprints | 3 | Local candidate [Rubric Blueprint carrier](rubric-blueprint/v1/artifact.json) and request; six dimensions each remain draft. |
| Draft Administration Policy | 1 | Local candidate [Administration Policy carrier](administration-policy/v1/artifact.json) and request; timed values remain unapproved. |
| Recovery rules | 21 | Local candidate [Recovery Rule carrier](recovery-rule/v1/artifact.json) and request; one source-bound rule per failure class. |
| Integration boundaries | 6 | Stable, source-bound [producer/consumer seams](../integration/boundary-index.json) with data, interface, invariants and failure routes; one local candidate carrier request. |
| Integration option reviews and verification contracts | 12 | Six source-bound comparisons and six prospective test contracts under [integration governance](../integration/README.md); two local candidate carrier requests. |
| Technology components | 25 | Source-bound [candidate identities](../integration/component-index.json) for named vendors, libraries, APIs and tools; no production versions or processor approvals selected. |
| Integration bindings | 0 | Candidate [binding carrier](integration-binding/v1/artifact.json) for a later version-pinned release; no selection or deployment instance. |
| Candidate policy bundles | 14 | Selected Lab [Policy/v2 records](../policies/index.json) with 46 local candidate Policy Clauses; all unissued. |
| Retention Schedule and Assistance Matrix | 2 | Local candidate [schedule](../policies/retention-schedule.json) and [matrix](../policies/assistance-matrix.json); durations and policy approval open. |
| Integration choice Challenge Contract | 1 | Candidate selected Lab [Challenge Contract/v1](../lab-records/integration-choice-challenge-contract.json) with seven future trigger grounds; draft policy is unissued. |
| Experience design records | 55 | [Source-bound UX records](../../design/index.json): brand, design system, flows, screens, components and analytics event specifications under six local candidate carriers and requests. |

Of the 264 records under local candidate carriers, 209 predate the [55 UX records](../../design/index.json). All retain source digests. The 14 [Policy/v2 candidates](../policies/index.json), 27 roles and 94 definitions use selected Lab carriers; none is admitted as an instance. There are 28 selected-schema Artifact Type Requests, including six for UX. Recovery Decision and Upload Attempt have synthetic shape witnesses only; Integration Binding has no instance. These local descriptors explicitly do **not** claim Lab Artifact Type/v3 conformance while their definitions and type-owner bindings remain unadmitted.

The [three E05 register entries](../concrete-records/study-design-crosswalk.json) map to candidate Experiment Design/v1 records and are not extra runs. The [114 relation proposals](../lab-records/relation-proposals.json) are a control manifest, not applied Typed Relation/v3 instances. `model/ontology.json`, the relation manifest and source/lookup indexes have exact [gap dispositions](gaps.json). Six thesis hypotheses remain embedded because the selected Hypothesis/v1 carrier requires an evidence counterpart that does not exist.

## Evidence and limits

- `python3 tools/validate_concrete_records.py` checks 123 source-bound records, candidate schemas, exact source rows, nine requests and role source links.
- `python3 tools/validate_recovery_records.py` checks twenty-one source-bound rules, one draft policy, four new requests, candidate schemas and synthetic witnesses.
- `python3 tools/validate_boundary_records.py` checks six boundary specifications, source parity, carrier and linked reviews/contracts.
- `python3 tools/validate_integration_records.py` checks twelve source-bound option and verification records and two candidate carrier schemas.
- `python3 tools/validate_component_records.py` checks 25 component identities, the empty binding index, and two candidate carrier requests.
- `python3 tools/validate_policy_records.py` checks fourteen Lab Policy/v2 candidates, forty-six clauses, the ten-class retention schedule and twenty-four assistance rows.
- `python3 tools/validate_ux_records.py` checks 55 source-bound experience contracts, six closed candidate carriers, type requests and cross-record references.
- `python3 tools/validate_carrier_coverage.py` checks all counted record families, twenty-eight type requests and eighteen gap dispositions.
- `python3 tools/validate_challenge_contract.py` checks the candidate Lab Challenge Contract, policy, seven grounds and six linked reviews.
- `python3 tools/validate_lab_carriers.py` checks 201 candidate files against selected Lab carrier schemas, including 94 Definitions, 27 Roles and twenty-eight Artifact Type Requests.
- Source-bound rows preserve wording; they do not by themselves supply executable metric calculations, permission predicates, state machines or released-case fields. Each candidate descriptor lists its open typed fields.

The first unfilled domain instances are real participant/answer/rating/report records, Experiment or Research Runs, evidence/results/findings, applied relations and owner Decisions. Their carriers must be selected or admitted and their purpose/authority gates satisfied before any such instance is created.
