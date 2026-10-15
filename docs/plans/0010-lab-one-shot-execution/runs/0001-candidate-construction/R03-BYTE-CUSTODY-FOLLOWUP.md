# R03 admission integration: retain original candidate bytes

Status: pending implementation analysis. Authority effect: none. No admission was attempted by the preparation proof.

The new preparation API retains original candidate content bytes and hashes them independently from the selected runtime target/core structural digest. The realistic fixture deliberately uses an original JSON encoding distinct from the runtime inherited canonical encoding.

Before implementing admission.apply, files.materialize, exports and complete canonical/projection joins, close this transport obligation: the approved original target bytes must remain exactly retrievable after publication. The inherited transaction stores parsed record objects and derives embedded-value bytes with its canonical encoder. A writer adapter must not silently substitute those encoded bytes for the reviewed original content while retaining its byte-exact header claim.

Declare the selected original-byte custody representation, bind it into exact target/review/core and signature closure, verify parsed-value equivalence separately, and implement canonical/query/export/cold/recovery parity for the actual original bytes. Preserve legacy original transaction representations and signatures. Any new carrier/encoding/publisher contract is an independently scoped S02/R08 review member.

The partial preparation proof establishes exact staging, prospective schema/core checks and private operation inspection only. It closes no admission or original-byte publication obligation.

Sources: api-v12/example_fixture.py, candidate.py, artifact_model.py, the frozen runtime v2 operations/store source, and docs/proposals/0008-lab-api-contracts/POLICIES.md. This analysis introduces no new approval stage or scoped runtime exception.
