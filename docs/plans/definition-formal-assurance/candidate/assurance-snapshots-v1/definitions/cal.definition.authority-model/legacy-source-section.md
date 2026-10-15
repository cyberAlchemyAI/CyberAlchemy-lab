## CAV2-D41: Authority Model

Status: active
Term: authority model
Aliases: CAV2 authority model, project authority model, owner-route model, authority routing model
Ancestral provenance (non-normative): the owner-route traffic map re-authors the CyberAlchemy Method's "Route" anchor ([`arcanum/framework/CYBERALCHEMY-METHOD.md`](../../../arcanum/framework/CYBERALCHEMY-METHOD.md)). Evidence posture — not deployed. See [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md) § Ancestral Lineage Reconciliation.

### Normative Definition

An authority model is the governed structure that classifies candidate material by
authority kind, reliance posture, owner route, admissible movement, gate
vocabulary, validation surface, and non-collapse rule so CyberAlchemy v2 can
decide what may count for which purpose without letting evidence, ontology,
research, generated projections, implementation success, or narrative repetition
silently become authority.

An authority model must name the authority surfaces it coordinates, the route
that owns each kind of promotion, the states or postures a candidate may occupy,
the gates that control movement between states, and the boundary conditions that
prevent one authority layer from overriding another.

### Formal Interpretation

For a candidate object `x`, a CyberAlchemy v2 authority model provides a routing
function:

```text
A(x) =
  (kind, posture, owner_route, allowed_use, blocked_use,
   gate, validation_surface, non_collapse_rules)
```

Movement is admissible only when the responsible `owner_route` records a gate
verdict and the candidate's `allowed_use` covers the intended downstream effect.
If a candidate crosses from evidence or model into local authority, the model
requires a promotion gate rather than implied authority by proximity.

### Operational Interpretation

Use authority model when deciding whether a source fragment, definition
candidate, ontology node, research finding, discipline, constitution rule,
decision, spec, runtime contract, generated projection, validation result, or
implementation artifact is allowed to influence CyberAlchemy v2 work.

The authority model answers: what kind of thing is this, what may we rely on it
for, who owns the next move, which gate must run, and what must not be collapsed
into what?

### Plain-Language Intuition

The authority model is the traffic map for what is allowed to count, who can make
it count, and what it must not be confused with.

### Domain-Context Voice

In CyberAlchemy v2, the authority model is authored in
[../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md). It coordinates definitions,
constitutions, disciplines, decisions, promotion policy, boundaries, ontology
candidate views, inventory evidence, validation traces, and future implementation
work. It turns the stable-repository objective into an owner-routed contract:
ontology can model authority, inventory can preserve evidence, disciplines can
name recurring practices, and constitutions can enforce scoped rules, but each
promotion still needs the responsible owner route.

### Boundary

Authority model is not ontology by itself, not a schema by itself, not a
decision, not access control, not proof, not a universal constitution, and not a
license to promote all modeled material. It coordinates authority movement; the
responsible owner routes still make the actual promotion decisions.

### Primary Consumers

- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md)
- [../README.md](../README.md)
- [../promotion-policy.md](../promotion-policy.md)
- [../../ontology/AUTHORITY-KINDS.md](../../ontology/AUTHORITY-KINDS.md)
- [../../ontology/AUTHORITY-POSTURES.md](../../ontology/AUTHORITY-POSTURES.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
