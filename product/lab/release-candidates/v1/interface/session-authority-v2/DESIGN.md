# Explicit source revision binding

This successor preserves all fresh participation and host-permission checks.
The default body-version/reference equality rule remains enforced.

A host-selected carrier may separately declare verified-source-revision as its
binding rule. It then requires an exact SignedRevisionWitness for every selected
record: same signed source cut, complete Artifact Reference, enclosing original
bytes/hash, explicit selector and declared encoding. Whole-file bytes must equal
the original record. Legacy embedded-value bytes must equal the selected value's
already declared inherited encoding. The host source guard independently verifies
the signed archive, executable, configuration, transaction chain and projection.
A witness is never constructed from public request claims and grants no authority.

This is needed for the current Product Identity source: the signed projection
names product:cyberalchemy-lab@foundation.1 while the original body's version is
2.0.0-foundation.1. The immutable reader explicitly treats its revision reference
as transaction metadata qualifying identity. Its operations enforce that prefix;
they do not derive a revision from the Product body's version field. Both values
and the original byte hash are retained, without renaming or rewriting either.

The same-source adapter declares this rule only for Product Identity/v2. Other
carrier sources keep the default rule. This candidate protocol boundary is an
independent S02/R08 review member. It is distinct from future admission of incoming
original file bytes, from cryptographic authorization, and from ontology mapping.
