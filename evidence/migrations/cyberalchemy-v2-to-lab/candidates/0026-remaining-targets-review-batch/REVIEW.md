# Review the remaining 83 candidates

83 missing targets -> bounded implementations -> passing checks -> your adoption review.

All 83 requested targets are constructed as candidates: 26 Artifact Types, 25 profiles, 25 relation kinds and 7 derived views. The original ledger is now 13 admitted + 182 constructed candidates = 195, with zero scaffold-only targets. Construction is complete for this bounded reconstruction; admission and production integration are separate.

Start with [the searchable local review page](REVIEW.html), or use the target table below. Each entry links to its exact contract, examples, implemented checks and limits. [Validation](receipts/validation.json) and [per-target results](receipts/target-validation.json) bind the tested scope. The entire batch is snapshotted by manifest.json.

What you would approve:

- Artifact Types -> use the exact fields and reference rules for a named purpose.
- Profiles -> use the proposed states, criteria, limits and routing rules. The displayed parameters are new proposals, not inherited approval.
- Relation kinds -> use the specified direction, endpoint types and evidence requirements.
- Derived views -> use the selected source data and projection rules for navigation, with no authority granted by the view.

Your earlier instruction authorized construction and testing. This package contains no adoption decisions and does not publish, deploy, delete records, authenticate people or retire the sibling source repository.

## Boundaries worth reviewing first

- The 51-node, 25-edge integration graph is illustrative. Twenty-three support nodes are explicitly fixture-only placeholders for earlier record kinds; they do not prove real runs, receipts, people or grants. The 28 native records include two additional identity examples.
- Exact file hashes protect graph membership. Reference consistency does not prove that observations are true, owners are authentic or evidence is sufficient.
- Profile evaluations are pure previews. A supplied approval or gate boolean is not authenticated authorization. Publication performs no publication; retention performs no deletion.
- The proposed profiles have their own input contracts. Earlier frozen Policy, Gate and Evaluation carriers are preserved; applying these broader profiles to live workflows requires separate integration.
- Stable identity revisions and immutable run/observation checks are local checks. A real identity migration or accepted successor needs its own owner record.
- Team roster current/history uses an explicit as-of instant and half-open periods. No identity-link relation merges people or implies permission.
- Derived views are complete only relative to supplied records. The promotion queue is a navigation view of gates, evaluations, decisions and their links, not a readiness or approval decision.
- Source verification preserves 32 inherited lineage residues and the prior D53 layout exception. Product and Project meanings reuse admitted Lab Definitions; candidate meanings remain candidates.

