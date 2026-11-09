# Reusable architecture patterns

Six concept cards and four relationship cards extracted or proposed from the
review. Each card labels observed behavior, recommendations and known gaps.

## Choose a small reading pack

| Task | Concept cards | Relationship cards |
| --- | --- | --- |
| Stable reads for agents | Fixed input and scope | Store to fixed input |
| Better agent context | Purpose-preserving views | Source to agent view |
| Review a proposed change | Semantic change preview; evidence-carrying results | Result to checker |
| Bring in new data | Hypothesis and loss ledger | Lab to analysis report |
| Strengthen evidence checks | Non-vacuous verification; evidence-carrying results | Result to checker |

## Concepts

| Card | Area | Purpose |
| --- | --- | --- |
| [One fixed input for a run](pattern-library/concepts/fixed-input-and-scope.md) | Graph selection and reasoning | Keep an answer about one selected dataset even while other callers change the live graph. |
| [A result label needs checked evidence](pattern-library/concepts/evidence-carrying-results.md) | Result and checker boundary | Make an unchecked result harder to mistake for a checked one. |
| [Check what a smaller view loses](pattern-library/concepts/purpose-preserving-views.md) | Context selection and reasoning | Give an agent less material while checking that the claims its task needs remain supported. |
| [Preview consequences of a change](pattern-library/concepts/semantic-change-preview.md) | Ontology change analysis | Show when a small graph edit changes many conclusions about existing terms. |
| [Keep interpretation and missing meaning visible](pattern-library/concepts/hypothesis-and-loss-ledger.md) | Data intake and model translation | Make generated schemas and translated meanings reviewable instead of silently declaring them true or complete. |
| [Check that checks really ran](pattern-library/concepts/non-vacuous-verification.md) | Testing and CI evidence | Prevent a green job caused by missing tools, skipped cases or an empty comparison. |

## Relationships

| Card | Direction |
| --- | --- |
| [Live store to fixed reasoning input](pattern-library/relationships/store-to-fixed-input.md) | GraphStore and explicit scope -> Owned input for reasoning and evidence |
| [Engine result to independently checked evidence](pattern-library/relationships/result-to-checker.md) | Search/reasoning/solver result -> Separate checker and scoped verdict |
| [Selected source to a task view](pattern-library/relationships/source-to-agent-view.md) | Source ontology and task claims -> Smaller projection and per-claim support report |
| [Lab history to an optional analytical report](pattern-library/relationships/lab-to-analysis-report.md) | Exact Lab ontology cut and review references -> Disposable RDF view and inert returned evidence |

Load only the relevant cards, then the dependency and testing guides.
Source counts, exact files and symbols are in the [inventory](pattern-library/inventory/README.md).
These patterns do not change the Lab architecture or admit a dependency.
