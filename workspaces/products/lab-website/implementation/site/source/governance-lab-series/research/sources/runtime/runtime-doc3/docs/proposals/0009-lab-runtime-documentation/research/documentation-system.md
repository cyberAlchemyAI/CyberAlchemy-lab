# Runtime documentation system: research and recommendation

Status: **research proposal; no documentation migration or runtime change performed**. Scope: the existing Lab website and repository-readable edition. This brief uses research/context components only; it does not claim completion of an Invoke define/design mode whose installed contracts are unavailable.

## Recommendation

Add a maintained **Using the runtime** section to the existing Lab website, and mirror it into `docs/lab/` through the existing renderer/import pipeline. Keep one editable source per passage, exact contracts beside their selected implementations, and a separate source-bound current-status projection. Preserve immutable package READMEs and captured reference bodies as historical evidence. Improve their reading context through the maintained front door rather than editing frozen packages.

The website already supplies the necessary shell, editorial voice, search, portable relative links, exact-body preservation checks and Markdown importer. Replacing it with another documentation platform would add migration cost before resolving the actual gaps: runtime entry points, task-oriented instructions, release/source selection and ambiguous freshness.

## What the repository currently establishes

These are read-only observations, not new acceptance or liveness claims.

| Observed source | Existing behavior and documentation implication |
| --- | --- |
| [Root README](../../../../README.md) and [runtime admission](../../../../implementation/lab-runtime/ADMISSION.md) | The front door distinguishes admitted local runtime v1/D75 from the separately selected D74 execution profile, v2/D75 candidate and stable-release target. Runtime identity, selected foundation and release standing must remain separate. |
| [Frozen v1 README](../../../../implementation/lab-runtime/v1/README.md), [contract](../../../../implementation/lab-runtime/v1/CONTRACT.md), [v2 review](../../../../implementation/lab-runtime/v2/REVIEW.md) | v1 still leads with candidate-era wording while its exact package has later admission evidence. The v2 review explicitly distinguishes a source body's candidate lifecycle from effective instance admission. This is a real reading problem, not justification to rewrite reviewed bytes. |
| [Documentation home](../../../lab/README.md), [maintenance](../../../lab/MAINTENANCE.md), [source/status](../../../lab/source-and-status.md) | The explanatory prose edition is dated 12 October; the reference and operational source capture is 8 October. “What exists today” is easy to read as live status even though the text explains that its source selection is captured. |
| [Website README](../../../../website/README.md), [migration](../../../../website/MIGRATION.md), [site maintenance](../../../../website/source/governance-lab-series/SITE-MAINTENANCE.md) | Maintained templates and renderers produce HTML; adopted prose is applied afterward; search uses final pages; the Markdown import is a separate reviewed operation. The build normally uses a captured edition, not live repository capture. |
| [Schema package](../../0007-lab-integrated-schema-package/PROPOSAL.md), [catalog](../../0007-lab-integrated-schema-package/schema-catalog.json), [runtime obligations](../../0007-lab-integrated-schema-package/RUNTIME-OBLIGATIONS.md) | Schemas describe interfaces; obligations additionally require hashes, signatures, currentness, causal evidence and actual effects. Neither a declared operation nor a valid result envelope proves the complete behavior. |
| [Product acceptance](../../../../product/lab/release-candidates/v1/PRODUCT-ACCEPTANCE.md), [release selection](../../../../product/lab/release-candidates/v1/release-selection.json) | Pre-implementation acceptance text still contains “not collected” observations, while later scoped receipts exist. The selection explicitly retains partial standing and publication restrictions. Current presentation needs exact evidence selection, not edits to those historical declarations or inference from the newest directory name. |
| [Paperclip runner README](../../../../product/lab/release-candidates/v1/interface/paperclip-runner-v3/README.md) and [public technical closure](../../../plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/paperclip-local-pilot-0270/closure.json) | The frozen runner says Paperclip is not installed; the later public episode records local setup and process execution. That episode explicitly leaves human usefulness unobserved. A dated integration overview can reconcile these facts without claiming current server health or a completed human pilot. |

The admitted CLI foundation, expanded 34-operation API families, schema proposal, candidate release, and Paperclip adapter must not be flattened into one unnamed “runtime.” Likewise, the machine-readable catalog’s declared 34 operations is not a qualification result.

## Information architecture and audiences

