---
node_type: reference
is_session: false
status: candidate
created: 2026-07-02
authored_by: task-session (M4 worked example)
artifact_kind: target-state
template: ../TEMPLATE.md
feature: CampusRead — book lending (the novice-test task; resolves stall S8)
promotion_boundary: local research example.
---

# Target-State — CampusRead: a settled Loan

Worked instance of [TEMPLATE.md](../TEMPLATE.md). This is the exact target-state the blind novice could not
express (stall S8 — "target-state has no meta-type, template, or definition"). With the template it becomes
a checkable artifact.

## 1. Buildable narrative — "Done looks like…"
A loan is **settled** when the borrowed copy is physically back and re-shelvable, the library is made whole
for any lateness, and the borrowing is closed out while the history is kept. Concretely: the patron has
returned the copy, it's available for the next borrower, any late fee has been paid off, and the loan
record still exists so the patron's borrowing history survives. Nothing about the loan is still "in flight"
or owed.

## 2. Oracle-by-example — the discriminator

### DONE — a concrete instance that satisfies the target-state
> **Loan L-4471** — patron `p_881`, copy `c_2210` (barcode `39001-0042`), title *Clean Code*.
> - lifecycle state = `returned`
> - copy `c_2210` availability = `available` (re-shelved at its home branch)
> - late fee assessed = `$4.50 USD`; outstanding balance = `$0.00` (paid)
> - loan record L-4471 = **retained** (appears in patron p_881's history)
>
> → **settled.**

### NOT-DONE — the nearest miss (the discriminator)
> **Same Loan L-4471, identical in every field except:** outstanding fee balance = `$0.50` (patron paid
> $4.00 of the $4.50).
> - state = `returned`, copy = `available`, record retained — everything else is done…
> - …but `$0.50` is still owed.
>
> → **NOT settled.** The single flipping feature: **`outstandingFee != 0`**.
>
> *(A second, independent near-miss: everything paid and returned, but the loan record was **deleted** on
> checkout — history did not survive → NOT settled. Flipping feature: `retained == false`.)*

### Discriminating predicate — the checkable core
```
settled(loan) :=
      loan.state == returned
  &&  loan.copy.availability == available
  &&  loan.outstandingFee == 0
  &&  loan.retained == true
```

## 3. Fitness signals (Lane A — checkable, no human judgment needed)
- **Invariant:** a settled loan's copy is countable as on-shelf inventory (`availability == available`).
- **Oracle:** querying the patron's history returns L-4471 (retention holds) — a deleted record fails this.
- **Invariant:** `outstandingFee == 0` ⇒ the ledger shows no receivable against this loan.

## 4. Anti-ceremony check (Lane Z attack)
The narrative in §1 **earns its place**: it names *why* the four predicate terms exist (copy re-shelvable,
library made whole, closed out, history kept) — direction a bare `settled(loan) := …` boolean doesn't
convey to a builder. It is one paragraph, not seven forms. Kept.

---
**What this demonstrates (M4 acceptance):** the template turns an un-expressible target-state (S8) into a
narrative + a **discriminating** oracle — the DONE and NOT-DONE differ by exactly one predicate term
(`outstandingFee`), so "done" is checkable, not vibes. This is the comprehension model's Region-4 result:
narrative lands at the **document level**, carrying an oracle, not as a per-meta-type layer.
