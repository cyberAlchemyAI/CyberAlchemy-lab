# Context policy/topology successor 0002

Effect-disabled, pure/inert construction. No AUTH, policy, key, private root, signature, protected Source body, socket or Docker operation is created. The candidate defines and projects the minimum semantic changes necessary for a parent-custodied policy and original Context child to coexist. It is not a deployable endpoint or authority provider.

This disjoint successor corrects R01/R02 in the frozen 0001 independent HOLD review. The exact projected guard, control, build and release-hook bytes and six-bind topology remain unchanged. The pure proof and retention state machines now make the first attempted request or release terminal on failure, including malformed requests, wrong peer/currentness, wrong ordinal, nonempty scratch, and detached policy. No valid second attempt can follow an invalid first attempt. The 0001 freeze and review remain immutable.

## Exact path and mount contract

The selected host private policy directory is `/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-jit-private-attempt-0001`; the selected child view is `/context-policy`. Both select exactly `permission.json`. The original guard receives `ROOT` (the complete stage root), not the Source role subdirectory: host stage root is `.../context-attempt/root`, child stage root is `/workspace`.

`project_policy_guard('host'|'child')` replaces only the original `/tmp` ancestry restriction with exact selected private-root and stage-root equality. `project_control()` performs the same exact replacement in the actual projected control module used by HostChannel. The no-follow ancestor traversal, no root containment/alias, real/effective UID/GID equality, 0700 directory, 0600 bounded single-link policy, held/reopened identities and all-close checks remain unchanged. Exact-span inversion proves all other bytes unchanged. This is stronger than allowing any durable path; wrong view, old /tmp root, alternate stage or traversal refuses.

A future reviewed runner must add a **sixth RO bind** of this policy-only host directory to `/context-policy`. Its inventory must be exactly one `permission.json`; no key, journal, grant, control record or unrelated private file may be included. Key lives only in the parent process. Admission/consumption/cleanup journal belongs in a separate unmounted attempt evidence directory, not inside this policy directory. AUTH remains the separately selected 0600 leaf in the Source role's 0700 authorization subtree, visible via the selected RO workspace. Mode/owner requirements must hold for the actual selected child UID/GID with explicit `--userns host`; rootless/remapped Docker is not silently equivalent.

The former five bind public probe proves nothing about the additional policy directory, policy leaf visibility, custody or transport. A disjoint six-bind public-only fixture probe must verify exact inspect sources, child mountinfo RO, owner/modes, readable exact fixture leaf, excluded sibling/key/journal, unchanged workspace RO and post-ACK output visibility. Do not mount the actual host private directory until its own reviewed effect selection exists. Existing namespace PID0 convention belongs only to the selected parent-peer view; parent must independently join actual child PID/start/pidfd/credentials and daemon CID/name. Same-UID hostile host mutation remains outside current cooperative local proof.

## Original child and parent proof transport

`project_build()` selects exact historical guarded build bytes and produces a reversible projection:

- bind `JIT_PRIVATE_ROOT` to the child policy view;
- `_ctx_retained_policy_scope` yields an already selected, retained policy path and never creates/deletes it;
- `_ctx_selected_policy_pin` revalidates held policy bytes/current signed scope; it does not provision a policy or key;
- `_ctx_parent_proof` requests the original exact HostChannel challenge proof from the parent;
- close HostChannel and drop the child's proof handle; retain the attached policy;
- release only the Writer's empty transport scratch at the existing boundary;
- report `owned_host_policy_and_transport_key_removed: false`, `private_policy_retained_pending_external_verification: true`, and `parent_key_custody: EXTERNAL_PENDING_POSTCLOSE_OBSERVATION`.

The build still contains its original effect guards. The projection retains old family/import/source pins and therefore is **not** the final selected family build. A later exact composition must first rebind those pins, install fixed hook bodies, and bind regenerated source/manifest hashes. The existing original `provision` function remains guarded and is no longer called from projected `build`; its dormant definition is not a new reachable provisioning route. The child still invokes original HostChannel authentication, which must verify the returned signature itself.

