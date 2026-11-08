<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Export identifier completeness

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.export-identifier-completeness`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-authority`
- Lifecycle posture reference: `candidate:define-pack-lab-mapping:authored`

## Scientific/formal voice

For a fixed source snapshot S, declared account A, declared filters F and saved output E, export identifier completeness holds exactly when every identifier required by S, A and F appears in E.

```text
CompleteIds(S,A,F,E) iff RequiredIds(S,A,F) subseteq ExportedIds(E).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| S | One fixed, identified source snapshot. |
| A | The declared account whose records are required. |
| F | The declared filters evaluated against S within A. |
| E | One saved, identified export output. |
| RequiredIds(S,A,F) | The established set of identifiers required by S, A and F. |
| ExportedIds(E) | The set of identifiers actually present in E; multiplicity is ignored. |
| subseteq | Every member of the required set appears in the exported set; equality and absence of extras are not asserted. |

### Boundary conditions

- The required population must be established; an unknown population is not an empty set.
- Use the same fixed snapshot, account and filter semantics in the expected population and export comparison.
- A genuinely established empty required set satisfies the coverage criterion.
- Extra identifiers, duplicate rows, inaccurate values, and closure decisions require separate criteria.

### Testable conditions

- Every required identifier present implies CompleteIds=true.
- One missing required identifier implies CompleteIds=false.
- Equal row counts with duplicate IDs can still fail identifier completeness.
- All required IDs with inaccurate values pass coverage while accuracy can fail.
- Without an established required population, the criterion is not evaluable.

## Plain-language voice

Every required row identifier for the chosen account, filters and snapshot must appear in the saved output.

## Domain-context voice

Workspace: `example:INC-1042-Northstar-export-investigation`

The agent investigates INC-1042 using saved S-1042, the Northstar account, status=active filters and E-1042. The synthetic missing-ID case has 12,000 required identifiers and 11,800 unique exported identifiers, leaving 200 missing. This applies the proposed criterion and does not establish an actual production finding.

### Examples

- The missing-ID fixture fails identifier coverage.
- A retry containing all 12,000 required IDs passes coverage; the incident still needs its independent accuracy, exclusivity and closure reviews.
- A file with 12,000 rows but 200 duplicates replacing required IDs still fails coverage.

## Applicability

A proposed shared identifier-coverage criterion for Lab export investigations with fixed, identified S, A, F and E and an established required identifier population. It does not assert an external customer policy.

### Exclusions

- Value accuracy.
- Account exclusivity, extra identifiers and unauthorized disclosure.
- Duplicate-row multiplicity and row ordering.
- Live-source or cross-snapshot consistency.
- Permission to run extraction, repair production, or close an incident.

## Boundaries

- Coverage is a semantic criterion, not a Measurement Method, Measurement Result, Finding or Decision.
- An admitted meaning would govern only its exact scope; it grants no agent permission.
- A fixed account and filters identify the required population, but this coverage predicate does not itself forbid extra account records.
- Changing an application to a different snapshot requires a new evidence comparison; changing the normative meaning requires a new Definition version.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole exact governing Definition record; structure and authority boundary only | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |

## Primary consumers

- example:work:INC-1042-investigation
- example:evaluation:INC-1042-identifier-coverage

## Lookup and drift

- Index: `proposal:define-pack-lab-mapping:registry-postimage` / `cal.definition.export-identifier-completeness`
- Drift owner: `role:definition-owner`
- Audit: `proposal:define-pack-lab-mapping:drift-audit-postimage`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

No typed relations declared.

## Evidence

- definition-pack:9543947b1a56cbf954560862a5be21d3fd1b6cd9399087d93da8ab56d67ec2e1
- proposal:define-pack-lab-mapping:incident-ticket
- proposal:define-pack-lab-mapping:criterion-cases
- proposal:define-pack-lab-mapping:field-lineage

## Residue

- mapping-policy-not-admitted
- exact-semantic-owner-review-pending
- example-consumers-unadmitted
- domain-applicability-review-pending
- exact-definition-admission-decision-pending

## Claim ceiling

Proposed Definition/v2 mapping specimen. No definition admission, source promotion, accepted incident finding, consumer adoption, agent permission or incident closure is asserted.
