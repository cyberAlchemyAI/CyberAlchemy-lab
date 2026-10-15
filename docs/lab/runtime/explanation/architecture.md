[Documentation home](../../README.md)

<a id="runtime-architecture"></a>

Lab runtime · proposed documentation

# Runtime architecture and ownership

Follow the executable paths and the independent stores they own.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

<a id="runtime-architecture-two-entrypaths"></a>

<a id="runtime-architecture-two-entrypaths-title"></a>

## Two entrypaths

The admitted local CLI enters lab.py, then cli.main. With no selected store, read_data captures the frozen repository envelope; explicit init constructs a local store. Review/sign/apply/replay/recover and ephemeral Session are local store operations.

The captured Base stdio API enters serve.main and constructs a Base service after independent source/profile/policy/nonce checks. IntegrationService composes Base28, Action3 and Governance3 with the same Schemas object and independent authenticated branch contexts. A Base connection cannot advertise full34 readiness. The [maintained composite candidate](../../assets/c034636b312a-README.md) supplies a separately selected serialized launcher contract.

<a id="components"></a>

````mermaid
flowchart LR
  CLI[Admitted local CLI] --> LS[Local transaction store / HEAD]
  CALL[Exact stdio envelope] --> F[Composite IntegrationService]
  F --> B[Base Service 28]
  F --> A[Action Service 3]
  F --> G[Governance Service 3]
  B --> W[Owned workspace journal]
  B --> R[Signed readers / native replay]
  R --> C[Context / ephemeral Session]
  A --> AJ[Action grant / effect journal]
  G --> GS[Selected native governance store]
  R -. derive .-> Q[SQLite / graph views]
````

The CLI owns a separate local transaction store. The composite routes unchanged calls to three independently authenticated branches. Base workspace, Action effects and native Governance state are distinct; readers derive Context and disposable query representations.

Explanatory component/sequence map, not a declaration of new ontology relation kinds or qualified runtime execution.

<a id="runtime-architecture-ten-implementation-areas"></a>

<a id="runtime-architecture-ten-implementation-areas-title"></a>

## Ten implementation areas

| Area | Concrete responsibility |
| --- | --- |
| lab-runtime | [CLI](../../assets/43799f3efb2c-cli.py), source selection, local transaction/replay/recovery, graph, Session |
| lab-provisioning | [Pinned scoped branch](../../assets/fdfe260336ac-provision.py) and configuration/HEAD selection |
| lab-bootstrap | [Seed/package composition](../../assets/22103d4007e1-bootstrap.py) and controlled candidate changes |
| lab-integration | [Composition verification](../../assets/b25e3ed86dcc-validate.py), distinct from component admission |
| lab-review | [Bounded review material](../../assets/de263ca7b90b-review.py), not an actual owner decision |
| lab-context | [Native reader](../../assets/358b00bc3069-native_reader.py) and [generator/consumer](../../assets/03f81c418f33-context.py) |
| lab-ontology | [Semantic/governance event replay](../../assets/ed9f4a9f5e21-lib.rs) and represented views |
| lab-continuity | [Durable custody evidence](../../assets/762da7574611-custody.py) without restoring live memory |
| lab-work | [Bounded episode](../../assets/fece8ebfe270-episode.py) and public evidence/archive verification |
| lab-workflows | [Engineering](../../assets/91eb2420596c-engineering.py), [research](../../assets/20f1749ef038-research.py), [authority](../../assets/0ba615a11a18-evaluator.py), [dispatch](../../assets/b4f22eb96952-dispatch.py) and learning |

These are implementation responsibilities. Candidate carriers, actual effects and effective admission retain their own records.

<a id="runtime-architecture-the-call-chain"></a>

<a id="runtime-architecture-the-call-chain-title"></a>

## The call chain

The Base service verifies channel, byte/envelope/profile bounds, allowed operation, call ID, actor, strictest deadline, budgets, cut, domain schema and actual selected code. An effectful request claims an exact fingerprint/key in the owned Vault. Prior outcomes return before fresh allocation; pending outcomes are not redispatched.

Source selection names the actual source, reader, mapper, Context producer, package, Principal and period. Native replay verifies original histories; a mapper produces a source-bound projection; Context is generated under current policy; a live Session/Machine borrows only what its actual resource permits. No internal adapter nickname can replace those public identities.

<a id="runtime-architecture-state-ownership-and-dependencies"></a>

<a id="runtime-architecture-state-ownership-and-dependencies-title"></a>

## State ownership and dependencies

Local immutable transactions/HEAD, native event histories, private API journal material, derived SQLite/graph files and ephemeral Session RAM have separate owners and recovery contracts. The [state/authority/memory page](state-authority-and-memory.md) follows those stores without drawing them as one database.

The selected interpreter/native/library closure is independent of code/source/profile selection. Full historical provenance and the narrower schema execution dependency table remain explicit; unavailable historical inputs are not silently aliased to current files. Fresh original guards remain required even when pure preparation reuses a scoped snapshot.

<a id="runtime-architecture-current-integration-standing"></a>

