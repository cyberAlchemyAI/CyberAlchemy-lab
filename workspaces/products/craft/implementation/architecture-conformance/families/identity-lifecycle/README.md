# Identity lifecycle family

This candidate-local family evaluates Entity construction evidence against an
owner-authored definition. It proves stable typed identity across immutable
snapshots, identity-only equality and hashing, owner-bound validation before
identity resolution and construction, additive acyclic extension, and the exact
four construction routes. It does not intercept or prove a native target runtime.

The existing `ConstructionObservation/v1` complete-value transport remains
unchanged. Entity uses the additive sibling
`EntityLifecycleConstructionObservation/v1`; complete-field tuple equality is
never reinterpreted as Entity identity.
