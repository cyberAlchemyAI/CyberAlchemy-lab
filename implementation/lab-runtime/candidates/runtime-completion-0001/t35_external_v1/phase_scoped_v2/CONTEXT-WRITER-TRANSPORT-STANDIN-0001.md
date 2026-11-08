# Context scratch writer and transport — frozen stand-in 0001

Status: **frozen for independent review; no broader effect selected**.

| New file | SHA-256 |
|---|---|
| context_package_writer_0001.py | `76cb04453692165c7253a0616870be5507f35f331dfce97eb266f51f1a4b1e5b` |
| context_package_transport_0001.py | `9b9197776ecf8324a85a1b50af8a24b9601f10e199f84c98494d032a3dbec307` |
| test_context_writer_transport_0001.py | `a199ca265878befea243206118e0183badb5c1a97ce0407b2d0b2f3a51fc3f18` |

The frozen Context adapter/model and reviewed Mapper files remain unchanged. This slice reuses only Mapper held-directory/write/readback and credential-bearing seqpacket primitives. It does not invoke Mapper spawning, a generated Context role, either missing bridge, native code, Bubblewrap or protected Source8.

A one-shot scratch session admits only a dedicated owned mode-0700 `/tmp/lc-u02-05-context-writer-*` tree ending in `output/legacy-fixture-source/context` and one matching private scratch root. An exclusive fsynced marker precedes package creation. Any preexisting `packages` entry or private root, including empty, refuses without adoption. Held nofollow ancestors and directory/mount identities are checked before writes. Each leaf uses O_EXCL, mode0600, complete bounded writes, file fsync, exact inode/metadata/byte readback and parent fsync before acknowledgment. Emitted descriptors remain held to prevent inode-reuse adoption. Extra leaves, symlinks, FIFOs, changed emitted bytes/inodes or attachments fence the writer.

The frozen model determines all46 steps: prepare, private root, public policy, four initial leaves, synthetic native digest,30 artifacts, four derived leaves, private release, result, manifest and finish. Real public policy bytes are written in the held private root. RELEASE_PRIVATE checks the exact policy and root, unlinks only that policy, syncs, removes only that held empty root and syncs its parent. The result and manifest cannot be emitted before release. Partial release remains UNKNOWN and does not authorize final leaves.

The manifest is explicitly `lab-context-scratch-package/v1-inert`, with a scratch-only claim ceiling. It has39 sorted exact filesystem byte bindings, selected source binding, and exact delivery/provenance bindings. Finish reopens/reads and hashes all40 leaves and checks names/custody. This is not the historical actual-delivery schema and no implicit conversion or broad content validation is claimed. The selected source binding is syntactically checked fixture data, not a real Source lineage proof.

The socket protocol uses bounded canonical frames, strict ordinal/attempt/selection, one bounded uploaded blob,32768-byte chunks and a closed next-leaf target. Buffered chunks receive BUFFER_ONLY; file/policy/directory observations are explicitly scratch observations. Genuine kernel credentials are checked on both sides, SCM_RIGHTS are closed then refused, truncation/replay/disconnect poison the session. Lost final ACK marks UNKNOWN even after complete files; no reconnect/retry path exists. NATIVE_READ remains MODEL_ONLY.

**24 normal +24 optimized checks passed**, OS exit0, with776 selected files unchanged. Tests include the complete40-leaf/39-row package and real multi-chunk socket transfer, empty-preexisting refusal, private ordering/key-field rejection, exact manifest mismatch, symlink/FIFO/inode substitution, partial write, file/parent/private-release fsync errors, lost final ACK, replay, rights closure, peer-start mismatch, truncation, disconnection, umask0777 and uncertain close. Each run logs24 exclusive scratch/private root cleanup pairs and verifies their absence after test-only teardown. Failure residue is first asserted; production code does not clean partial packages.

The two endpoints are in one process. There is no builder FD isolation, RO mount, hostile same-UID protection, process containment, authentic host enrollment, current Source lease, native projection or actual Context delivery proof. The model’s `readonly_visible` field remains explicitly synthetic while host scratch is writable. Private keys stay local to test generation and only public policy/proof enter transport. No source schema, frozen adapter, accepted broker or prior reviewer artifact was edited.

Exact commands, environments, timestamps, input manifest, outputs, exit codes, cleanup observations and all source hashes are in `context-writer-transport-freeze-0001.json` (SHA-256 `ccdd1b61105df88cb1dc5e198b4c344e265bd0546188e01f346a7a983f5af40d`). Stop here for independent review before any broader composition or effect.
