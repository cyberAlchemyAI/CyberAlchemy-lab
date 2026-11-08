# Installer continuity boundary for T19/T25

The recovered native install verifies exactly 1,010 selected payload files. The
previous T16 signed family nevertheless stopped after its `/tmp` install was
lost because `context-native-role.json` selected an absolute directory path,
filesystem device/inode, receipt hash and role-code binding. Recreating a
same-named directory or copying that old attestation would not establish the
same host. The durable successor fixed the immediate loss by selecting the
actual durable installation and producing a fresh signed family; that alone
is not two-install or restore qualification.

The final package must carry stable code, artifact bytes, schema/profile
contracts, native ELF/wheel selection and an exact host-role input contract.
After the selected ABI is verified in each private application root, the
provisioner must generate a new host-role binding over that root's real path,
owner/mode, device/inode, installation receipt and executable/dependency
hashes. Select that binding independently for the Context/native executor
before allocating a resource or writing an effect. Host-role metadata is an
execution proof, not an Artifact graph node or a governing role assignment.

For the current source constructor, the role JSON is itself a Source manifest
input. If retained during the installer rehearsal, each installation needs a
fresh exact Source/Context selection containing its true host-role binding;
record those differences explicitly. Do not claim byte-identical Source
profiles across these installations. The preferred final seam separates the
stable Source/artifact/code closure from its per-install selected host inputs.
Neither route may silently rewrite or weaken a frozen predecessor.

The installer acceptance record should compare these independently:

| Selection | Required observation |
| --- | --- |
| Public engineering package | Same SHA-256 and exact member bytes in both roots. |
| Stable artifact/code/schema closure | Same declared public identity and bytes; no host proof imported as an Artifact. |
| Selected ABI payload | Same 1,010 member names/digests/modes after empty install and restore. |
| Host-role binding | Fresh path, owner/mode, device/inode and receipt for each actual root; binding digests may differ. |
| Source/Context execution selection | Exact observed pins, with any per-install source metadata differences disclosed. |
| Sessions and opaque contexts | Fresh identities/nonces; no private RAM, identity reuse, key restoration or prior live proof carried across roots. |

Exercise empty install and cold startup in two separate private roots, exact
retry, fresh-process replay, third-root restore and rollback. Destroy only
owned resources. A copied stale inode attestation, substituted native binary,
wrong receipt, byte-changed artifact, scope mismatch and escaped path must
refuse before resource allocation/effect. Record each root's actual evidence
and keep the original protected/owner/canonical-release obligations separate
from this local engineering qualification.
