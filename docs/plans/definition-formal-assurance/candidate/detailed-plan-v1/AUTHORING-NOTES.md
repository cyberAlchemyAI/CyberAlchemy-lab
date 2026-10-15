# Authoring provenance and open gates

Observed capability: Invoke-inspired candidate design/plan authoring. Target: Definition Formal Assurance, project-local analysis and detailed DAG. Complexity: high. Output: split Work Pack with 112 task pages and shared JSON plan/unit manifest. Current request: analysis and planning only. Authority effect: none.

## Skill and template fit

- Installed root: `/mnt/c/Users/vlad_/.codex/skills/invoke/SKILL.md`.
- Its installation lacks the linked `design.md`/`plan.md`; the current canonical contracts were read at `/home/vlad_/projects/domainspec-core/arcanum/spells/invoke/design.md` and `plan.md`.
- Normal producer-backed Invoke Design/Plan inputs and admissions are absent in this project. No stage/admission receipt is manufactured. Direct candidate planning satisfies the user's explicit request without claiming normal Invoke admission or executing implementation.
- The current Plan contract treats JSON as canonical. The older Work Pack template is used only for task/SWU/scope/validation navigation; it does not override that ownership rule.
- Implementation Layering was read at `/mnt/c/Users/vlad_/.codex/skills/implementation-layering/SKILL.md`. Four decision layers and per-layer slices are documented.

The authoring recipe in `build_plan.py` records the initial source-bound partition and task generation. `dag.json` and `swu-manifest.json` own the delivered planning decisions; task pages, DAG, queue and Work Pack are human views. Future revisions should produce a new candidate package and regenerated views. Do not silently rerun the initial recipe over later hand-edited planning decisions.

## Gate status

| Gate | Status | Meaning |
| --- | --- | --- |
| Direct authorization for candidate analysis/planning | Present | User explicitly requested complete analysis and detailed DAG |
| Structural graph/source/SWU validation | See planning-validation.json | Actual planning checks only |
| Normal Invoke Define/Design/Plan producer/admission | Not run / prerequisites absent | No claim of producer-backed canonical artifact admission |
| Future implementation readiness | Not run | Candidate SWUs have planned output/verification contracts, not actual produced implementation |
| Semantic fidelity and provider-strength choices | Pending future tasks | Reviewable candidates/clauses/examples must precede real owner decisions |
| Owner semantic admission | Not requested by this planning instruction | H03 remains conditional on later exact selected effects |

## Scope and coordination

All present writes are inside `docs/plans/definition-formal-assurance/candidate/detailed-plan-v1/`. The initial source baseline, existing D0–D2 package, canonical registries/definitions/admissions, frozen schemas, historical Lean sources and unrelated dirty work are preserved. Cross-project runtime/Craft interfaces were read for fit, not changed. No subagents were spawned.

No repository-local Invoke observability package was present. Planning inputs, algorithm/decision notes, structural validation and the exact package manifest form the scoped authoring record. Reusable-sigil experiment validation is not applicable. A failed or pending semantic gate is recorded in the actual future unit, not simulated by a planning label.
