# LC-U02-05 Mapper read-only poststate candidate, version 0003

The sealed 0002 disposable attempt ended `FAIL-disposable-mapper-readonly` at
`mapper_poststate`. Its reviewer identified a deterministic contradiction:
Mapper materialization deliberately adds exactly four `mapped/` roles and
`mapped/source-manifest.json`, but the 0002 post-child check calls the
pre-Mapper prefix inventory, which refuses every `mapped/` path. The receipt
does not prove the child return code, stdout, or subsequent native check.
Its Source, Reader, and Mapper child closure observations and cleaned scratch
remain historical evidence for that failed attempt only.

Version 0003 is copied from the frozen 0002 candidate. The only effect-path
change is at `mapper_poststate`: it inventories the whole disposable family
with `source._tree_files` and `source._tree_dirs`, then requires exact equality
to the inventory returned by Mapper materialization. The check still refuses
nonzero child exit, stderr, changed predecessor or Mapper bytes, extra leaves,
`mapped/packages`, and `context`. Its numbered result name is
`phase-mapper-readonly-result-0003.json`. Child launch, timing, group cleanup,
scratch retention, receipt claim ceiling, and no-replace publication remain
the 0002 implementation.

Pure tests construct an exact five-leaf Mapper poststate and show that the
prefix oracle refuses it while the 0003 poststate check accepts it. Mutation,
extra Mapper leaves, Context and package directories, nonzero exit, and
stderr all refuse. This is an inactive candidate pending an independent
exact-byte review and a separately controlled one-run disposable attempt.
It proves no Mapper child success, native Mapper construction, protected
authority, escaped-session absence, host qualification, activation, or unit
acceptance. The receipt's process claim remains original-group-only; the
LC-U03-02 cgroup oracle is still required for protected host containment.
