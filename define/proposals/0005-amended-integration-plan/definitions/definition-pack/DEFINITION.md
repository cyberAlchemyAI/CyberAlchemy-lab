<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Pack

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-pack`
- Version: `1.0.0-candidate.2`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `proposal:define-amended-integration-plan:candidate-authored`

## Scientific/formal voice

A Definition Pack is an identifiable, version-exact, reviewable bundle that freezes a bounded goal, originating intent, context and named intended use together with the required concept set, exactly one current handling disposition per concept, its disposition payload, exact source and evidence standing, owner routes, relationship scope, unresolved obligations and validation scope. Its handling dispositions are reuse, specialize, propose and open. Reused meanings remain bound to their exact authority; candidate meanings and unresolved obligations remain identifiable. Pack existence, validation or consumer readiness grants no new semantic admission or permission to execute.

```text
P=(id,revision,g,i,k,u,C,delta,H,E,O,R,Q,V); D={reuse,specialize,propose,open}; WellFormed(P) iff ExactIdentity(id,revision) and BoundedGoalContextUse(g,k,u) and TraceableIntent(g,i) and FiniteNonempty(C) and (delta in Functions(C,D)) and (dom(H)=C) and (forall c in C: PayloadMatches(H(c),delta(c))) and (forall r in References(P): (ResolvedWithStanding(r) or DeclaredGap(r,Q))) and ValidationScopeDeclared(V). WellFormed(P) does not entail ConsumerReady(P,u), admission of a candidate Definition, or permission to execute.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P | One exact frozen pack revision; tuple components are defined in formal-interpretation.json. |
| C | Finite nonempty set of distinct required concept identities, decoded only after rejecting duplicate input rows. |
| D | Closed disposition set reuse, specialize, propose and open. |
| delta in Functions(C,D) | A total single-valued handling function; it is not an authority-admission function. |
| H | Matching disposition payload function whose domain is exactly C. |
| g,i,k,u | Bounded goal, attributable originating intent, declared context and exact named consumer/intended use. |
| E,O,R,Q,V | Source/evidence standing, owner routes, scoped relationships, explicit gaps and declared validation scope. |
| References(P) | The selected references relevant to the named use, each resolved with standing or named in an explicit scoped gap. |
| ValidationScopeDeclared(V) | Required independently of whether references resolve; binds subject/input/profile/check scope and evidence ceiling. |
| ConsumerReady(P,u) | Independent readiness for the named use; it grants no new authority or permission. |

### Boundary conditions

- An open concept is a recorded unresolved outcome; it is not an omitted answer or a proposed Definition.
- One pack may produce zero, one or many Definition candidates; it is not itself one Definition.
- An unchanged-meaning parameter binding may narrow a use. A changed normative meaning requires an explicit new Definition identity or successor route. The specialize label cannot decide that route alone.
- A changed selected input, meaning, consumer use or disposition requires a new frozen revision and lineage.
- Owner routing hints do not establish Role Assignments. Relationship suggestions do not declare global Typed Relations.
- Validation posture, source currency, disposition, consumer readiness and admission are separate; dependencies between them must be explicit.
- A separate owner Decision may admit selected outputs or authorize a named use; it does not rewrite the pack as a Decision or confer authority on unselected contents.
- Input disposition rows must be unique and closed over C before constructing delta; duplicate overwrite is invalid.

### Testable conditions

- Every required concept has exactly one current disposition; duplicate, absent and undeclared dispositions violate the contract.
- An unresolved source or owner reference is visible as a scoped gap rather than labeled resolved.
- A structurally reviewable pack with a blocking open concept cannot be advertised as ready for its blocked consumer action.
- Accepted reuse retains the exact current source authority without fabricating a new admission.
- Pack PASS does not establish semantic-owner acceptance or agent action permission.
- All references resolving does not satisfy WellFormed when validation scope is absent.
- An unresolved reference without a named scoped gap fails WellFormed.

## Plain-language voice

A saved bundle records what each needed concept means or why it remains open, where that information came from, and who must resolve it for a stated use. You can review the bundle without assuming its proposed meanings have been accepted.

## Domain-context voice

Workspace: `workspace:cyberalchemy-lab`

In the Lab, the candidate CLI pack is input to a separate preparation Method. That Method may reference existing meanings, prepare complete Definition/v2 candidates, or preserve blockers. The outer CLI result schema and finite readiness checks do not currently enforce this entire proposed contract.

### Examples

- An incident pack reuses an exact Incident Definition, proposes an identifier-coverage meaning and keeps an unknown account-exclusivity criterion open.
- A pack containing only reuse and open dispositions creates no new Definition candidate.
- An owner can admit one exact prepared Definition without accepting every concept or closing the incident.

## Applicability

Shared meaning for the Lab-owned Define integration and its explicitly named consumers. This proposed meaning does not adopt the upstream runtime or every historical package record.

### Exclusions

- Canonical definition admission by candidate generation.
- Permission to execute consumer work.
- Authority to change an external organization or production system.

## Boundaries

- An open concept is a recorded unresolved outcome; it is not an omitted answer or a proposed Definition.
- One pack may produce zero, one or many Definition candidates; it is not itself one Definition.
- An unchanged-meaning parameter binding may narrow a use. A changed normative meaning requires an explicit new Definition identity or successor route. The specialize label cannot decide that route alone.
- A changed selected input, meaning, consumer use or disposition requires a new frozen revision and lineage.
- Owner routing hints do not establish Role Assignments. Relationship suggestions do not declare global Typed Relations.
- Validation posture, source currency, disposition, consumer readiness and admission are separate; dependencies between them must be explicit.
- A separate owner Decision may admit selected outputs or authorize a named use; it does not rewrite the pack as a Decision or confer authority on unselected contents.
- Input disposition rows must be unique and closed over C before constructing delta; duplicate overwrite is invalid.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | /voices/scientific_formal/normative_statement | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.source@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `aefe53df65d0697772ccb565ec9c279927b1ace67bfd770d2dd959309f11d63a` | `admitted` |
| cal.definition.review@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d` | `admitted` |
| cal.definition.decision-scope@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `1bc60f945b301ebede21fd1aae5f3bf12eff021437dc253b6bce1a772223f1f5` | `admitted` |
| cal.definition.typed-connection-extension-rule@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962` | `admitted` |

## Primary consumers

- define/INTEGRATION.md
- implementation/define-cli/v1/CONTRACT.md
- define/proposals/0005-amended-integration-plan/DESIGN.md

## Lookup and drift

- Index: `proposal:define-amended-integration-plan:candidate-index` / `cal.definition.definition-pack`
- Drift owner: `role:definition-owner`
- Audit: `proposal:define-amended-integration-plan:impact-manifest-pending`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- proposal:define-amended-integration-plan:source-lineage
- proposal:define-amended-integration-plan:formal-interpretation
- proposal:define-amended-integration-plan:risk-resolution

## Residue

- exact-semantic-owner-decision-pending
- v2-profiles-and-required-representation-amendment-pending
- required-formal-and-fidelity-evidence-pending
- declared-consumer-impact-closure-pending
- exact-admission-postimages-pending

## Claim ceiling

Revised authored Definition/v2 candidate in the amended work plan. Source lineage is candidate evidence; governing source_refs retain their admitted scope. No formal assurance execution, source promotion, semantic admission, runtime adoption or action authority.
