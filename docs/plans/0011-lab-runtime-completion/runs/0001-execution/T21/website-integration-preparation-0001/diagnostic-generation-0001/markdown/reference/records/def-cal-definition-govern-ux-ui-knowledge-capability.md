[Documentation home](../../README.md)

# Govern UX/UI Knowledge

<a id="def-cal-definition-govern-ux-ui-knowledge-capability"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Govern UX/UI Knowledge

# Govern UX/UI Knowledge

The process for retaining and reviewing interface evidence and lessons without treating appearance, screenshots or passing browser checks as proof of human experience.

**When it applies**

Use UX/UI knowledge governance when UI work produces reusable lessons, design patterns, validation claims, accessibility claims, layout evidence, interaction evidence, or subjective experience claims. Route lesson capture through `ux-lessons`, validator-safe evidence through `ux-evidence-validator`, studio mutation intents through `ui-prototyping-studio`, and promotion through the CyberAlchemy authority model.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-govern-ux-ui-knowledge-capability-section-2"></a>

## Source explanatory wording

UX/UI governance is how the project remembers interface learning without pretending that a nice-looking screen, a screenshot, or a passing browser test is automatically truth.

<a id="def-cal-definition-govern-ux-ui-knowledge-capability-section-3"></a>

## Exact governing statement

Govern UX/UI Knowledge is the normalized product-capability identified by semantic.govern-ux-ui-knowledge-capability, owned within scope.ux-ui, and carried by type.product-capability. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D45 without silently merging it with another target.

Bound source-semantic basis:

UX/UI knowledge governance is the CyberAlchemy v2 lens-specific governance interface that turns interface iteration, browser evidence, accessibility evidence, visual evidence, interaction traces, user-study residue, and reusable experience lessons into governed candidates without treating subjective experience quality as automatic authority.

It must separate at least these lanes:

- captured interface lesson - reusable UX/UI pattern candidate - browser-observable evidence - accessibility and semantic evidence - layout and interaction evidence - cognitive or attention risk proxy - domain-practice heuristic - human-study or expert-review residue - promotion request and owner decision

UX/UI knowledge governance can produce candidate lessons, patterns, claim maps, validator specs, fixture plans, studio annotation intents, evidence reports, and promotion requests. It does not promote UX/UI authority by itself.

````
For interface knowledge object `u`, CyberAlchemy v2 tracks:

```text
UXG(u) =
  (lesson_ref, pattern_candidate, browser_evidence, accessibility_evidence,
   layout_interaction_evidence, cognitive_attention_proxy,
   domain_practice_claim, human_study_residue,
   owner_route, promotion_path, challenge_contract)
```

The object is authority-bearing only when the relevant owner route records the
promotion effect and the claim strength remains bounded by available evidence.
````

- UX/UI knowledge governance is not a universal UX score, not an accessibility certificate, not a design-system authority, not a human-study substitute, not a studio mutation approval, and not a promotion event.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/384ae660674c-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.govern-ux-ui-knowledge-capability@1.0.0-candidate.1

**Content fingerprint · SHA-256**

384ae660674c8afc14816922ced8b36dc99eb70e7c082b8d1c33bd044b43a442

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use UX/UI knowledge governance when UI work produces reusable lessons, design\npatterns, validation claims, accessibility claims, layout evidence, interaction\nevidence, or subjective experience claims. Route lesson capture through\n`ux-lessons`, validator-safe evidence through `ux-evidence-validator`, studio\nmutation intents through `ui-prototyping-studio`, and promotion through the\nCyberAlchemy authority model.",
  "authority_scope_ref": "scope.ux-ui",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
