# Dependencies and boundaries

## Observed directions

| Caller | Dependencies or target |
| --- | --- |
| CLI, batch and MCP wrappers | Shared Rust domain functions and input/output records. |
| Domain services | Graph store, SQLite metadata, files and optional external providers. |
| Reasoning/checking paths | Selected graph data, rule table, emitted evidence and separately built checker processes. |
| Studio | Tauri engine/agent sidecars, MCP and sessionless REST. |
| Python Lite | pyoxigraph and pure Python code, optional MCP/pyshacl/HNSW. |
| WASM plugins | Explicit JSON request, no implicit graph access or host imports. |

Sources: [Rust dependencies and features](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/Cargo.toml#L1), [MCP services over shared graph and state](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/server.rs#L1), [Python package boundary](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/python/pyproject.toml#L1), [bounded WASM extension host](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plugins.rs#L1).

The [lexical edge inventory](inventory/dependency-edges.json) records local Rust
module references. It includes conditional/test code and is not a resolved
call graph. There are no compiler-enforced rules forbidding every upward or
cross-area reference in our navigation grouping.

## Build choices

Default optional features are empty. PostgreSQL/DuckDB add database adapters;
embeddings add local ONNX/tokenizer/vector dependencies; TurboVec implies
embeddings; plugins add the WASM interpreter. Causal-Python invokes external
Python packages rather than adding a Rust dependency for them.

The core includes 36 declared direct dependency entries, including optional
ones. Oxigraph is patched to exact revision
`37db8e1522585ed2f9aa994be6c5c716859af5c8`. The fork supplies the snapshot API
and literal/query fixes this code depends on. Stock Oxigraph 0.5 is not an
interchangeable version. Source: [pinned Oxigraph fork](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/Cargo.toml#L160).

Lean checkers are separately built. Isabelle-generated ML, Rocq extraction,
Aeneas, Dafny, Kani, Z3/Mace4/provers and local model assets have different
toolchain and runtime obligations. A cargo build does not imply they exist.

## Recommended Lab boundary

Keep the source cut, representation mapping and logical profile explicit.
Analytical dependencies should receive a disposable export and return inert
evidence. The Lab should check source/version bindings and retain authority
over writes. Review each enabled operation's file/network/process effects;
an analytical name or narrow tool-discovery profile is not an approval system.
