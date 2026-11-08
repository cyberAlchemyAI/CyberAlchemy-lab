# CyberAlchemy Define CLI

This package is the candidate conversational terminal realization of `CA2-CAP-DEFINE-SHARED-MEANING`.
It is ready for local testing, but it is not accepted, published, deployed, or installed globally.

The primary conversational command performs one bounded reviewed lifecycle:

```text
broad new-work / domain / subject / context / project opening
  -> persistent ARE gateway
  -> shared app-server RPC client
  -> conversational discovery through the Codex app-server wrapper
  -> direct user-language capture across terms, distinctions, relationships, constraints, ownership, and open questions
  -> explicit scope review and confirmation
  -> candidate meaning options
  -> one-option-at-a-time review
  -> verified ARE route and frozen inline Context Envelope
  -> candidate Definition Pack
  -> explicit Definition Pack Alch handoff
  -> generated semantic-contract ontology
  -> Craft / DomainSpec project and compilation
  -> candidate executable runtime projection plus digest-bound receipt
```

The agent may reflect, summarize, and propose. It preserves the user's phrases separately from
candidate interpretations and may not silently confirm its own inference. For unbounded new-work
intent, scope cannot become ready until the user has addressed the desired outcome, consumers,
terms, distinctions and relationships, constraints, ownership, and open questions. Unknown and
not-applicable answers remain valid user answers rather than being invented by the agent.

Before presenting scope for confirmation, the runtime evaluates a structured language-quality
contract. Every language item must point to an exact user phrase; every unordered term pair must
carry non-collapse evidence; and every declared classification-axis pair must be independent or
have an explicit typed coupling. Candidate inferences remain `review` until the user confirms
them. Missing grounding, collapsed terms, redundant axes, unresolved pairs, and unnamed coupling
block pack creation. These deterministic checks validate coverage and concrete contradictions;
they do not prove canonical semantic truth.
The exact scope requires a human confirmation, and every option requires an explicit accept,
edit, discuss, or defer action.

Define's semantic and workflow dispositions are no longer owned by handwritten
prototype code. Their canonical construction sources are the `.alch` files in
`alch/`, assembled by `alch/define-runtime.alch` as eleven non-overlapping entry
points. `GroundingEvidence`, `NonCollapseEvidence`, and
`OrthogonalityEvidence` own per-record posture meaning; `SemanticGrounding`,
`NonCollapse`, `Orthogonality`, and `LanguageReadiness` own quality aggregation;
`ScopeReadiness`, `ConceptDisposition`, and `PackReadiness` carry the pack
workflow decisions. `AlchHandoffReadiness` independently requires structural
readiness, semantic grounding, non-collapse, orthogonality, and a new output
target before compilation. The exact candidate business and system ontology records are selected in
`alch/define-runtime.ontology-selection.json`.

```text
host evidence extraction and interaction adapters
  -> canonical multi-entry AlchLang declarations
  -> source-linked composition ontology for every entry
  -> Craft / DomainSpec v2 project for every entry
  -> generated executable decision service
  -> conversational scope, disposition, and Definition Pack gates
```

JavaScript remains responsible for model/RPC transport, evidence collection,
user-facing prose, canonical object construction, context-source
reads, persistence, locks, atomic writes, and audit delivery. Those adapters
consume the generated decisions rather than independently replacing them.
The condition-by-condition boundary is recorded in
`HOST-SEMANTIC-INVENTORY.md`.

Unicode semantic-key normalization and boundary-aware phrase containment are
declared by the Alch semantic prelude and consumed through its shared direct
compiled-artifact adapter. Define, Router, and ARE request intent bind the same
runtime bytes while retaining separate quality, route, and objective policies.
The exact dependency and construction pipeline are recorded in
`alch/define-runtime.ontology-selection.json`; the host no longer implements
those two semantics itself.

`npm test` runs `scripts/verify-alch-runtime.mjs` first. Verification blocks on
a missing `.alch` source, selected-ontology drift, service-entry drift,
ontology or Craft-project mismatch, compiler-certificate mismatch,
generated-file drift, incorrect executable outcomes, or non-repeatable
recompilation. Generated output remains candidate construction evidence and
grants no ontology admission or runtime authority.

## Definition Pack Alch handoff

A reviewed, handoff-ready conversational result can be materialized explicitly:

```bash
node cyberAlchemy-v2/implementation/define-cli/bin/define.mjs compile \
  --input /path/to/definition-pack-result.json \
  --out /path/to/new-definition-contract
```

The output directory must not exist. It contains `definition-pack.alch`, finite
language fixtures, `compiled/`, and `handoff-receipt.json`. The compiler pipeline
is recorded as Definition Pack, Alch source, semantic-contract ontology, Craft
project, DomainSpec compilation, runtime projection, and fixture validation.
The receipt binds the exact pack, source, fixture, and compiler manifest digests.

Compilation blocks if the pack has open meaning, lacks a reviewed language-quality
evaluation, or if semantic grounding, non-collapse, or orthogonality does not
pass. This is a candidate semantic runtime projection, not generated product
behavior: it does not make the definitions canonical and does not authorize
implementation, effects, publication, or deployment.

## Durable session runtime

The package also exports a transport-neutral durable session core for CLI and
chat adapters. It implements the smallest unit selected by the Define runtime
design: one versioned command against one expected revision, followed by one
atomic confirmed-state boundary.

`createDurableDefineRuntime`, `createDefineSessionClient`, and
`JsonFileSessionRepository` provide:

