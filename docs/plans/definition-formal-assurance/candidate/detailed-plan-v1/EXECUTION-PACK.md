# Candidate execution protocol

This package delivers analysis and a future plan. No implementation task has run. [dag.json](dag.json) and [swu-manifest.json](swu-manifest.json) own the graph and unit contracts; task Markdown and diagrams are navigation views.

## Selection and readiness

1. Select exactly one ready task/unit from [the frontiers](topological-frontiers.json). A dependency is satisfied by its actual criterion and bound receipt, not by its file existing or a task being labelled complete.
2. Read that unit's exact inputs, ordered rules, edge cases, declared outputs, narrow scope and validation. Read [the algorithm contracts](IMPLEMENTATION-DETAILS.md) and the applicable [layer](IMPLEMENTATION-LAYERING.md).
3. Rehash the source registry, selected definition bytes and required upstream artifacts. If they differ from the sealed baseline, capture a successor snapshot and affected closure before execution. Do not overwrite the original plan or force stale receipts to pass.
4. Check the intended output paths are absent. Implement in the declared new candidate scope. A retry has a fresh attempt/snapshot identity; it must not overwrite prior evidence. Preserve unrelated dirty work.
5. Resolve a conditional provider against the actual required logical fragment and minimum strength. If non-applicable, emit a reasoned receipt and run that route's receipt/control validation. Only product paths carrying `activation_condition` may be absent on this branch. The branch cannot remove a required obligation. A missing necessary provider remains unresolved.
6. For review tasks, assemble the exact reviewable package and obtain an actual attributable decision. A command or generated review file cannot manufacture acceptance. Pending/rejected fidelity does not satisfy a readiness join.

The first ready unit is [A01.1](tasks/A01.md). It creates the strict candidate envelope/decoder and its malformed-input controls. Its validation is same-unit post-produce. Interpretation-specific correspondence contracts follow in A04; this ordering avoids demanding future contracts before their producers exist.

## Production and closeout

Implement the specified behavior and required hostile controls, then run the declared post-produce command or actual reviewable check. Commands in the manifest describe future interfaces and are not claimed installed today. A passing unit test is only the unit's software evidence; semantic acceptance additionally requires its specified statement/model/proof/currentness/fidelity criteria.

Emit a receipt binding unit ID, exact input/output digests, attempt ID, command/tool versions, actual criterion results and unresolved limitations. Update a project-local status snapshot in the new candidate data scope. Keep the original planning JSON immutable. Failed execution, unsupported logic, timeout, cancellation, stale source, insufficient evidence and pending review remain different outcomes.

The family stage is conservative: all translation drafts precede S01/S02 closure, and all family reviews precede family joins. Once actual dependency SCCs are known, a successor schedule may narrow those barriers with explicit evidence. Editorial family numbers never supply semantic ordering.

## Authority and ownership

Source definitions, admission records, registry, frozen schemas and historical proofs are read-only inputs. This plan grants no live admission effect. H03 always produces the selected-owner handoff disposition, including a valid no-effect branch; actual application belongs to a separately authorized owner workflow.

A workflow item can receive an honest unresolved disposition. The assurance objective is complete only when supported source-faithful interpretations, complete required evidence and the full included theory meet [the completion contract](PLAN.md). Administrative closeout cannot convert unsupported semantics into formal assurance.