<a id="runtime-architecture-current-integration-standing-title"></a>

## Current integration standing

The eight API17 overlay leaves are reviewed code, not current all34 qualification. The old execution capture is ineligible. Family4's Source table bound future-changing API preparation files, so final publication would invalidate the family. The capture guard rejects that cycle.

A successor needs exact historical snapshot technical bindings and complete preserved native history/role/code proof. The driver4 private loader and margin component have scoped peer checks; no successful complete learning/empirical margin follows. See [the capture flag](../../assets/e9ce84547f5d-independent-review-0001.json) and [dated status](../status.md) .

<a id="runtime-architecture-sources"></a>

## Selected public evidence

- [product/lab/release-candidates/v1/interface/api-integration-v16/integration_dispatch.py](../../assets/240dbfa9faa7-integration_dispatch.py). SHA-256 240dbfa9faa79b33e59d423343f23e4b86aaa8c962579c730ec7785275cfe0ea; 4440 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/api-integration-v16/service.py](../../assets/34e0a3b88ffc-service.py). SHA-256 34e0a3b88ffc7c348830fcf5ccd422610741a70adaeda3c13f6a3a1bfb6bebcd; 45673 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-bootstrap/candidates/v1/bootstrap.py](../../assets/22103d4007e1-bootstrap.py). SHA-256 22103d4007e15c9156a4641f64b61404d680475ed8c99e60c4ab4474bb5d4b1b; 41190 bytes. Public technical snapshot; no authority transfer.
- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/api17-task-local-capture-0004/independent-review-0001.json](../../assets/e9ce84547f5d-independent-review-0001.json). SHA-256 e9ce84547f5d6f9fd6571afc4a56146e76b2baac0a005ad836c5b02a756ac53f; 12336 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-context/candidates/v1/context.py](../../assets/03f81c418f33-context.py). SHA-256 03f81c418f33894911ad045d3316d14cfc1232906da9b79cdd9ea3074aabccad; 20746 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-continuity/candidates/v2/custody.py](../../assets/762da7574611-custody.py). SHA-256 762da75746114573b8a42fd23a850204c5a74c7f40dd541c1a5af1ba15ef9f3f; 15471 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-workflows/candidates/v1/authority/dispatch.py](../../assets/b4f22eb96952-dispatch.py). SHA-256 b4f22eb96952b7e1dabf13ae93d567502eea70078d35ec938623ae6ff40a266e; 12509 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-workflows/candidates/v1/workflows/engineering.py](../../assets/91eb2420596c-engineering.py). SHA-256 91eb2420596cd0ece48bfdec749342c0ebfaf0df0f6d06171e3e295e1255569f; 31148 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-workflows/candidates/v1/authority/evaluator.py](../../assets/0ba615a11a18-evaluator.py). SHA-256 0ba615a11a1896f64e254b2f2a6cca251707ace309601737b4ff4d4148ab24c9; 15880 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-integration/candidates/v1/validate.py](../../assets/b25e3ed86dcc-validate.py). SHA-256 b25e3ed86dcc6dbbaa5a3e7171f4a815622016f4b55fe145a4ab144f42ee5148; 10689 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-context/candidates/v1/native_reader.py](../../assets/358b00bc3069-native_reader.py). SHA-256 358b00bc306991565f90b414bdea5048783bb340314eee9818ae82001c190828; 4645 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-ontology/candidates/v1/adapters/native/src/lib.rs](../../assets/ed9f4a9f5e21-lib.rs). SHA-256 ed9f4a9f5e21bc522f3586cc046799fe7ad7cdc08868afc189f0bd0bf708eea7; 84297 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-provisioning/candidates/v1/provision.py](../../assets/fdfe260336ac-provision.py). SHA-256 fdfe260336ac5e2ed3063d3d57044a3ab841074ec5ab26f6966ff02c563cfa4b; 7886 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-workflows/candidates/v1/workflows/research.py](../../assets/20f1749ef038-research.py). SHA-256 20f1749ef038c5153f293615126151a87c21794dd39b52338bc0f59c3c7be8ad; 40950 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-review/candidates/v1/review.py](../../assets/de263ca7b90b-review.py). SHA-256 de263ca7b90b870dcc5796f10806b36ffc78fb589cf93e34fa18ddc38ef61a2f; 16550 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/README.md](../../assets/c034636b312a-README.md). SHA-256 c034636b312ac42c3ecd25b6c8e5ec0586cbf606459a9ab1cd37343a3b541a1e; 11032 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-runtime/v1/lab_runtime/cli.py](../../assets/43799f3efb2c-cli.py). SHA-256 43799f3efb2c53a4c9b39c99a681ecc7134182094aa06c14d66a378b594ba056; 11813 bytes. Public technical snapshot; no authority transfer.
- [implementation/lab-work/candidates/v1/episode.py](../../assets/fece8ebfe270-episode.py). SHA-256 fece8ebfe270b46792df74dd906c419131eccf93bbb36a682075d10e72543133; 14456 bytes. Public technical snapshot; no authority transfer.
