# Discipline carrier

Repeated practice across capabilities -> named steward -> exact evidence -> next improvement.

A Discipline is a stewarded recurring practice. This candidate reconstructs the Discipline carrier from D50 and the repository-stewardship use in D6. The example describes keeping reconstructed repository surfaces traceable, validated and resumable.

The Schema and Method validation records provide two distinct local occurrences. Each record must pass, contain passing checks and bind the exact capability artifact it checked. All recorded material hashes are verified. Duplicate occurrences, reused receipts, aliases of the same capability, uncovered capabilities and mismatched evidence are rejected.

A steward is the named role responsible for the practice. The hardening move is the next improvement, with an owner, route and required completion evidence. Naming it does not prove that it is complete.

This profile supports candidate maturity only. It does not implement the source maturity transitions to active-pattern or canonical. Those claims are rejected, and recurrence never automatically grants promotion authority. Receipt integrity does not authenticate an author or independently prove that every reported check ran; the result is bounded to exact local validation records. It does not establish continuous stewardship, complete capability coverage, or the full meaning of free-text practice claims.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0012-discipline-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0012-discipline-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0012-discipline-carrier/artifact-types/discipline/v1/fixtures/valid/discipline-record.json
```

Validation covers 16 behavioral tests and 8 invalid contract fixtures. Source checks bind seven Definition dependencies and their seven source sections, plus both normalized D6/D50 selectors. Three inherited source-lineage residues remain explicit; the existing D53 source overlay is verified without rewriting prior evidence. Generated files reproduce exactly and the predecessor snapshot stays unchanged.

The 195-target ledger now has 13 admitted targets, 86 constructed candidates and 96 remaining scaffolds. Next: `type.architecture-pattern`.

The user's `next` authorizes construction and testing. A later promotion decision would approve a particular practice's maturity in its named scope, based on evidence and its steward's governance route. This candidate grants no promotion.
