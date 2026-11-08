# Ontology derived from Alch

For `declarative-function-v1`, author the program once. Alch derives missing ontology bindings before DomainSpec validates the typed model. Every build emits `ontology.json`, and these read-only commands expose the same model without building a bundle:

```sh
node dist/cli.js ontology ../extensions/derived-ontology-v1/quantity-price.alch
node dist/cli.js explain ../extensions/derived-ontology-v1/quantity-price.alch Cheapest
```

`ontology` returns the complete JSON scaffold. `explain` accepts one exact declaration name or ontology ID and returns its meaning, typed definition, source clauses and dependencies. It explains static source semantics; it does not assert why an individual runtime invocation selected a price. Both commands validate the source before answering and write only stdout.

## Minimal authored source

```text
query Cheapest:
  meaning "Eligible tiers with no strictly cheaper eligible witness; preserve every tie."
  from p in Eligible
  where not (exists q in Eligible: q.amountMinor < p.amountMinor)
  select p
```

`meaning` is optional. Without it, the compiler supplies a clearly marked structural description; it does not invent a business rationale. The compiler derives nodes, field types and cardinalities, schema constraints, typed behavior, source references, and integration/endpoint bindings from the declarations. Entity, Mapping, Query, Rule, Calculation and Interface retain their existing meanings. Boundary schemas and target integration bindings are explicitly identified without inventing new DomainSpec meta-types.

The output marks every description as `authored` or `derived-structural`, and includes exact source paths, line numbers and source hashes. Explanations cite authored descriptions at their actual annotation lines. Record properties retain their declaration and description provenance. Compiler reference roles such as maps-from, maps-to, calls and depends-on are navigation evidence, not automatically admitted ontology relationship types.

## Identity and overrides

A derived declaration ID is deterministic from the domain ID, declaration kind and stable key. The key defaults to the declaration name. Comments, formatting, descriptions, declaration order and filesystem location do not enter this identity. Renaming a declaration normally changes its ID; preserve the old key explicitly when it is the same concept:

```text
query Best:
  key "Cheapest"
  from p in Eligible
  where not (exists q in Eligible: q.amountMinor < p.amountMinor)
  select p
```

Use an explicit binding to retain an existing ontology identity, including when moving domains:

```text
query Cheapest:
  ontology "EXISTING-PRICE-SELECTION"
  ...
```

The last example is abbreviated; `...` is not language syntax. Removing an existing explicit ontology ID changes its binding to the generated ID. Retain that override when migrating an existing identity. Duplicate keys or ontology IDs fail validation.

Core `ontology Name:` blocks remain supported as optional overrides. Missing IDs, descriptions and property bindings are filled from the declarations. Conflicting inline and block annotations fail rather than silently overwriting one another. Core property selectors retain DomainSpec's `parentId#fieldName` convention; a property rename therefore changes its identity in this version.

For an Entity, exactly one required `identifier` field provides an unambiguous identity candidate. Otherwise author `identity fieldName` in the entity or its optional ontology block. The selected field must be a required identifier/string field; the compiler never chooses between multiple candidates. `key`, `meaning` and `ontology` annotations are supported on declarative-profile declarations, including boundary schemas, integrations and the result Query.

## Construction and open questions

`ontology.json` is a generated scaffold with `authority_effect: none` and `ontology_admitted: false`. It is not product approval, registry admission or composition certification. Meta-Type Factory automation remains deferred. The existing core certificate keeps its original scope; the composition and derived ontology artifacts do not expand it.

Use [invocation traces](INVOCATION-TRACES.md) for source-linked observations of a local run. Future work includes property rename migrations, broader ontology certification, and persisted or remote trace verification. Other Alch profiles retain their existing binding requirements. See ../../extensions/derived-ontology-v1/PLAN.md for the construction frontier and operational residue.
