# First contract-checked source import

Sibling source records -> approved contract lookup -> isolated candidate store -> missing-data review.

Four exact records from `../cyberAlchemy-v2/people-and-teams/nodes.json` were selected in [plan.json](plan.json). One Product passed and was imported into `.local/contract-checked-sample-0002/import.json`. Three records were blocked. Review [the rendered results](REVIEW.html) or [the exact source/result records](results.json).

The importer uses the migration admission registry to verify exact contracts, scope, dependencies and implementation bytes before loading the validation engine. It preserves each selected source record and its file hash and JSON selector. Successful normalization creates a candidate record, not an admitted business instance.

The Product mapping uses the source label as name, plain-language description as purpose, explicit exclusions as its source-stated identity boundary, and owner route as a declared owner reference. The source-qualified ID and migration scope are adapter metadata. This boundary mapping makes no claim of global identity equivalence or authenticated ownership.

The Thesis and Capability lack complete instance fields and have candidate Definition dependencies. The Team entry describes the general Team concept; it does not identify an actual team. They are retained in the report with their missing fields and dependency bindings, without invented values or placeholder instances.

The new bounded JSON importer is separate from the earlier v4 raw event importer. It consumes real sibling data through the admitted contracts; the earlier event store is unchanged. Only one complete Product mapping is implemented. This run covers no relations or profile execution.

To repeat with a new isolated destination:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tooling/importers/migration_contract_import.py evidence/migrations/cyberalchemy-v2-to-lab/executions/0002-contract-checked-sample/plan.json .local/contract-checked-sample-repeat
```

Existing destinations are refused. Six integration tests passed: real-record outcomes, deterministic import and overwrite protection, source drift, scope and unknown target rejection, identity mismatch and duplicate selection, and missing Product data. [verification.json](verification.json) binds the implementation, plan, results and store. The registry and reviewed batch integrity checks still pass.

## Open questions and next step

Which source records supply the missing Thesis and Capability fields and their exact Product references? Resolve these using source evidence, retain unresolved fields as blockers, and handle the candidate Definition dependencies before adding those mappings. A general Team concept must remain a concept until an actual team record is supplied by the source. Expanding this importer and connecting the raw event runtime remain subsequent integration work.
