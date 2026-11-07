# Define, standalone

Define organizes an authored request, exact source meanings, task values, reported assessments and open questions into a reconstructable Definition Pack. It can run without CyberAlchemy Lab, a Lab checkout, a provisioned host or a model service.

This is the `0.3.0rc2` implementation candidate. It introduces request/Pack v3 and capture v2. Existing Lab v1/v2 entrypoints and their contracts remain unchanged. The release-candidate qualification covers isolated installation, the complete standalone suite and API/CLI workflows on Linux with Python 3.11–3.14. See the release evidence for exact artifact hashes and outcomes. This candidate has not been published or designated stable.

## Install and interfaces

Python 3.11+ is required. Local CLI output publication currently requires Linux and `renameat2`. The stateless API uses memory and portable installed-resource reads; it does not publish local directories. There is one Python distribution for all consumers. The CLI file adapter currently has Linux-qualified publication semantics; native Windows/macOS file workflows have not been qualified.

```bash
python3 -m pip install /path/to/cyberalchemy-define-distribution
```

The distribution directory contains `pyproject.toml`, this README and the complete `define_core` package. Installation resolves the declared `jsonschema` dependency. A built wheel can be installed instead. No files outside the distribution are required at runtime.

Two installed commands expose the same implementation:

- `define-standalone`: trusted local file workflow and explicit Lab snapshot translation.
- `define-api`: one versioned JSON request on stdin, one response on stdout. No daemon is started.

The repository wrapper `./define/define-standalone` runs the same candidate from source. The wrapper locates the source distribution; installed commands have no repository lookup.

## A first Definition Pack

The bundled example investigates missing rows in an export. It reuses an exact local investigation boundary, proposes a definition of completeness, binds source snapshot/account/filters/expected IDs and retains an explicitly synthetic FAIL report for four observed rows against five expected rows. Define checks bindings and structure; it does not execute the completeness comparison or conclude a real incident.

```bash
DEFINE_DEMO=$(mktemp -d)
define-standalone example --output "$DEFINE_DEMO/input"
define-standalone capture-local \
  --request "$DEFINE_DEMO/input/request.json" \
  --source-root "$DEFINE_DEMO/input" \
  --permit-retention --output "$DEFINE_DEMO/capture"
define-standalone prepare \
  --request "$DEFINE_DEMO/input/request.json" \
  --capture "$DEFINE_DEMO/capture" --output "$DEFINE_DEMO/package"
define-standalone inspect "$DEFINE_DEMO/package"
define-standalone reconstruct "$DEFINE_DEMO/package" --output "$DEFINE_DEMO/restored"
```

The release qualification runs this workflow outside the Lab checkout. Its exact transcripts and reconstructed bytes are retained with the release evidence. Every output destination must be new, with an existing parent. Existing files/directories are never overwritten. `--capture` takes a capture **directory**, containing `capture.json` and `inputs/`. `--permit-retention` asserts local retention rights for the selected sources; it confers no admission or operator authority. Without it, source retention remains an explicit unresolved gap. A capture marked forbidden is refused by preparation.

### What is inside

```text
package/
  manifest.json     exact members, roots, digests and closure
  request.json      original request bytes
  capture.json      exact source selection and limitations
  pack.json         candidate meanings, applications, gaps and reported assessments
  report.json       structural checks and readiness for named uses
  inputs/           original selected source and catalog bytes
```

Task-specific values and assessments remain in this Pack. An account ID, filter or incident report does not become a new shared definition. A complete shared Definition is materialized only through explicit `materialization_selection` and the separate `materialize` operation.

## Public API

```text
Agent / application / workflow
                │ request + supplied bytes
                ▼
          Define public API
                │ deterministic preparation
                ▼
        candidate Pack + exact package
                │ caller stores or submits
                ▼
        independent consuming system
```

The interface is transport-independent data. An application can call Python directly, launch `define-api` as a child process, or wrap the API in its own HTTP/MCP service. This package does not implement an HTTP server, authentication service, automatic tool discovery or model reasoning. Future wrappers own identity, isolation, storage, retention policy and retries.

