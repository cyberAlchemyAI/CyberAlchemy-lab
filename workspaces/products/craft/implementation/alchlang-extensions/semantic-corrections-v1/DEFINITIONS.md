# Semantic host construction definitions

Status: prototype definitions; no admission or operational authority.

| Meaning | Owner | Invariant / observation |
|---|---|---|
| Command | Alch author | Only its declared fields enter the producer (F2). |
| Entity state | Business owner | Identity is (entity, key); version and schema generation are storage metadata (F1, F6). |
| Event payload | Business owner | A typed projection of committed next state; independent of the delivery envelope (F6). |
| Projection | Consumer owner | Identity is (projection, key), separate from the source entity (F6). |
| Envelope / outbox / inbox | Binding owner | Versioned imported system records; never empty business entities (F5). |
| Actor and boundary selection | Author / host respectively | Author names the actor and boundary once. Only trusted host context grants access (F8). |
| Transition | Business owner | Read persisted source state inside the write transaction; destination controls next state (F1). |
| Default | Business owner | Apply only on absence. Null is invalid; false, zero, and empty strings remain values (F4). |
| Assignment | Business owner | Explicitly replace a field; a transition owns its state-field assignment (F4). |
| Backfill | Migration owner | Add a declared default only to a missing field in an eligible old record (F4). |
| Transport attempt | Transport owner | Increment when a lease is issued; bound independently of consumer receives (F3). |
| Consumer receive | Consumer owner | Count authenticated, validated nonduplicate execution attempts, including rolled-back attempts (F3). |
| Retention | Data owner | Expiration stops delivery and stores a terminal copy in the selected local dead-letter channel; no receipt deletion (F3). |
| Typed ontology | Compiler | Preserve roles, selections, effects, transitions, types, mappings and source provenance (F7). |

Product: placing an order atomically stores business state and an event. A local consumer builds a separate order projection. Retries retain message identity. The business owner chooses lifecycle, payload, defaults, actor and boundary. The compiler derives identity mappings, structural effect references, and envelope types. No actor is inferred from a name or granted by compilation.

Compatibility: semantic-host-v1 uses alch.semantic-execution/v2 and entity/projection storage keys. Earlier operation-keyed databases require explicit snapshot migration. The declarative-function ontology remains a separate projection, linked through generated DomainSpec Mapping contracts. This profile supports one producer, one consumer, one local delivery binding; unsupported syntax rejects.

## Authored versus derived

| Surface | Authored choice | Derived result |
|---|---|---|
| Authority | Actor and boundary selected once | Operation and permission references; no grant |
| Persistence | Binding and business record | Imported system types and atomic effect references |
| Data | Entity and command properties | Independent validators and typed Mapping contracts |
| Events | Source record or explicit payload properties | Typed next-state payload projection |
| Consumer | Event, projection and key | Projection Mapping and inbox identity |
| Lifecycle | Field, source state and destination | Persisted-state guard and destination assignment |
| Delivery | Attempts, receives, retention, lease and terminal channel | DomainSpec delivery/failure contracts and runtime enforcement |
| Migration | New property and default; explicit legacy ownership if needed | Missing-field backfill plan and generated default Mapping |
| Envelope | Caller retry message ID; host clock | Event envelope; internal schema/version metadata |

The generated [ontology scaffold](ontology-scaffold.json) joins these roles and relationships. It remains a local construction scaffold.
