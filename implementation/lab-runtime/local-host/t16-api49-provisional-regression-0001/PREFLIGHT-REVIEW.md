# T16 API49 provisional regression preflight

The selected API49 T31 candidate has exactly 345 declared test methods in 21 whole-class buckets. The historical API-v96 baseline has 323 methods; the 22 added methods are all retained. Twenty inherited method ASTs differ and require final-cut review. This is a closed inventory, not a T15 freeze or full T16 qualification.

Selected API49 source manifest: `e283b71d9947be8f1dde8ce714664eefd3743fc2f872add5b586fb9bcf86cae1`. Selected contract profile: `dc0106126515b58907fa299987c52e9b4afb79ca4c482fb9428f3d12a453cbb5`. The inventory is `INVENTORY-0001.json` SHA `bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3`; the class source-route classification is `CLASSIFICATION-0001.json` SHA `5434fb592bf665b50c1c799ccf86bd78cd870ac0c2c1321303ff38b784159d2b`.

The inherited class setup routes divide into 113 methods in six current-T31-source buckets, 48 in two `reference-corrected` buckets, and 184 in thirteen historical `custody-participation` buckets. These are static route counts, not pass counts. Individual methods may also call a different source route.

Fresh-process, byte-backed provisional executions:

| Bucket | Actual terminal observation | Receipt SHA-256 |
|---|---|---|
| `worker:14` TerminationBoundaries | 6/6 PASS, exact method set, entry/exit guards | `22c33b71cfe27589da73fc7c6a68eb35f8f00a9bc75c50e482bd870d09480059` |
| `worker:11` CurrentControls | 10 PASS, 1 FAIL; original expired-source assertion sees an earlier R02 environment refusal | `09b92ebb419b0e842da096044cdb6ae9191f5618d67fcfdb2757ec0a4041d7d4` |
| `worker:16` CorrectedPreparation | 3 PASS, 2 FAIL; protected historical Session requests now receive `stale-cut` | `9a11ba986512c07f4dabcc5e5cc607ca3f9e3182b082719ebc62514a6aaa6a5f` |
| `worker:17` CarrierReferenceChecks | 0 methods; setUpClass refuses `independent source environment differs` | `f10ce38e56838e96d626e473a6b9cf10df291a4db268e1e878d0f7ab594475a5` |
| `worker:8` OriginalAPI | Interrupted at parent request to protect concurrent native runs; five completed rows retained: 3 PASS, 1 FAIL, 1 ERROR. No 14-case claim. | `1916371bb20c111124750d97a1a50dd3f5149f18c54b74abcb3787fed1a30364` |

The historical Source5 manifest requires Python 3.14.4, cryptography 46.0.5, and jsonschema 4.23.0. The selected API49 host uses jsonschema 4.19.2. Source5's signed period also expired on 13 October. A fresh process cannot truthfully run the historical `custody-participation` class setup as a current same-cut positive. The `worker:17` refusal proves this path; the other twelve historical buckets have not been run or counted. In `worker:8`, a current-source class's first method independently selected an old action-0148 reader and refused at its environment check. Its third method expected 23 source subjects but observed 27 in the new current family.

For the final T15/T16 cut, select a new signed current fixture family and versioned exact test selectors for the 184 historical-route methods. Preserve explicit old-source expiry and wrong-origin refusals as separate negatives. Reconcile `reference-corrected` cut semantics, the old R02 environment-versus-expiry expectation, and current-source subject-count assumptions without weakening guards. Independently review all 20 changed inherited method ASTs and any further successor changes. Then freeze source/profile/runner/method plan, serialize source-corrupting classes, run each whole class in a fresh process within its actual lease, and aggregate only after all 345 exact IDs have terminal PASS with entry/exit guards. No provisional result here transfers to that later cut.

The provisional worker captures API49 Python module bytes from its source manifest before import and runs the source/profile guards at entry and exit. It does not qualify historical external module code against import-window substitution; a final worker needs closed byte-backed execution or an equivalent origin proof for those selected dependencies. The interrupted bucket has completed per-case events but no whole-class verdict. No authority effect occurred.