### Discover from another language or an agent tool

```bash
printf '%s\n' '{"api_version":"define.api/v1","id":"discover-1","operation":"capabilities","params":{}}' | define-api
```

`define-api` reads through stdin EOF. It accepts exactly one bounded JSON object; trailing documents, duplicate keys, invalid UTF-8 and unsupported numeric representations are refused. It is **not** a JSON-RPC or MCP server. The protocol uses its own `define.api/v1` contract.

### Python

```python
from define_core import call

result = call({
    "api_version": "define.api/v1",
    "id": "schema-1",
    "operation": "schema",
    "params": {"kind": "request"},
})
request_schema = result["data"]["schema"]
```

`call()` returns a result envelope; diagnostics do not echo source values. The public Python contract is `call(document)`. Internal helpers are implementation details.

### Prepare through the byte API

```python
import base64
import json
from define_core import call

# The caller reads or retrieves its own files; Define receives no host file paths.
request_utf8 = request_bytes.decode("utf-8")
inputs = {name: base64.b64encode(raw).decode("ascii")
          for name, raw in selected_files.items()}

def invoke(identity, operation, params):
    response = call({"api_version": "define.api/v1", "id": identity,
                     "operation": operation, "params": params})
    if response["outcome"] not in ("prepared", "prepared-with-gaps"):
        raise RuntimeError(response["diagnostics"])
    return response["data"]

captured = invoke("capture-1", "capture", {
    "request_utf8": request_utf8, "inputs": inputs,
    "permit_retention": True,
})
prepared = invoke("prepare-1", "prepare", {
    "request_utf8": request_utf8,
    "capture_utf8": captured["capture_utf8"],
    "inputs": captured["inputs"],
})
# Persist these returned members using the caller's own storage policy.
frozen_package = prepared["package_members"]
```

An agent authors the request using the advertised schema. Define validates/assembles that input. It does not turn an arbitrary natural-language goal into proposed meanings by itself. Context/ontology retrieval belongs to the caller or its explicit adapter, and such content must be supplied as selected source/evidence bytes.

### Operations

| Operation | Parameters | Data returned |
| --- | --- | --- |
| `capabilities` | `{}` | Operations, schema names, bounds, claim boundaries |
| `schema` | `kind` | JSON Schema; request, capture, Pack, catalog, report, API request/result and `definition-carrier` (including resource digests) |
| `capture` | `request_utf8`, `inputs`; optional `catalog_utf8`, `permit_retention`, `captured_at` | Capture record/text and complete input members |
| `prepare` | `request_utf8`, `capture_utf8`, `inputs` | Pack, report, readiness, package members and digests |
| `inspect` | `package_members` | Exact closure integrity; no current standing inferred |
| `reconstruct` | `package_members` | Exact package members; no file writes |
| `materialize` | `package_members` | Explicitly selected complete candidate Definitions, Markdown and field lineage |
| `observe-use` | `package_members`, `requested_use`, `consumer`; optional `current_source_base64` | Separate frozen-integrity/freshness/use observation |

`inputs` and `package_members` map canonical logical paths to canonical standard base64 strings. Original request/capture text is retained byte-for-byte after strict UTF-8 encoding. New records use sorted compact UTF-8 JSON plus LF. Original-file, selected-entry, Pack and manifest digests remain separate.

Frame limit: 32 MiB. Decoded member limit: 16 MiB total, 256 members, 16 MiB per member; local capture limits selected source content to 12 MiB and 240 rows to leave control-record space. A final package can still refuse if control records exceed aggregate bounds. Absolute paths, traversal, symlinks in trusted CLI reads, reserved names and file/directory prefix collisions are refused. API members cannot cause arbitrary file reads, URL fetching or executable loading. Integrity checking and materialization do read installed package resources.

### Results and errors

