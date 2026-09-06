# UI Profile Placement Contracts

These machine-readable contracts close development representation for required
UI concepts that are not new node kinds:

- [`adapter.yml`](./adapter.yml) normalizes Adapter vocabulary into an active
  Mapping node with a UI-boundary specialization.
- [`state-indicator.yml`](./state-indicator.yml) separates domain-state
  projection from the async-request role on Component.

They do not mutate DS-D1 or DS-D8. Each unresolved current relationship
endpoint is retained in `relationship_residue` for its canonical owner.
