[Documentation home](../../README.md)

# Definition

<a id="def-cal-definition-definition"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Definition

# Definition

An owner-controlled record stating exactly what a term means, where that meaning applies and how drift can be challenged. Acceptance is separate from draft checks or explanatory wording.

**When it applies**

When a shared meaning needs an exact version, accountable owner, scope and boundaries.

**Record formats**

[Definition · v2](type-cal-artifact-type-definition-v2.md#type-cal-artifact-type-definition-v2)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The owner-accepted completeness criterion governs identifier coverage for Northstar, the declared filters and S1.

**Common mistake**

Treating a generated summary or an unaccepted draft as an accepted definition.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-definition-section-2"></a>

## Source explanatory wording

The project-owned record that says exactly what a term means, where that meaning applies, and how drift can be challenged. A passing candidate is not canonical until its owner admits it.

<a id="def-cal-definition-definition-section-3"></a>

## Exact governing statement

A Definition is a versioned, owner-scoped semantic artifact that assigns a term one normative meaning within an exact authority scope. It is structurally complete only when stable identity, applicability, exclusions, a scientific/formal normative voice, explicitly non-normative plain-language and domain-context voices, boundaries, admitted source posture, primary consumers, a synchronized registry postimage, generated index, and a current drift route are declared. Only an exact owner promotion decision can make one exact Definition version canonical authority.

````
DefinitionComplete(d) iff StableId(d) and ExactScope(d) and FormalVoice(d) and NonNormativePlainVoice(d) and NonNormativeDomainVoice(d) and Boundaries(d) and AdmittedSources(d) and RegistryPostimage(d) and GeneratedIndex(d) and CurrentDriftRoute(d). DefinitionComplete(d) does not imply Admitted(d).
````

- A changed normative meaning requires a new Definition version.
- Interpretive voices cannot weaken or expand the normative voice.
- Schema validity and evidence do not perform promotion.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition and initial context promotion

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/definition/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.definition@1.0.0-candidate.1

**Content fingerprint · SHA-256**

eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-shared-authority",
  "applicability": "Normative meanings intentionally shared across CyberAlchemy Lab authority and construction surfaces.",
  "exclusions": [
    "Context-local expressions that have no shared semantic role.",
    "Generated summaries, glossary hints, and source quotations."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
