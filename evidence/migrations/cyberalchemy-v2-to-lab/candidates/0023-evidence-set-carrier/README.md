# Evidence Set carrier

Declared question -> exact supporting, opposing or contextual members -> explicit gaps -> review.

An Evidence Set aggregates exact supporting and counterevidence references without becoming a conclusion. This candidate preserves the normalized Evidence Set meaning and both D61 Research and D62 Experiment source selectors.

The example inventories the preceding Residue checker: its validation record supports the narrow question about reported local checks, while its documented limitations oppose a broader claim of general semantic preservation. A separate gap records the absent independent semantic evidence. These roles are declared interpretations, not judgments made by the checker.

The checker verifies every member's content hash, unique member identity, and question references. Identical files or copied bytes cannot count as distinct members. One member has one role per question; it can contribute differently to different questions. Duplicate or conflicting entries are rejected rather than silently merged.

Every declared question needs at least one evidence contribution or an explicit gap. Gaps name missing evidence, an owner route and a next step. A set containing only gaps is valid as an inventory; zero verified members remains explicit. Supporting material, counterevidence, context and gaps stay separate in the report.

The bounded profile does not discover omitted questions or counterevidence, assess relevance, authenticate provenance, evaluate role assignments, establish sufficiency or derive conclusions. Exact file integrity does not prove that an experiment ran. There are no scores or automatic majority decisions.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0023-evidence-set-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0023-evidence-set-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0023-evidence-set-carrier/artifact-types/evidence-set/v1/fixtures/valid/evidence-set-record.json
```

CLI status 0 means inventory integrity and declared coverage; 2 means invalid input or inconsistent inventory. Status 0 establishes no conclusion.

Validation passes 14 behavioral tests and 8 invalid contract fixtures. It verifies seven Definition dependencies and two source sections, both normalized D61/D62 selectors, eleven inherited source-lineage residues and the existing D53 overlay. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 97 constructed candidates and 85 remaining scaffolds. Next: `type.receipt`.

The user's `next` authorizes construction and testing. A later reliance decision would approve using this exact evidence inventory for the named questions, with its counterevidence and gaps. Findings, sufficiency judgments and governing decisions remain separate.
