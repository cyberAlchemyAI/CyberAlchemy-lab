# Documenting the implemented Lab runtime

Status: **documentation proposal for review**. Research date: **13 October 2026**. This package proposes documentation work; it changes no runtime, admission, permission, installation or release state.

## Recommendation

Add an **Operate the Lab** section to the existing documentation and website. Give readers a clear starting point, a practical operator handbook, an explanation of the implemented architecture, and an API reference generated from the selected contracts. Put a dated runtime and evidence summary alongside these pages.

The existing model guide should remain the explanation of what the Lab means. The new section should explain what its software does, which implementation to select, how to use it, and what to do when a request fails. A reader should be able to move from a concept to its implementation and an observed example without searching a construction run directory.

Reuse the repository's existing website, search, editorial style and Markdown import. The proposal introduces a new documentation section rather than a second documentation platform.

## The problem the research found

The Lab has an admitted local runtime and extensive candidate integration code. Documentation already exists for its model, the v1/v2 command line, the schema/API designs, individual implementation packages and construction evidence. Those sources describe different versions and scopes, and no single operator route brings them together.

Several preserved statements can confuse a reader. The admitted v1 package still has its original candidate-era README; the integrated API contract proposal correctly describes its own authoring-only scope even though handlers now exist elsewhere; API16's copied DESIGN still says “successor 14” and “unfrozen”; the Paperclip runner's earlier README predates the verified local installation. These historical files should remain intact. A maintained front door should explain their standing and link the independent admission and execution evidence.

The documentation also needs to explain practical boundaries that are easy to miss in a list of capabilities: the base reader adapter and the composite dispatcher expose different surfaces; actions and governance require separate authenticated channels; an API result can report a denial or blocked domain posture; expired permission cannot be restored by replaying metadata; and a working adapter does not establish a completed human task.

## What exists at the research cut

| Surface | Implemented behavior and evidence | Standing to show readers |
| --- | --- | --- |
| Local runtime v1 | Source-bound inspection, exact signed local transactions, replay/recovery and ephemeral context. Decision 0075 admits its exact local scope. It reads its frozen D74 foundation. | Admitted implementation; local provisioning and activation are separate facts. |
| Local runtime v2 | The source-profile successor reads D75 and retains the v1 interface. Its implementation and validation are separately selected. | Candidate successor. |
| Integrated API16 | A frozen common candidate with 34 declared operation contracts and separately selected services/members. | Implemented candidate, with incomplete final qualification. |
| API16 regression evidence | All 345 declared cases have retained reports: 342 PASS, two FAIL and one ERROR. | A failing complete regression run, not release acceptance. |
| API16 common-call evidence | Twenty-two passing units contain positive and refusal evidence for 27 of 34 operations. The remaining grouped session/lesson lifetime failed. | Partial wire qualification. The seven remaining operations have different degrees of partial evidence; they are not all absent implementations. |
| Paperclip integration | The pinned 2026.1005.0 local process adapter ran the Lab reader successfully. It performed three authenticated reads of preserved W09 engineering history. | Observed read-only integration; no human usefulness or engineering action execution established. The recorded grant expired at 06:00:59 UTC on 13 October. |
| Define, Craft and ontology lifecycle | Adjacent implemented tools and separately scoped models, compiler paths and event/representation runtimes. | Document their integration points and individual standing; their presence does not establish complete composite Lab operation. |

Final release preparation also remains incomplete: package target/representation closure, actual governing owner-role evidence, the exact mixed-member publisher closure, the final-family privacy review and genuine human pilot are still separate requirements. The remaining work is broader than the three regression cases. Documentation should expose these limits while explaining the useful implemented paths.

The sources and detailed qualifications are in [the research index](RESEARCH.md), [the evidence audit](research/runtime-evidence.md), and [the exact source selection](sources.json). A read-only v1 `status` invocation was also checked during this research: it exited 0, selected D74, and created no local store. This is an inspection check, not a new transaction or activation test.

## Who the documentation must serve

