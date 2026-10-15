K02 checker and diagnostic preparation

K02 meaning has the exact actual human semantic-owner acceptance in
../../assessments/K02.json. The original MODEL-REVIEW.md is retained unchanged
because that assessment binds it. This addendum records later candidate proof work;
its claims do not retroactively accept proofs or discharge inherited obligations.

IntentAddressingCheck.lean implements a finite checker on resolved Claim/World
values and proves its result equivalent to independently specified Addresses.
It checks all 30 meaning constraints; test ownership iterates all declared tests.
A false result means this claim is unqualified in this fragment, not that an
unresolved fact is false in the world. Public unknown/unsupported status remains
future integration work. The raw decoder and catalog authenticity are not proved.

Diagnostics contain every failed constraint. General theorems establish that an
empty diagnostic list is equivalent to Addresses and every refusal has a diagnostic.
IntentAddressingDiagnostics.lean tests 11 single-failure scenarios for each of six
source kinds: excluded overlap, unselected subject, different Intent, different
resolution qualifier, wrong role kind, missing owner decision, stale snapshot,
missing test ownership, missing role ownership, duplicate test and wrong role code.
Owned record membership is kept consistent by replacing each changed record in the
World and Claim together. Every scenario returns exactly its intended one-element
list; valid claims return an empty list. This is 66 isolated resolved-model cases,
not end-to-end raw/runtime diagnostic validation or full-catalog consistency proof.

CompletionRegression.lean contains owned R1/R2 requirements, full exact criteria,
and separately captured evidence. The easier contract requires R1. The stricter
contract requires R1 and R2. With only R1 evidence, the old existential contract rule
accepts while Completed refuses. Adding exact R2 evidence makes both contracts
fulfilled and Completed accepts. This checks the discovered omission failure and
a positive control, without assuming a completion flag or caller-chosen criterion
subset. The shared FulfillmentMeaning uses the retained positive-support model;
conflict-sensitive fulfillment and its policy assessment remain separate work.

The enlarged module set is rebuilt and replayed with the pinned compiler/library.
verification.json gives exact counts, hashes and axiom inspections. This is not
independent checking. All seven inherited K02 IDs still need raw source refinement,
owned complete catalog/provenance, whole-rule countermodels, qualified/idempotent
recording, public status/diagnostic integration and independent closure checks.
