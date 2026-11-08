# Independent Context JIT policy0002 static review

Verdict: **PASS for the effect-disabled synthetic validator only.** The two policy0001 authorization-join failures are corrected. Context effect, protected authority, and actual Source scope/family selection remain unproven.

## Exact reviewed state

- Frozen `context-jit-policy-0002/freeze.json` SHA-256 `e0286814e0e34770a0fa4b7fe0d9ab08161e5ea3264386c9f0b6cb76f201a391`. All seven bound members independently matched exact frozen sizes and SHA-256 values; `jit_policy.py` is `f40ca49a9f9f72e1c8490d753633c1db4307736a1b2f41080ee8a5f684c33a7a`, and its test file is `c5350950ad3e2676d67a6f218fa43490259b9d2b491b1d624a734d2969ab23c6`. The predecessor freeze and FAIL review pins also match.
- Independent normal and `python3 -O` test runs each passed 31/31. Rehashes of the selected local Source package/period, Reader code/manifest, Mapper package, and four reviewed public AUTH/policy guard inputs match the constants in the source and freeze. The selected period is the local candidate's 24-hour interval from `2026-10-20T08:20:00+00:00` to `2026-10-21T08:20:00+00:00`, authority `none`, owner outcome null.

## Corrections verified

At `jit_policy.py:223-235`, `validate_policy` now takes authorization **bytes** and an expected SHA-256 instead of a result dictionary. It checks the exact digest and re-runs `validate_authorization()` on the same bytes. That validator enforces the closed canonical schema, family, episode, scope, period binding, current <=1,200-second interval, no issuer claim, authority `none`, null owner outcome, and real/effective UID/GID. Policy validation separately enforces principal/scope, UID, period, fixed operations, posture, <=1,200-second interval, input/output/session budgets, canonical 32-byte public key, and identity recheck. The policy result carries the computed authorization digest. At lines 250-253, both authorization endpoints bound the policy interval.

I independently reproduced the prior attacks with synthetic data. A policy call supplied the old forged result dictionary (`authorization_sha256` all zero and extended expiry): **REFUSED**. Expired authorization bytes with their matching digest: **REFUSED**. Valid authorization bytes with an unrelated digest: **REFUSED**. A policy starting `11:50` before its valid authorization's `11:59` start: **REFUSED**. The exact valid bytes/digest and contained policy interval: **ACCEPTED**. The v1-to-v2 source diff confines the material change to byte-bound revalidation, the start endpoint, the returned digest, and malformed-JSON refusal.

The inert selection still refuses literal `UNSELECTED` family and scope inputs, noncanonical or non-`/tmp` family/source/private-root paths, ancestor/alias overlap, wrong role/period pins, expired period, and real/effective UID/GID mismatch. The authorization path remains under the selected Source root; the policy path remains in a disjoint private root. The only private-root test uses schema-invalid dummy bytes with the reviewed held readers and owned cleanup. `EFFECT_ENABLED` is false; both actual provision and Context launch entrypoints refuse unconditionally.

## Claim ceiling and effect-time obligations

`select()` still accepts a syntactically prefixed placeholder such as `scope:UNSELECTED` as an **inert** synthetic selection; it does not establish that a scope was issued by the selected Source. It also accepts a caller-selected `/tmp` family path without proving a closed actual family. This is consistent with the declared synthetic-only claim but cannot be promoted to effect authorization. The expected authorization digest is caller-supplied to this oracle; the future adapter must bind it to exact bytes obtained through the reviewed held no-follow AUTH reader and independently pinned authorization artifact. `reviewed_preimages()` is explicit, not automatically called by `select()` or either validator, so the adapter must enforce that check and the actual Source scope. The lifecycle remains an order model, not a filesystem implementation. The original Context builder's key/path effects, private-root provisioning, Context bridge/writer, protected issuer grants, and Context Docker effect are outside this review.

No key, grant, protected Source body, private authorization/policy artifact, or Context effect was created or read in this review.
