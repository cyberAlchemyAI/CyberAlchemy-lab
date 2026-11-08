---
node_type: reference
is_session: false
status: candidate
created: 2026-07-02
authored_by: task-session (M4 — spec-comprehension-model)
artifact_kind: target-state (a first-class buildable target-state doc — SEED.md Lane Z + Lane A unified)
source:
  - ./SEED.md (the tower seed: buildable-narrative primitive + the "is it checkable?" attack)
  - ../../development/spec-comprehension-model/DESIGN.md (M4)
  - ../../development/comprehension-novice-test/stall-dataset.md (S8 — the stall this resolves)
promotion_boundary: local research; adopting this into the DomainSpec spec template is a later approved task-session.
---

# Target-State Template

A **target-state** answers "where are we going and what does *done* look like?" as a **buildable
narrative** (a human can read it and build toward it) paired with an **oracle-by-example** (a machine or a
human can *check* whether done is reached). The oracle is the answer to the SEED's own attack on narrative
("is it checkable?"): the narrative gives direction, the oracle gives a verdict.

**Scope:** per **feature / capability** (SEED residue resolved → per-feature, as its own artifact, not a
per-meta-type layer). Copy this file, fill the four sections, delete the guidance comments.

---

## 1. Buildable narrative — "Done looks like…"
> One plain-language paragraph, ≤ one screen, no DomainSpec jargon required. Describe the end state as an
> observer would *see* it — concrete enough to build toward, not a vague goal. A builder who reads only
> this should know what they're aiming at.

`<Done looks like: …>`

## 2. Oracle-by-example — the discriminator
> The narrative is checkable only if you can show a case that IS done and the *nearest* case that is NOT,
> differing by the ONE thing that matters. This is the target-state's equivalent of a meta-type's
> discriminating fixture pair.

### DONE — a concrete instance that satisfies the target-state
> Real values, not placeholders. A specific example a reviewer can point at and say "yes, that's done."

`<a concrete, checkable DONE example>`

### NOT-DONE — the nearest miss (the discriminator)
> The *smallest* change to the DONE example that flips it to not-done. Name the single feature that flips
> it. If you need a big change to make it not-done, your target-state is too loose — tighten it.

`<the nearest-neighbour NOT-DONE example + the one flipping feature>`

### Discriminating predicate — the checkable core
> The boolean the two examples differ on. This is what a fitness signal / validator / reviewer checks.

`done(x) := <predicate over observable state>`

## 3. Fitness signals (SEED Lane A — optional but recommended)
> The invariants/oracles that must hold at done, beyond the single discriminator — the things that would
> let an agent verify "done" without human judgment. Keep these checkable (an invariant, a query result, a
> state value), not aspirational.

- `<invariant / oracle 1>`
- `<invariant / oracle 2>`

## 4. Anti-ceremony check (SEED Lane Z attack — required)
> One line: does the narrative in §1 add *direction* the oracle in §2 doesn't already give? If §1 is just
> prose restating §2, cut §1 to a sentence. Narrative earns its place only by making the *aim* legible;
> the oracle carries the *check*.

`<what the narrative adds beyond the oracle — or "trim §1, the oracle suffices">`

---
<!-- Worked instance of this template: ./examples/campusread-settled-loan.md -->
