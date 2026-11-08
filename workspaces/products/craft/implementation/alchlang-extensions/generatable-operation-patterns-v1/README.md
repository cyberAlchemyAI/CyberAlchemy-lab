# Generatable operation patterns v1

This candidate capability inventories operation patterns the AlchLang CLI may
generate. Availability is fail-closed over four prerequisites: admitted
meta-type, formed integration binding, registered generator and executable
conformance.

Registration never makes a pattern stable. `architecture_pattern_status` is
owner-controlled; the CLI only reports it. A blocked pattern stays visible with
causal blockers and cannot generate implementation code.

The first inventory proves the distinction:

- `operation-port` is available as target-neutral structural generation.
- `transactional-outbox` is blocked until explicit language semantics, a
  provider binding, generator and executable conformance exist.

Residue: the active DomainSpec relationship authority has no admitted
`Operation -> Entity` write edge for registry mutation. The Operation body owns
the declared write set; the graph does not invent a substitute relationship.
