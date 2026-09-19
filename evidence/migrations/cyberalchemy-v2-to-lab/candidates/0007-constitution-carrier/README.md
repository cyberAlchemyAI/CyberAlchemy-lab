# Constitution carrier and selector preview

`Invariants -> scoped rulebook -> matching rules -> separate owner-adoption decision`

**Constitution** means an owner-scoped rulebook that organizes rules, policies, selectors, validation bindings, composition and challenge routes. It governs only after exact-version owner adoption and only within its declared scope.

**Why this matters:** Lab needs to inspect which rules concern a subject without treating the presence of a candidate rulebook as permission to govern or enforce anything.

## What the prototype does

The record carries its version, scope, subject kinds, owner route, proposed authority level, selectors, rules, policies, rule order, composition policy, conflict and challenge routes, validation bindings and retirement/split conditions. This first profile uses exact string selectors and references the preceding batch's exact integer-invariant record.

```text
Matching scope + matching runtime selector -> preserve-counts and preserve-meaning rules match
Matching scope + missing runtime attribute -> indeterminate
Different scope or subject kind -> rules do not match
Matching candidate -> governs: false
```

The example connects the existing import-count invariant to a deterministic validation binding and records a separate human review rule for preservation of source meaning. It checks the binding's file hash, invariant identity, scope, profile and record validity. Preview does not execute that invariant or complete the human review.

## Try it

From the Lab root:

```bash
cd evidence/migrations/cyberalchemy-v2-to-lab/candidates/0007-constitution-carrier
python3 check.py artifact-types/constitution/v1/fixtures/valid/constitution.json examples/matching.json
python3 check.py artifact-types/constitution/v1/fixtures/valid/constitution.json examples/missing.json
python3 check.py artifact-types/constitution/v1/fixtures/valid/constitution.json examples/outside-scope.json
```

The commands are read-only. Exit 0 means a valid preview was produced, including valid nonmatches and indeterminate results; exit 1 means the record or input is invalid. Without a subject argument, the command validates the rulebook record only.

Every rule retains its own selector outcome. A rule requires all of its named selectors to match. A known nonmatch excludes the rule even when another selector is unknown. Missing or non-string attribute values are indeterminate. Exact scope and subject-kind boundaries are checked before any matching claim.

The declared precedence list orders the preview and must cover every rule exactly once. All matching rules remain visible: no rule silently overrides another. Conflict routes are recorded for owner review; the prototype does not discover or resolve natural-language conflicts or compose multiple constitutions.

## Verification

Run `PYTHONDONTWRITEBYTECODE=1 python3 validate.py` from this directory. It verifies source and dependency hashes, shared Artifact Type mechanics, 17 behavioral tests, eight invalid schema fixtures, three demonstrations, deterministic generation and all 195 reconciliation entries. The preceding candidate is checked for byte preservation.

Construction closes over 27 existing Definition candidates and 25 source sections. The previously recorded D53 narrow source binding and eight source-lineage residues remain explicit. Source documents and admission registries are unchanged.

[Demonstration evidence](receipts/demonstration.json) binds the rulebook and subjects. [Validation evidence](receipts/validation.json) records the checks. Revalidation writes new evidence in this candidate only; an older `manifest.json` must be replaced by a new exact review snapshot if its bound bytes change.

## Migration state

| State | Before | After |
| --- | ---: | ---: |
| Current recorded admission | 13 | 13 |
| Constructed candidate | 80 | 81 |
| Scaffold awaiting implementation | 102 | 101 |

The next scaffold in ledger order is `type.decision`.

## What a later Product review would accept

`Candidate rulebook -> validate its structure and references -> preview matching rules without granting authority`

The reviewable capability is this exact Constitution record type and bounded selector preview. This batch records implementation completion, not Product approval, constitution adoption, type admission or enforcement authorization.

Owner authentication, adoption verification, rule execution, semantic conflict resolution, general validation profiles and resolution of grounding-reference strings remain outside the capability.

## Open questions

- The Constitution owner owns exact adoption and interpretation of conflicting rules.
- The validation owner owns additional binding profiles and any later authorized rule execution.
- The source Definition owner retains the D53 section-layout issue recorded by the proposition batch.
