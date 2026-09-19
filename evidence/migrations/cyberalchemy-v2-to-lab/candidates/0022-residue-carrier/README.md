# Residue carrier

Source operation + preservation requirement -> resulting representation -> meaningful remainder -> owner treatment route.

Residue is meaningful information that an operation's target representation did not preserve, name, justify, validate or carry. This candidate preserves the D18 meaning and records the operation, preservation condition, observed remainder, residue type, exact evidence, owner route and treatment.

The illustrative operation projects a record to its ID. The declared requirement also preserves owner and meaning, so their absence is recorded as residue. The example does not claim to observe a real production transformation.

The checker compares required top-level fields in exact source and result JSON objects. Missing fields produce missing residue; changed values produce changed residue. It requires the recorded remainder to match the observed remainder completely. Omitted, invented or duplicate remainder fields are rejected. A requirement for a field absent from the source is invalid; no observed loss cannot masquerade as residue.

JSON object key order is ignored, while value types remain distinct. This is structural comparison, not semantic equivalence. Source and result hashes prevent silently reusing a record after either input changes.

The six treatments are repair, type, gate, climb, accept and defer. They name how the owner proposes to handle the remainder. Even accept does not establish accepted closure, and climb does not authorize promotion. The treatment and closure condition remain recorded instructions, not executed workflow.

This bounded profile does not prove that the named operation produced the result, authenticate ownership, evaluate preservation meaning or cover probabilistic, category-theoretic or higher-layer residue. It does not repair files, execute treatment or close the issue.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0022-residue-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0022-residue-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0022-residue-carrier/artifact-types/residue/v1/fixtures/valid/residue-record.json
```

CLI status 0 means the recorded remainder agrees with the supplied evidence; 2 means invalid input or a mismatched remainder. Status 0 does not mean the residue is closed.

Validation passes 14 behavioral tests and 8 invalid contract fixtures. It verifies four Definition dependencies and five source sections, the normalized D18 selector, two inherited source-lineage residues and the existing narrow D53 overlay. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 96 constructed candidates and 86 remaining scaffolds. Next: `type.evidence-set`.

The user's `next` authorizes construction and testing. A later treatment decision would approve how an owner handles this exact remainder and its consequences. Closure requires its own evidence and acceptance; this candidate grants neither.
