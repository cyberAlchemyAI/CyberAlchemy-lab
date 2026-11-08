# Every main Rust source module

All 107 files under `src/`, grouped by responsibility. Line counts include
comments and blank lines. References are extracted from `crate::...` and
`use crate::{...}` text, including conditional and test code. They are a
navigation aid, not proof of enforced architectural boundaries.

Each module link points to the reviewed commit. Public symbols and line numbers
are available in [the module inventory](pattern-library/inventory/module-inventory.json).

## Requests and responses

CLI/batch, MCP, HTTP, daemon/socket dispatch, tool filtering and output.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [batch](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/batch.rs#L1) | 1904 | `closure_diff`, `conservativity`, `crosswalk`, `defects`, `drift`, `enforce`, `exceptions`, `fol_solve`, `graph`, `induce`, `ingest`, `mapping`, `marketplace`, `matcert`, `modules`, `monitor`, `ofn_writer`, `ontology`, `output`, `pack`, `plan`, `projection_entailment`, `reason`, `repair`, `rulesyntax`, `runtime`, `shacl`, `shacl_verified`, `state`, `temporal`, `tptp`, `trace_label`, `tstp`, `vocab_check` |
| [daemon](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/daemon.rs#L1) | 287 | `config` |
| [lib](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/lib.rs#L1) | 170 | — |
| [main](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/main.rs#L1) | 4648 | — |
| [mcp_handshake](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/mcp_handshake.rs#L1) | 134 | — |
| [output](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/output.rs#L1) | 1539 | `exceptions`, `repair` |
| [server](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/server.rs#L1) | 3624 | `align`, `align_fuzzy`, `borderline_loop`, `civex`, `classify_el`, `clinical`, `closure_diff`, `coevolve`, `communities`, `config`, `conservativity`, `cq`, `defects`, `dlp`, `drift`, `dynamics`, `dynamics_bcplus`, `embed`, `enforce`, `eval_alignment`, `eval_rag`, `exceptions`, `extract_scaffold`, `feedback`, `flora_pipeline`, `fol_solve`, `graph`, `hnsw_index`, `induce`, `ingest`, `inputs`, `justify`, `lineage`, `mapping`, `marketplace`, `module_extract`, `monitor`, `ofn_writer`, `ontology`, `ossie`, `pack`, `plan`, `plan_classical`, `plan_pddl`, `plan_validate`, `plugins`, `poincare`, `policy`, `projection_check`, `projection_entailment`, `provenance`, `reason`, `reason_incremental`, `registry`, `repair`, `repo`, `rulesyntax`, `runtime`, `schema`, `segment_retrieve`, `shacl`, `shacl_report`, `shacl_verified`, `shape_combinatorics`, `sql_sync`, `sqlsource`, `state`, `structembed`, `support`, `tableaux`, `temporal`, `toolfilter`, `tptp`, `trace_label`, `tstp`, `vecstore`, `vocab_check` |
| [socket](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/socket.rs#L1) | 400 | `graph`, `reason` |
| [socket_windows](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/socket_windows.rs#L1) | 10 | `graph` |
| [toolfilter](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/toolfilter.rs#L1) | 653 | — |

## Graph state and version reads

Oxigraph graph, SQLite metadata, saved versions, temporal scope, canonicalization and caches.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [cache](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/cache.rs#L1) | 586 | `runtime`, `state` |
| [canon](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/canon.rs#L1) | 491 | — |
| [graph](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/graph.rs#L1) | 1591 | `canon`, `ofn`, `reason` |
| [lineage](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/lineage.rs#L1) | 96 | `state`, `webhook` |
| [ontology](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/ontology.rs#L1) | 297 | `feedback`, `graph`, `state` |
| [registry](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/registry.rs#L1) | 533 | `cache`, `config`, `graph`, `state` |
| [state](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/state.rs#L1) | 451 | — |
| [temporal](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/temporal.rs#L1) | 3297 | `graph`, `reason` |

## Change review and operation

Structural plans, drift, policy/monitor checks, enforcement, feedback, notifications and KGCL edits.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [drift](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/drift.rs#L1) | 458 | `graph`, `kgcl`, `state` |
| [enforce](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/enforce.rs#L1) | 664 | `feedback`, `graph`, `state` |
| [feedback](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/feedback.rs#L1) | 268 | `runtime`, `state` |
| [kgcl](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/kgcl.rs#L1) | 380 | — |
| [monitor](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/monitor.rs#L1) | 298 | `graph`, `ontology`, `state`, `webhook` |
| [plan](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan.rs#L1) | 1000 | `conservativity`, `defects`, `drift`, `graph`, `lineage`, `monitor`, `state`, `tableaux` |
| [policy](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/policy.rs#L1) | 253 | `graph`, `state` |
| [webhook](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/webhook.rs#L1) | 27 | `runtime` |

## Reasoning over meaning

Forward rules, supplied-rule frontends, incremental inference, EL completion, tableaux and compiled claim checks.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [claimcheck](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/claimcheck.rs#L1) | 1053 | — |
| [classify_el](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/classify_el.rs#L1) | 921 | `graph`, `reason`, `tableaux` |
| [exceptions](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/exceptions.rs#L1) | 858 | `graph` |
| [reason](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/reason.rs#L1) | 4332 | `boundary_core`, `graph`, `justify`, `projection_entailment`, `provenance`, `runtime`, `tableaux`, `temporal`, `verdict` |
| [reason_incremental](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/reason_incremental.rs#L1) | 491 | `graph`, `temporal` |
| [rulesyntax](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/rulesyntax.rs#L1) | 1429 | `graph`, `reason`, `tableaux`, `verdict` |
| [tableaux](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/tableaux.rs#L1) | 6679 | `boundary_core`, `dl_refute`, `graph`, `runtime` |

## Evidence, explanations and external solvers

Typed verdicts, proof formats, model/refutation checking, explanations, provenance and repair.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [boundary_core](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/boundary_core.rs#L1) | 173 | — |
| [dl_refute](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/dl_refute.rs#L1) | 994 | `tableaux` |
| [fol_model](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/fol_model.rs#L1) | 1242 | `fol_solve`, `tptp` |
| [fol_solve](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/fol_solve.rs#L1) | 991 | `fol_model`, `graph`, `tptp`, `verdict` |
| [justify](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/justify.rs#L1) | 727 | `graph`, `projection_entailment`, `provenance`, `reason` |
| [matcert](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/matcert.rs#L1) | 231 | `verdict` |
| [provenance](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/provenance.rs#L1) | 977 | `graph`, `justify`, `projection_entailment`, `reason` |
| [repair](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/repair.rs#L1) | 2384 | `defects`, `graph`, `justify`, `output`, `reason`, `sat` |
| [sat](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/sat.rs#L1) | 182 | `verdict` |
| [tptp](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/tptp.rs#L1) | 4757 | `graph` |
| [tstp](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/tstp.rs#L1) | 2986 | `graph`, `tptp`, `verdict` |
| [verdict](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/verdict.rs#L1) | 774 | — |

## Data and rule checks

SHACL, result reports, vocabulary defects, competency questions and combinatorial shape analysis.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [cq](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/cq.rs#L1) | 289 | `graph`, `state` |
| [defects](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/defects.rs#L1) | 404 | `exceptions`, `graph` |
| [shacl](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/shacl.rs#L1) | 4011 | `graph`, `shacl_report`, `temporal` |
| [shacl_report](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/shacl_report.rs#L1) | 231 | `shacl` |
| [shacl_verified](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/shacl_verified.rs#L1) | 257 | `graph`, `shacl`, `verdict` |
| [shape_combinatorics](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/shape_combinatorics.rs#L1) | 571 | `graph` |
| [vocab_check](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/vocab_check.rs#L1) | 249 | `graph` |

## Smaller views and change consequences

Graph selection, modules, lost/support-preserved claims, closure differences and conservativity under selected rules.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [closure_diff](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/closure_diff.rs#L1) | 1005 | `graph`, `projection_entailment`, `reason`, `runtime`, `verdict` |
| [conservativity](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/conservativity.rs#L1) | 502 | `closure_diff`, `graph`, `projection_entailment` |
| [module_extract](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/module_extract.rs#L1) | 1558 | `closure_diff`, `graph`, `projection_entailment`, `segment_retrieve` |
| [modules](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/modules.rs#L1) | 138 | `graph`, `reason` |
| [projection_check](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/projection_check.rs#L1) | 330 | `closure_diff`, `graph`, `projection_entailment` |
| [projection_entailment](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/projection_entailment.rs#L1) | 1980 | `graph`, `projection_check`, `reason`, `runtime`, `verdict` |
| [segment_retrieve](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/segment_retrieve.rs#L1) | 291 | `graph` |

## Getting records into a graph

File/SQL intake, field mapping, conceptual-model conversion, schema suggestions and packs.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [extract_scaffold](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/extract_scaffold.rs#L1) | 517 | `graph`, `language` |
| [flora_pipeline](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/flora_pipeline.rs#L1) | 407 | `align_fuzzy`, `eval_alignment`, `graph` |
| [induce](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/induce.rs#L1) | 802 | `graph`, `mapping` |
| [ingest](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/ingest.rs#L1) | 551 | — |
| [inputs](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/inputs.rs#L1) | 1747 | — |
| [mapping](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/mapping.rs#L1) | 202 | `induce` |
| [ofn](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/ofn.rs#L1) | 1783 | `ofn_writer` |
| [ofn_writer](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/ofn_writer.rs#L1) | 1758 | `canon`, `graph`, `ofn` |
| [ossie](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/ossie.rs#L1) | 1291 | `graph` |
| [pack](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/pack.rs#L1) | 1127 | `graph`, `projection_entailment`, `reason`, `verdict` |
| [schema](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/schema.rs#L1) | 324 | — |
| [sql_sync](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/sql_sync.rs#L1) | 320 | `state` |
| [sqlsource](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/sqlsource.rs#L1) | 337 | `ingest`, `mapping`, `schema` |

## Comparing vocabularies and domain models

Alignment signals, crosswalks, clinical inputs, language and communities.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [align](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/align.rs#L1) | 1823 | `drift`, `graph`, `language`, `poincare`, `runtime`, `state`, `vecstore` |
| [align_fuzzy](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/align_fuzzy.rs#L1) | 367 | — |
| [borderline_loop](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/borderline_loop.rs#L1) | 227 | `state` |
| [clinical](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/clinical.rs#L1) | 215 | `drift`, `graph` |
| [communities](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/communities.rs#L1) | 352 | `graph` |
| [crosswalk](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/crosswalk.rs#L1) | 664 | `graph`, `reason` |
| [eval_alignment](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/eval_alignment.rs#L1) | 142 | — |
| [language](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/language.rs#L1) | 203 | — |

## Similarity and retrieval

Optional vectors, local/remote embeddings, model fingerprints, indexes and retrieval measurements.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [embed](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/embed.rs#L1) | 467 | `cache`, `config`, `embed_fingerprint`, `embed_remote`, `poincare` |
| [embed_fingerprint](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/embed_fingerprint.rs#L1) | 410 | `cache`, `config`, `embed` |
| [embed_remote](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/embed_remote.rs#L1) | 166 | `poincare` |
| [eval_rag](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/eval_rag.rs#L1) | 579 | — |
| [hnsw_index](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/hnsw_index.rs#L1) | 311 | `poincare`, `vecstore` |
| [poincare](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/poincare.rs#L1) | 132 | — |
| [structembed](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/structembed.rs#L1) | 190 | `graph`, `poincare` |
| [turbo_index](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/turbo_index.rs#L1) | 308 | `hnsw_index` |
| [vecstore](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/vecstore.rs#L1) | 983 | `embed_fingerprint`, `hnsw_index`, `poincare`, `state`, `turbo_index` |

## Action and causal experiments

Action effects, PDDL/BC+ integration, defaults, coevolution and structural/optional causal analysis.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [civex](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/civex.rs#L1) | 687 | `civex_pywhy`, `graph`, `lineage`, `plan`, `state` |
| [civex_pywhy](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/civex_pywhy.rs#L1) | 337 | — |
| [coevolve](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/coevolve.rs#L1) | 398 | `graph`, `reason`, `shacl` |
| [dlp](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/dlp.rs#L1) | 1545 | `graph`, `reason`, `tableaux`, `trace_label` |
| [dynamics](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/dynamics.rs#L1) | 837 | `graph`, `lineage`, `reason`, `state` |
| [dynamics_bcplus](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/dynamics_bcplus.rs#L1) | 683 | `dynamics`, `graph`, `state` |
| [plan_classical](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan_classical.rs#L1) | 305 | — |
| [plan_pddl](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan_pddl.rs#L1) | 349 | `dynamics` |
| [plan_validate](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan_validate.rs#L1) | 401 | `dynamics`, `graph`, `plan_pddl`, `state` |

## Settings and extensions

Effective configuration, caches/buffers, registries, connection fallback, plugins and supporting reports.

| Module | Lines | Lexical module references |
| --- | ---: | --- |
| [buffer](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/buffer.rs#L1) | 550 | `state` |
| [config](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/config.rs#L1) | 963 | `toolfilter` |
| [connect](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/connect.rs#L1) | 96 | `daemon`, `output` |
| [marketplace](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/marketplace.rs#L1) | 738 | `graph` |
| [plugins](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plugins.rs#L1) | 215 | `config` |
| [repo](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/repo.rs#L1) | 286 | `config` |
| [runtime](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/runtime.rs#L1) | 298 | `config` |
| [support](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/support.rs#L1) | 323 | `graph`, `state` |
| [trace_label](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/trace_label.rs#L1) | 1365 | `boundary_core`, `dlp`, `graph`, `projection_entailment`, `reason`, `verdict` |
