<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Exact Publication Authorization Invariant

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.exact-publication-authorization-invariant`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.repository-governance`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Exact Publication Authorization Invariant is the normalized invariant identified by semantic.exact-publication-authorization-invariant, owned within scope.repository-governance, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D57 without silently merging it with another target.

Bound source-semantic basis:

Exact publication authorization is the CyberAlchemy v2 rule that private
material may cross a publication boundary only after two separate decisions:

1. every source owner authorizes an exact candidate slice, its allowed claims,
   audience, channel, privacy policies, and requested publishing principal; and
2. after private generation and privacy validation, that publishing principal
   approves the exact final output bytes, digest, audience, channel, and claim
   ceiling.

The first decision permits creation and review of a private publication
candidate. It does not permit unknown future bytes to be published. The second
decision applies only to the exact output it binds. Any change to the sources,
claims, policies, generator, output bytes, audience, channel, or publishing
principal requires the applicable decisions to be repeated.

All material is private by default when no valid exact authorization exists.
Generation, validation, proof, obligation discharge, CAV2 promotion, or domain
adoption does not grant publication permission.

```text
```text
PublicationAuthorization =
  (release_authorizations, exact_output_approval, publication_receipt?)

publishable(output, audience, channel)
  <-> every contributing source has a valid exact release authorization
      and privacy_validation(output) = pass
      and exact_output_approval binds
          (output bytes, output digest, audience, channel, claim ceiling)

generated(output) =/=> publishable(output, audience, channel)
validated(output) =/=> publishable(output, audience, channel)
promoted(output)  =/=> publishable(output, audience, channel)
```

Source owners and the publishing principal are separate authority roles. A
generator or validator may check that bindings exist and match; it cannot act as
either owner unless a separate authority decision explicitly assigns that role.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.exact-publication-authorization-invariant | Stable normalized identity for Exact Publication Authorization Invariant. |
| CAV2-D57 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Exact publication authorization is not classification authority, adoption,
promotion, proof, truth, freshness, privacy validation, deployment, or release by
itself. It does not create a universal classification vocabulary: each source
owner retains its own meanings, and a projection carries exact owner-qualified
references without reinterpreting them. It authorizes no present public output;
every actual publication still needs exact permissions and a boundary-crossing
receipt.

### Testable conditions

- The candidate identity remains cal.definition.exact-publication-authorization-invariant.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Permission to prepare a public draft is not permission to publish it. Owners
first approve the ingredients and limits; a publisher later approves the exact
finished file and destination.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Exact Publication Authorization Invariant is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2 this definition keeps the private authority spine and its
domain evidence private while still allowing a later, deliberately bounded
public explanation or result. A generated documentation page remains a private
projection until both decisions exist. Public Arcanum receives no private prose,
proof internals, engine mechanisms, research, or validation material merely
because a generator or checker succeeded.

### Examples

- Resolve semantic.exact-publication-authorization-invariant by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Exact Publication Authorization Invariant.

## Applicability

Use this definition when someone wants to turn private DomainSpec, CAV2,
proof-substrate, Mint, Cedar, Datalog, Lean, research, evidence, or generated
material into a public-safe output. First ask each source owner exactly what may
be used and said. Generate and check the candidate privately. Then ask the named
publishing principal about the final bytes, not a template or promise. If any
bound input or output changes, return to the relevant decision.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Exact publication authorization is not classification authority, adoption,
promotion, proof, truth, freshness, privacy validation, deployment, or release by
itself. It does not create a universal classification vocabulary: each source
owner retains its own meanings, and a projection carries exact owner-qualified
references without reinterpreting them. It authorizes no present public output;
every actual publication still needs exact permissions and a boundary-crossing
receipt.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D57 | ## CAV2-D57: Exact Publication Authorization | `1234325bacabe593f4924bd9cf55562ea4ffc52909d70686da270def84e5ffd9` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.exact-publication-authorization-invariant@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.exact-publication-authorization-invariant | cyberalchemy-v2:CAV2-D57 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-exact-publication-authorization-invariant/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
