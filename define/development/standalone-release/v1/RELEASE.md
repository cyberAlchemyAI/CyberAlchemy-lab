# Define standalone release qualification

**Candidate:** `cyberalchemy-define 0.3.0rc2`  
**Result:** standalone installation, tests and end-to-end qualification pass in the recorded Linux scope. Public stable publication remains pending the decisions below.

## What was actually run

The archives were copied and installed outside the Lab checkout under:

`/home/vlad_/.local/share/define-qualification/20261015-MbsEfG/`

Each final environment was created without system site packages. Tests came from the extracted final source archive, while `define_core` was imported from the installed distribution. All dependency checks passed.

| Distribution | Interpreter | Standalone suite |
| --- | --- | --- |
| Same wheel | Python 3.11.17 | 91 passed |
| Same wheel | Python 3.12.15 | 91 passed |
| Same wheel | Python 3.13.16 | 91 passed |
| Same wheel | Python 3.14.4 | 91 passed |
| Source archive installation | Python 3.14.4 | 91 passed |
| Existing Define v1 | Existing selected Node/runtime cohort | 39 passed |
| Existing Define v2 | Existing selected Python/runtime cohort | 46 passed |

That is **176 distinct test methods**, with **540 final passing executions** across the installation matrix and legacy suites. Earlier candidate/intermediate runs are retained separately and are not added to that total.

The host was Linux x86_64 on WSL2. This is one Python distribution, not four interpreter-specific or OS-specific Define products. The byte API and bundled-resource access do not use the Linux file helper; CLI atomic publication still has a Linux implementation. Native Windows/macOS execution and a broader Linux distribution/filesystem matrix were not performed.

## End-to-end result

The retained run in `evidence/e2e/` includes:

1. Installed CLI integrity and capability discovery.
2. Self-contained incident inputs, exact capture and Pack preparation.
3. Frozen package inspection and reconstruction: **all nine files identical byte-for-byte**.
4. Python, JSON executable and CLI preparation producing the same package root.
5. Separate use observations: missing current evidence is not evaluable, matching bytes permit the narrow observation, and governing use remains blocked.
6. Explicit candidate Definition materialization, generated Markdown and complete field lineage.

The incident Pack retains one proposed meaning, one application and one synthetic reported FAIL. It records four observed rows against five expected rows, with account, snapshot and filters bound. That FAIL is authored evidence preserved by Define; the software workflow itself passes. Define executes no domain completeness assessment and grants no incident-closure permission. The suite additionally preserves supplied 4/5, 5/5 and 6/5 reports without claiming to compute their results.

An installed child process also completes byte capture, preparation and reconstruction under Python audit rules denying Lab repository reads. This is evidence about that execution path, not an operating-system sandbox claim. The optional Lab snapshot adapter was exercised with synthetic source roots and remains historical reported evidence only.

## Problems found and fixed

Seven regressions were reproduced against the previous rc1 installation:

| Finding | Correction |
| --- | --- |
| JSON executable classified source drift as invalid input/exit 2 | Consistent blocked runtime result and exit 3 |
| Task objects resembling file bindings became unintended source references | Task values and schema literals excluded from reference traversal |
| A selected file could collide with generated catalog/control paths | Shared collection path checks include generated controls |
| Supplied captured bytes could be ignored | Complete supplied-member closure enforced |
| Captured row selectors were accepted but ignored | Whole-file row selection required; meanings retain explicit selectors |
| PASS/FAIL could carry a contradictory not-evaluable reason | Conflicting assessment fields rejected |
| A materialization selection could name a wrong embedded digest until later | Preparation verifies selected meaning and parent references |

Additional qualification work made the post-rename sync failure explicit as `outcome-unknown`, preserved rc1 empty-capture controls, confirmed empty-source API/CLI parity, moved installed-resource reads off the Linux helper and included the suite in the source archive.

The rc2 reader successfully inspects the exact rc1 demonstration package. Frozen v1/v2 implementation selections were not modified. `artifact-review.json` verifies **552 v1 files, 29 v2 runtime files and the prior 74-file v2 review envelope** remained unchanged.

## Exact artifacts

- Wheel: `dist/cyberalchemy_define-0.3.0rc2-py3-none-any.whl`  
  SHA-256: `ca9f6a8bc94e56f23b3eb9a4bf53d240180dd2600e8d08c82cb635ff5559cb9c`
- Source archive: `dist/cyberalchemy_define-0.3.0rc2.tar.gz`  
  SHA-256: `ce8347f98c27ace45425c9d44d02d35691a9aad2e83641c746ab4346eaa268ba`

Both contain all 27 selected runtime members matching the source/resource seal. The source archive also includes the complete suite and synthetic fixtures. Exact environment versions, installation logs, test logs, hashes and timing are in `QUALIFICATION.json` and `evidence/`.

## What remains before a public stable release

1. **Approve the distribution's license.** The package currently declares no project license. The adapted/vendored project material needs an approved distribution license; third-party dependency metadata reports its own licenses. No license was invented or applied during qualification.
2. **Cut the selected stable version from these reviewed changes.** `0.3.0` is the natural successor to this rc2. Apply the version-only promotion, build its exact archives and repeat artifact qualification so the final published filenames/digests are the qualified ones.
3. **Publish/tag the approved bytes at the chosen destination.** This task performed no push, public upload, deployment or default-runtime adoption.

There are **no remaining failing tests in the qualified standalone scope**. New platforms and broader deployment guarantees require their own execution evidence. Native Lab v3 mapping, owner review/admission, authenticated standing, hosted HTTP/MCP services and domain assessment execution remain separate integration capabilities; they are not prerequisites for the declared standalone preparation release.

## How to inspect the installed result

Active installed environment:

`/home/vlad_/.local/share/define-qualification/20261015-MbsEfG/final-py314/`

```bash
/home/vlad_/.local/share/define-qualification/20261015-MbsEfG/final-py314/bin/define-standalone doctor
/home/vlad_/.local/share/define-qualification/20261015-MbsEfG/final-py314/bin/define-standalone inspect /home/vlad_/.local/share/define-qualification/20261015-MbsEfG/e2e-final/package
```

The `doctor` command establishes local source consistency only. Its `qualification: not-established` field means that the command itself does not run the qualification suite or import an external release verdict; compare its inventory hash with this report for the tested selection.

The qualification does not admit any canonical meaning, establish a native owner outcome, authenticate a current external source or select the repository's runtime. Package integrity is drift detection under the documented trusted bootstrap/dependency environment.