Use the four Diátaxis forms to answer distinct needs: guided learning, accomplishing a task, exact lookup and understanding. Separate these forms within the existing subject navigation instead of creating four empty documentation silos. Reference should reflect the actual machinery; tutorials should teach through a bounded experience. [Diátaxis primer](https://www.diataxis.fr/start-here/)

| Audience | Immediate question | Entry and completion criterion |
| --- | --- | --- |
| Repository user | What can I inspect, and which answer applies? | Runtime overview → first read tutorial → status/cut explanation. The reader can identify an exact record, its standing and its evidence. |
| Operator | How do I select a version, provision a bounded branch, recover or revoke access? | Task-specific how-to → exact profile/authority/recovery reference. The operator knows expected results, refusal conditions and residue. |
| Integrator/developer | How do I call the interface and extend or test it correctly? | API reference → transport/authentication explanation → isolated examples and conformance instructions. The developer binds the exact producer/profile and handles declared errors and uncertainty. |
| Reviewer | Which claim is supported, by which bytes and observations? | Current status → version-specific evidence index → original receipts and decisions. The reviewer distinguishes implementation, scoped verification, admission, activation and human value. |

Keep authority, provenance and lifecycle explanations canonical in the existing guide. Runtime pages link to those chapters and explain only the additional operational mechanics. Keep the fictional incident and genuine recorded episodes clearly identified; neither should silently become the other.

### Practical draft table of contents

Placement respects the current sidebar: Getting started, Governance, The Lab model, Practical guides, Software design, Expanded essays, Reference, About CyberAlchemy.

| Page/topic | Form and existing sidebar placement | Proposed repository mirror |
| --- | --- | --- |
| Runtime overview: choose the interface and version | Getting started; short audience routes | `docs/lab/runtime/README.md` |
| First inspection: status, catalog, one record, one connection | Tutorial under Practical guides; read-only, no key/store initialization | `docs/lab/tutorials/first-runtime-read.md` |
| Prepare and review one change in a disposable branch | Separate tutorial; explicit local authority and cleanup | `docs/lab/tutorials/local-runtime-change.md` |
| Select a source/profile and diagnose drift | Operator how-to under Using the runtime | `docs/lab/how-to/select-runtime-profile.md` |
| Provision an isolated store and operator | Operator how-to; exact selected version | `docs/lab/how-to/provision-local-runtime.md` |
| Replay and recover after interruption | Operator how-to; reconcile before uncertain retry | `docs/lab/how-to/recover-runtime.md` |
| Open, close and reconstruct an agent session | How-to; complement existing resume-agent-work | `docs/lab/how-to/use-runtime-session.md` |
| Run bounded Lab reads through Paperclip | Integrator how-to; direct runner then process-agent episode | `docs/lab/how-to/run-lab-from-paperclip.md` |
| Runtime architecture: source, canonical store, projections and ephemeral sessions | Explanation, linked from Lab model/system map | `docs/lab/runtime/architecture.md` |
| Runtime/source/release status and compatibility | Reference; reachable from Source & status | `docs/lab/runtime/status.md` |
| CLI commands and exact limits | Runtime reference; selected implementation’s argument definitions | `docs/lab/reference/runtime-cli.md` |
| API request/result/error contracts and source bindings | Runtime reference; grouped by actual operation families | `docs/lab/reference/runtime-api.md` |
| Authentication, policy scope, source cut, cursors and error/retry semantics | Runtime reference plus focused explanation links | `docs/lab/reference/runtime-transport.md` |
| Installation, upgrade, rollback and verification | Operator reference/how-to with actual supported environment | `docs/lab/how-to/install-and-upgrade-runtime.md` |

These are proposed destinations, not files created by this research. Start with overview, first read, status and exact interface reference; add later pages when their selected recipes can actually be verified. Do not present disposable examples as production provisioning or manufacture missing human outcome evidence.

## Ownership and rendering strategy

Retain the site-first workflow for these new pages. The Markdown edition is a reviewed projection, with its directly maintained indexes retained. The proposed maintained sources and integration points are explicit:

| Content responsibility | Maintained source or proposed destination | Derived output |
| --- | --- | --- |
| Enduring concepts and existing governance explanation | Existing guide templates and `website/source/governance-lab-series/reference_reading.py`; original authority records remain normative | Existing guide/reference pages and imported Markdown |
| Runtime page structure | **Proposed** `website/source/governance-lab-series/templates/runtime-overview.html.in`, `runtime-read-tutorial.html.in`, `runtime-how-to.html.in`, `runtime-reference.html.in` | Portable `governance-lab-series/runtime-*.html` pages |
| Runtime composition and typed data binding | **Proposed** `website/source/governance-lab-series/runtime_docs.py`, called by the existing `render_article.py` | Shared shell, links, selected reference tables and documentation manifest |
| Approved explanatory runtime passages | Existing `website/editorial-copy.json`; new entries use the existing original/editorial/link-label mechanism | Editorial HTML pass; no change to exact contracts, examples or protected bodies |
| Version/interface selection and public status facts | **Proposed** `website/source/governance-lab-series/research/runtime-selection.json` and generated `runtime-status.json`; exact evidence refs, not heuristics | Status cards, compatibility table and evidence index |
| Actual CLI/protocol facts | Selected `implementation/lab-runtime/<version>/CONTRACT.md`, schemas/argument definitions; selected API family’s `contract-profile.json` and bound operation schemas | Generated reference facts with producer/version/schema identities; explanations remain reviewed prose |
| Website sidebar and topic order | Existing `website/source/governance-lab-series/assets/site-search.js` core groups plus static guide/start templates | Consistent desktop/compact navigation; one canonical route per topic |
| Search vocabulary and judgment destinations | Existing `search_vocabulary.json`, `search_relevance.py`, `research/search-judgments.json`, `build_site_search.py` | Search generated after final editorial pages; independent expected destinations |
| Repository mirror routes | Existing `tooling/docs/import_site_docs.py`; extend its explicit HTML/anchor-to-Markdown mapping | Proposed mirrors in the table above and `docs/lab/IMPORT-MANIFEST.json` |
| Reader indexes and contribution instructions | Existing `docs/lab/README.md`, `docs/lab/reference/README.md`, `docs/lab/MAINTENANCE.md`, root `README.md` | Thin entry points linking to the maintained edition and exact frozen packages |

Do not edit `website/dist` or imported `docs/lab` paragraphs as parallel authoring sources. Do not create a second runtime website or copy an entire README into several how-to pages. Reuse a command/example source once, wrap it with audience-specific guidance, and link to deeper contracts. Preserve stable routes and redirect retired routes; redirects should not become duplicate search hits.

Follow the existing pipeline: maintained templates/data → examples and rendering in isolated stage → editorial pass → final presentation/reference shell → search → structural/body-preservation checks → deterministic packaging → reviewed Markdown import. The website build alone must continue to neither refresh the source capture nor import Markdown silently.

Docs-as-code supports shared version control, review and automated checks; the local recommendation is to strengthen this existing workflow, not introduce a platform migration. [Write the Docs](https://www.writethedocs.org/guide/docs-as-code/)

## Current status without damaging frozen evidence

A current page needs a **selected evidence basis**, not a timeless claim. Its public selection should identify:

- runtime family and exact version; documentation revision and source-capture date;
- selected implementation/source/profile bindings and compatibility constraints;
- effective implementation admission, separately from the source body’s domain lifecycle;
- exact scoped qualification evidence and counterevidence; uncertainty remains explicit;
- repository State selection versus the executable’s frozen State/profile versus an independently provisioned local store;
- release/publication standing from its exact reviewed decision and selected release artifacts;
- public operational observations with observation time and scope; live availability is unknown unless separately observed;
- evidence/review date and the next explicit review trigger.

“Admitted v1, executing its frozen D74 foundation; repository selection D75” is more useful than a blanket candidate badge. “Local Paperclip process episode observed on 13 October; human usefulness not established by that technical record” is more accurate than inheriting “not installed” from its earlier package. These are examples of presentation logic, not refreshed observations of a live instance.

Show a small status panel on the runtime front door and Source & status page. Give captured guide/reference pages a clear **source edition** label, and a link to the maintained runtime status. Keep the enduring Start here page free of changing test counts, as its existing maintenance instructions require. Show full digests and detailed receipts in reference disclosures, not every task paragraph.

The projection must not select the newest directory, largest operation count, file modification time or a historical README sentence as current authority. A maintainer selects exact public inputs; a deterministic validator checks their bindings. If a selected receipt is missing, conflicts, belongs to another producer/profile, or lacks its required terminal/cleanup evidence, display unknown or a scoped failure. Do not silently carry predecessor qualification across families. No build should change admission or release standing.

### Pinned Paperclip integration contract

The recorded integration used published **2026.1005.0**. Its inspected process adapter accepts an executable `command`, separate `args`, working directory and timeout, with direct process spawning rather than a shell recipe. The [published adapter probe](../../../plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/Paperclip-process-adapter-probe-0140.json) and its bound launcher/package inputs are the authority for that recorded contract. Upstream master currently describes a shell-command string, so its example is not interchangeable with those pinned executable/argument bytes. A later version needs its own compatibility review.

Keep Paperclip orchestration credentials separate from Lab authority: Paperclip IDs/tokens supply correlation, while a separately provisioned Lab policy/key and actual nonce proof establish the allowed read channel. Document credential custody using illustrative placeholders, never private files, DBs, server logs or real secrets. A recorded bounded read episode does not establish permanent service availability, unrestricted Lab actions, runtime admission or human benefit. The upstream adapter documentation is useful conceptual context, subject to its version: [official process-adapter source](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/process.md).

## Automation and acceptance checks for a later implementation

Extend the existing checks rather than replacing the renderer. Suggested checks:

1. **Selection/freshness:** exact runtime/source/profile/schema/evidence bindings; admission/capture/release facts displayed separately; conflicting or missing evidence fails explicitly. Verify no frozen “not installed/not collected/candidate” sentence is used as an unqualified current-status summary.
2. **Single source and preservation:** selected reference bodies, formal statements, code blocks and approved examples keep their existing preservation checks. Import drift is detectable; directly maintained indexes are exempt from replacement.
3. **Routes and portability:** all new local links/fragments resolve; support file origin and project subpaths; no absolute personal paths or private source inventories are bundled. Add explicit importer mappings and review unresolved references.
4. **Search:** independently specified queries include “run the Lab,” “runtime status,” “recover after interruption,” “source profile,” “session expires” and “Paperclip.” Expected destinations must be authored before ranking results are inspected. Search runs after adopted prose; archived copies and redirects do not compete with current instructions.
5. **Recipes:** read-only examples run against the selected implementation in controlled checks; effectful examples use disposable owned stores and separately scoped test keys. Verify results and causal refusals, not merely command exit or envelope shape. A docs CI job must not contact a live Lab/Paperclip service or reuse operator credentials.
6. **Change impact:** require a documentation assessment when CLI arguments, protocol/schema/profile selection, error semantics, installation or release selection change. Review current-status selection when admission/qualification evidence changes; a prose edit does not refresh an authority snapshot.

A proposed validation workflow can run on pull requests affecting these maintained inputs and on explicit refresh; publishing stays separate from validation and retains the existing manual deployment posture. GitHub provides event/path-filtered and manually dispatched workflows, which can express that separation. This brief does not add a workflow or publish anything. [GitHub workflow triggers](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)

Success is observable when an unfamiliar reader can find the supported interface, inspect one exact record, explain its standing/source cut and reach recovery or Paperclip instructions without treating frozen package notices as live status. Reviewer acceptance should separately check user, operator and developer journeys. Automated links and source hashes cannot prove comprehension.

## Suggested implementation order and open decisions

1. Select the documentation’s current runtime/version/evidence basis; retain all historical package notices and qualify the present reading routes.
2. Draft runtime overview, status and first read; review them with one reader from each audience.
3. Add generated CLI/API reference and the four highest-demand how-to routes; extend sidebar, independent search judgments and importer mapping.
4. Add isolated recipe checks and selection/change-impact checks; build and import only in a separately authorized implementation task.
5. Review the exact website/Markdown edition and portability results before deployment.

Decisions still needed: which runtime family is the primary supported interface; which exact release/qualification facts belong in the public selection; who maintains that selector; which effectful recipes are supported within the actual local environment; and how public status review dates should be refreshed. The renderer choice need not block drafting: reuse the current website and its source ownership first.

No website build, renderer, importer, live API, credentials or deployment was invoked for this research. The sole authored artifact is this file. External sources above informed the architecture; repository observations and the proposed design are distinguished throughout. The ARE authoring boundary is non-authorizing and applies only to writing this requested research file; it supplies no runtime or publication approval.

