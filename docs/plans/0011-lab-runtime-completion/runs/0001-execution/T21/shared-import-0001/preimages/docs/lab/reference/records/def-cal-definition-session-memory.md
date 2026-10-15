[Documentation home](../../README.md)

# Session Memory

<a id="def-cal-definition-session-memory"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Session Memory

Temporary working information owned by exactly one agent session. It ends with that session and cannot be shared as hidden private memory with another.

**When it applies**

When identifying temporary working memory owned by one Agent Session.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The current session holds temporary working notes while inspecting the comparison.

**Common mistake**

Relying on those notes as durable project knowledge after termination.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Session Memory is ephemeral working state owned by exactly one Agent Session and used only to continue that Session. Session Memory belongs to exactly one Agent Session and cannot be shared as private state with another Session.

## Exact governing statement

Session Memory is ephemeral working state owned by exactly one Agent Session and used only to continue that Session. It has no authority effect, cannot be canonical Project State, cannot silently survive termination, and cannot become hidden cross-session Machine Agent memory.

````
SessionMemory(m,s) => exactlyOneSession(m,s) and lifetime(m) subseteq lifetime(s) and authorityEffect(m)=none; end(s) => expired(m).
````

- Session Memory belongs to exactly one Agent Session and cannot be shared as private state with another Session.
- It has no authority effect and cannot satisfy a canonical dependency, evidence obligation, Decision basis, or Project State reference after expiry.
- Material survives only when an attributable Agent Action writes a separate governed artifact, event, evidence record, or receipt.
- Copying Session Memory into a later Session without governed persistence and new View selection is forbidden.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/session-memory/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.session-memory@1.0.0-candidate.1

**Content fingerprint · SHA-256**

60f0fe600f278b14c65a81da00726e470091c8f66bb7a8c1aa79d2ba147f2d45

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Session Memory is ephemeral working state owned by exactly one Agent Session and used only to continue that Session.",
  "authority_scope_ref": "scope:session-memory-definition",
  "exclusions": [
    "Session Memory belongs to exactly one Agent Session and cannot be shared as private state with another Session.",
    "It has no authority effect and cannot satisfy a canonical dependency, evidence obligation, Decision basis, or Project State reference after expiry.",
    "Material survives only when an attributable Agent Action writes a separate governed artifact, event, evidence record, or receipt.",
    "Copying Session Memory into a later Session without governed persistence and new View selection is forbidden.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