A future fixed parent endpoint uses a second independently selected bounded SOCK_SEQPACKET connection at `/control/proof`, not arbitrary signing through the leaf-writer opcode. One request is permitted between READY/GO and first EMIT; its reply neither changes nor resets Writer ordinals. Closed request: `schema=context-parent-proof-request/v1`, exact attempt, and original challenge. Closed original challenge fields are schema_version, host_instance_ref, connection_ref, nonce, policy_sha256, expires_at, authority_effect. They must retain `lab-context-host-challenge/v1-candidate`, selected policy SHA/expiry, none authority, exact current connection/host binding and 64-hex nonce. Parent must additionally select Source/Reader/Mapper/profile/issuer/AUTH scope, join the policy public key to its actual in-memory key, and check currentness before durable consumption, signature and send. An authenticated peer or supplied SHA alone is insufficient authority.

Signature bytes must be the original `API.compact(challenge)` bytes. The pure model specifies sorted compact UTF-8 JSON with ensure_ascii=False and allow_nan=False. Before enabling signing, the composed original API.compact implementation must be independently pinned and compared on actual selected challenges, including Unicode. Tests here establish specified encoding only; they do not execute the full original API or cryptography.

`ProofModel` moves UNUSED → UNKNOWN_CONSUMED as soon as its first request is attempted. Only a fully valid first request advances to CONSUMED_PENDING_DURABILITY and then SIGN_ELIGIBLE_MODEL_ONLY after observed durability; invalid framing, peer/currentness, scope or challenge remains permanently UNKNOWN_CONSUMED. Its raw observations and current flag are fixture inputs, never attestation. No sign method is enabled. The actual endpoint still needs exclusive attempt claim, bounded durable admission/consumption originals and capacity reserve, no replay/reset after process restart, credential/truncation/ancillary cleanup, fresh guarded currentness and bounded timing. A lost signature/send reply must remain consumed. The fixed server, host key custody and journal mechanisms are construction work still required, not an external permission excuse.

## Retention and output semantics

Keep original output absence before lazy parent creation; 38 EMITs, RELEASE_PRIVATE transport request, result leaf39, manifest leaf40, sole FINISH41 (42 requests including release) and durable per-leaf ACK. The old release hook requires `not exists(private_root)` and must not be reused. `project_release_hook()` replaces that test with `_ctx_policy_retained_exact`; this fixed hook must revalidate the exact selected mounted policy, not accept a generic callback or boolean. The hook's historical comment remains predecessor text; the new contract supersedes its absence interpretation. The function still releases only the Writer's empty scratch; it does not remove policy or authorize parent cleanup.

The old output validator expects a true removal assertion. Its successor must accept and require the new explicit retention fields for this version, reject old true-removal claims, and preserve exact original delivery/provenance/schema/native checks. Do not alter an already-written manifest after cleanup. A separate parent postclose receipt records key-reference disposal, channel/FD outcomes, exact original output hashes, strict outer OS integer 0, daemon/CID/name absence and independent review. Only after that gate may an independently selected cleanup remove held-identity policy objects and fsync the parent. Failure or interruption preserves UNKNOWN and retained evidence/no retry. Dropping a key reference is not proof of memory zeroization.

`RetentionModel` exercises this order but does not verify external OS or review provenance itself. Its first failed release attempt poisons UNKNOWN with no second release, including wrong ordinal, nonempty scratch and detached policy. Its success state is CLEANUP_ELIGIBLE_MODEL_ONLY, never PASS or an enabled deletion. Actual parent close/cleanup faults require effect-adapter tests before release. Parent death, kernel hard-deadline bounds, inherited FDs, alias/ACL custody and authentic issuer/current Source scope remain separate runtime/integration obligations.

## Next minimal units

1. Independently review these exact projections and revised result/mount contract.
2. Implement fixed proof endpoint/client and retained policy hooks with durable consumption and key-free synthetic causal tests; adapt output validator to truthful result schema.
3. Compose exact fresh family/import/schema closure and six-bind runtime controller; run one separately reviewed public-only six-bind/proof fixture probe.
4. After actual reviewed Mapper evidence and current signed Source scope, separately select/review one-use stage/AUTH/policy effect and Context release. Preserve the original Source expiry (2026-10-21 15:00 UTC); no lease extension or Source8/G01/G02 qualification follows here.
