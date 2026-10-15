# Maintained full34 composite operator — T06 candidate

`launch.py` is the maintained entrypoint for the Base28 + Action3 + Governance3 composition. It verifies the independently pinned launcher sources and all 1,010 selected T07 installed files before starting the selected Python 3.14.4 interpreter in isolation. It starts a serialized stdio process; it creates no network service, background installation or admitted operational mode.

The executable configuration contract lives in `composite.config.schema.json` and the stricter semantic `config_shape`, `preflight` and `authorize_handoff` checks in `composite.py`. The configuration has one candidate purpose, exact software/profile/member/bootstrap pins, T34 technical receipt provenance, stable dependency selection, all three independent workspace/policy/public-key/file selectors, three separate handoff issuers, and bounded transport. The absolute startup window is independently selected between 1 and 300 seconds so mandatory source/schema checks have time to run; no grant, policy or lease expiry is extended. Pass an independently retained SHA256 of its canonical JSON encoding (`control.compact`); keep the physical configuration outside Git, owned by the operator with mode 0600.

Example invocation once the coordinator has provided the exact candidate inputs:

```bash
python3 /home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/launch.py \
  --launcher-source-sha256 <independently-selected-launcher-manifest-sha256> \
  --config /tmp/<independently-owned-operator-root>/operator-config.json \
  --config-sha256 <independently-selected-canonical-configuration-sha256>
```

These placeholders are prerequisites, not fabricated working credentials or source pins. The selected API17 source guard is called as implemented; the launcher never substitutes a PASS, supplies a reduced source profile, reuses API16 pins for changed code, or treats an absent branch as a complete composition. T34's technical receipt is metadata provenance only. Its reader key is not upgraded to Action, Governance or governing authority, and expired/revoked T34 custody cannot be renewed by this launcher.

Startup validates every selected private policy, credential public key, root inode, owned input inode/mode/digest, current policy period and immutable software before any actual branch construction. Private material comes only from explicitly selected owned locators. `O_NOFOLLOW` traversal, selected UID/mode checks and preimage checks refuse changed roots, symlinks and foreign selectors. Neither private keys nor policy bodies are printed. Missing credentials refuse before a challenge, service lock or auth evidence effect.

Action requires an actual newly constructed UTC `SessionLease`, with newly generated instance and session references. A previously signed source bound to an old lease cannot simply be reused in a fresh process. The explicit two-stage contract is:

1. After preflight the same process constructs a real lease, capped by the original unchanged grant/policy expiry, and emits only its public fresh references and deadline.
2. A separately selected producer supplies a bounded handoff with exact new source/signature/status/grant/policy selectors. Three independently configured current issuer selections sign it separately for custody, grant and policy. The existing source key must also sign the exact new source bytes. A custody signature alone cannot authorize a changed grant or policy digest. Technical issuer selections do not prove genuine governing issuance; operational issuance remains a separate prerequisite.
3. The launcher preserves source records, RoleAssignments, refs, scopes and periods exactly. Only source runtime references and matching status handle attributions, the grant's source digest, and the policy's source/grant digest bindings can change. No budget, permission, current stop/revocation state or expiry is widened. It never restores Session RAM or copies old Session identifiers into the new lease.
4. The process holds that same lease while waiting, bounded by the startup deadline and unchanged permission period. If it exits or restarts, new references require a new independently authorized handoff. Missing, stale, exhausted or unauthenticated handoffs refuse.

With a valid current handoff, code calls the actual `ActionRuntime`, `ActionChannel`, `ActionService`, `ReaderChannel`, Base `Service`, `GovernanceHost`, `GovernanceChannel`, `GovernanceService` and `IntegrationService`. All three receive the same exact `Schemas` object and common profile binding. No dispatcher callback or clock is replaced. Every original guard remains active.

The composite emits three independent nonce challenges. Proof frames arrive in Base, Action, Governance order as the closed wrapper below; the Base and Action proofs validate before Governance's original authentication writes its owned proof evidence. Decode only the wrapper's base64; pass its exact original proof bytes to the selected original channel:

```json
{"schema_version":"lab-composite-branch-proof/v1-candidate","branch":"base","proof_base64":"<original-proof-bytes-base64>"}
```

After all three authenticate and the actual composition passes, `lab-composite-ready/v1-candidate` reports the full34 catalog and independent contexts. Catalog visibility is distinct from permission. A common principal across independent policies does not combine their permissions; branch nonce/context, grants, periods and original call checks remain separate. Base-only startup cannot emit full34 readiness.

Calls then use one LF-terminated UTF-8 JSON envelope per frame. Remove only framing LF; preserve all other bytes, including whitespace, CR, object order and the original embedded message bytes. Pass each envelope directly to `IntegrationService.call`. Its original context/operation routing selects branch-owned `operation.inspect`; the launcher supplies no replacement inspector. Dispatch is strictly serialized and synchronous. Per-branch call IDs, nonce, request/response budgets and expiry stay with the original branch.

Clean EOF closes owned channels/services and the live lease in reverse construction order. Partial EOF, oversize lines, exhausted frame/wire budgets or startup deadlines emit a bounded transport error and terminate; the launcher does not drain an unbounded line or redispatch effects. Response limits are independently configured and must cover every selected branch policy. Exceptions emit a generic bounded error without policy/private/source-body detail. Cleanup closes only resources created in this invocation; durable operator roots, old keys, grants, ledgers and unknown residue are retained.

Focused development evidence currently proves 28 preflight/handoff/framing controls, actual UTC lease freshness in the helper tests, a real pipe deadline, and a fresh selected subprocess missing Governance credentials refusing before challenges/locks/readiness. The semantic handoff fixtures are explicitly inert and schema-unqualified; no actual branch consumes them. Transport observers are declared observers, not fake authenticated services. These controls do not prove full34 construction, genuine issuer authority, catalog output, actual branch-owned inspection or final shutdown across the three selected original services.

Full fresh-process qualification remains pending the coordinator's exact API17 task-local source/profile/bootstrap/execution selection and independently scoped actual branch inputs. Genuine operational issuer authority and admitted operation remain separate obligations. T06 and the complete Lab goal are not closed by focused helper evidence.
