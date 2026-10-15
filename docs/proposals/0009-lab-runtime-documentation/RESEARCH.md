# Research brief: Lab runtime documentation

Status: **source-backed proposal research completed for the declared scope**. Updated: 13 October 2026. Authority effect: none. Documentation implementation, runtime repair and publication are separate later work.

## Objective and method

Determine how to explain and operate the implemented Lab software without conflating the model, a candidate contract, an admitted implementation, a provisioned instance, a passing fixture or an observed human outcome.

The research inspected the documentation/website pipeline, all ten `implementation/lab-*` areas, the admitted v1 and candidate v2 profiles, the latest selected frozen integrated API16, the 34-operation contract catalog, retained execution and release evidence, and the Define/Craft/ontology/Paperclip integration boundaries. Historical families were selected when needed to explain a dependency, conflicting status notice or failure; every archived candidate file was not independently re-audited.

Three independent audits cover [runtime architecture](research/runtime-architecture.md), [evidence and operation](research/runtime-evidence.md), and [documentation ownership and publishing](research/documentation-system.md). Exact selected source files and hashes are in [sources.json](sources.json). External sources contribute documentation organization and adapter background, not proof of Lab behavior.

One bounded read-only command was executed: admitted v1 `status` with an explicitly nonexistent `/tmp` store. It exited 0 and created no store. [The command observation](research/read-only-command-observation.json) records its exact arguments and output. Existing runtime suites were not rerun, no live stores or private credentials were inspected, and no runtime code or existing docs were changed.

## Questions answered

| Question | Finding and documentation consequence | Evidence |
| --- | --- | --- |
| What software has actually been built? | Ten Lab implementation areas supply native state/history, context, ontology, provisioning/bootstrap, review, work/workflows and continuity. The larger API composes independently scoped services. Document their implemented responsibilities and entrypoints. | Architecture audit, sections 2–5. |
| Which runtime should a user choose? | v1 is admitted by Decision0075 and reads D74; v2 is a D75 candidate; API16 is a separately frozen integrated candidate; Paperclip's recorded reader used API14/history. A runtime chooser is necessary. | Admission overlay, profiles, current State lookup and evidence audit. |
| Is the integrated runtime finished? | No. The retained API16 run has 342 PASS/two FAIL/one ERROR; common positive/refusal reports cover27/34; the complete grouped session/lesson lifetime failed at expiry. Final package/owner/privacy/human gates also remain open. | Evidence audit, sections 1–2 and 5. |
| What can be the first reliable documentation task? | Read-only foundation inspection needs no key/store provisioning and worked during this research. Start with that tutorial and its profile/cut interpretation. | Current read-only command observation; v1 operator guide. |
| How does an integration reach all34 operations? | `serve.py` constructs the base28 reader service. The composite dispatcher adds independent three-operation Action and Governance branches; actual channels and grants must exist. No universal 34-operation stdio launch recipe is established by the catalog. | Architecture audit, section3; evidence audit, section3. |
| How should users handle changes and uncertainty? | Separate preparation, review, exact authorization, commit and independent derived effects. Preserve operation keys/history; inspect/reconcile uncertain effects; never infer no effect from timeout. Session RAM is not a replay source. | Native store/publisher, API policies, workspace journal and recovery evidence. |
| How should the new docs be maintained? | Extend the existing maintained site source → rendering/editorial → final search/checks → packaging, with a separately reviewed Markdown import. Generate contract reference and a deliberately selected evidence summary. | Documentation-system audit and existing MAINTENANCE/build/import code. |

## Major documentation gaps

1. **Runtime selection and scope:** one front door that distinguishes version, foundation, source, effective admission and observed operation.
2. **A complete implementation map:** concept-to-code links and the actual data/control flow, including independent stores and commit points.
3. **Task instructions:** environment/preflight, inspection, owned provisioning, exact review/authorization, sessions/disposal, uncertainty/recovery, selected packages and integrations.
4. **Transport and authority:** real channel/nonce/policy versus public Actor claims; base/composite dispatch; budgets, keys, postures and current cuts.
5. **Evidence presentation:** whole-run failures, partial paths, fixtures, historical work, expired permission, public/private dependencies and missing human outcomes.
6. **Maintained references:** selected CLI arguments, generated operation pages and change-impact checks rather than duplicated prose or edited frozen READMEs.

## Options considered

| Option | Value | Limit/cost | Recommendation |
| --- | --- | --- | --- |
| Only expand a runtime README | Fast local clarification. | Does not solve cross-version selection, shared search, learning path, API reference or website/Markdown consistency; frozen package bytes cannot simply be rewritten. | Use thin package pointers where appropriate, not as the complete solution. |
| Create another standalone documentation site | New independent structure. | Adds rendering/navigation/search/maintenance and duplicates a working site/import system. | Do not select for this scope. |
| Add a maintained runtime section to the existing docs | Shared navigation, presentation, search and preserved source boundaries; practical and technical material can grow together. | Requires a runtime renderer, deliberate evidence selection and importer/search mappings. | Recommended. |

## Source authority and external research

Prefer, in order: exact admission/decision and current State records for authority; actual implementation/selected profiles for behavior; exact bound execution reports for observed results; contract catalogs for declared interfaces; maintained docs for their chosen explanatory edition. Disagreements become an explained version/scope difference or a visible gap, not a reason to replace original history.

- [Diátaxis](https://diataxis.fr/) distinguishes tutorials, task guides, reference and explanation. Its [tutorial guidance](https://diataxis.fr/tutorials/) supports a concrete, reliable first task with visible expected output and user observation. Its [how-to guidance](https://diataxis.fr/how-to-guides/) supports focused operational procedures. The proposed Lab page map is this proposal's application of those ideas.
- [Write the Docs: docs as code](https://www.writethedocs.org/guide/docs-as-code/) provides background for version control, review and automated checking; the repository already has the concrete build/import mechanisms to reuse.
- [Official Paperclip process-adapter documentation](https://github.com/paperclipai/paperclip/blob/master/docs/adapters/process.md) explains its process-oriented role. Its moving master examples are not the configuration authority for the inspected2026.1005.0 executable-plus-args adapter and actual Lab episode. The local pinned code and receipts remain the evidence for that version.

## Decisions proposed, not yet adopted

Use the existing website pipeline; add **Operate the Lab**; maintain one narrative source with an imported repository mirror; generate the34-operation reference; select status/evidence by exact version and scope; start with verified read-only inspection; and keep blocked complete journeys visible until new exact observations qualify them.

Remaining implementation choices include maintainer ownership, exact runtime renderer/layout, machine-readable evidence-selection format, reproducible environments for effectful examples and internal-only procedures. The proposal's [page map](CONTENTS.md), [sample opening](PREVIEW.md), and [acceptance/delivery outline](PROPOSAL.md) make those choices reviewable.

## Workflow provenance

The current ARE research route permits `local-read` and `draft` for the explicitly requested proposal; its receipts are non-authorizing. The Arcanum context/research-brief components informed source selection and question mapping. The installed Invoke root references define/design mode contracts absent from its installed package and the searched sibling capability source. No complete Invoke define/design/plan run or execution-ready work-pack is claimed. This tooling limitation did not prevent the directly authorized source research and proposal drafting.

Next owner: documentation authoring/maintenance after proposal review. Runtime failures remain owned by the runtime's existing work, and final admission/release remain on their actual owner routes.
