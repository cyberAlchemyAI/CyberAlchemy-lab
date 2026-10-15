# How profile selection is now prepared

Previously the capture pipeline received a profile supplied by its caller. This
component derives that profile from two kinds of retained source records: a
declaration describes a digest algorithm and encoding; a selection names the
complete reference of the declaration to use in one exact frame.

For example, declaration D@1 contains the candidate SHA-256 algorithm identifier
and lower-case hexadecimal encoding. The preparation verifies the submitted
bytes of D@1 with an explicit bootstrap profile, then derives D@1's complete
reference from its revision key and original-byte digest. Selection S@1 names
that reference. A successful result contains the selected profile and both
ordered lists of checked sources. The declaration does not contain its own hash,
so computing its identity does not require finding a self-referential digest.

## What the result establishes

The main result is an equivalence:

```text
prepareSelectedProfile(bootstrap, limits, frame, declarations, selections) = some stage
  iff SelectedDataMeaning(bootstrap, limits, frame, declarations, selections, stage)
```

The right side is an independently stated meaning, not a call to the checker.
It requires supported bootstrap settings, configured input/count/byte limits,
checked original-byte meanings for every input, agreement of selection records,
non-equivocating declarations, exact full-reference resolution and exact frames.
The selected declaration and selection must have the appropriate tokens, recorded
accepted review and clear revocation postures, and an expiry strictly after the
frame's epoch. The resulting algorithm and encoding must be supported.

Different selection records refuse in either list order. Conflicting content at
one declaration revision key refuses even when that declaration is not selected.
Identical duplicate records are retained. Nothing silently selects the latest
revision, ignores an unused malformed input, or drops a conflicting source.

Separate results establish uniqueness, retained source order and envelopes,
selected profile provenance, resource refusal and exact posture/closed-object
decoding. These are source-data guarantees within the candidate model.

## Where trust is still required

An `accepted` review string is a recorded claim. A `clear` revocation string is
also a recorded claim. Successful preparation does not establish either claim's
authenticity. A bootstrap profile cannot acquire authentic ownership merely by
being supplied to the function.

The separate `OwnedSelectionMeaning` requires an authentic complete snapshot,
authentic bootstrap selection, authentic declaration/selection issuance, exact
principal entitlements and faithful review/lifecycle evidence. Every retained
source row has these obligations. The `withSelectedOwnership` adapter installs
this full meaning as the capture ownership policy; it preserves the other four
capture predicates. No working authentic evidence provider is supplied here.

The conditional capture theorem says that **if** those ownership obligations,
checked capture data, actual Schema meaning and reviewed-entry requirements are
established, the composed capture satisfies the complete capture meaning. It
does not manufacture those missing premises or discharge the nineteen complete
K02 source policies.

## Schemas and local APIs

The two separately versioned schemas describe decoded declaration and selection
values. The API contract exposes three existing pure Lean functions. There is no
HTTP service or frozen N03 public API.

JSON Schema validates decoded values. It cannot retain duplicate object keys or
distinguish an integral number written as `42`, `42.0` or an exponent spelling.
The exact source decoder retains those distinctions and requires canonical Nat
lexemes. The schema audit deliberately records this representation gap; it does
not claim schema/byte-decoder equivalence. Unsupported algorithm strings are
shape-valid but fail supported-profile selection. Recorded missing/rejected/
unknown/revoked postures are representable, then fail selection eligibility.

## Validation and remaining scope

The package has 28 general declarations and 24 closed typed-data controls. Its
26 runtime cases exercise captured sources, a derived content digest, duplicate
retention, missing references, posture/expiry failures, unsupported settings,
conflicts in both orders, an unused conflicting declaration, full-frame mismatch,
a same-count byte change and configured limits. Concrete source fixtures retain
their exact byte counts, submitted digests and independently recomputed hashes.

The typed-data controls do not prove captured-source authenticity. Large captured
positive cases are runtime composition checks, not closed kernel reductions of
their entire digest computation. Fresh isolated compilation/replay and exact
import resolution are recorded in `verification.json` and the import audit;
same-kernel replay is not the required independent checker. Compilation timings
do not qualify an operational resource envelope.

All principals, bootstrap/profile references and review roots in examples remain
synthetic. Actual evidence providers, Schema interpretation, complete K02 source
refinement, public diagnostics, independent checking and final bounded-use review
remain open. All 263 inherited IDs remain pending; the 90 original discharges keep
their scope. K00-K03 meanings are accepted; K04 and global D01-D08 remain pending.
This component does not complete N01, N02, N03 or the twenty-task plan.
