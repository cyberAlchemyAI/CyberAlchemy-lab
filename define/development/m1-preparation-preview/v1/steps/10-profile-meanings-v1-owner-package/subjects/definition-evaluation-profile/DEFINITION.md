<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Evaluation Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-evaluation-profile`
- Version: `1.0.0-candidate.3`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-m1:profile-source-closure-unadmitted`

## Scientific/formal voice

A Definition Evaluation Profile is a reusable, owner-qualified, version-exact contract declaring how an Evaluation assesses one exact Definition version and its declared review package within a named scope and phase. It binds the subject and input selection, applicable governing contracts, required checks, evidence requirements, permitted outcomes, causal blockers, phase-specific aggregation, pre-decision eligibility and claim limits. It specifies the rules for producing and interpreting evaluation evidence; a declared profile does not establish that an Evaluation occurred, that its criteria passed, that an owner selected admission or that an effect was applied.

```text
P=(id,v,T,Sel,C,Omega,B,G,R,A,o,s,L); Omega={PASS,FAIL,NOT_EVALUABLE};
ConformingEvaluation(e,P,S,I,g) implies ExactBinding(e,P,S,I,g) and dom(O_e)=C and BlockersPreserved(e,P).
For g in G, R(P,g) subseteq C; A(P,g,O_e)=FAIL if any c in R(P,g) has O_e(c)=FAIL;
else NOT_EVALUABLE if any required c has O_e(c)=NOT_EVALUABLE; else PASS.
Declaration(P) does not entail Executed(e), A(P,g,O_e)=PASS, Admitted(S), or Applied(S).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P; id,v; T | Exact profile identity/revision and selected Definition subject representation. |
| Sel; S; I; s; g | Exact subject/input selection, one Definition version, input state, authority/applicability scope and named phase. |
| C; Omega; O_e; B | Finite declared check identities, outcome vocabulary, one complete evaluation result map and causal blocker contract. |
| G; R(P,g); A | Declared phases, required aggregation subset for one phase, and its outcome rule. Completeness of check reporting and phase aggregation are different obligations. |
| o; L | Qualified profile owner and explicit coverage/authority claim limits. |
| ConformingEvaluation; ExactBinding | Interpretation of a conforming completed evidence record, not a guarantee that every attempt succeeds. Relevant subject/profile/input versions and scope must match. |

### Boundary conditions

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- Every declared check receives a scoped result or an explicit not-evaluable blocker; only the named phase subset contributes to its aggregate.
- A required check with missing applicable evidence is NOT_EVALUABLE; an established violation is FAIL. Missing evidence is not a proof of violation.
- Admission-selection/application checks can be reported as pending while excluded from pre-decision aggregation.

### Testable conditions

- The semantic record preserves exact identity, scope, three voices and selected carrier/generator bindings.
- Profile declarations, completed evidence, owner selection and confirmed effects have separate identifiers and evidence.
- The incident example retains the account, filters, source snapshot and saved output boundaries.
- No missing review or unperformed effect is reported as completed.

## Plain-language voice

The contract for checking a Definition and understanding the results. It says which evidence is required, which checks contribute to each phase and why other checks are blocked. The results describe only what was actually established; they do not approve the Definition.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

This revised semantic binding applies to the proposed v2 profile/carrier. The candidate itself uses admitted Definition/v1 mechanics and current v1 review routes as the explicit bootstrap choice, independent of the meaning’s scope. No v2 self-approval or owner acceptance is claimed.

### Examples

- For the identifier-completeness Definition, schema and projection checks pass while required semantic evidence remains NOT_EVALUABLE.
- The incident’s 200 missing IDs make its proposed coverage predicate false. That is a different subject from whether the Definition record meets its governance contract.

## Applicability

Shared meaning for Lab Definition evaluation contracts and exact phase-scoped review packages.

### Exclusions

- Profiles for unrelated artifact kinds without their own declared extension.
- Automatic owner decisions, lifecycle events, application or machine-agent permission.

## Boundaries

- The semantic meaning is independent of its carrier revision. Exact v1 bootstrap mechanics and later v2 adoption are separately declared representation/review choices.
- The declared scope is Lab Definition governance. It does not supply a general profile for unrelated artifact kinds.
- A changed subject, profile, selected source or evidence epoch invalidates affected evidence; prior material is preserved without automatic refreshing.
- Schema/projection PASS, semantic interpretation fidelity, applicable owner selection and confirmed application remain separate obligations.
- Every declared check receives a scoped result or an explicit not-evaluable blocker; only the named phase subset contributes to its aggregate.
- A required check with missing applicable evidence is NOT_EVALUABLE; an established violation is FAIL. Missing evidence is not a proof of violation.
- Admission-selection/application checks can be reported as pending while excluded from pre-decision aggregation.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.evaluation@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `7ca1fc6de116223f93d026856c7780320d600b79e454c0b4ef957bd03dd24a7b` | `admitted` |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /checks | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /admission_rule | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| cal.definition.review@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /outcomes | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /evaluation_mode | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /subject_artifact_type_ref | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-EVALUATION-DEFINITION-V1 | /owner_ref | `8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/2 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | /role_assignments/4 | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/staged-carriers/definition-evaluation-profile/artifact.json

## Lookup and drift

- Index: `define/development/m1-preparation-preview/v1/DEFINITIONS-INDEX.md` / `cal.definition.definition-evaluation-profile`
- Drift owner: `role:definition-owner`
- Audit: `define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/semantic-binding-review.json
- define/development/m1-preparation-preview/v1/steps/05-carrier-foundational-compatibility/compatibility.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/interpretation.json
- define/development/m1-preparation-preview/v1/steps/06-profile-definition-meaning-review/example.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-core.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/formal-results.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/correspondence.json
- define/development/m1-preparation-preview/v1/steps/07-profile-formal-source-evidence/source-closure.json

## Residue

- owner-interpretation-and-semantic-fidelity-decision-pending
- bounded-model-not-whole-natural-language-consistency
- exact-registry-index-review-postimages-pending
- carrier-profile-adoption-pending
- owner-admission-pending

## Claim ceiling

Source-completed candidate with unchanged candidate.2 normative statement and formal expression. Finite model/exhaustive rule evidence applies only to the explicit interpreted core and pinned inputs. It does not establish whole-repository consistency, real-world owner authentication, semantic fidelity acceptance, admission or applied effects.
