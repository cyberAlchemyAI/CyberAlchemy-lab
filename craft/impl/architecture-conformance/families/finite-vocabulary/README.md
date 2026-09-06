# Finite-vocabulary family

This family proves one portable Enum promise before any language target is
implemented:

> An owner-authored catalogue defines one closed set of members. Every member
> has one native key and one explicit wire value, known wires round-trip, an
> unknown wire fails structurally, and declaration order carries no meaning.

The denominator is independent of generated or runtime members. Target adapters
may contribute observations, but they cannot define the expected catalogue or
read the hostile catalogue's expected findings.

Native identity is deliberately outside the portable parity claim. The existing
TypeScript const-object form can report `collapsed-literal`; Python and Rust can
report `nominal`. Both diagnostics remain visible while the portable member/wire
proof is evaluated identically.

The `shipment-priority` fixture supplies ten positive proof decisions and nine
hostile classes: missing, extra, duplicate, alias, round-trip cycle, wire
collision, order authority, implementation-owned provenance, and accepted
unknown wire. This is candidate evidence only; it contains no Python, Rust, or
new TypeScript target implementation.