- complete resumable snapshots with exact state digests;
- shared CLI/chat session identity without interface-owned state;
- optimistic revision conflicts and command-id idempotency;
- atomic mode-0600 JSON persistence and tamper detection;
- visible denied, invalid, conflict, incompatible-schema, and storage-failure
  outcomes; and
- content-minimizing audit records that exclude prompts, answers, sources, and
  raw session identifiers.

`resolveDefineContextCandidates` applies the committed explicit-user,
related-reference, current-window, and saved-session order without allowing an
inferred candidate to overwrite explicit context. Conflicts and the need for
user correction remain visible. `createDefineContextSufficiencyAdapter` maps
the private semantic-judgment evaluator into the Define three-valued result and
caches exact frozen requests so historical replay does not rerun evaluation.

The in-memory repository remains available for deterministic tests. The file
repository is a local candidate backend, not an adopted storage, backup,
retention, encryption, or deployment choice. Actor access context must be
supplied by a trusted adapter; this package does not invent an identity
provider.

## Conversational run

Use Node 26.8.1 on PATH. Start from the directory containing `cyberAlchemy-v2`
in the checkout or extracted engine:

```bash
node cyberAlchemy-v2/implementation/define-cli/bin/define.mjs
```

You can also supply the broad opening immediately:

```bash
node cyberAlchemy-v2/implementation/define-cli/bin/define.mjs \
  "We are building a knowledge system for clinical research teams and the language is becoming inconsistent"
```

The conversational path connects to the persistent ARE gateway at
`$XDG_RUNTIME_DIR/are-codex/gateway.sock` (or `/run/user/<uid>/are-codex/gateway.sock`) and
creates an ephemeral read-only Codex thread on the dedicated `codex:define-cli`
interaction consumer. It no longer attaches to the hosted Windows client's
`codex:human-chat` gateway session. The
gateway preserves its consumer runtime across transport reconnects; Define itself does not
create durable conversation storage. Use `--gateway-socket <path>` for a different gateway.
The client pins `codex-app-server/v1` in the gateway handshake and uses
`ARE_GATEWAY_CONNECTION_TOKEN` when the gateway requires one. Thread and turn
requests use on-request approval, a read-only sandbox, and stable request keys;
the shared RPC client declines approvals by default. Define sends its bounded
application request as turn input and a separate ARE request-context hint, then
validates the returned JSON against its own candidate-turn contract. The
no-tools instruction is a prompt constraint, not proof that every host tool is
unavailable. This fixed Define consumer ID supports one attached Define client
at a time; a second concurrent Define process is rejected rather than sharing
the first process's session. It is not a unique invocation ID, durable Define
conversation, or the current desktop task's identity. Existing historical
`codex:human-chat` gateway sessions are not migrated or adopted by Define.
The local gateway/real-wrapper fixture proves one no-provider turn. The
installed-host canary below separately proves one Define turn through the
pinned local Codex binary and fixed loopback provider, including structured
output on the provider wire. Neither test proves live-model behavior, a desktop
task handover, or general multi-client operation.

`--direct` is an explicit diagnostic fallback that spawns the strict app-server wrapper for
this process. It does not permit protocol drift and is not the normal conversational path.
Use `--output <path>` to atomically retain the final pack, and `--json` to print the complete
result instead of the compact human summary.

## Advanced scripted run

`define run` retains the deterministic exact-input interface for automation:

```bash
node cyberAlchemy-v2/implementation/define-cli/bin/define.mjs run \
  --goal "Define a release channel" \
  --intent "Remove ambiguity for a local consumer" \
  --context "A release channel names how candidate output reaches a consumer." \
  --consumer local-test \
  --input cyberAlchemy-v2/implementation/define-cli/fixtures/smoke-input.json \
  --json
```

Scripted input has this shape:

```json
{
  "concepts": [{"concept_id":"concept:term","term":"term","question":"What does term mean?","owner_route":"Definitions Governance owner"}],
  "responses": [{"concept_id":"concept:term","action":"propose","payload":{"definition":"Candidate meaning."}}]
}
```

The advanced path supports `reuse`, `specialize`, `propose`, `open`, `defer`, and `refuse`.
Open dispositions cause exit code `4`; they never invent an answer.

Exit codes: `0` complete candidate pack or compiled handoff, `2` CLI/input error,
`3` context, compiler, or structural failure, and `4` open meaning or a handoff
readiness block. All outputs retain `authority_effect: none`.

## Test

```bash
cd cyberAlchemy-v2/implementation/define-cli
npm test
```

To check the installed host without reaching an external model or touching the
current desktop task, run the isolated canary with an exact installed binary
and version:

```bash
node scripts/native-gateway-canary.mjs /absolute/path/to/codex 'codex-cli <exact-version>'
```

The canary uses a temporary `CODEX_HOME`, a fixed loopback Responses provider,
and a disposable gateway socket. Its JSON report binds the host path, version,
and SHA-256 and reports provider-wire and teardown checks.

The candidate intentionally excludes an adopted identity provider, encryption
and secret handling, backup/restore policy, retention duration and deletion
authority, numeric SLOs, deployment topology, canonical definition promotion,
automatic consumer execution, publication, deployment, and global installation.

## Open Questions

- Which authenticated adapter supplies actor access context in an adopted runtime?
- Which storage, backup, retention, encryption, and migration policies replace
  the local candidate backend?
- Which owner-approved accessibility criteria, numeric SLOs, and deployment
  topology govern a later accepted realization?
