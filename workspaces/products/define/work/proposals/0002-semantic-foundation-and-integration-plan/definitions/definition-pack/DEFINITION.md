<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Definition Pack

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.definition-pack`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `proposal:define-semantic-foundation-and-integration:candidate-authored`

## Scientific/formal voice

A Definition Pack is an identifiable, version-exact, reviewable bundle that freezes a bounded goal, originating intent, context and named intended use together with the required concept set, exactly one current handling disposition per concept, its disposition payload, exact source and evidence standing, owner routes, relationship scope, unresolved obligations and validation scope. Its handling dispositions are reuse, specialize, propose and open. Reused meanings remain bound to their exact authority; candidate meanings and unresolved obligations remain identifiable. Pack existence, validation or consumer readiness grants no new semantic admission or permission to execute.

```text
P=(id,revision,g,i,k,u,C,delta,H,E,O,R,Q,V); D={reuse,specialize,propose,open}; WellFormed(P) iff ExactIdentity(P) and Bounded(g,k,u) and Traceable(g,i) and NonEmpty(C) and dom(delta)=C and forall c in C: ExactlyOne(delta(c) in D) and PayloadMatches(H(c),delta(c)) and forall r in References(P): ResolvedWithStanding(r) or DeclaredGap(r,Q) and ValidationScopeDeclared(V). WellFormed(P) does not imply ConsumerReady(P,u), Admitted(candidate(P)), or MayExecute(u).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| P | One exact frozen pack revision; this tuple is a semantic contract, not a particular wire schema. |
| g,i,k,u | Bounded goal, attributable originating intent, declared context and named consumer with intended use. |
| C,delta,H | Nonempty required concept set, total single-valued current disposition map and matching per-concept payloads. |
| E,O,R,Q,V | Exact source/evidence standing, owner routes, scoped relationship records, explicit unresolved obligations and bounded validation results. |
| References(P) | References relevant to the named use; unresolved references carry their own visible gaps. |
| ConsumerReady(P,u) | A separate use-specific assessment of blocking obligations; this cannot grant authority. |

### Boundary conditions

- An open concept is a recorded unresolved outcome; it is not an omitted answer or a proposed Definition.
- One pack may produce zero, one or many Definition candidates; it is not itself one Definition.
- An unchanged-meaning parameter binding may narrow a use. A changed normative meaning requires an explicit new Definition identity or successor route. The specialize label cannot decide that route alone.
- A changed selected input, meaning, consumer use or disposition requires a new frozen revision and lineage.
- Owner routing hints do not establish Role Assignments. Relationship suggestions do not declare global Typed Relations.
- Validation posture, source currency, disposition, consumer readiness and admission are separate; dependencies between them must be explicit.
- A separate owner Decision may admit selected outputs or authorize a named use; it does not rewrite the pack as a Decision or confer authority on unselected contents.

### Testable conditions

- Every required concept has exactly one current disposition; duplicate, absent and undeclared dispositions violate the contract.
- An unresolved source or owner reference is visible as a scoped gap rather than labeled resolved.
- A structurally reviewable pack with a blocking open concept cannot be advertised as ready for its blocked consumer action.
- Accepted reuse retains the exact current source authority without fabricating a new admission.
- Pack PASS does not establish semantic-owner acceptance or agent action permission.

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

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.source@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `aefe53df65d0697772ccb565ec9c279927b1ace67bfd770d2dd959309f11d63a` | `admitted` |
| cal.definition.review@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d` | `admitted` |
| cal.definition.decision-scope@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `1bc60f945b301ebede21fd1aae5f3bf12eff021437dc253b6bce1a772223f1f5` | `admitted` |
| cal.definition.typed-connection-extension-rule@1.0.0-candidate.1 | whole exact Definition record; governing concept and boundary | `9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962` | `admitted` |
| define/source/cyberAlchemy-v2/define/definitions.json | /proposals/1 | `3ec8809ce4cede3074ccec6ff125ce7f02572042c7086afd5e1ccfd84bd45dc5` | `candidate-unadmitted` |

## Primary consumers

- define/INTEGRATION.md
- implementation/define-cli/v1/CONTRACT.md
- define/proposals/0001-definition-pack-lab-mapping/mapping.json

## Lookup and drift

- Index: `proposal:define-semantic-foundation-and-integration:candidate-index` / `cal.definition.definition-pack`
- Drift owner: `role:definition-owner`
- Audit: `proposal:define-semantic-foundation-and-integration:gap-plan`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- proposal:define-semantic-foundation-and-integration:semantic-coverage
- proposal:define-semantic-foundation-and-integration:distinction-review

## Residue

- exact-semantic-owner-review-pending
- v2-evaluation-lifecycle-binding-pending
- candidate-upstream-source-disposition-pending
- exact-admission-postimages-pending
- consumer-and-product-adoption-pending
- exact-admission-decision-pending

## Claim ceiling

Authored proposed Lab meaning using Definition/v2. Candidate upstream lineage remains unadmitted. No admission readiness, product ownership, runtime adoption, execution authority or global semantic consistency is established.
