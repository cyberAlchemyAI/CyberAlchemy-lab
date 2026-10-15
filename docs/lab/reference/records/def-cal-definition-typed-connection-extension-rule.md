[Documentation home](../../README.md)

# Typed Connection Extension Rule

<a id="def-cal-definition-typed-connection-extension-rule"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Typed Connection Extension Rule

# Typed Connection Extension Rule

Specifies how new global connection kinds or permitted pairs are declared, reviewed and admitted with endpoint contracts, ownership and challenge rules. Local graph edges and endpoint registration do not create global permission.

**When it applies**

Proposing one additional global ordered source endpoint kind to target endpoint kind connection under an existing Relation Kind, proposing a distinct Relation Kind when the semantic question differs, or proving that an ontology-local connection remains bounded to one exact Ontology contract.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Creating relation instances or admitting endpoint carriers.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-typed-connection-extension-rule-section-2"></a>

## Source explanatory wording

A new kind of wire must name its two plug types, purpose, labels, owner, challenge route, and one authoritative record. Both plug contracts must exist. A wire drawn only inside one Ontology stays local. Adding a plug, copying a local wire, or validating a draft does not connect anything globally.

<a id="def-cal-definition-typed-connection-extension-rule-section-3"></a>

## Exact governing statement

The Typed Connection Extension Rule requires every global Relation Kind to expose a finite closed set of exact ordered source-kind to target-kind connections. A proposed extension must bind one effective predecessor Relation Kind version, one source endpoint contract, one target endpoint contract, direction, global scope, an exact qualifier schema with pair-specific values and constraints, canonical relation authority, contestability, owner, evidence, lifecycle effect, validation effect, and the exact successor contract version. It may reuse the Relation Kind only when the same unique semantic question remains intact; otherwise it must propose a distinct Relation Kind. Ontology-local connections must remain scoped to their exact Ontology contract. No global connection is created by endpoint registration, separate source and target lists, wildcard matching, historical observation, local graph use, shared naming, candidate validation, endpoint admission, or a second writable projection.

````
For each global Relation Kind r, Conn(r) is a finite closed set of ordered pairs (s,t) in K x K. ValidExtend(r@v,s,t,r@v_prime) requires Effective(r@v), Resolved(s), Resolved(t), SameQuestion(r@v,r@v_prime), PairQualifierSchema(r@v_prime,s,t), CanonicalAuthority(r@v_prime,s,t) in {TypedRelation, SpecializedCarrier}, Contestable(r@v_prime,s,t), and exact owner, evidence, lifecycle, validation, and successor bindings. A relation instance e conforms only when (kind(source(e)),kind(target(e))) is in Conn(r@v_prime), direction and qualifiers validate, and the exact contract is admitted and effective. Local(o,s,t) does not imply (s,t) in Conn(r). Register(k) does not imply any (k,x) or (x,k) in Conn(r).
````

- Conn(r) contains ordered endpoint-kind pairs, so (s,t) and (t,s) are distinct unless both are explicitly declared.
- SourceKinds(r) and TargetKinds(r) are generated projections of Conn(r); they do not authorize SourceKinds(r) x TargetKinds(r).
- The effective predecessor version must be resolved through exact decision and succession overlays before a successor pair set is computed.
- Both endpoint kinds must resolve to admitted carriers or explicitly permitted governed internal record contracts.
- Each pair binds a qualifier schema, allowed values, and cross-qualifier constraints; open qualifier strings do not close the connection contract.
- One canonical relation authority is selected. A specialized carrier projection and generic Typed Relation cannot both accept independent writes.
- Global and ontology-local scope are distinct. Local(o,s,t) supplies no global pair.
- Every effective contract supplies contestability, owner, evidence, lifecycle, and authority-effect boundaries.
- Only an exact admitted successor Relation Kind contract makes a proposed global pair available.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Typed Connection Extension Rule admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0012-typed-connection-extension-rule/definitions/typed-connection-extension-rule/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.typed-connection-extension-rule@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Proposing one additional global ordered source endpoint kind to target endpoint kind connection under an existing Relation Kind, proposing a distinct Relation Kind when the semantic question differs, or proving that an ontology-local connection remains bounded to one exact Ontology contract.",
  "authority_scope_ref": "scope:typed-connection-extension-rule-definition",
  "exclusions": [
    "Creating relation instances or admitting endpoint carriers.",
    "Inferring connections from separate source and target indexes.",
    "Changing Relation Kind meaning through an endpoint extension.",
    "Using wildcard or catch-all endpoint kinds.",
    "Publishing ontology-local edges as global connections without a separate admitted global contract.",
    "Treating a specialized binding and its Typed Relation projection as two writable authorities.",
    "Treating candidate validation, structural conformance, or endpoint admission as connection admission."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
