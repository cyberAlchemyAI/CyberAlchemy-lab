[Documentation home](../../README.md)

<a id="runtime-cli"></a>

Lab runtime · proposed documentation

# CLI and environment reference

Look up exact parser surfaces and their selected source/environment limits.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

<a id="runtime-cli-admitted-v1-syntax"></a>

<a id="runtime-cli-admitted-v1-syntax-title"></a>

## Admitted v1 syntax

The entrypoint is implementation/lab-runtime/v1/lab.py; it imports that package's cli.main. Global --repo PATH and --store PATH precede the subcommand. Its default store is .local/lab-runtime/store, so public inspection examples explicitly choose a nonexistent store to avoid an existing operator branch.

| Command | Actual parser arguments |
| --- | --- |
| verify / status | No additional positional arguments |
| inspect | SUBJECT and optional --record |
| catalog | Optional --category definition/artifact-type/relation-kind/artifact-instance/typed-relation and --current |
| query | Optional ROOT, --direction both/incoming/outgoing, --depth, --max-nodes, --max-edges, repeatable --predicate |
| rebuild | Required --out; writes disposable derived output |
| keygen | Required --private and --public; private file must be outside repository |
| init | Required --id, --owner, --public-key; new store only |
| example / review | example --id/--out; review PROPOSAL |
| authorize / apply | authorize PROPOSAL --private-key/--out; apply PROPOSAL APPROVAL |
| recover | Required --expected-head |
| session | SUBJECT, optional --ttl and --context-only |

This table comes from [the selected parser](../../assets/43799f3efb2c-cli.py) . Command existence is not permission to perform its effects.

<a id="runtime-cli-environment-and-source-selection"></a>

<a id="runtime-cli-environment-and-source-selection-title"></a>

## Environment and source selection

The v1 requirements are jsonschema >=4.23,<5 and cryptography >=43,<49. The first walkthrough selected existing isolated Python 3.14.4/dependencies0004 with explicit dependency/v1 import roots. Its proof does not establish a fresh installation. Select the whole [dependency declaration](../../assets/2345d4d3a59c-dependency-selection-0002.json) independently rather than trusting the interpreter filename alone.

v1's [source profile](../../assets/7bf11e361cc9-profile.json) selects D74. v2's [separate candidate profile](../../assets/cbfe3d7c5f92-profile.json) selects D75 and a distinct default store. Never use a v2 profile to relabel an existing v1 branch. The [first tutorial](../tutorials/first-inspection.md) defines its local shell convenience and three actual reads.

<a id="runtime-cli-api-and-sdk-are-different-interfaces"></a>

<a id="runtime-cli-api-and-sdk-are-different-interfaces-title"></a>

## API and SDK are different interfaces

The captured API has LF-terminated UTF-8 JSON envelopes, request/result/error schemas, exact selected profile/source, independent challenge/proof and live context. It does not accept CLI subcommands like init or a fabricated universal lab run command.

The candidate [composite launcher](../../assets/c034636b312a-README.md) takes independently selected launcher/config hashes and a protected canonical configuration. It is serialized stdio, not a network service. All Base/Action/Governance branch inputs/proofs and a same-process fresh Action lease/handoff are prerequisites. Its focused controls do not prove full34 readiness.

The [34-operation reference draft](../../assets/b989623e62b1-README.md) looks up declared effects/errors/deadlines/keys/readiness and exact conditional implementation sources. It is historical and unqualified for changed API17.

<a id="read-sequence"></a>

````mermaid
sequenceDiagram
  participant U as Selected caller
  participant C as ReaderChannel
  participant S as Selected service
  U->>C: Current policy and independent credential selection
  C->>U: Fresh nonce challenge
  U->>C: Exact signed proof
  C->>S: Trusted current context
  U->>S: Bounded exact envelope and source cut
  S->>S: Current source/schema/permission/deadline checks
  S-->>U: Bound reply and domain posture
````

This is the API candidate read sequence, not the key-free v1 repository-inspection tutorial. Policy/key/nonce establish the trusted context; the service checks exact source/cut/bounds before replying. A reply still needs posture assessment.

Explanatory component/sequence map, not a declaration of new ontology relation kinds or qualified runtime execution.

<a id="runtime-cli-limits-and-safe-failures"></a>

<a id="runtime-cli-limits-and-safe-failures-title"></a>

## Limits and safe failures

Input/output/line/frame/call budgets belong to the selected interface/policy. Composite startup is independently bounded from 1 to 300 seconds; it does not extend a grant. The pinned Paperclip runner's whole episode limit is at most 900 seconds. Source fixture 24-hour periods, reader grants and 900-second Session limits are independent clocks, not interchangeable defaults.

Distinguish malformed contract, unauthorized context, source integrity/stale cut, deadline/budget exhaustion, ambiguous/unresolved reference and pending/recovery-required outcomes. Preserve exact input/result hashes and public class/code location; private args/locals/proofs stay out of diagnostic output.

<a id="runtime-cli-sources"></a>

## Selected public evidence

- [product/lab/release-candidates/v1/interface/api-integration-v16/auth.py](../../assets/e9f3524267ee-auth.py). SHA-256 e9f3524267ee82b841c128b85f67714f3de7c9bb963c614c7bf06ca3fe697394; 32487 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/api-integration-v16/integration_dispatch.py](../../assets/240dbfa9faa7-integration_dispatch.py). SHA-256 240dbfa9faa79b33e59d423343f23e4b86aaa8c962579c730ec7785275cfe0ea; 4440 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T21/api-reference-preparation-0003/reference-0001/README.md](../../assets/b989623e62b1-README.md). SHA-256 b989623e62b14b4d791d12347483f9107a28cf86adffdb01ce4c2c2fa78eb753; 10119 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/api-integration-v16/protocol.py](../../assets/8202c836488d-protocol.py). SHA-256 8202c836488df5b53e4b279012926dce43c80aabd57e6c66840ba9b77eacc947; 10792 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/api-integration-v16/service.py](../../assets/34e0a3b88ffc-service.py). SHA-256 34e0a3b88ffc7c348830fcf5ccd422610741a70adaeda3c13f6a3a1bfb6bebcd; 45673 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json](../../assets/2345d4d3a59c-dependency-selection-0002.json). SHA-256 2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835; 317618 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/README.md](../../assets/c034636b312a-README.md). SHA-256 c034636b312ac42c3ecd25b6c8e5ec0586cbf606459a9ab1cd37343a3b541a1e; 11032 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-runtime/v1/lab_runtime/cli.py](../../assets/43799f3efb2c-cli.py). SHA-256 43799f3efb2c53a4c9b39c99a681ecc7134182094aa06c14d66a378b594ba056; 11813 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-runtime/v1/profile.json](../../assets/7bf11e361cc9-profile.json). SHA-256 7bf11e361cc9d893dd809c28df464e66a8263ef0b14d48b1f34d0663dd2b2842; 5263 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-runtime/v2/profile.json](../../assets/cbfe3d7c5f92-profile.json). SHA-256 cbfe3d7c5f92d0bc547b836a9d84616b9be26cb399a587aab8800f93fd96ed58; 6442 bytes. Public technical snapshot; no authority transfer.
