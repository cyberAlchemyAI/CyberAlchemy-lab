[Documentation home](../../README.md)

# Discipline

<a id="def-cal-definition-discipline"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Discipline

# Discipline

A recurring practice across capabilities with evidence, a steward and a hardening route. Recurrence supports review but does not itself promote the practice to authority.

**When it applies**

Use when a recurring practice spans capabilities and needs a steward + hardening path (AUTHORITY-MODEL narrowest-owner rule: *"a recurring practice needs a steward and hardening path → discipline-governance"*). It turns a habit into a governed, hardenable practice rather than ad-hoc repetition.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-discipline-section-2"></a>

## Source explanatory wording

A habit the project does across many capabilities — named and hardened so it's done consistently. It earns authority by recurring and being stewarded, not by being declared.

<a id="def-cal-definition-discipline-section-3"></a>

## Exact governing statement

Discipline is the normalized definition identified by semantic.discipline, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D50 without silently merging it with another target.

Bound source-semantic basis:

A discipline is a **recurring, cross-capability practice** promoted to authority via **discipline-governance** — cataloged in `../../disciplines/` with a steward/owner, evidence that it already recurs, a maturity status (`candidate -> active-pattern -> canonical`), and a named hardening route. Evidence of recurrence alone does **not** self-promote a discipline; the owner route does.

````
```text
Discipline = (practice, steward/owner, recurrence_evidence, maturity_status, hardening_move)
maturity_status in { candidate, active-pattern, canonical }
promotion: discipline-governance over the maturity ladder (never auto)
```

A discipline is valid only when it names its steward, recurrence evidence, maturity,
and hardening move; `CAV2-D38` bounds any claim of "canonical" to the evidence.
````

- A discipline is **not** a canonical term (definitions-governance owns terms), **not** a sigil, **not** a spell, **not** an implementation task (AUTHORITY-MODEL Authority Kinds "must not collapse into"), and **not** Craft method specifically (`CAV2-D20` is one discipline). Per AUTHORITY-MODEL non-collapse rule 4: *a discipline can recommend a route, but it cannot define a term or author a constitution.* It is **not** operational work (`CAV2-D20` Craft work-state) — authoring a discipline may be work, but the discipline-as-authority-kind is governance.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/discipline/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.discipline@1.0.0-candidate.1

**Content fingerprint · SHA-256**

afb74b043d7c3448f9e9580948afeb070a898a4252e31019c69b1b2558f8992f

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use when a recurring practice spans capabilities and needs a steward + hardening path\n(AUTHORITY-MODEL narrowest-owner rule: *\"a recurring practice needs a steward and\nhardening path → discipline-governance\"*). It turns a habit into a governed, hardenable\npractice rather than ad-hoc repetition.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