## Reproduce the checks

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch/check.py graph evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch/examples/graph-manifest.json
```

The CLI also provides profile, view and revision modes. Use --help for arguments. Results never execute the represented domain operation. Revalidation preserves predecessor bytes; generated receipt files may be refreshed inside this batch.

## Targets

| Target | Family | What to review |
|---|---|---|
| [type.intent](targets/type.intent/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Intent in an explicitly named scope. |
| [type.product](targets/type.product/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Product in an explicitly named scope. |
| [type.product-thesis](targets/type.product-thesis/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Product Thesis in an explicitly named scope. |
| [type.product-capability](targets/type.product-capability/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Product Capability in an explicitly named scope. |
| [type.capability-realization-binding](targets/type.capability-realization-binding/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Capability Realization Binding in an explicitly named scope. |
| [type.project](targets/type.project/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Project in an explicitly named scope. |
| [type.research-inquiry](targets/type.research-inquiry/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Research Inquiry in an explicitly named scope. |
| [type.research-run](targets/type.research-run/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Research Run in an explicitly named scope. |
| [type.finding](targets/type.finding/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Finding in an explicitly named scope. |
| [type.experiment-design](targets/type.experiment-design/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Experiment Design in an explicitly named scope. |
| [type.experiment-run](targets/type.experiment-run/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Experiment Run in an explicitly named scope. |
| [type.observation](targets/type.observation/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Observation in an explicitly named scope. |
| [type.measurement-method](targets/type.measurement-method/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Measurement Method in an explicitly named scope. |
| [type.measurement-result](targets/type.measurement-result/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Measurement Result in an explicitly named scope. |
| [type.ontology](targets/type.ontology/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Ontology in an explicitly named scope. |
| [type.context](targets/type.context/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Context in an explicitly named scope. |
| [type.context-profile](targets/type.context-profile/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Context Profile in an explicitly named scope. |
| [type.context-request](targets/type.context-request/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Context Request in an explicitly named scope. |
| [type.context-view](targets/type.context-view/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Context View in an explicitly named scope. |
| [type.model-instance-binding](targets/type.model-instance-binding/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Model Instance Binding in an explicitly named scope. |
| [type.person-reference](targets/type.person-reference/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Person Reference in an explicitly named scope. |
| [type.identity-claim](targets/type.identity-claim/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Identity Claim in an explicitly named scope. |
| [type.team](targets/type.team/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Team in an explicitly named scope. |
| [type.team-membership](targets/type.team-membership/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Team Membership in an explicitly named scope. |
| [type.role](targets/type.role/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Role in an explicitly named scope. |
| [type.role-assignment](targets/type.role-assignment/REVIEW.md) | artifact-type | Use these record fields and reference constraints for Role Assignment in an explicitly named scope. |
| [profile.repository-layout-policy](targets/profile.repository-layout-policy/REVIEW.md) | profile | Use these exact proposed parameters and rules for Repository Layout Policy. Review the states, limits or criteria before adoption. |
| [profile.source-selection-policy](targets/profile.source-selection-policy/REVIEW.md) | profile | Use these exact proposed parameters and rules for Source Selection Policy. Review the states, limits or criteria before adoption. |
| [profile.authority-aware-navigation](targets/profile.authority-aware-navigation/REVIEW.md) | profile | Use these exact proposed parameters and rules for Authority-Aware Navigation Policy. Review the states, limits or criteria before adoption. |
| [profile.challenge](targets/profile.challenge/REVIEW.md) | profile | Use these exact proposed parameters and rules for Challenge Policy. Review the states, limits or criteria before adoption. |
| [profile.retention](targets/profile.retention/REVIEW.md) | profile | Use these exact proposed parameters and rules for Retention Policy. Review the states, limits or criteria before adoption. |
| [profile.semantic-consistency](targets/profile.semantic-consistency/REVIEW.md) | profile | Use these exact proposed parameters and rules for Semantic Consistency Policy. Review the states, limits or criteria before adoption. |
| [profile.publication](targets/profile.publication/REVIEW.md) | profile | Use these exact proposed parameters and rules for Publication Policy. Review the states, limits or criteria before adoption. |
| [profile.cross-context-generalization](targets/profile.cross-context-generalization/REVIEW.md) | profile | Use these exact proposed parameters and rules for Cross-Context Generalization Policy. Review the states, limits or criteria before adoption. |
| [profile.context-resolution](targets/profile.context-resolution/REVIEW.md) | profile | Use these exact proposed parameters and rules for Context Resolution Policy. Review the states, limits or criteria before adoption. |
| [profile.recursion](targets/profile.recursion/REVIEW.md) | profile | Use these exact proposed parameters and rules for Recursion Policy. Review the states, limits or criteria before adoption. |
| [profile.architecture-pattern-promotion](targets/profile.architecture-pattern-promotion/REVIEW.md) | profile | Use these exact proposed parameters and rules for Architecture Pattern Promotion Profile. Review the states, limits or criteria before adoption. |
| [profile.ux-authority-promotion](targets/profile.ux-authority-promotion/REVIEW.md) | profile | Use these exact proposed parameters and rules for UX/UI Authority Promotion Profile. Review the states, limits or criteria before adoption. |
| [profile.ux-evidence-compatibility](targets/profile.ux-evidence-compatibility/REVIEW.md) | profile | Use these exact proposed parameters and rules for UX/UI Evidence Compatibility Profile. Review the states, limits or criteria before adoption. |
| [profile.authority-lifecycle](targets/profile.authority-lifecycle/REVIEW.md) | profile | Use these exact proposed parameters and rules for Authority Lifecycle Profile. Review the states, limits or criteria before adoption. |
| [profile.goal-lifecycle](targets/profile.goal-lifecycle/REVIEW.md) | profile | Use these exact proposed parameters and rules for Goal Lifecycle Profile. Review the states, limits or criteria before adoption. |
| [profile.project-lifecycle](targets/profile.project-lifecycle/REVIEW.md) | profile | Use these exact proposed parameters and rules for Project Lifecycle Profile. Review the states, limits or criteria before adoption. |
| [profile.product-thesis-lifecycle](targets/profile.product-thesis-lifecycle/REVIEW.md) | profile | Use these exact proposed parameters and rules for Product Thesis Lifecycle Profile. Review the states, limits or criteria before adoption. |
| [profile.context-lifecycle](targets/profile.context-lifecycle/REVIEW.md) | profile | Use these exact proposed parameters and rules for Context Lifecycle Profile. Review the states, limits or criteria before adoption. |
| [profile.capability-lifecycle](targets/profile.capability-lifecycle/REVIEW.md) | profile | Use these exact proposed parameters and rules for Capability Lifecycle Profile. Review the states, limits or criteria before adoption. |
| [profile.team-lifecycle](targets/profile.team-lifecycle/REVIEW.md) | profile | Use these exact proposed parameters and rules for Team Lifecycle Profile. Review the states, limits or criteria before adoption. |
| [profile.gate-evaluation](targets/profile.gate-evaluation/REVIEW.md) | profile | Use these exact proposed parameters and rules for Gate Evaluation Profile. Review the states, limits or criteria before adoption. |
| [profile.goal-evaluation](targets/profile.goal-evaluation/REVIEW.md) | profile | Use these exact proposed parameters and rules for Goal Evaluation Profile. Review the states, limits or criteria before adoption. |
| [profile.project-evaluation](targets/profile.project-evaluation/REVIEW.md) | profile | Use these exact proposed parameters and rules for Project Evaluation Profile. Review the states, limits or criteria before adoption. |
| [profile.product-thesis-evaluation](targets/profile.product-thesis-evaluation/REVIEW.md) | profile | Use these exact proposed parameters and rules for Product Thesis Evaluation Profile. Review the states, limits or criteria before adoption. |
| [profile.model-instance-binding-evaluation](targets/profile.model-instance-binding-evaluation/REVIEW.md) | profile | Use these exact proposed parameters and rules for Model Instance Binding Evaluation Profile. Review the states, limits or criteria before adoption. |
| [relation.belongs-to-product](targets/relation.belongs-to-product/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.belongs-to-project](targets/relation.belongs-to-project/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.originates-from](targets/relation.originates-from/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.successor-of](targets/relation.successor-of/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.supersedes](targets/relation.supersedes/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.uses-method](targets/relation.uses-method/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.derives-from](targets/relation.derives-from/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.supports](targets/relation.supports/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.contradicts](targets/relation.contradicts/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.evaluates](targets/relation.evaluates/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.governed-by](targets/relation.governed-by/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.authorizes](targets/relation.authorizes/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.adopts](targets/relation.adopts/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.realizes](targets/relation.realizes/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.instance-of](targets/relation.instance-of/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.compiles-to](targets/relation.compiles-to/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.binds-implementation](targets/relation.binds-implementation/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.frames](targets/relation.frames/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.references-bounded-context](targets/relation.references-bounded-context/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.member-of](targets/relation.member-of/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.assigned-role](targets/relation.assigned-role/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.assigned-responsibility](targets/relation.assigned-responsibility/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.represents-person](targets/relation.represents-person/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.identity-link](targets/relation.identity-link/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [relation.claims-authority-over](targets/relation.claims-authority-over/REVIEW.md) | relation-kind | Use this directed relation and endpoint contract; its presence grants no authority. |
| [derived.definition-graph](targets/derived.definition-graph/REVIEW.md) | derived-surface | Use this derived view for navigation within the supplied data; it remains non-authoritative. |
| [derived.promotion-queue](targets/derived.promotion-queue/REVIEW.md) | derived-surface | Use this derived view for navigation within the supplied data; it remains non-authoritative. |
| [derived.source-index](targets/derived.source-index/REVIEW.md) | derived-surface | Use this derived view for navigation within the supplied data; it remains non-authoritative. |
| [derived.artifact-graph](targets/derived.artifact-graph/REVIEW.md) | derived-surface | Use this derived view for navigation within the supplied data; it remains non-authoritative. |
| [derived.project-index](targets/derived.project-index/REVIEW.md) | derived-surface | Use this derived view for navigation within the supplied data; it remains non-authoritative. |
| [derived.capability-ontology](targets/derived.capability-ontology/REVIEW.md) | derived-surface | Use this derived view for navigation within the supplied data; it remains non-authoritative. |
| [derived.team-roster](targets/derived.team-roster/REVIEW.md) | derived-surface | Use this derived view for navigation within the supplied data; it remains non-authoritative. |
