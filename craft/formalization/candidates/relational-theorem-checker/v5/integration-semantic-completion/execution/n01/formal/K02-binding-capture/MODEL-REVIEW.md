K02 capture-to-entry projection and retained catalog staging

This component connects the complete binding-record AST decoder to the existing
owned qualifier catalog. It derives identity, body, bytes and review reference
from one record/capture pair and retains the original record and envelope beside
the derived catalog. It also fixes a gap found during review: mixed digest profiles
must refuse before projection hides their difference. Authentic capture and all
263 inherited obligations remain open.

The missing integration

The earlier catalog received already typed entries. A caller could assemble an
entry from a record key, digest, body, bytes and owner-review pointer obtained
from different sources. The AST decoder, meanwhile, returned a complete record
without a catalog projection. The bridge now has these layers:

| Layer | Independent meaning | Implemented result |
|---|---|---|
| Envelope | Actual byte count equals declared length; nonempty claimed digest and complete digest-profile reference | Adequacy check, with no digest or authentication claim |
| Prepared record | Exact fixed-version/kind record AST meaning, exact requested eight-field Frame, exact submitted envelope | Prepared retains the full Record and Envelope |
| Entry projection | Key from Record; digest and bytes from Envelope; kind/body/review from Record | Derived existing catalog Entry, with no second identity/body/review input |
| Ordered batch | Each input corresponds to one Prepared output under the same version, kind and Frame | Complete preparation or refusal; no silently dropped input |
| Catalog stage | Both ordered batches, requested Frame and digest profile, uniform profile alignment, global catalog structural meaning | Stage retains all Prepared records/roots beside its derived catalog |
| Capture contract | Preparation plus byte parsing, digest computation, owned profile, Schema meaning and authentic exact review | Conditional theorem; no concrete provider realization |

The public preparation functions fix Resolution versus Role target schemas and
version/kind constants. The catalog functions also fix the target identity selector
to target.ref.key. Their inputs are the requested Frame and digest-profile revision,
plus record/root input lists. Each input contains a retained AST and its capture
envelope. Existing catalog checks still enforce global binding-key uniqueness,
token-to-complete-target functionality, target-key consistency, exact complete
Frame and membership of each submitted record in the captured root list.

Meaning and theorem

The principal staging equivalence is:

    prepareCatalog(frame, digestProfile, recordInputs, rootInputs) = Some(stage)
        if and only if
    IndependentCatalogStagingMeaning(..., stage).

The right side says every input is decoded and retained in order, all decoded
frames match the requested Frame, every envelope uses the requested digest-profile
revision, and the derived catalog satisfies the global structural guards. It is
not defined as success of the implementation. Its component predicates are
independent record/object/number meanings, field equalities, ordered batch
constructors and catalog uniqueness/membership/functionality conditions.

A separate field theorem proves that a successfully prepared entry uses exactly
its decoded binding key and owner review, its fixed record kind and complete
body, the capture's bytes and claimed digest, and the requested Frame. No caller
supplies another source revision or body for this projection. The batch theorem
preserves length and connects every output to a specific original input. The
profile-alignment theorem is quantified over all prepared records and roots.

Why retaining the envelope matters

The old Entry type does not contain schemaVersion, byteLength or digestProfile.
Returning only a projected catalog would erase these facts before authentication.
CatalogStage therefore retains the Prepared records and roots; each Prepared
retains its full record and envelope. The old catalog is computed from those
values, rather than stored as another independently mutable field.

Suppose two envelopes have the same record key, claimed digest, body, bytes and
review pointer, but different digest-profile revisions. They would produce equal
old Entries. The new staging guard compares every envelope profile to the exact
requested profile before accepting the catalog, so the difference cannot disappear
through projection. This guard establishes equality, not ownership of the requested
profile. The eventual admitted entrypoint must obtain that profile from authentic
snapshot/context evidence.

Similarly, two captures with different bytes remain distinct old Entries even
when their claimed digest strings are identical. With the same binding revision
key, the global catalog identity guard refuses the conflict. This is exact retained
byte comparison, not a proof that a cryptographic digest is injective.

What the capture contract still requires

CapturePolicies defines five open requirements:

1. The original bytes parse to the exact retained AST, with complete consumption,
   duplicates, numeric spelling and string/Unicode semantics preserved.
2. The named exact digest-profile revision computes the claimed digest for those
   exact bytes. A nonempty digest label is insufficient.
3. That digest profile is owned/admissible for this exact Frame and snapshot.
4. The exact version/kind/AST satisfies the applicable Schema meaning.
5. An authentic review supports the exact derived Entry within this Frame.

The contract theorem requires all five in addition to preparation. It has no
approval booleans or default providers. A theorem prevents CaptureMeaning when
review evidence is absent; another prevents it when the byte-to-AST relation is
absent. These are conditional logical boundaries. They do not authenticate an
issuer, implement a parser/hash/signature algorithm, validate a real owner review
or realize the nineteen complete K02 source-policy predicates. An arbitrary
provider whose predicates always return True cannot discharge those obligations.

Worked controls

There are 32 controls, 16 each for Resolution and Role. They cover original
preparation, wrong byte length, empty claimed digest/profile digest, stale epoch,
null AST, valid rooted staging, missing roots, identical retry, conflicting bytes,
wrong requested digest profile, mixed profiles, retention of profile/version and
non-entailment of authentic capture from prepared syntax.

Two controls intentionally show permissive syntax boundaries: replacing two
synthetic bytes by two different bytes still prepares; replacing a claimed digest
by another nonempty label still prepares. That behavior exposes the remaining
parser/hash requirements instead of disguising preparation as authentication.
The synthetic byte pair [1,2] is not parsed JSON; the digest is an uncomputed label;
the root entries and reviews are synthetic. They provide no real source authority.

Limits and next integration

- The AST/record layer is proved. Original UTF-8 bytes, escapes, Unicode, duplicate
  retention, complete consumption and exact digest computation remain unimplemented
  and unproved here. The fixture-to-literal generator is also not a proved parser.
- The independent meanings do not implement a general JSON Schema interpreter or
  prove schema-document translation. This remains a candidate profile and API.
- A requested profile reference is an input, not proof of ownership. Empty staging
  can be structurally valid; it neither resolves a relation nor grants authority.
- Captured-root membership is a structural condition. Actual root issuance and
  review authenticity must be checked by the source providers before admission.
- The existing qualification pipeline still needs an authenticated staged-catalog
  input adapter, complete source/Selection joins and all nineteen realized policies.
- None is a local refusal result; public syntax/semantic/authenticity/freshness/
  resource classifications and measured runtime limits remain pending.
- Whole-source/effect/theory closure and mandatory independent checking remain
  separate. Fresh pinned Lean replay is not independent proof checking.

N01 remains in progress, N02/N03 remain unstarted, and K04/global meanings remain
pending. K00-K03 acceptance retains its actual meaning-only scope. All seven
extensions, 41 relations, 550 endpoint pairs, 263 pending IDs, 90 retained original
discharges and the actual final new bounded-use assessment remain in the plan.

Fresh verification passes 50 new declarations (18 general/field/boundary results
and 32 worked controls), through 50 compile/replay invocations, 468 dependency-
inclusive axiom inspections and 50 matching-phase import audits. Only the allowed
standard axioms occur. Fresh compilation/elaboration took 86.573 seconds
total, with a 17.181-second maximum module. These timings are not runtime
resource measurements. Same pinned-kernel replay is not independent checking.
