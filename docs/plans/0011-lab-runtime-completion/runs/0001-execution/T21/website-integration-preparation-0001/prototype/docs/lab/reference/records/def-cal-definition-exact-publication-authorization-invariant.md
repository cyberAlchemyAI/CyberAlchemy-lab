[Documentation home](../../README.md)

# Exact Publication Authorization Invariant

<a id="def-cal-definition-exact-publication-authorization-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Exact Publication Authorization Invariant

# Exact Publication Authorization Invariant

For private material, each source owner must authorize an exact candidate slice and its permitted use. After private generation and validation, the publishing principal separately approves the exact finished bytes, audience, channel and claim limits.

**When it applies**

Use this definition when someone wants to turn private DomainSpec, CAV2, proof-substrate, Mint, Cedar, Datalog, Lean, research, evidence, or generated material into a public-safe output. First ask each source owner exactly what may be used and said. Generate and check the candidate privately. Then ask the named publishing principal about the final bytes, not a template or promise. If any bound input or output changes, return to the relevant decision.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-exact-publication-authorization-invariant-section-2"></a>

## Source explanatory wording

Permission to prepare a public draft is not permission to publish it. Owners first approve the ingredients and limits; a publisher later approves the exact finished file and destination.

<a id="def-cal-definition-exact-publication-authorization-invariant-section-3"></a>

## Exact governing statement

Exact Publication Authorization Invariant is the normalized invariant identified by semantic.exact-publication-authorization-invariant, owned within scope.repository-governance, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D57 without silently merging it with another target.

Bound source-semantic basis:

Exact publication authorization is the CyberAlchemy v2 rule that private material may cross a publication boundary only after two separate decisions:

1. every source owner authorizes an exact candidate slice, its allowed claims, audience, channel, privacy policies, and requested publishing principal; and 2. after private generation and privacy validation, that publishing principal approves the exact final output bytes, digest, audience, channel, and claim ceiling.

The first decision permits creation and review of a private publication candidate. It does not permit unknown future bytes to be published. The second decision applies only to the exact output it binds. Any change to the sources, claims, policies, generator, output bytes, audience, channel, or publishing principal requires the applicable decisions to be repeated.

All material is private by default when no valid exact authorization exists. Generation, validation, proof, obligation discharge, CAV2 promotion, or domain adoption does not grant publication permission.

````
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
````

- Exact publication authorization is not classification authority, adoption, promotion, proof, truth, freshness, privacy validation, deployment, or release by itself. It does not create a universal classification vocabulary: each source owner retains its own meanings, and a projection carries exact owner-qualified references without reinterpreting them. It authorizes no present public output; every actual publication still needs exact permissions and a boundary-crossing receipt.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/24378c6653c4-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.exact-publication-authorization-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

24378c6653c419fdb2a079ebb164fbb3f4e38d8ba1b6828f6cb49b4aafae1822

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this definition when someone wants to turn private DomainSpec, CAV2,\nproof-substrate, Mint, Cedar, Datalog, Lean, research, evidence, or generated\nmaterial into a public-safe output. First ask each source owner exactly what may\nbe used and said. Generate and check the candidate privately. Then ask the named\npublishing principal about the final bytes, not a template or promise. If any\nbound input or output changes, return to the relevant decision.",
  "authority_scope_ref": "scope.repository-governance",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
