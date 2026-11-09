# Complete Product ownership and workspace runtime migration

Ownership and runtime-model migration are implemented. All 19 migration verification groups pass. Broader product qualification remains partial for the explicit pre-existing TDE failures and the unavailable shared compiler described below.

All six nested Product homes use product/, project/, work/, authority/, ontology/, architecture/, implementation/ and docs/. The Lab uses the same areas at the repository root. Forty-five additional inode-preserving moves consolidate Define CLI ownership, Craft predecessor source and research, Ontology bindings and six plans, website work, and external reference evidence. Compatibility names are symlinks, not duplicate Product homes.

Shared Lab operations remain under root implementation/lab-*/. Define integration lives under implementation/lab-integration/define/; product-owned CLI source lives under workspaces/products/define/implementation/cli/. Ontology owns both packages and its runtime bindings. Existing Node and Python dependency installations are referenced; no runtime installation is copied or provisioned.

The current shared runtime entrypoint is implementation/lab-runtime/lab.py. Its workspace commands select lab-workspace-model/v2 through implementation/lab-workspaces/CURRENT.json. Seven local Product profiles select one shared target. Product contexts can omit a Project; Project-owned operations require the selected Project, and Goal/Work ownership is checked. Project-only v1 conversion is explicit. A Project scope need not create a Product. No additional Project workspace is provisioned for Craft or Ontology coordination.

Native store dispatch requires an explicit catalog binding and valid sealed native replay. Workspace/Project/scope mismatches refuse before native execution; existing native review, signing and application checks remain in force. Source-only reads cannot accidentally use the default private store.

The successor cal.definition.lab-workspace@2.0.0-candidate.1 was captured, prepared, inspected, materialized and reconstructed by the real Define CLI. Its 103 field leaves have exact lineage. The old candidate and frozen Packs remain exact. The successor is selected as the executable configuration contract; this is not native semantic admission or an authority grant.

## Verification

| Surface | Current result |
| --- | --- |
| Workspace model, dispatch, version and exact-binding checks | 42 tests pass |
| Existing native runtime and checkpoint checks | 39 + 6 tests pass; source digests unchanged |
| Define source API / native workflow | 66 + 7 tests pass |
| Craft source build and relocation/Ontology integration | Build passed; 10 tests pass |
| Ontology Product / Lifecycle / relocated binding | 8 + 23 + 5 tests pass |
| Body War no-effect checks | 33 Node + 16 Python tests and validators pass |
| Website | Isolated render selects 1,241 resources |
| Ownership, catalog and retained dependency inputs | Pass; 45 moves, 110 source pins, 3,050 observed inputs |

### Qualification boundaries

The full legacy TDE suite has 381 passing, 77 failing and 17 pending tests. The 77 failed test names are exactly the same as the pre-migration tracked qualification report; no tests were removed or skipped to manufacture a pass, and no retired proof inputs were restored.

The shared C toolchain lost its payload outside this checkout during verification: inspection found zero regular files and 171 links, with no installation receipt. The supported installer could not restore it because libc-dev-bin 2.43-2ubuntu2.3, libc6-dev 2.43-2ubuntu2.3 and linux-libc-dev 7.0.0-31.31 are no longer available from the configured apt indexes. Its original link-only skeleton was restored. Existing successful Rust builds/tests are recorded; a new complete locked-toolchain rebuild remains blocked. No upstream source or lock file was changed and no alternate toolchain was silently substituted.

Current and previous attempts are consolidated in CHECKS.json and ATTEMPTS.json. Both native runtime snapshot digests remain unchanged. The source-only and full native tests, Define workflow tests, workspace contract tests, ownership checks, canonical Git paths, current builds and product-specific checks are verified separately. Existing legacy proof-suite failures are retained without restoring obsolete historical data or redirecting test writes into external checkouts.

## Repeatable checks

    python3 tooling/verify_workspace_migration.py
    python3 implementation/lab-runtime/lab.py workspace verify
    python3 -m unittest discover -s implementation/lab-workspaces/v2 -v
    python3 tooling/verify_product_workflows.py define-api
    website/.venv/bin/python tooling/verify_product_workflows.py website-render

See verification-commands.json for component commands. Native runtime tests use disposable local stores, not production operator state. No native admission, runtime deployment or external source mutation is performed by this migration.

## Definitions Governance Summary

- Definitions updated: cal.definition.lab-workspace@2.0.0-candidate.1, explicit successor through Define.
- Index synced: ontology/lab-workspace/INDEX.json and the current runtime selector.
- Drift found: the old Project-only contract is retained as a versioned predecessor; current consumers select v2.
- Undefined critical terms: none introduced outside the typed operational contract.
- Conflicting consumers: legacy profiles remain explicitly v1; no implicit conversion.
- Validation: recorded by stage in CHECKS.json.
- Follow-ups: native semantic admission remains distinct from this implementation and is not inferred.
