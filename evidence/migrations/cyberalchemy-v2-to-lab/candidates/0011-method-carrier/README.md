# Method carrier

Purpose -> declared inputs -> ordered actions and roles -> outputs -> required checks.

A Method describes a repeatable transformation. This candidate reuses the admitted CAV2-D32 meaning and supplies its missing structured record and static checker. The Method, its binding to a particular scope, and an execution remain separate records.

The example describes reviewing a schema change: inspect the proposal -> preserve an assessment -> review unresolved obligations. A gate is a required check before the procedure may continue. Residue is an unresolved issue that needs an owner and a continuation route.

The checker verifies that steps read only available inputs or earlier outputs, each output is produced once and covered by a gate, all roles and gates exist, and completion requires all gates. Reuse rules identify which minimum Method fields stay fixed and which can be specialized. Supplied evidence is bound to exact file contents.

Instructions and gate conditions remain text. The checker does not evaluate their meaning, execute the procedure, establish successful outcomes, authenticate roles or authorize application. This bounded profile has ordered actions, named slots and one assignment per gate; branching, loops, typed value validation and executable gate predicates are outside its scope.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0011-method-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0011-method-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0011-method-carrier/artifact-types/method/v1/fixtures/valid/method-record.json
```

Validation passes 21 behavioral tests and 8 invalid contract fixtures. It checks the admitted Method Definition against its registry, verifies the normalized D32 source section, reproduces generated files and preserves the predecessor snapshot. The admitted Definition's historical line-selector provenance remains unchanged; this batch does not claim to rebind it.

The 195-target ledger now has 13 admitted targets, 85 constructed candidates and 97 remaining scaffolds. Next: `type.discipline`.

The user's `next` authorizes construction and testing. A later application decision would approve using an exact Method in a named scope, with its roles, gates and unresolved obligations. This candidate grants no application or execution authority.
