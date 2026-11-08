# Docker Source8 chain preparation 0002 — independent review handoff

Status: **PROPOSED_SELECTION_ONLY; effect NOT_RUN; pending independent review**. This is a disjoint correction of `docker-chain-preparation-0001`. The 0001 files and its independent HOLD review are preserved. No generated role, native executable, Docker container, Source/Reader/Mapper/Context effect, signer, store, grant, cgroup, or host setup was run or created.

The 0001 reviewer reproduced DCP-R01: each of four caller-labelled T35 code bindings could be substituted with a different real file and its correct hash while the actual imported constructor and all 27 projections remained unchanged. In 0002, `checked_t35_selection` requires each of `constructor`, `phase_rebind`, `hardener`, and `path_contract` to equal its own independently pinned repository path and digest before any proposal is constructed. `checked_imported_closure` then checks the four imported module paths and bytes after projection, including the lazily imported hardener. Thus caller-selected provenance is joined to the selected T35 code. Both checks use ordinary quiescent-process files, not an immutable held-byte loader; concurrent mutation or a future effectful import still needs a stronger custody boundary.

`selection.json` has schema `lab-docker-chain-proposed-selection/v2-effect-disabled`. All 27 original preimages, all 27 projected bytes/hashes, the reverse patches, external Source bindings, episode proposal, feasibility refusal and claimed ceiling are unchanged from 0001. The 27 role rows and `selected_inputs` in both proposed outputs compare exactly equal. The new code rejects each reviewed coherent substitution: path-contract file as constructor, phase rewriter or hardener, and Compose file as path contract. The older zero-hash negatives and all other refusal cases remain. Normal and optimized suites each pass **15 test methods**, including all four causal subcases.

The proposed identity `completion-legacy-docker-chain-20261020-0001`, fixed 24-hour UTC period, and distinct scope are preparation values only. `authorization_state=NOT_GRANTED`; the old authorization is only a historical Source preimage. Mapper/Context phase rebinding remains deferred until signed predecessors exist. The proposed pin order is Source source → Source package → Reader adapter source → Mapper source → Mapper package → Context source → Context package; Reader has no package and future package hashes are null.

The feasibility manifest remains a mandatory refusal: current image Python 3.12 versus Source exact 3.14.4, read-only `/workspace` versus Source writes, unresolved `HERE.parents[5]` and sibling layout, original Mapper host `/tmp` native path absent in container, unproved container native ABI loading, absent selected Bubblewrap/direct-native route, unproved FD and scratch budgets, unproved original Context writer shape, and no fresh Source authorization/engine selection. The 27 roles plus five Source dependencies are not the complete executable transitive closure. A public-only Source closure is downstream work, not proof of a runnable chain or Source effect readiness.

Reproduce without effects:

- `python3 -B implementation/lab-runtime/local-host/docker-chain-preparation-0002/prepare.py` produces the frozen proposed JSON on stdout.
- `python3 -B implementation/lab-runtime/local-host/docker-chain-preparation-0002/test_prepare.py` passes 15 methods.
- `python3 -B -O implementation/lab-runtime/local-host/docker-chain-preparation-0002/test_prepare.py` passes 15 methods.

The tests only invoke pure proposal construction and inspect pinned native bytes. Generated role bytes are never written or imported. Source package creation, private source inspection, Docker execution, original-plan task acceptance, and protected host qualification are outside this unit.

| File | SHA-256 |
| --- | --- |
| `prepare.py` | `d8f744bd5afe4cfe3f3b3979f49f4d07078f09dbadae89a7e9bc6d20013d0ba1` |
| `selection.json` | `0959f9193b4caaa1ecae6f565e9d1274565ba580a7bbbd7a759deececeb1343f` |
| `proposed-selection.json` | `49d9e1872aa2fde7cc4ee22dd7128fd85d3eab81cadebdf1163957acc6a7795d` |
| `test_prepare.py` | `26477be10d611edfc33a2addaf69d414995769e9a9d8ecf3609a864ce7c48b17` |
| `test-normal.log` | `42c53cc171dada20a553c042fe8fc0e9d84d68c2938a26f7cdb1c58eaa9f1433` |
| `test-optimized.log` | `7490675eb5c2c9a6fb786ebf74c3c04eae5a03f5f3956d80e9bb9c8562a08b6d` |
