[Documentation home](../../README.md)

# Evidence

<a id="def-cal-definition-evidence"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Evidence

# Evidence

Inspectable material bearing on a particular claim within stated conditions. Support or opposition must be assessed; the material does not decide acceptance by itself.

**When it applies**

When inspectable material bears on a specific claim within a declared scope.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The saved comparison and inputs bear on the scoped identifier-omission claim.

**Common mistake**

Using evidence of omission as sufficient evidence of successful recovery.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-evidence-section-2"></a>

## Source explanatory wording

Evidence is something inspectable that bears on a specific claim. It can help prove or disprove that claim, but it does not decide by itself what is true or approved.

<a id="def-cal-definition-evidence-section-3"></a>

## Exact governing statement

Evidence is a provenance-bound observation or record E associated with an explicit claim C, subject S, scope Q, and currentness condition. Its evidential force is limited to the declared relation support(E,C,S,Q); collection, existence, or volume does not establish sufficiency or authority.

````
E = (evidence_id, claim_ref, subject_ref, provenance, scope, observed_at, currentness, content); exists(E) =/=> proves(C); supports(E,C,Q) only within Q.
````

- Evidence must identify its claim, subject, provenance, and scope.
- Stale or mismatched evidence cannot silently support a current claim.
- Evidence assessment and authority decisions remain separate.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0007-cml07-semantic-closure/definitions/evidence/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.evidence@1.0.0-candidate.1

**Content fingerprint · SHA-256**

748f0817911993a064c33f4cb59dcc69c8c2a9b061545fa0a56e8ccca8363da6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:evidence-definition",
  "applicability": "An inspectable, provenance-bound record capable of supporting, weakening, or leaving unevaluable one explicit claim within a declared scope.",
  "exclusions": [
    "The claim itself.",
    "Automatic proof, truth, acceptance, admission, or authority.",
    "Unscoped output whose subject, origin, or applicability cannot be resolved."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
