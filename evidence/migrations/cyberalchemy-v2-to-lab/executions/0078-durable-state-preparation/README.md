# Durable Capability State preparation

Capability -> state it must retain -> durability requirements -> external/provider boundaries.

The missing registration is `cav2.durable-storage.business`, owned by capability `CA2-CAP-PRESERVE-DURABLE-CAPABILITY-STATE`. It is distinct from 0038's encrypted-knowledge-object storage model. Their similar names must not collapse their identities or evidence.

Pinned 25 concepts, 22 relationships, seven storage classes, thirteen requirements and five residue records. Six of ten exact source selections were recovered, including historical D65/D67 and the shared schema. Four expected whole-file versions were not found in inspected local/sibling snapshots, 133 matching evidence files or targeted Git histories across three repositories.

A separate successor changes only four source fingerprint fields, binding the available captured capability-reference, routing, ontology-runtime and Ontology Product records. It is a repair candidate, not a currentness claim about later edits. Original source files and receipts remain archived.

The original native validator reports five errors. On the staged successor it reports one error: `CA2-REF-ARC-INVOKE-DEFINE` is absent from its selected capability-reference evidence. The current reference set includes `CA2-REF-DEFINE-CLI`, but this is not automatically the same external capability. The original external-owner requirement is preserved, with no storage classes or provider assigned to that external subject.

No runtime import was performed. Native BLOCK is retained even though the validator emits some candidate-shape construction labels; those labels do not override its result. No durability, recovery, provider or conformance proof is inferred.

## Open Questions

Next: resolve the external Arcanum Invoke reference using source-owned identity/evidence or an explicit documented successor. Then rerun native validation and its negative suite before importing through the existing runtime. Do not manufacture a reference or substitute the private Define CLI by name similarity.

The combined runtime catalog and validator/request integration remain later work. The source checkout, capability inventory and existing runtime stores remain unchanged.

Reproduce the bounded preparation with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0078-durable-state-preparation/verify.py` from the Lab root.