| Reader | Main question | Successful outcome |
| --- | --- | --- |
| New user or project owner | What does this runtime let me do today? | Selects a usable entry point and distinguishes available behavior from an unfinished journey. |
| Operator | How do I start, provision, inspect, review, recover and stop it? | Follows a bounded procedure with explicit prerequisites, expected output, effects and recovery steps. |
| Agent/integration author | How do I call the Lab through a tool or Paperclip? | Selects the correct implementation, source/profile, channel, operation contracts and retry rules. |
| Runtime contributor | Where is a behavior implemented and how is it verified? | Traces an operation through dispatch, guards, services, storage and source-bound evidence. |
| Reviewer | What proves the capability and what remains unknown? | Can inspect exact versioned evidence and distinguish tests, actual operation and human outcomes. |

## Proposed reading structure

Use tutorials for guided learning, how-to pages for a specific task, explanation for architecture and reasoning, and reference for exact contracts. This follows the reader-needs distinction described by [Diátaxis](https://diataxis.fr/). It is an information architecture choice, not a change to Lab governance.

### Start and current scope

The front door should answer, in this order:

1. What the software is and the outcome a reader can achieve.
2. Which interface to use: admitted local CLI, candidate source-profile CLI, candidate integrated API, or the bounded Paperclip reader.
3. What the selected implementation reads and may change.
4. The first useful read-only action and what its output means.
5. Where to continue for a particular task, with a visible current limitation when that task is not qualified.

Keep the ordinary page concise. Version hashes, exact manifests and proof selections belong in a source-details section and the technical reference, while admission, currentness and permission remain visible next to the relevant action.

### Operator handbook and tutorials

The operator pages should cover environment checks; inspection without a store; explicitly owned local branch/key provisioning; candidate preparation and review; exact authorization and application; fresh context/session creation and disposal; uncertainty and recovery; rebuilding projections; importing/exporting selected bytes; and local installation/upgrade/rollback boundaries.

Start with one reliable read-only tutorial. Add an isolated local Work transaction tutorial only when its documented environment, new workspace, authorization and cleanup have a replayable witness. Treat the complete integrated session/lesson journey as a documented limitation until its selected runtime passes that journey. Explain its intended sequence in the architecture section without presenting it as a reliable quickstart.

Every procedure should declare the selected version, prerequisites, whether it creates or changes anything, expected result, common refusals, evidence produced and how to finish or recover. Use realistic, clearly identified examples; private keys, live credentials and session RAM should never appear in downloadable examples.

### Architecture explanation

Explain the implemented layers, with links to code symbols:

- Repository authority and source/profile selection.
- Local CLI, authenticated reader transport and composite API dispatch.
- Context, assignment eligibility, temporary sessions, Machine peers and disposal.
- Candidate workspaces, operation journals and idempotency.
- Engineering, research, workflow, classification, failures, challenges and learning.
- Native transaction/state/history machinery and publisher recovery.
- Ontology representation, SQLite generations and managed exports, each with its own source cut and effect boundary.
- Review/checkpoint, actual owner evidence, admission, adoption, release and installation.
- Define, Craft and Paperclip adapters as separately scoped integrations.

Include five diagrams: a component map; a read/authentication sequence; a candidate-to-commit sequence; a session/memory lifetime; and recovery after an uncertain effect. Diagrams should show which component owns a state or guard. A dotted connection should identify an intended or unqualified complete journey rather than imply a running service.

### Technical reference

Generate an index and one page per declared API operation from `api-contracts.json` and its bound schemas. Each page should include request/result/error contracts, allowed effects, channel/identity prerequisites, source cuts, budgets, idempotency, recovery and completion rules. Link implementation and actual positive/refusal evidence separately from illustrative contract examples.

Add a CLI command reference, implementation/component map, configuration/environment reference, source/profile selection guide, and glossary of runtime-specific terms. Reuse the existing Definition library for meanings; do not create competing semantic definitions in runtime prose.

The 34 operation pages may all be generated before all 34 operations are fully qualified. Their per-version implementation/evidence labels must make that distinction explicit.

## Proposed pages

The full page map, source responsibilities and acceptance criteria are in [CONTENTS.md](CONTENTS.md). The initial scope is 14 maintained runtime pages plus a generated operation index and 34 operation pages. Existing conceptual, Craft and Definition pages remain reusable destinations.

[PREVIEW.md](PREVIEW.md) demonstrates the proposed first page and its tone. It is a review sample inside this proposal, not a newly published operator guide.

## Source and publication design

Maintain new runtime narrative under the existing website source tree in a dedicated runtime section. Feed the current editorial stage, then the final shared search and preservation checks. Extend the Markdown importer to emit the same maintained runtime pages under `docs/lab/runtime/`. Preserve the direct Markdown indexes as the documented exception already used by the repository.

Generate API reference content from a deliberately selected, hash-bound contract catalog and schema inputs. Generate the evidence summary from a reviewed source/evidence selection. Do not discover a default implementation by the largest `api-vN` filename or reuse an old test total as evidence for new bytes.

The selected schema below is a design for that summary, not an existing runtime API:

```text
implementation identity and version
source/profile and evidence-selection bindings
source snapshot and documentation capture date
effective admission and its decision reference
observed activation/provisioning scope and observation time
tested operations and actual positive/refusal coverage
complete-run failures and unresolved paths
human-use observations, including missing outcomes
environment and protected/nonportable dependency limits
```

Treat these as independent facts. A generator should validate links/digests and report stale or missing evidence, not infer authority, activation or user benefit from filenames, JSON body labels or successful replies.

The 8 October reference capture and the 12 October prose edition should keep their identities. A new runtime research cut is a separately identified selection. Updating runtime documentation should not silently refresh the formal reference catalog or alter preserved definitions, schemas, decisions or historical runtime packages.

## Delivery order

| Phase | Deliverable | Required acceptance |
| --- | --- | --- |
| 1 — Orientation | Runtime front door, implementation selector, dated scope/evidence summary and the read-only tutorial. | Reader can choose v1/v2/API/Paperclip, inspect selected foundation, and identify what is unavailable without searching execution logs. |
| 2 — Operation | Provisioning/review/authorization, session boundaries, recovery and Paperclip how-to pages. | Commands verified in owned isolated environments; version/effect/prerequisites and negative outcomes are explicit. Unqualified paths remain marked unavailable. |
| 3 — Architecture/reference | Component and sequence diagrams, contributor guide, generated 34-operation reference and exact evidence links. | Every declared operation has a page and an honest per-version evidence row; every architecture responsibility has an implementation or declared gap. |
| 4 — Site and maintenance | Shared navigation/search, Markdown import, portability and freshness checks. | HTML/Markdown content parity, valid links, mobile/readable diagrams, preserved canonical records and reviewed public-safe examples. |

These are proposed delivery slices, not an execution-ready runtime work-pack or approval to repair the implementation. Runtime fixes and their new evidence belong to the runtime's existing lifecycle; documentation can proceed for verified surfaces while those fixes remain open.

## Definition of done for the documentation

- A new reader can locate and perform the selected read-only task using the documentation alone.
- An operator can identify where data and keys belong, what a command changes, who authorizes it, and what to inspect after uncertainty.
- All 34 declared API operations are mapped to their contracts, implementation and correctly scoped evidence or a visible gap.
- The documentation distinguishes v1's D74 profile, v2's D75 profile, integrated candidate versions, controlled fixtures and actual Paperclip history reads.
- The three current regression problems and failed session/lesson journey remain visible until new exact evidence replaces their current status selection.
- Examples do not claim that all requests returning `result` completed their intended work; result postures and effect receipts are explained.
- One maintained source feeds the new HTML and imported Markdown narrative; links, generated reference, search and diagram text are checked.
- Private credentials, live databases, process RAM and protected construction payloads stay outside public examples and documentation packaging.
- A real first-time reader completes the tutorial and reports confusion/usefulness. That checks documentation usability, independently of the larger Lab Product pilot.
- Publication occurs through a separately selected documentation delivery step; this proposal itself publishes nothing.

## Choices and unresolved decisions

Recommended: add the runtime section to the existing site, use the existing editorial/import pipeline, and publish verified subsets with explicit limitations. Updating only a frozen package README would not solve navigation or version/evidence selection. Starting another site would duplicate the current rendering/search/import responsibilities.

The implementation phase still needs to select the exact evidence-summary format, the qualified environment for each tutorial, which candidate procedures are internal-only, and the documentation maintainer. An unqualified full session/lesson tutorial and a general Paperclip engineering-task tutorial remain gated by actual runtime/integration evidence. These gaps do not prevent documenting the admitted inspection path or the implemented architecture now.

Next action after review: implement Phase 1 in the existing documentation pipeline, then verify it with a new reader before expanding the operator/reference sections.
