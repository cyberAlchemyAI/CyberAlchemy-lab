# Independent review: WSL host storage bootstrap candidate 0002

Reviewed 21 October 2026. **Verdict: PASS-BOUNDED for the inactive plan, scratch model, dry-run rollback, and isolated container parent-denial oracle. Host installation and protected runtime activation remain NO-GO.** No candidate source was edited during this review.

Frozen SHA-256 inputs checked before and after execution:

| Input | SHA-256 |
| --- | --- |
| `host-install-candidate-0002/README.md` | `d102424fcc4980c773e0f27daa39e093e416cbbe32ad48cb240978e6cdf80a43` |
| `host-install-candidate-0002/storage_bootstrap.py` | `6245643d0805986049dba3a833f47c33e93102558f5ddf39480f3fbc494b1c6a` |
| `host-install-candidate-0002/test_storage_bootstrap.py` | `1dd406b153bf52743b4f92535ccb30c405750752d162f31ecb96a8e8184ca744` |
| `host-install-candidate-0002/docker_parent_oracle.py` | `eb0e73c31f84628b3a02ae3c8bba2166502aba1f8866ee0c624f23ed27e49eb4` |
| `host-install-candidate-0002/run-docker-oracle.sh` | `f87ff1285f1ad3c83435846d1f28eab7a77aa4d0d83ff25adc8105f0bb50c949` |
| `host-install-candidate-0002/write-manifest.json` | `622b62ba04fe72df0de25e54232d376b07550ae887d76970def400b7f24b61a5` |

`storage_bootstrap.py --plan` returned `INACTIVE_NO_HOST_APPLY`, `activation: false`, the exact five proposed paths absent, and root:root `0755` `/var` and `/var/lib` on device 2096. Held nofollow ancestor descriptors reported both access and default POSIX ACL xattrs absent (`ENODATA`) at this observation. A separate injected `EACCES` on every xattr read was reported as `unknown:EACCES`, not as absence. The path survey and held ACL reads are separate observations; they do not establish an atomic preimage or exclude alternate writable aliases, capabilities, inherited FDs, or later change. `--apply` returned 3 with `HOST_INSTALL_EFFECT_DISABLED`; source inspection confirms that refusal precedes `plan()` and any host installer call.

All 9 tests passed with `-W error::ResourceWarning` in both normal and `python3 -O` modes. The scratch session is freshly made under `/tmp`, bound to a process-local token and inode, and `_make` rejects unrelated descriptors and wrong stage parents in the tested cases. Every scratch creation starts at `0700`, fsyncs held parent and child, and widens only the public ancestor after the private descendants exist. This is an accidental-use guard, not an authority boundary: the retained same-UID interleaving demonstrates that another actor can replace a newly created name between `mkdir` and `open`, so the model can witness an alien inode. The rollback route checks the five inode witnesses and empty shape but returns `DRY_RUN_ONLY_PARENT_WRITABLE`; it contains no unlink or `rmdir` for the scratch or host storage tree. Its changed-inode and dependency tests refuse without deletion. Test teardown uses `shutil.rmtree` only on each new disposable scratch fixture.

The explicit Docker oracle ran the pinned local image ID with no host bind or network, read-only image root, tmpfs `/tmp`, dropped capabilities except those needed for setup, and `--rm`. Container root held a `0700` parent; the UID/GID 20001 outsider had no inherited directory descriptor or effective capabilities. Rename of the selected child, sibling creation, parent open, child stat, and `/proc/<root-pid>/fd/<child-fd>` open all returned `EACCES`. A post-run `docker ps -a` filter for that image ID listed no remaining container. This proves those five denials in that disposable container configuration only; it is not the WSL host's installed negative oracle.

The five proposed host paths and order in `write-manifest.json` are consistent with the scratch ordering, but no root-owned parent has been installed. Before any effectful release, a distinct exact implementation and independent review must establish the selected ext4 mount and root-held ancestors at effect time, exclude hostile writers and writable aliases, choose a collision-free service UID/GID, specify unit/cgroup/proc and private FD handoff, and test same-UID exclusion on the actual WSL host. It must account for parent metadata, durability, partial failure, and rollback under that exclusion. This candidate selects no account, unit, broker, protected Source8 package, or issuer grants; it completes no G01/G02, T02/T35, or original protected runtime qualification.
