# Define CLI for CyberAlchemy Lab

**Version:** `0.1.0-candidate` · **Standing:** local candidate realization · **Authority effect:** none

Define clarifies the meanings needed for a goal. It reads the Lab's selected Project State, definitions and bounded ontology views, then produces a candidate Definition Pack for one named consumer. It supports conversational review, scripted preparation, review inspection and a bounded Alch → Craft handoff.

## Start

From the Lab repository root:

```bash
./define/define doctor
./define/define context
./define/define ontology Authority
./define/define inspect cal.definition.definition
./define/define chat "Investigate missing rows in an account export"
```

The launcher also works from another directory when addressed by its absolute path. Linux (including WSL), Node ≥26.8.1 and Python with `jsonschema` and `cryptography` are required. Chat uses the installed `codex` command and its normal login. Set `DEFINE_CODEX_BINARY` for a different executable or `DEFINE_PYTHON` for the Python interpreter. Scripted preparation and inspection require no model call.

## Prepare and compile an incident example

The fixture supplies reviewed language, grounding and a candidate completion criterion. It concerns the same source snapshot, account and filters throughout.

```bash
./define/define run \
  --goal 'Define complete export for the incident' \
  --intent 'Investigate missing rows without changing customer data' \
  --context 'Account A, filters F, source snapshot S' \
  --consumer incident-investigator \
  --input implementation/define-cli/v1/fixtures/incident-input.json \
  --output /tmp/incident-definition-pack.json --json

./define/define compile \
  --input /tmp/incident-definition-pack.json \
  --out /tmp/incident-definition-build --json
```

Use new output paths: existing candidate files and build directories are refused. Compilation checks the pack digest, replays language checks, and verifies that its Lab context is current and unexpired. Re-run Define after a context expiry or state change. Compilation emits candidate source, graph, compiler certificate, finite fixture results and a handoff receipt. It does not approve the meaning or execute the incident response.

The simpler `fixtures/smoke-input.json` demonstrates a **structure-only** pack. Such a pack can be examined, but cannot pass the Alch handoff without reviewed language-quality evidence. An unresolved concept produces an open disposition and exit status 4.

## Select context and prepare review

```bash
./define/define context --subject cal.definition.authority
./define/define context --definition-ref 'cal.definition.definition@1.0.0-candidate.1'
./define/define review --store /path/to/provisioned/lab-store --proposal /path/to/proposal.json
```

For exact references, use the `version_ref` returned by `inspect`; do not guess a reference from the term. `--definition-ref` is repeatable and must resolve to a current Definition. Without it, Define selects nine common Lab terms. Reuse and specialization bind the resolved version; an invented or outdated reference is rejected.

`--store` selects an existing operational runtime v2 branch. Without a provisioned store, context uses the selected repository foundation for inspection. It creates no keys or store. Review requires an explicit initialized branch and an existing **Lab runtime proposal**. A Definition Pack is a different contract: it must be prepared for the Lab's Definition and owner review requirements before admission. See [Prepare a definition](../../../docs/lab/how-to/prepare-definition.md).

Review returns planned consequences and exact decision cores. It never calls authorization or apply. The source Project State keeps its original standing; the temporary agent session has the selected local branch scope.

## Conversation and memory

Chat asks one question at a time, confirms scope, reviews each proposed meaning, then asks to create the pack. Edited meanings are checked again. The adapter initializes a native Codex app-server, sends `initialized`, and opens an ephemeral read-only thread. It requests a no-tool conversation; approval requests are declined by the retained RPC client.

Agent context comes from Lab state and views. Temporary Lab sessions close after export; conversation memory ends when the owned process closes. The revisioned durable Define-session API remains available for project work records. Its caller-provided access context is a local policy input, not authenticated human identity or repository admission authority. The default chat does not automatically persist a durable session.

## Verify

```bash
cd implementation/define-cli/v1
npm test
npm run audit
npm run doctor
node scripts/check-native-host.mjs
```

The host check uses a temporary Codex home and sends no model turn. Tests cover real Lab context/review interfaces, the installed compiler path, CLI commands, language checks and retained durable-session behavior. See [the audit](AUDIT.md) and [the interface contract](CONTRACT.md).

## Source and supported scope

The unchanged upstream snapshot is under [`define/source`](../../../define/source/cyberAlchemy-v2/). This successor selects the compiled Define service, durable session core, bounded semantic compiler and leaf RPC providers. Old ARE gateway/router/Module Port and standalone ontology-stage interfaces remain in the snapshot; they are not active dependencies or supported successor exports. This is a deliberate Lab interface selection, not full parity with every historical adapter.

The [runtime manifest](runtime-manifest.json) pins selected executable providers. Commands check it before proceeding; `--help` remains available. The manifest is a drift check, not a signature or authorization credential. Source-profile currentness is checked independently by the Lab runtime. Rebinding after an intentional provider change requires review and regenerating the manifest, followed by the suite and audit; never refresh a pin just to hide drift.
