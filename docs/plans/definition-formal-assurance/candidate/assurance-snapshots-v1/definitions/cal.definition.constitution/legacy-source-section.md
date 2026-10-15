## CAV2-D58: Constitution

Status: active
Term: constitution
Aliases: governed constitution, modular constitution, structure constitution, constitution artifact
Promoted: 2026-08-29 by owner-requested definitions defect repair; definition authority only, with no constitution, rule, policy, validator, or gate activation

### Normative Definition

A constitution is an **owner-scoped, selector-bound, composable authority
artifact** that turns axioms and invariants into reusable governance rules and
policies for named kinds of governed subject. Those subjects may be artifacts,
tasks or workflows, repository-owned agent actions, system operations or state
transitions, validation surfaces, or authority movements.

A constitution must declare its scope, subject kinds, selectors, owner route,
authority level, rules and policies, precedence and composition behavior,
validation modes or bindings, downstream effect, challenge route, and retirement
or split conditions. It constrains a subject only after an owner decision adopts
the exact constitution version and scope and the subject matches its selectors.
A candidate, selected, or context-loaded constitution does not govern by those
facts alone.

### Formal Interpretation

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

### Operational Interpretation

Use a constitution when a recurring class of future subjects needs the same
authoritative constraints, ownership, precedence, examples, and validation
expectations. Keep one-off advice, observations, and owner decisions outside it.
A discipline may gather evidence and route a constitution proposal, but cannot
author or adopt the constitution. A validator may check an adopted rule, but
cannot supply the authority that the constitution and owner decision provide.

### Plain-Language Intuition

A constitution is a named rulebook for named things. It says which rules apply,
to what, under whose authority, and how conflicts and checks work. It is not a
universal prompt for every person, agent, repository, or external system.

### Domain-Context Voice

In CyberAlchemy v2, Constitution is one closed authority kind in
[AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md). The candidate
[Stable Repository Constitution](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
is an instance candidate; this definition does not promote or activate it. A
repository constitution cannot override system, developer, host, external-owner,
or other higher-precedence authority outside its declared scope.

### Boundary

A constitution is **not** an axiom (`CAV2-D53`), invariant (`CAV2-D54`),
discipline (`CAV2-D50`), decision, validator, gate (`CAV2-D37`), evidence, or
proof. Axiom grounds; invariant states what must remain true; governance rule or
policy operationalizes; discipline stewards a recurring practice; owner decision
adopts; constitution carries the adopted constraints; validator or gate checks or
performs enforcement. Authority (`CAV2-D34`) scopes every part of that graph.

Promoting this term creates Definition authority for the meaning of
`constitution`. It does not promote any constitution artifact, adopt a rule or
policy, activate a validation binding, or authorize an effect.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md)
- [../constitutions/](../constitutions/)
- [../../../.agents/skills/constitution-governance/SKILL.md](../../../.agents/skills/constitution-governance/SKILL.md)
