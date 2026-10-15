# Workflow model candidates

Status: ten proposed coordination models. They are schema-valid model instances with stage-specific outputs. They are not admitted Workflow Profiles or executable lifecycle mappings. Input/output carrier declarations identify permissible contracts, not fabricated artifact instances or automatically satisfied requirements.

Each model requires an exact Workflow Decision Profile, actor/authority routes, domain lifecycle mappings, concrete preconditions, declared connections and satisfaction checks. [domain-lifecycle-mapping](schemas/domain-lifecycle-mapping.schema.json) provides the schema for this binding. The current templates intentionally retain unbound authoring references and empty mapping bindings; execution must block until they are resolved. Blocked and indeterminate states require a bound recovery disposition; this package does not invent automatic retry transitions.

| Model | Proposed coordination path | Required completion evidence |
|---|---|---|
| [intent-framing](workflows/intent-framing.json) | framed → resolved → prepared | Resolve intent into explicit Goal/Work/method scope and implementation route; retain the one-Goal Coordination Context. |
| [agent-context](workflows/agent-context.json) | requested → context-ready → session-ready | Verify assignment/authority and bounded Context/Ontology Views before opening the ephemeral session. |
| [engineering](workflows/engineering.json) | prepared → designed → implemented → assessed | Bind reviewed design, implemented outputs and required observations; assess Work outcome against its satisfaction contract. |
| [research](workflows/research.json) | prepared → designed → executed → evaluated | Bind inquiry/hypothesis/design, method/measurements and run evidence; assess findings with stated uncertainty. |
| [failure-assessment](workflows/failure-assessment.json) | observed → classified → assessed → response-assessed | Keep occurrence, classification, cause assessment and response/control evidence distinct; evaluate recovery and incident criteria. |
| [challenge-handling](workflows/challenge-handling.json) | submitted → eligible → responded → resolved | Establish eligibility, response and actual owner Decision under the bound Challenge Contract; preserve contestability and history. |
| [operational-learning](workflows/operational-learning.json) | observed → lesson-prepared → application-recorded → outcome-assessed | Prepare an evidenced lesson, record a scoped application and assess its outcome/counterevidence before declaring effectiveness. |
| [review-admission](workflows/review-admission.json) | prepared → review-ready → owner-resolved → applied | Materialize the whole review package, record exact authorized member outcomes and verify canonical application independently of projections. |
| [ontology-migration](workflows/ontology-migration.json) | selected → mapped → candidate-validated → selected-scope-assessed | Map selected source items and representations, validate candidates and account for every selected disposition; no global migration completion inferred. |
| [product-adoption-release](workflows/product-adoption-release.json) | scoped → candidate-assessed → pilot-assessed → release-reviewed | Assess capability realization/conformance, actual scoped pilot observations and owner release Decision; no service activation implied. |
## A realistic future Work example

Suppose a Project needs a capability that shows all definitions and their current status.

1. The owner prepares an Intent, Goal and Work: “show definition content, effective admission, version, evidence and unresolved gaps.” A Coordination Context binds that one Goal. Intent Resolution selects an engineering method and implementation route.
2. An assignment selects an Agent Profile, Implementation and capabilities. Existing Delegation and Authority Boundary permit repository inspection and candidate authoring. They do not imply permission to admit every future output.
3. The Agent requests exact Context and Ontology Views. The Lab returns current Definition contracts, registry references, predecessor decisions and relevant lessons. Missing references are visible gaps.
4. The Agent inspects definitions through `artifact.inspect`/`artifact.query`, prepares interface and query candidates, and uses bounded tool actions where permitted. Action receipts attribute actual outputs and uncertainty.
5. Generated Output, Evidence Set and Work Outcome Assessment bind the observed implementation and its required checks. If a failure occurs, classification and failure assessment feed a scoped lesson candidate rather than a hidden session-memory dump.
6. Once the complete selected package and required observations exist, one owner checkpoint reviews independent exact Decision cores. Each member binds its actual scope, bytes and evidence.
7. The authorized application adapter verifies current heads and commits the selected artifact effects. Project State/history consequences follow that exact transaction. SQLite and ontology projections expose their independent freshness.
8. A requested file generation exports original definition bytes or renders an explanatory index from pinned inputs. The session closes and short memory expires. The next Agent reconstructs continuity from updated Project State and views.

This walkthrough is a proposed execution path. The [example messages](examples/README.md) demonstrate structures; they contain placeholders and provide no evidence that this Work was executed or authorized.

## One final checkpoint

The review/admission model separates preparation, owner resolution and application. Challenge and product-release models also identify owner decisions. A single final interaction is possible for an exact package only when its Workflow Decision Profile permits composition and all required owners can authorize their members. Evidence-producing local actions before that checkpoint require existing exact authority or isolated candidate operation; an end-of-work checkpoint cannot retrospectively authorize their execution.

Future unknown Work, findings, lessons and release bytes cannot be pre-admitted. External provisioning, deployment, network operations and service activation need separately declared scopes and extensions beyond this selected local protocol package.
