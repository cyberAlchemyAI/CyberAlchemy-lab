[Documentation home](../../README.md)

# Interface Claim-Support Compatibility Invariant

<a id="def-cal-definition-interface-claim-support-compatibility-invariant"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Interface Claim-Support Compatibility Invariant

Browser evidence can support claims about what occurred on a page. Claims about human understanding, trust or preference need suitable human evidence.

**When it applies**

Use interface evidence boundary when writing validator specs, Playwright reports, UI review findings, UX pattern cards, screenshot reviews, or studio mutation handoffs. Ask whether the claim is deterministic, a risk proxy, a visual review prompt, a human-study need, or not automatable.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A browser can show what happened on the page. It cannot by itself prove what a human understood, trusted, felt, or preferred.

## Exact governing statement

Interface Claim-Support Compatibility Invariant is the normalized invariant identified by semantic.interface-claim-support-compatibility-invariant, owned within scope.ux-ui, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D47 without silently merging it with another target.

Bound source-semantic basis:

Interface evidence boundary is the CyberAlchemy v2 rule that UX/UI claims must state which kind of evidence can support them and what that evidence cannot prove.

At minimum, UX/UI claims must be classified as one of:

- hard gate - soft flag - screenshot review - human study - not automatable

Browser automation may directly support page-load, accessibility-tree, keyboard, layout, interaction, screenshot, trace, console/network, and DOM measurement claims. It may prepare evidence for cognitive, attention, perception, trust, comprehension, delight, and real-user success claims, but it must not turn them into deterministic authority without calibrated fixtures and owner approval.

````
For UX/UI claim `c`, let:

```text
IEB(c) = (claim_class, evidence_kind, proxy_limit, owner_route, residue)
```

The claim is valid only when `claim_class` matches `evidence_kind` and the
`proxy_limit` states what remains unproven. If the evidence class is weaker than
the claim, `CAV2-D38` requires downgrading, routing, or blocking the claim.
````

- Interface evidence boundary is not a validator implementation, not a complete accessibility audit, not user research, not a universal UX score, and not a license to block dense expert interfaces without false-positive calibration.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/interface-claim-support-compatibility-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.interface-claim-support-compatibility-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

59775ceff8eff5c7683b8c2513b669a0b20b3b38a5f93c124e62d2fd28c4ced7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use interface evidence boundary when writing validator specs, Playwright\nreports, UI review findings, UX pattern cards, screenshot reviews, or studio\nmutation handoffs. Ask whether the claim is deterministic, a risk proxy, a\nvisual review prompt, a human-study need, or not automatable.",
  "authority_scope_ref": "scope.ux-ui",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
