# Generate Contextual Framings imported

Source-owned Business Rules -> explicit acceptance conditions -> candidate import.

A contextual framing explains source knowledge for a named consumer and context, using a perspective or bounded analogy while preserving important limits. The blocked declaration lacked an acceptance-conditions field, but its package already declared five Business Rules and explicit constraint relationships.

The import now carries those five rules verbatim:

- Preserve material constraints, uncertainty, contradictions, provenance and authority boundaries.
- State what an analogy matches, what it does not match and when relying on it becomes unsafe.
- Restrict validity to the named consumer, objective, context, source epoch and expiry condition.
- Allow supporting detail to be explored without changing the claim or hiding unresolved issues.
- Grant no authority or permission through a framing or preference.

The mapping verifies each rule's constraint link to the Capability, generating workflow, output or used analogy. Source `inputs` and `outputs` are mapped explicitly to reference checks. These are acceptance requirements, not proof that the Capability is implemented or improves cognition.

[result.json](result.json) preserves the original source record, exact rule mappings and dependency bindings. [imports.json](imports.json) contains the previous 22 imports plus this candidate. The new isolated store is `.local/capability-inventory-import-0009/imports.json`; earlier stores and sibling source files remain unchanged.

Five checks passed: deterministic replay, rejection of a missing rule, rejection of an unrelated constraint, rejection when the analogy is disconnected from the output, and equality between the store and import report. The combined graph also validates. [verification.json](verification.json) binds the run.

Current queue: **23 imported candidates / 22 blocked declarations**. The next blocked declaration is Recover Recent Repository Context. Its gap is missing acceptance conditions or linked obligations. Definition admission, realization and operational use remain separate from candidate storage.
