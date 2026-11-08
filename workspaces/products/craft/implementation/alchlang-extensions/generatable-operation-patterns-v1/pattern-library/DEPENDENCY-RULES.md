# Dependency rules

1. Language syntax depends on canonical meta-type meaning, never the reverse.
2. A generator depends on one explicit pattern and integration binding.
3. CLI selection depends on derived availability and fails closed.
4. Generated code cannot widen the declared read, write or effect set.
5. Provider-specific generators remain behind concern-specific bindings; no
   universal infrastructure port is inferred.
6. Owner stability decisions are inputs to the registry, not outputs of tests.

Current residue: DomainSpec relationship authority does not expose an admitted
`Operation -> Entity` write edge. The write set remains in the Operation body.
