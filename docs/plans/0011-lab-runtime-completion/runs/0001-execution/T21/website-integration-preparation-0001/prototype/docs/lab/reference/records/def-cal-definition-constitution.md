[Documentation home](../../README.md)

# Constitution

<a id="def-cal-definition-constitution"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Constitution

# Constitution

A versioned, owner-scoped rulebook for selected kinds of subject. Its requirements apply only after the exact version and scope are adopted and the subject matches its selectors; loading it into context does not adopt it.

**When it applies**

Use a constitution when a recurring class of future subjects needs the same authoritative constraints, ownership, precedence, examples, and validation expectations. Keep one-off advice, observations, and owner decisions outside it. A discipline may gather evidence and route a constitution proposal, but cannot author or adopt the constitution. A validator may check an adopted rule, but cannot supply the authority that the constitution and owner decision provide.

**Record formats**

[Constitution · v1](type-cal-artifact-type-constitution-v1.md#type-cal-artifact-type-constitution-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-constitution-section-2"></a>

## Source explanatory wording

A constitution is a named rulebook for named things. It says which rules apply, to what, under whose authority, and how conflicts and checks work. It is not a universal prompt for every person, agent, repository, or external system.

<a id="def-cal-definition-constitution-section-3"></a>

## Exact governing statement

Constitution is the normalized definition identified by semantic.constitution, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D58 without silently merging it with another target.

Bound source-semantic basis:

A constitution is an **owner-scoped, selector-bound, composable authority artifact** that turns axioms and invariants into reusable governance rules and policies for named kinds of governed subject. Those subjects may be artifacts, tasks or workflows, repository-owned agent actions, system operations or state transitions, validation surfaces, or authority movements.

A constitution must declare its scope, subject kinds, selectors, owner route, authority level, rules and policies, precedence and composition behavior, validation modes or bindings, downstream effect, challenge route, and retirement or split conditions. It constrains a subject only after an owner decision adopts the exact constitution version and scope and the subject matches its selectors. A candidate, selected, or context-loaded constitution does not govern by those facts alone.

````
```text
Constitution C =
  (id, version, scope, subject_kinds, selectors, rules, policies,
   precedence, composition, owner_route, authority_level,
   validation_bindings, downstream_effect, challenge_route,
   retirement_or_split_rule)

subject_kinds(C) subset-of
  { artifact, task_or_workflow, repository_owned_agent_action,
    system_operation_or_state_transition, validation_surface,
    authority_movement }

applies(C, subject) <->
  promoted(C) and version_exact_owner_adoption(C) and
  subject in scope(C) and selector_matches(C, subject)

validation_mode(rule) in { deterministic, review, hybrid, none-yet }
candidate(C) or selected(C) or context_loaded(C) =/=> applies(C, subject)
```

Schema handle: `CAV2-D58-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary);
no machine validator is activated by this definition.
````

- A constitution is **not** an axiom (`CAV2-D53`), invariant (`CAV2-D54`), discipline (`CAV2-D50`), decision, validator, gate (`CAV2-D37`), evidence, or proof. Axiom grounds; invariant states what must remain true; governance rule or policy operationalizes; discipline stewards a recurring practice; owner decision adopts; constitution carries the adopted constraints; validator or gate checks or performs enforcement. Authority (`CAV2-D34`) scopes every part of that graph. Promoting this term creates Definition authority for the meaning of `constitution`. It does not promote any constitution artifact, adopt a rule or policy, activate a validation binding, or authorize an effect.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/ed01aeb7e833-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.constitution@1.0.0-candidate.1

**Content fingerprint · SHA-256**

ed01aeb7e83336774412a31bb3798fb3650377874e135e84036771af9ecf434b

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use a constitution when a recurring class of future subjects needs the same\nauthoritative constraints, ownership, precedence, examples, and validation\nexpectations. Keep one-off advice, observations, and owner decisions outside it.\nA discipline may gather evidence and route a constitution proposal, but cannot\nauthor or adopt the constitution. A validator may check an adopted rule, but\ncannot supply the authority that the constitution and owner decision provide.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
