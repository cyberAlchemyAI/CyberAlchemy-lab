# Context phase pure slice 0001 — review freeze

Status: **inert implementation candidate for independent static review**. This implements only the first pure slice of `CONTEXT-PACKAGE-ADAPTER-IPC-DESIGN-0002.md` (SHA-256 `fd03555e24cc274d6a8706ba99b2a0605eb6e7c235520bc054ac3440caea6d32`), whose independent design review returned bounded PASS (SHA-256 `328869e5356b9a1c575c13a9d0135292b53ff3c8242d5d536dc263e81a7cbb1a`). It creates no family/package leaves, starts no process and does not read protected Source8 inputs.

Frozen files:

| File | SHA-256 |
|---|---|
| `context_projection_0001.py` | `6cbe039fe3e625c8820df8606e7c43484536841d9b4e0ad3a07a300c5a251afe` |
| `context_package_adapter_0001.py` | `689d47856f695e19e1ea405d61ec6425c11e54e70260f99039612a188076b47a` |
| `tests/LC-U02-05/test_context_pure_slice_0001.py` | `2f1aa0f122c50a00b827201be4086a39041c611e5ed3af8bb6c91a90727cfadc` |

`context_projection_0001.context_rows` revalidates the immutable 27-role plan, requires the exact Source source/package and Mapper source/package predecessor paths, reads each through a caller-supplied held-byte callback and checks its digest, applies the existing exact-count `phase_rebind.rebind` to the three Context code leaves, and returns all 11 output bytes/bindings in selected role order. `context_bindings` returns the 11 prospective bindings. This callback does not establish FD custody by itself; the future effect controller must hold and recheck identities.

`context_package_adapter_0001.adapt` accepts only exact externally selected full preimage SHA-256 values for `build.py` or `generation.py`. It pins the six reviewed old/new AST span hashes for guarded package PREPARE, complete `emit` write, and complete `provision` write, plus the single native-call span. It requires the original `emit` boundary predicate and `provision` readback/hash successor, inserts only a selected inert bridge import, proves an inverse AST diff back to the complete input tree, and compiles at Python optimization 0 and 2. The build postimage still contains **two** `_t35_effect_refused()` calls for the unimplemented private-root lifecycle. The bridge module does not exist, and `effect_ready` is false; executing the postimage is outside this candidate's authority.

Validation on Python 3.14.4:

```text
python3 -m unittest implementation/lab-runtime/candidates/runtime-completion-0001/tests/LC-U02-05/test_context_pure_slice_0001.py -v
5 tests OK
python3 -O -m unittest implementation/lab-runtime/candidates/runtime-completion-0001/tests/LC-U02-05/test_context_pure_slice_0001.py -v
5 tests OK
```

The tests use only checked-in historical role templates and synthetic disposable predecessor bytes. They cover exact 11-role output, three pin rewrites, all unchanged roles, wrong held bytes/path/missing predecessor refusal, inverse AST/postimage verification, two retained effect refusals, and rehashed mutations of the package guard, FD/write span, raw encoding branch, policy readback, timing prefix, native call and output parity guard. No Bubblewrap, native executable, builder entrypoint, package mediator or host policy effect was invoked.

Remaining before any Context package effect: private-root `TemporaryDirectory`/`chmod`/absence adapter and mount-visible cleanup semantics, selected IPC bridge/held writer, full independent Context validators, exact native outer argv/ABI, packet arithmetic and process cleanup, current Source lease and actual same-scratch Mapper package. The present code supports static construction/projection review only, not a fresh Context package, protected grant, activation or LC-U02-05 acceptance.
