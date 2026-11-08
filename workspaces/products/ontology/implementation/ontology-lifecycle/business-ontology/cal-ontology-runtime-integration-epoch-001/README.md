# Ontology runtime integration business ontology

Status: validated candidate awaiting `G-D65-BUSINESS` owner admission

This private package defines the capability-local business meaning required by
D65-S3. Its central contract allows a governed CyberAlchemy Context to request
one deterministic ontology projection from canonical per-node and per-relation
events at one exact event cut, with exact governance joins and challenge routes.

The package distinguishes three things that must not collapse:

1. Business meaning: Context, selector, binding, cut, projection, policies,
   workflows, outcomes, and failure behavior.
2. Future system meaning: independently generated and admitted system-runtime
   ontology endpoints, which do not exist at D65-S3.
3. Realization: exact implementation bindings and Rust adapters, reserved for
   later D65 stages.

`CAL-BIZ-CONTRACT-BUSINESS-SYSTEM-BRIDGE` is therefore a type contract with
`contract-defined-no-system-endpoint-or-realization-claimed`. This prevents an
empty or name-only bridge from masquerading as implementation alignment.

Canonical events remain the only ontology truth. Contexts, projections,
snapshots, indexes, compiled graphs, and system ontologies are derivative or
descriptive outputs and may never become replay sources.

Run `python3 validate.py` for a check-only validation. Use
`python3 validate.py --write-receipt` only when explicitly materializing a new
candidate validation receipt.
