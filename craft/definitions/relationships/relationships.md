# DomainSpec Relationship Signatures

Root `definitions/relationships/` owns DomainSpec relationship authority. Implementation files may project
this surface, but validators read `relationships.yml` directly.

R3 defines a typed composable graph fragment, not full category law. See
[`domainspec-v2-D19`](../DEFINITIONS.md#domainspec-v2-d19).

The relationship non-collapse test is: a relationship is first-class only if removing it would change at least
one tracked property: reject/allow decision, derivation consequence, projection consequence, composition path
consequence, owner route consequence, or generated artifact consequence. See
[`domainspec-v2-D18`](../DEFINITIONS.md#domainspec-v2-d18).

The display notation `Source --[verb]--> Target` is human-facing projection only; authority lives in the
finite machine relation.

## Scope Tokens

Authored graph placement is either `same-feature` or `cross-feature`. Registry
tokens `ui` and `ui-backend` are same-feature UI/cross-layer lanes: they admit
edges in a feature's Concept Graph but do not admit a Cross-Feature Dependency.
Only a signature carrying `cross-feature` admits placement across feature
identities.

## Canonical Count

`relationships.yml` currently defines 31 active signatures.

The count is post-reconciliation:

- `enforces-cross` is deprecated; use `enforces` in the cross-feature dependency surface.
- `creates` is an edge-canonical, partial-one-to-one same-feature Operation-to-Entity relation;
  `creation_targets` is a generated projection.
- `reads` admits `Query` and `Operation` sources; `queries` is a deprecated migration alias.
- `Calculation` is not a `reads` source: its canonical relation is `calculates`, and input provenance remains a separate decision.
- `applies` targets both `Operation` and `Calculation`.
- `owns` and `belongs-to` are first-class; Workflow orchestration admits same-feature and cross-feature scope.
- `depends-on`, Operation returns to Value Object, and Event payload/publisher split remain residue.

## Relationship Non-Collapse Test

Use a relationship as an authored DS-D2/DS-D8 edge only when removing it would change at least one tracked
property:

- reject/allow decision (`domainspec-v2-D20`);
- derivation consequence (`domainspec-v2-D21`);
- projection consequence (`domainspec-v2-D22`);
- composition path consequence (`domainspec-v2-D23`);
- owner route consequence (`domainspec-v2-D24`);
- generated artifact consequence (`domainspec-v2-D25`).

If removal changes only prose, drawing notation, reverse navigation convenience, or a field-level label, keep
the candidate as generated, deferred, collapsed into metadata, or non-authoritative explanation.

## Backend Signatures

| Signature | Meaning |
| --- | --- |
| `Entity --[performs]--> Operation` | An entity or actor initiates an operation. |
| `Operation --[produces]--> Event` | An operation causes an event on successful completion. |
| `Operation --[produces-for]--> Entity` | An operation writes or projects into a foreign entity. |
| `Operation --[creates]--> Entity` | An operation owns creation of one same-feature entity type; the edge generates its `creation_targets` projection. |
| `Event --[triggers-cross]--> Operation` | An event activates an operation across a feature boundary. |
| `Rule --[enforces]--> Operation` | A rule gates whether an operation may execute within one feature or across feature boundaries. |
| `Calculation --[calculates]--> Operation` | A calculation derives values used by an operation. |
| `Event --[transitions]--> State Machine` | An event advances a lifecycle state machine. |
| `Interface --[exposes]--> Operation\|Query` | An interface makes behavior callable. |
| `Workflow --[orchestrates]--> Operation[]` | A workflow coordinates ordered operations under same-feature or cross-feature scope. |
| `Policy --[applies]--> Operation\|Calculation` | A policy selects behavior for an operation or calculation. |
| `Mapping --[maps]--> Entity\|Interface` | A mapping transforms boundary or entity data. |
| `Entity --[contains]--> Value Object` | An entity embeds a value object as a field. |
| `Query\|Operation --[reads]--> Entity` | An operation or query depends on entity data without implying ownership or whole-behavior read-only semantics. |
| `Entity --[emits]--> Event` | An entity is the subject/source of a domain event. |
| `Entity --[owns]--> Entity` | An entity has lifecycle, custody, or write-responsibility ownership over another entity. |
| `Entity --[belongs-to]--> Entity` | An entity has membership, classification, or home-assignment to another entity. |

## UI Signatures

| Signature | Meaning |
| --- | --- |
| `Page --[renders]--> Component[]` | A page renders components. |
| `Layout --[wraps]--> Page[]` | A layout wraps pages. |
| `Component --[composes]--> Component[]` | A component includes child components. |
| `Component --[consumes]--> Hook` | A component consumes a hook. |
| `Form --[submits]--> Action` | A form delegates to an action. |
| `Adapter --[shapes]--> View Model` | An adapter shapes data for rendering. |
| `Guard --[protects]--> Page` | A guard controls page access. |
| `Component --[displays]--> View Model` | A component displays a view model. |

## Cross-Layer Signatures

| Signature | Meaning |
| --- | --- |
| `Binding --[fetches]--> Query` | A binding fetches data from a query. |
| `Binding --[mutates]--> Operation` | A binding invokes an operation. |
| `State Indicator --[reflects]--> State Machine` | A UI state indicator mirrors backend lifecycle state. |
| `View Model --[derives]--> Entity` | A view model derives from entity fields. |
| `Form --[contracts]--> Interface` | A form schema aligns with an interface endpoint. |
| `Guard --[mirrors]--> Rule` | A client guard mirrors a backend rule. |

## Canonical Responsibility Application

`creates` is the executable DS-D8 application of
[`domainspec-v2-D27`](../DEFINITIONS.md#domainspec-v2-d27):

```text
CreatePlayer --[creates]--> Player
```

The edge is authored once. `CreatePlayer.creation_targets = [Player]` is a generated projection, not a
second source declaration. One Operation may have at most one `creates` target and one Entity may have at
most one incoming `creates` source. This is partial one-to-one participation (`0..1` on both sides), not a
requirement that every Operation or Entity participate.

Other independently meaningful relations remain separate:

```text
FindPlayer   --[reads]--> Player
CanCreate    --[enforces]--> CreatePlayer
CreatePlayer --[produces]--> PlayerCreated
```

Many executions of the one `CreatePlayer` concept may still create many distinct runtime `Player` instances.
Runtime instance cardinality is not graph concept cardinality.

## Enforcement Scope Policy

`enforces` is the sole canonical Rule-to-Operation gating verb for both admitted locations:

```text
same-feature:  CanCreatePlayer --[enforces]--> CreatePlayer
cross-feature: compliance.AccessRule --[enforces]--> payments.ProcessRefund
```

In Markdown specifications, placement in `Feature Concept Graph` means same-feature and placement in
`Cross-Feature Dependencies` means cross-feature. Do not encode location by changing the semantic verb:
`enforces-cross` remains a deprecated alias and validators reject it with `enforces` replacement guidance.
The multiplicity remains many-to-many because independently meaningful Rules may gate several Operations and
an Operation may require several Rules.

`queries` is likewise a deprecated alias and validators reject it with `reads` replacement guidance. `Query`
remains the read-only callable meta-type; `reads` is the separate Entity-data dependency that either a Query or
an Operation may declare. A Calculation consumes explicit values and therefore does not gain an Entity-reading
edge from this signature.

## Entity Relation Policy

`owns` and `belongs-to` are distinct signatures.

- Use `owns` when the source entity has lifecycle authority, custody, containment authority, or write
  responsibility over the target entity.
- Use `belongs-to` when the source entity is a member of, classified by, or assigned to the target entity.
- Use generated `owned-by` only as reverse navigation for `owns`; do not author it as a canonical edge.
- Do not treat `belongs-to` as `owns^-1`.
- Keep `depends-on` deferred until a concrete witness proves distinct validation behavior.

## Event Endpoint Policy

Use `Operation --[produces]--> Event` when an operation causes an event on completion.

Use `Entity --[emits]--> Event` when an entity is the event subject/source.

`Operation --[emits]--> Event` is invalid.
