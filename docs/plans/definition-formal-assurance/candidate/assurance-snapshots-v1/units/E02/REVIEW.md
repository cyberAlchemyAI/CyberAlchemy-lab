# Immutable candidate evidence publication

E02 captures and publishes the exact evidence inputs defined by E01. It is a local candidate publisher: publication means installing a complete captured directory under the candidate evidence area. It establishes byte identity and a bounded currentness check, while source fidelity, actual logical evidence and independent readiness remain separate. The full project still covers all 183 current definitions.

## Capture and identity

The publisher validates the evidence contract against independently selected requirements, derives its explicit artifact-reference set, and reads each input through the descriptor-relative no-follow resolver. Every captured digest must match its declared reference. Native result data and the embedded required set must match their actual selected files. The selected source snapshot is also reconstructed and checked against the source root; every selected source must be a current identity/version in that snapshot.

The publisher keeps a closed list of original artifact paths, exact digests, sizes and content-addressed object paths. Equal bytes can share one stored object, but distinct logical input paths remain in the manifest. The bundle identity includes the envelope digest, complete file list, required-set identity and exact E01 schema/checker/receipt plus publisher build digests. Changing evidence bytes, a selected source version, path/context metadata or the producer build produces a different identity under the digest assumptions.

This identity establishes which bytes and declared producer context are selected. It does not authenticate a source-owner review or prove a provider result. Independently choosing the expected producer build is an additional verification input; inspection makes clear whether that choice was compared or remains a historical claim.

## Atomic create-only installation

Staging uses a newly created UUID directory with mode 0700 and exclusive files with mode 0600. The directory is private and absent before creation. Each object and metadata file is flushed and fsynced, and the object/staging directories are fsynced. The publisher does not modify existing outputs or clean up interrupted attempts.

Final installation uses Linux `renameat2` with `RENAME_NOREPLACE`. Ordinary directory rename can replace an existing empty directory, so a prior existence check followed by ordinary rename would leave a race. The no-replace operation rejects a competing target atomically, whether it is an empty directory, a populated directory, a regular file or a symlink. When the syscall is unavailable, publication remains unresolved and preserves the private attempt. There is no unsafe replacement fallback.

Output parents must be under the candidate evidence area. Their components are opened as directories without following symlinks. A held parent descriptor is compared with the selected repository path before installation. This protects the operation against an already substituted parent and detects a moved parent at that check; it does not claim permanent filesystem isolation against a same-user actor after the verification boundary.

The published directory is create-only and byte-bound. Its owner can still edit filesystem bytes, so immutable identity does not mean an operating-system immutable flag. Inspection detects changed objects, manifest/envelope substitutions, unknown files or objects, missing files, duplicate/changed input bindings and identity/directory disagreement. No permission or digest is described as proof authority.

## Publication outcomes and currentness

| Outcome | Preserved state | Meaning |
| --- | --- | --- |
| Published candidate | A complete new captured directory | Exact installation and source/artifact checks succeeded at the publication boundary; semantic readiness remains false. |
| Collision | Existing target and private staged attempt | The target was not replaced. The attempt can be inspected separately. |
| Unresolved before installation | Inputs, earlier published outputs and any created private attempt | No successful installation is claimed. |
| Currentness unconfirmed after installation | Newly installed captured directory and earlier outputs | A race/change was detected; the new directory is retained as evidence but is not reported current. |
| Durability unconfirmed after installation | Newly installed directory and earlier outputs | Post-install fsync failed; durability is not claimed. |

All captured artifacts and the complete source snapshot are checked before installation. They are checked again after installation before a successful publication report is returned. A source mutation or registry change during that boundary therefore prevents a current successful report. The checks describe that boundary, not a promise that inputs remain current forever. Later applicability verification must rehash the selected live bindings.

Historical inspection verifies the captured source registry/provenance and artifact bytes without substituting a newer live source. With a live source root, it also verifies currentness and rejects stale captures. A new source version does not delete or relabel its earlier evidence. The old package remains a valid historical capture while losing live-current applicability.

## Manifest closure and runtime limits

The capture closes over E01's explicitly defined artifact references. Toolchain records can carry exact external executable/package requirements, but this publisher does not ingest arbitrary nested path strings or assert that a whole runtime distribution is archived. E03 must independently check the selected provider/runtime requirements and the exact native semantics.

The existing safe resolver limits each artifact read to four million bytes. This publisher additionally limits total captured artifacts to 32 million bytes and the envelope to four million bytes. Exceeding a limit leaves publication unresolved rather than dropping inputs or producing a partial manifest. These are bounded candidate limits; this unit does not assert arbitrary-size or complete semantic coverage merely because a package was installed.

## Verified controls

All 22 tests pass. They exercise actual publication and closed inspection; repeated identities; a competing empty directory, file and symlink at the final race; interrupted and partial writes; changed source, registry or alignment artifacts; restrictive modes; unsafe output parents; unavailable atomic support; corrupt/extra objects; changed evidence; an admitted synthetic next-version epoch; old historical capture preservation; independent producer-build comparison; total byte limits; and post-install source/fsync uncertainty.

The retained worked cases contain two successful synthetic source epochs, a same-identity collision, an interruption, and the empty-directory final race. The two packages are replayed after relocation as historical captures. Their fake source identities stay inside the captured objects; no synthetic definitions or admissions are installed in the Lab's canonical authority directories. The actual Lab source snapshot remains separately verified.

Candidate agent review accepts these publication and preservation controls for the next stage. E03 must independently regenerate requirements, check model witnesses and provider builds, and keep source fidelity and theorem trust separate. All-current translations, dependency closure, joint populations/theories, required universal evidence, source-owner dispositions and the final complete review remain outstanding.
