# Reuse Open Ontologies to strengthen Lab checks

**Candidate design — implementation has not started.**

We already have definition-model search, relation proofs, versioned ontology
views, and exact evidence handling. This design adds stronger definition proof
results and useful ontology analysis by copying existing code wherever its
meaning fits.

## What we will reuse

- The complete upstream Lean workspace: **84 files**, with its existing
  theorems, checkers, parsers and build definitions.
- The complete main Rust source tree: **107 files**, with the original Cargo
  build and pinned graph-store dependency.
- Upstream Rust test code and selected model/Horn fixtures, preserving both
  valid and deliberately bad cases.
- Our source capture, obligation generation, exact evidence binding and worker
  supervision code, through compatible interfaces or a separate reviewed copy.
- Optional later Isabelle/Rocq Horn workspaces.

The [copy manifest](UPSTREAM-COPY-MANIFEST.json) identifies **597
planned source files**, their exact hashes and destinations. This includes later
optional units; it is not evidence that files have been imported or built.

## What changes for a user

For a supported definition model, the Lab can retain its existing search, then
produce a small Lean proof for the exact example and check it afresh. For an
agent view, the Lab can report which required conclusions remain supported.
For an ontology change, it can show newly derived consequences before review.

A successful imported checker run and a fresh kernel-checked Lab proof are
different result levels. The design keeps that difference visible, together
with whether the translation and source meaning have been reviewed.

## Read the design

1. [Architecture: the parts and six views](ARCHITECTURE.md).
2. [Exactly which code is copied or adapted](CODE-REUSE.md).
3. [Proof profiles and meaning preservation](PROOF-PROFILES.md).
4. [Requests, results and owned execution](INTERFACES.md).
5. [Validation and failure controls](VALIDATION.md).
6. [Delivery layers](DELIVERY-LAYERS.md).
7. [Terms and source context](GLOSSARY.md).
8. [Design review and resolved findings](DESIGN-REVIEW.md).
9. [Design/source-accounting checks](DESIGN-CHECKS.json).

The new provider lives under `craft/formalization/candidates/open-ontologies-assurance-v1/`. Its imported source stays separate
from Lab adapters. Existing accepted checkers and their evidence are preserved.
The imported engine only receives a disposable export; it cannot become the
owner of canonical ontology events or Lab approval.

The source pin is `c7fd75f9491253c56e4d4f408ceac179de343e48`. Upstream and the inspected Lab Lean workspaces
both select Lean 4.33.1. Matching version files do not establish build success.
The design, source selection and machine-readable profiles were checked; no
new toolchain, engine build, runtime integration or proof run was performed.
