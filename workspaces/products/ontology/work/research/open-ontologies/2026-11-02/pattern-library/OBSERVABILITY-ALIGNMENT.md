# Runtime signals and evidence

The repository's strongest signals are structured result files: selected scope,
input/rule digests, result status, checker output, limits and named omissions.
They make answers inspectable after the run.

| Area | Signals observed | Limit |
| --- | --- | --- |
| Startup and transports | Configurable tracing levels, text/JSON logs, stderr/stdout/file routing and tool-surface counts. | Not evidence of a complete metrics or distributed-tracing platform. |
| Reasoning and checkers | Derivations, model/refutation files, checker outcomes and input bindings. | Strong verdicts still depend on checker identity and source selection. |
| Partial validation | Unknown/null results, unsupported counts and skipped features. | A consumer must keep these visible instead of displaying an empty success list. |
| Change review | Structural diff, blast-radius/risk reasons, logical checks and consequence reports. | Reports do not all block apply. |
| Monitor and lineage | SQLite watcher state, operation logs and asynchronous webhooks. | Some insertion/notification errors are ignored; not a canonical transactional audit. |
| Live/replay UI | Explicit source adapter and unavailable/undetermined errors. | Several live methods are unimplemented. |

Sources: [CLI, HTTP, and daemon entrypoints](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/main.rs#L1), [evidence-carrying verdicts](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/verdict.rs#L1), [plan application](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan.rs#L571), [Studio live-source limits](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/studio/src/lib/live-source.ts#L1), and
[operation lineage](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/lineage.rs#L1).

For a Lab experiment, retain the exact cut and review references, mapping and
rules versions, selected goals, output bytes, omissions, checker identity and
acceptance result. Keep produced evidence distinct from an owner decision and
from any later write receipt. This is our proposed observability contract,
not a claim that upstream already implements it for Lab records.
