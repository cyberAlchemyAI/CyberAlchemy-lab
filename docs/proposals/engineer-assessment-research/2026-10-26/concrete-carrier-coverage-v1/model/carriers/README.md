# Artifact Type coverage for authored records

This [coverage index](coverage.json) maps the concrete records currently authored in this project to their carrier contracts. The [gap register](gaps.json) records source/control surfaces that require adaptation or later owner decisions. It does not invent participant responses, research runs, scores, findings, decisions or released cases.

| Existing record group | Count | Carrier posture |
| --- | ---: | --- |
| Product, Project, six Goals, Product Thesis, seven Capabilities, eight Inquiries, ten Designs | 34 | Selected Lab Product/Project/Goal/Thesis/Capability/Inquiry/Design carriers; all candidate-unadmitted. |
| Individual Definition records | 78 | Selected Lab Definition/v1 carrier; all project-scoped candidates. |
| Actor role IDs in the MVP policy | 27 | Selected Lab Role/v1 carrier, one draft record per role; no assignment or grant. |
| Feedback and product metric specifications | 25 | Local candidate [Feedback Metric](feedback-metric-spec/v1/artifact.json) and [Product Success Metric](product-success-metric-spec/v1/artifact.json) carriers and requests. They preserve exact authored rules; typed calculation/decision fields remain open. |
| Question rules, use cases, operations and workflow | 29 | Four separate local candidate carriers and requests under `question-*/v1`; source-bound and not executable. |
| Application permission entries | 36 | Local candidate [Access Permission carrier](access-permission/v1/artifact.json) and request; no active policy. |
| Draft case scripts | 3 | Local candidate [Case Candidate carrier](case-candidate/v1/artifact.json) and request; source scripts remain draft/unreleased. |
| Case-specific rubric blueprints | 3 | Local candidate [Rubric Blueprint carrier](rubric-blueprint/v1/artifact.json) and request; six dimensions each remain draft. |

The 96 records under local candidate carriers were extracted into [individual JSON records](../concrete-records/index.json), with original file and row digests. The 27 roles were converted into [Lab Role/v1 candidate records](../lab-records/roles/) and retain a [source crosswalk](../concrete-records/role-source-index.json). The nine new local families each have a selected-schema [Artifact Type Request](feedback-metric-spec/v1/request.json), a candidate descriptor and a closed source-preserving instance schema. The earlier [Criterion Rating carrier](criterion-rating/v1/README.md) is the tenth request. These local descriptors explicitly do **not** claim Lab Artifact Type/v3 conformance while their definitions and type-owner bindings remain unadmitted.

The [three E05 register entries](../concrete-records/study-design-crosswalk.json) map to candidate Experiment Design/v1 records and are not extra runs. The [114 relation proposals](../lab-records/relation-proposals.json) are a control manifest, not applied Typed Relation/v3 instances. `model/ontology.json`, the relation manifest and source/lookup indexes have exact [gap dispositions](gaps.json). Six thesis hypotheses remain embedded because the selected Hypothesis/v1 carrier requires an evidence counterpart that does not exist.

## Evidence and limits

- `python3 tools/validate_concrete_records.py` checks 123 source-bound records, candidate schemas, exact source rows, nine requests and role source links.
- `python3 tools/validate_carrier_coverage.py` checks all counted record families, ten type requests and ten gap dispositions.
- `python3 tools/validate_lab_carriers.py` checks 149 candidate files against selected Lab carrier schemas, including 78 Definitions, 27 Roles and ten Artifact Type Requests.
- Source-bound rows preserve wording; they do not by themselves supply executable metric calculations, permission predicates, state machines or released-case fields. Each candidate descriptor lists its open typed fields.

The first unfilled domain instances are real participant/answer/rating/report records, Experiment or Research Runs, evidence/results/findings, applied relations and owner Decisions. Their carriers must be selected or admitted and their purpose/authority gates satisfied before any such instance is created.
