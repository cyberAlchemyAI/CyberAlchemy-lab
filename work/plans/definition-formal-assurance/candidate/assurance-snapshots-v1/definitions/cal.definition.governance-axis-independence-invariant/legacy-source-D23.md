## CAV2-D23: Authority Lifecycle Axis

Status: active
Term: authority lifecycle axis
Aliases: confidence lifecycle axis, authority axis split, maturity-evidence-commitment split, status-evidence-commitment split

### Normative Definition

Authority lifecycle axis is the CyberAlchemy v2 rule that authority posture must
separate at least these dimensions when they matter to a decision:

- role or kind
- maturity or status
- evidence confidence
- commitment or conviction
- provenance
- owner

No one axis may silently stand in for another. A definition can be mature but
weakly evidenced, an imported source can be well-evidenced but not locally
canonical, an ontology candidate can be useful but unpromoted, and an owner can
be committed to a hypothesis without that hypothesis becoming authority.

### Formal Interpretation

An authority-bearing artifact `a` has lifecycle posture:

```text
L(a) = (kind, status, evidence, commitment, provenance, owner, residue)
```

where each component may be known, unknown, deferred, or source-local. A
governance move is valid only if it changes the intended component and does not
imply changes to the others unless those changes are explicitly recorded.

### Schema

Schema handle: `CAV2-D23-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md).
Status: tracked (documentary).
Bound to: `CAV2-D23` authority lifecycle axis.

Lifecycle posture record:

```text
L(a) = (kind, status, evidence, commitment, provenance, owner, residue)
```

| Field | Meaning | Value posture |
| --- | --- | --- |
| `kind` | role or artifact kind of `a` | known, unknown, deferred, or source-local |
| `status` | maturity or lifecycle state | known, unknown, deferred, or source-local |
| `evidence` | evidence confidence | known, unknown, deferred, or source-local |
| `commitment` | owner conviction or commitment | known, unknown, deferred, or source-local |
| `provenance` | source or origin | known, unknown, deferred, or source-local |
| `owner` | responsible owner route | known, unknown, deferred, or source-local |
| `residue` | unresolved remainder per `CAV2-D18` | typed residue or none |

Schema invariant: a governance move changes the intended field without implying
a change to the others unless an explicit typed coupling (`CAV2-D16`) records the
link. This schema is documentary; a machine-checkable validator is a deferred
follow-up recorded in the registry. Schema changes follow `CAV2-D25` schema
amendment witness.

### Operational Interpretation

Use authority lifecycle axes when evaluating definitions, constitutions, axioms,
ontology nodes, inventory cards, task results, schemas, and implementation
claims. The reviewer should ask which axis is being advanced: source role,
maturity, evidence, owner commitment, provenance, or canonical authority.

### Plain-Language Intuition

"Useful", "trusted", "finished", "owned", and "canonical" are different words.
Do not let one of them impersonate the others.

### Domain-Context Voice

In CyberAlchemy v2, this definition absorbs the imported vault's mature split
between `node_type`, `status`, evidence confidence, and commitment language as a
local lifecycle principle. The source vocabulary is evidence, while CAV2 keeps
the more general axis split so Arcanum, DomainSpec, house_project, ontology,
inventory, Craft, and future implementation artifacts can share one governance
shape without sharing one exact status taxonomy.

### Boundary

Authority lifecycle axis is not a complete status schema and does not make
every artifact an ontology node. It gives the minimum separations that future
schemas, ledgers, and constitutions must preserve.

### Primary Consumers

- [../imports/house_project/docs/vault/ontology-conventions.md](../imports/house_project/docs/vault/ontology-conventions.md)
- [../imports/house_project/docs/vault/premise/ontology-premises.md](../imports/house_project/docs/vault/premise/ontology-premises.md)
- [../imports/house_project/docs/vault/confidence-levels.md](../imports/house_project/docs/vault/confidence-levels.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-authority-node-relationship-taxonomy-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-authority-node-relationship-taxonomy-cards.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md)
