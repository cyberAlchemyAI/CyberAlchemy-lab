# Proposed runtime documentation contents

Proposal companion. Paths below are proposed destinations; these pages have not been implemented by this package.

## Maintained pages

| Proposed Markdown route | Reader task and essential content | Principal source/evidence | Acceptance |
| --- | --- | --- | --- |
| `docs/lab/runtime/README.md` | Choose a runtime/interface and the next useful task. | Runtime admission overlay; v1/v2 guides; composite dispatcher; Paperclip public receipts. | Reader sees what is usable and selects the appropriate version without treating a candidate label as effective standing. |
| `docs/lab/runtime/status.md` | Understand dated implementation, admission, operation and qualification facts. | Exact reviewed status/evidence selection, source/profile manifests and current State lookup. | Independent facts and complete-run failures remain visible; hashes/details are available without dominating the first read. |
| `docs/lab/runtime/tutorials/first-inspection.md` | Inspect foundation without provisioning a store or key. | Admitted v1 CLI/profile; read-only command observation. | Selected environment and expected D74 output are reproducible; no store or effect is created. |
| `docs/lab/runtime/tutorials/local-work.md` | Prepare/review and, under explicit local authority, apply Work in a fresh isolated branch. | v1/v2 local transaction guides; publisher/replay/recovery contracts and witness. | New owned paths, exact approval, observed receipt, replay and cleanup; no repository admission or activated service implied. |
| `docs/lab/runtime/how-to/provision-and-review.md` | Check environment, choose profile, provision an owned branch and understand review/authorization boundaries. | R02 environment/package evidence; native CLI and signed-approval code. | Installation, store creation, key creation, review, authorization and application are distinguishable actions. |
| `docs/lab/runtime/how-to/agent-sessions.md` | Obtain bounded context; open, inspect and dispose a session; start a fresh one. | Context/session/transport implementations and exact complete-journey evidence. | Expiry, current policy and disposal are explained. Failed integrated paths are documented as unavailable; no successful tutorial until qualified. |
| `docs/lab/runtime/how-to/recover-and-retry.md` | Inspect pending/uncertain work, use exact keys, reconcile and rebuild disposable outputs. | Native recovery; workspace/journal; action reconciliation; projection/export publishers. | Preserve committed history and exact effect boundaries; timeout/absent metadata is not treated as proof of no effect. |
| `docs/lab/runtime/how-to/paperclip.md` | Start an approved local instance, configure the selected process reader, inspect results and diagnose expiry. | Pinned published process adapter, runner3/wrapper, public0270 observations. | Distinguishes Paperclip orchestration, current local credentials, historical Lab source, read-only scope and unproven engineering actions. |
| `docs/lab/runtime/how-to/packages-and-installation.md` | Export/import selected bytes and understand installation/upgrade/rollback prerequisites. | Package/import/export, R02 installer and release readiness; boundary review. | Public/private inputs, protected host dependencies, installation and activation limits are explicit. |
| `docs/lab/runtime/explanation/architecture.md` | Follow components, data flow and ownership from API/CLI to source guards, services and stores. | Ten Lab implementation areas; native engine; API16 service/composite dispatch. | Each node has code responsibility, state ownership and a current qualification or gap. |
| `docs/lab/runtime/explanation/work-evidence-learning.md` | Trace engineering/research attempts, workflows, failures, challenges and lessons. | Work/workflow/continuity/ontology implementations and original domain contracts. | Preparation, admission, observed work, application and assessed improvement remain distinct. |
| `docs/lab/runtime/explanation/state-authority-and-memory.md` | Understand immutable state/history, derived projections, trust channels and ephemeral memory. | Authority/current State; native store; auth/Session/Machine; ontology/SQLite boundaries. | Diagrams retain separate cuts and stores; metadata, message Actor claims or a graph do not grant authority. |
| `docs/lab/runtime/reference/cli-and-environment.md` | Look up exact commands, dependency versions, paths, limits and source-selection rules. | Selected CLI parsers/requirements/profile; packaging/dependency selection. | Each command names its interface/version; no general command is invented for the 34-operation composite or temporary credentials. |
| `docs/lab/runtime/development-and-maintenance.md` | Find code, meaningful verification and documentation source ownership; refresh a reviewed evidence cut. | Implementation source map; exact test plans/receipts; website build/editorial/import/search. | No tests of different versions are combined silently; updates preserve historical packages and formal records. |

## Generated API reference

Proposed destinations: `docs/lab/runtime/reference/api/README.md` and one `{operation}.md` page for each of the 34 declared operations.

| Reference group | Operations |
| --- | --- |
| Discovery and inspection | `lab.status`, `catalog.get`, `artifact.inspect`, `artifact.query`, `operation.inspect` |
| Context and sessions | `context.get`, `session.open`, `session.inspect`, `session.close` |
| Changes, review and admission | `change.prepare`, `change.validate`, `proposal.review`, `checkpoint.resolve`, `admission.apply` |
| Actions and workflow | `action.evaluate`, `action.dispatch`, `action.reconcile`, `workflow.transition` |
| Failure, challenges and learning | `classification.prepare`, `failure.assess`, `challenge.submit`, `challenge.resolve`, `lesson.select`, `lesson.apply`, `lesson.assess` |
| Representation and managed data | `ontology.project`, `projection.refresh`, `files.materialize`, `package.export`, `package.import`, `typed.extension.prepare` |
| Adoption, release and installation | `capability.adoption.prepare`, `release.prepare`, `installation.execute` |

Every generated page needs contract/source version; request/result/error schemas; required channel and actual authority; permitted effects; current-cut rules; input/output/deadline bounds; nested and envelope key behavior; possible domain postures; recovery; exact handler/member location; illustrative examples; and actual proof links or an explicit missing-proof field.

Generation selects `docs/proposals/0008-lab-api-contracts/api-contracts.json` and its bindings. Implementation/evidence fields come from the separately reviewed runtime selection. The catalog's preserved “candidate-contract-only” fields are not overwritten to assert admission.

## Diagrams

1. Component map: CLI/reader/composite dispatch, services and independent stores.
2. Read sequence: policy/key/nonce, trusted context, exact cut, reply and posture.
3. Review/commit sequence: candidate workspace, validation, independent owner cores, actual authorization, transaction/head and derived outputs.
4. Session lifetime: current assignment/context, resource and signer, allowed reads/actions, deadline/revocation, disposal and fresh-session reconstruction.
5. Recovery: claim/journal, uncertain outcome, operation inspection, authorized reconciliation and cold replay.

Prefer small Mermaid/SVG diagrams with text equivalents and linked implementation responsibilities. Distinguish conceptual connections from declared ontology relation kinds and qualified complete operation.

## Navigation and reuse

Add **Operate the Lab** alongside the existing conceptual model and practical guides. Keep the current Definition library, Craft article, essays and research pages as linked destinations. Place detailed developer and per-operation references beneath the runtime section so a new operator does not have to read implementation internals before the first inspection.

Proposed maintained HTML sources belong in the existing `website/source/governance-lab-series` runtime subtree. The precise renderer/editorial registration and import/search changes should be selected from [the documentation-system audit](research/documentation-system.md) during implementation. One maintained narrative should supply both HTML and Markdown.
