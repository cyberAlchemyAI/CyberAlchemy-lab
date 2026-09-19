# Shared Capability ontology runtime import

Product outcome -> agent capability or system realization -> contracts and obligations -> evidence.

Imported 25 graph concepts, nineteen typed relationships and 47 supporting documents into an isolated instance of the existing v4 runtime. The 91 source subjects become semantic/governance event pairs. The same exact executable built and tested in 0074 is reused; no runtime code was added or changed.

The ontology distinguishes Product Capability, Agent Capability, realization and source-owned reference. Its canonical/private authority claims remain source data: this migration does not promote them to Lab-wide authority, adopt capability instances, transfer ownership or establish behavioral conformance.

All 43 selected values across 24 dependency sources match exactly. Seven Define-owned records retain exact raw hashes. Three Arcanum files were recovered from the existing 0064 Git archive. Five containing-file fingerprints differ from historical observations while all selected content matches. These warnings and the missing current in-package PASS receipt warning remain visible. The captured current validation output passes; historical receipts are unchanged.

The source negative suite reports 16/17 passing expectations. Its one-sided bridge mutation correctly returns BLOCK but the expected message is obsolete. `check_negative_tests.py` changes only that expected diagnostic in memory, from public-private business/system wording to the validator's current meaning/realization wording. All seventeen original mutations then pass. The original failure, corrected result and unchanged source files are preserved.

Runtime verification checks exact graph records and full supporting-document bytes, independent fresh-store equality, separate-process replay, endpoint closure, overwrite refusal, unknown-package refusal and corruption rejection. Eleven import checks and four runtime rejection cases pass. Source validation is rerun ignoring only its generated validation timestamp.

Store: `.local/shared-capability-runtime-0075/`. Supporting documents are inert source material, including historical public/private definitions and source capability records. No server, enforcement hook or external service is activated.

Inspect:

```sh
.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime summary .local/shared-capability-runtime-0075
.local/people-teams-runtime-package-0074/runtime/target/debug/cal-ontology-source-runtime export .local/shared-capability-runtime-0075
```

The source archive, exact manifest, committed runtime archive and full export are recorded here. Reproduce from the Lab root with `PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0075-shared-capability-runtime-import/verify.py`.

## Open Questions

- Thirteen source residue records and all original obligation/conformance postures remain unchanged.
- Historical source versions are selected evidence, not current global authority.
- A combined runtime manifest, currentness catalog and native-verdict/request integration remain separate work.
- Next: Workspace capability ontology registration — determine how workspace context refers to capabilities, then import its supported scope through the existing runtime.