```json
{"api_version":"define.api/v1","id":"prepare-1","operation":"prepare","outcome":"prepared-with-gaps","diagnostics":[],"data":{},"authority_effect":"none"}
```

The closed outcome set is `prepared`, `prepared-with-gaps`, `ready`, `not-evaluable`, `invalid-input`, `blocked`, `unsupported`, `interrupted`, `outcome-unknown`. Observation outcomes `ready` and `not-evaluable` are limited to that stated observation; neither means governing permission. `data` is null on a refusal. Exit statuses: 0 for completed requests (including limited readiness observations), 2 invalid input, 3 blocked or unknown publication outcome, 4 unsupported, 130 interruption. Runtime source drift consistently reports blocked with exit 3 through Python, CLI and JSON entrypoints. Caller correlation IDs are echoed; do not put secrets in them. API result payloads intentionally include supplied retained source content; callers must protect them as data.

Preparation is deterministic for identical request, capture and member bytes. Capture records a timestamp; a caller can supply `captured_at` for reproducible authored input. Later-use observations record their own time and never rewrite the Pack. Interruption of the pure API causes no governing effects; a trusted CLI publication interrupted after its rename may leave the new destination present. A final parent-directory sync failure reports `outcome-unknown`; inspect the destination before retrying.

## Source catalogs and reuse

The optional catalog uses `define.source-catalog/v1`:

```json
{
  "schema_version": "define.source-catalog/v1",
  "entries": [{
    "input_id": "export-policy",
    "binding": {
      "path": "export-policy.json",
      "sha256": "<64 lowercase hex characters>",
      "bytes": 123,
      "digest_kind": "original-file-sha256"
    },
    "reported_standing": "The source system calls this approved; not authenticated by Define."
  }],
  "authority_effect": "none"
}
```

The digest/size shown are placeholders to replace with exact original-file values. A catalog identifies every selected source exactly once. Objects inside task parameter values and schema literals remain data even when they resemble file bindings. Every supplied captured member must belong to the selected closure; unselected bytes are refused. Without one, source paths become input IDs and standing is unreported. Catalogs cannot contain executable adapters or permission grants. `reported_standing` is bounded inert text and does not affect readiness.

For external meanings, a reference supplies the exact input ID, identity, string revision, carrier label, JSON Pointer and selected-entry digest. A supported source object identifies itself through `definition_id`, `node_id` or `id` and `version` or `revision`. Other systems translate their carriers explicitly into this contract. The entry digest uses Define's canonical encoding; its containing file retains its separate original-byte binding.

V3 `reuse` means **reuse this exact identified source meaning with unverified standing**. It does not imply that the meaning is admitted. Captures cannot claim admitted-current, host-member population, a live observation or operator permission. Reusing a complete external parameter declaration derives a mechanical contract named `parameters:<identity>@<revision>`; parameter types are not inferred from prose. An application must retain the enclosing request's consumer and intended use. Assessments remain synthetic/reported unless separately qualified; this version refuses claimed verified external execution.

## How Lab integrates

Lab is one source/consumer integration:

```text
Explicit Lab registry snapshot
        │ exact registry and selected definitions
        ▼
Optional adapters.lab.snapshot()
        │ source catalog + historical reported standing + registry evidence
        ▼
      Same standalone Define API
        │ candidate v3 Pack
        ▼
Explicit consuming connector and separately scoped native owner route
```

The trusted local command is:

```bash
define-standalone capture-lab-snapshot \
  --request /path/to/request-v3.json \
  --source-root /path/to/CyberAlchemy-lab \
  --permit-retention --output /path/to/new-capture
```

It reads the supplied root, checks exact selected registry/body identity, revision, current lookup, carrier and admission reference, and retains the registry. The adapter's historical findings are reported evidence, not authenticated current standing. Definition snapshots that do not match the registry remain local references; the adapter report distinguishes matched and unmatched references. The core never imports this adapter. No Lab runtime is started and no native record is written.

