# Context private-root adapter and IPC model — inert review freeze 0001

Status: **inert static candidate, no effect capability**. This follows the independently reviewed pure Context slice 0001 (`CONTEXT-PURE-SLICE-0001.md`, SHA-256 `6c1c0d18dba099a7eb845b9e5f2a0ee5ddf289adb0e58e5e0a9f6d77501cef75`) and its bounded PASS review (SHA-256 `ae3fd6ac2eb1638ee31deef663c301af266aefeba40309cae949137b20394e23`). All files below are new and versioned; prior candidates and Mapper files are unchanged.

| File | SHA-256 |
|---|---|
| `context_private_adapter_0002.py` | `5aedf3182649d09c401590e4dc2b706fa67dda694f65dff143e2ed8ef1c9e38f` |
| `context_ipc_model_0001.py` | `6a7c64b83a5ea391de72915e6c4f6d626e049225b8224d794d49116ea622d248` |
| `tests/LC-U02-05/test_context_private_ipc_0001.py` | `2d37e18924c5674b66d04203ea9eaa5268c3c7b8844c5f6bf1e7a4998527afc0` |

`context_private_adapter_0002.adapt` requires the **externally selected** full SHA-256 of the v1 `build.py` postimage. It selects the exact remaining `with` context expression and `root.chmod` refusal AST nodes and the original post-context `require(not root.exists())` node. Three pinned old/new AST hashes, the original Source `reader.open_signed` context, `root=Path(tmp)`, policy path/provision, and exact `finally: channel.close(); key=None` AST constrain the replacement. It substitutes `_ctx_private_root_context()`, `_ctx_private_root_guard(root)` and `_ctx_private_root_absent(root)`, inserts only a separate unimplemented v2 bridge import, proves inverse AST equality, and compiles at optimization 0 and 2. The output has zero direct `_t35_effect_refused` calls but remains `effect_ready:false` because neither bridge exists and the actual private-root custody/mount/cleanup semantics are unimplemented. The `_ctx_private_root_absent` name means an **external host absence receipt**; it does not assert disappearance of an active read-only mount in the builder namespace.

`context_ipc_model_0001.ProtocolModel` is an in-memory transition model, not a socket server, writer, grant verifier or durable ACK. It accepts canonical bounded JSON control frames through the existing pure codec, with exact attempt/selection/ordinal/peer-model fields and a sticky retained failure. Its closed 46-step sequence requires PREPARE with absent-before and empty-after package receipt; PRIVATE_ROOT receipt; public-policy PROVISION with current Source period, exact UID/scope/binding/budgets and Ed25519 public key; four initial leaves including a cryptographically verified synthetic nonce proof; one NATIVE_READ digest match against selected fresh Mapper output; 30 numbered artifacts plus four derived leaves; RELEASE_PRIVATE with policy/root absence receipt; result and manifest; and FINISH with 40 leaves and 39 sorted exact manifest bindings. Request, artifact, policy, per-leaf and total package sizes are bounded. A model receipt is explicitly synthetic and never evidence of held FDs, mount visibility, `fsync`, kernel credentials or actual package bytes; full blob transport/content validators remain unbuilt.

Validation on Python 3.14.4:

```text
python3 -m unittest implementation/lab-runtime/candidates/runtime-completion-0001/tests/LC-U02-05/test_context_private_ipc_0001.py -v
9 tests OK
python3 -O -m unittest implementation/lab-runtime/candidates/runtime-completion-0001/tests/LC-U02-05/test_context_private_ipc_0001.py -v
9 tests OK
```

Tests use checked-in historical role templates and synthetic predecessor bytes, a fixed synthetic Ed25519 key, a fixed clock and synthetic receipts. They cover inverse-diff/private-root mutation refusal, the full 46-message schedule, wrong ordinal, private-key field rejection without failure-text disclosure, stale policy, preexisting even-empty package, changed nonce signature, disconnect and sticky retention. They import or run no generated Context role, bridge, native child or Bubblewrap and write no package or protected input.

Before an effect, a separately reviewed implementation must supply real held nofollow absence and mount-source identity proofs, the read-only private `/tmp` visibility and UID/mode stand-in, credential-bearing socket/blob transport, durable no-replace writes and ACKs, full package/native/source validators, bounded process closure, exact outer native argv and a current same-scratch Source→Reader→Mapper predecessor. This slice supports static construction review only; it establishes no protected Source8 permission, Context delivery, activation or LC-U02-05 acceptance.
