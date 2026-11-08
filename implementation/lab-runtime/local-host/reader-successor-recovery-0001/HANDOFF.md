# Persistent Reader successor 0001 — dynamic selection, effect disabled

Status: **effect-disabled selector for independent static review**. This unit
targets the frozen public Source successor profile `context-successor-recovery-0001`
at SHA-256 `bb9f9be62c606dc87ccfdab9b5497c833cf781e89170d789379167582950bf66`.
The selected Source role is `docker-source-20261020-0002` under the durable
owner-only attempt `/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/source-attempt`.
No Source package or independent effect review exists there yet. The live
read-only probe returns `SOURCE_EFFECT_NOT_PRESENT`; `execute_reader()`
unconditionally refuses. It does not read or copy an archive body.

After a separately reviewed Source effect, `select()` requires the exact
public Source manifest SHA-256 `2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1`,
the **new actual** 36-member package manifest, its period bytes, a PASS
terminal, and a structured independent Source effect review pinned by an
outside SHA-256. It joins the actual package digest and terminal digest to
that review, validates the current 24-hour period and exact package/archive
paths, then projects seven original Reader role files to
`docker-reader-20261020-0002`. The projected `base.py` changes only the
producer role and module alias, and an inverse recovers its exact preimage.
The returned Reader manifest binds the newly observed dynamic package digest.
It is an in-memory selection; no Reader stage, cold-open, Docker or grant is
created.

The independently authored future Source effect review must use the exact
structured contract `lab-successor-source-effect-review/v1` and bind the
Source manifest, actual package manifest, terminal, and attempt. The outside
review digest must be selected before calling `select()`; passing a digest
computed from an unreviewed caller-authored review would not establish
independence. A later Reader effect adapter must durably claim a distinct
owner-only Reader attempt, stage held no-follow source bytes, cold-open the
actual `SelectedReader` against these pins, verify the signed view and close,
capture external OS exit, and obtain independent effect review. None of that
is implemented or implied by this selector.

Normal and optimized fixture suites pass 5/5 each. They test dynamic package
binding, exact role projection, forged/missing review, package and terminal
drift, period expiry, live absence, and effect refusal. The historical
`/tmp` Source/Reader/Mapper/Context attempts remain consumed evidence and
are not selected as live inputs. This unit does not qualify original
protected Source8/G01/G02 authority or complete the original runtime plan.