**V3 output cannot enter existing v2/native Lab review routes unchanged.** A consuming connector must establish carrier compatibility, current admitted standing where required, owner scope and native permission. Native review, custody, publication and current Project State selection remain separate Lab integration work. The existing `define/define-v2` continues to expose its original stricter Lab snapshot workflow.

The checkout now provides a separate [local Lab connector](../lab-integration/v1/README.md)
through `define/define lab`. It explicitly maps materialized Definition/v2 bodies,
provisions a private local operator, retains v3 bytes, prepares native v2 review,
and reconstructs from committed local Work. Its local scope does not qualify the
legacy gateway, perform canonical repository admission, or make the installed
standalone distribution depend on Lab.

## Materialization and integrity

The exact Definition/v2 schema and deterministic generator are bundled in `define_core/resources`; `provenance.json` records origins and hashes. They are versioned package resources, never loaded from a Lab installation. The `schema` operation with `kind: definition-carrier` returns its schema and exact schema/generator bindings. Full carrier fields, parameter notation, schema/generator bindings, exact field lineage and explicit selection remain required. Materialization creates candidate bytes; it grants no semantic fidelity acceptance, profile standing or admission.

Installed-source consistency is checked against package-relative `runtime-manifest.json` through the public entrypoints. After trusted bootstrap, selected Python sources are compiled from rechecked source bytes rather than unselected caches. The interpreter, bootstrap and installed dependency environment are trusted. This is **local drift detection**, not a signature, sandbox or proof of publisher authenticity. The manifest is generated only by explicit maintainer packaging with `python3 seal.py`, never regenerated on use. Retained package content is checked for excluded credential/private-key/session-memory patterns; unsupported encodings refuse. These conservative checks do not certify that arbitrary content is free of sensitive data. Required dependencies are declared in `pyproject.toml`; their execution is not authenticated by the source manifest.

When `observe-use` receives no current source-profile bytes, freshness is `not-evaluable`; exact frozen inspection remains available. Supplying matching bytes proves only the comparison, not that those bytes came from a current trusted source.

## Run the standalone suite

Install the wheel in a fresh environment outside the source checkout. Extract the source archive separately; it includes the portable tests and public fixtures. Use the installed environment to run:

```bash
python -I -m unittest discover -s /path/to/extracted-source/tests -v
python -m pip check
```

The suite verifies that imports come from the installed distribution. It exercises all eight API operations, API/CLI parity, exact reconstruction, source standing, parameter contracts, source/provider drift, malformed input, size limits, file collisions, interrupted publication and an actual byte workflow with Python audit rules denying Lab repository reads. The fixtures are synthetic; no owner grants or live Lab state are created.

## Release boundaries

The qualification report in `define/development/standalone-release/v1` records isolated Linux installations, exact artifacts, interpreter/dependency versions, the full suite results, the end-to-end transcript and preservation checks for v1/v2. The Apache-2.0 packaging update is recorded in `define/development/standalone-release/v2`; it preserves the tested runtime bytes. The preceding `standalone-api/v1` report is the historical design/source-review baseline.

This standalone distribution is licensed under Apache-2.0; see LICENSE and NOTICE. Separately distributed dependencies retain their own licenses. Stable public publication still needs a selected stable version and the final publication/tagging decision. None of those decisions is inferred from passing tests. Platform evidence is Linux x86_64 on the recorded WSL2 host, not a native macOS/Windows or multi-distribution Linux certification.

The separate checkout-local connector has its own native v3 mapping and local-owner integration evidence. Canonical Lab admission and broader operational qualification remain separate targets. They do not block a standalone release within this package's declared scope. No model inference, domain assessment execution, hosted HTTP/MCP service or native Lab admission is claimed by this standalone distribution.

## License

Copyright 2026 CyberAlchemy contributors. Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). The complete license and project attribution notice are included in the source distribution and installed package metadata as LICENSE and NOTICE. This license applies to the standalone Define distribution; user-supplied Definition Packs and evidence retain their own terms.
