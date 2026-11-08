# K39 — uses-tool

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded attributable invocation/use**.

**Meaning in plain language.** A session or action records a dependency on, proposed use of or invocation of a tool under an exact contract. Only an invocation constructor requires an invocation trace.

**Question answered.** Which Tool or Implementation does this Agent Session or Agent Action use?

**Formal definition.**

```text
Meaning_K39(W,e,f) := ∃ w ∈ W.ToolUse. Base_K39(W,e,f,w) ∧ (w.subject = s ∧ w.tool = t ∧ t = resolve(q.tool_version_ref) ∧ w.contract = resolve(q.invocation_contract_ref) ∧ w.role = code(q.use_role) ∧ ToolContractApplies(W,w,f) ∧ (w.constructor=invocation → InvocationObserved(W,w,f)))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ToolUse record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `subject` | Agent Session or Agent Action exact revision |
| `tool` | Tool or Implementation exact revision |
| `contract` | owned invocation contract exact revision |
| `role` | owned tool dependency/proposal/invocation role |
| `constructor` | dependency, proposedUse or invocation |
| `trace` | exact attempted/completed/failed invocation trace when invocation is claimed |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`ToolContractApplies`: The exact contract admits the subject/tool revision, scope, role and dependency/proposal/invocation constructor. Each code resolves to exactly one constructor; undeclared postures are unsupported.

`InvocationObserved`: An admissible attributable trace joins the invocation to this subject, tool revision and contract. Attempted, completed and failed postures remain distinct; external effects need separate observations.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `tool_version_ref` | `w.tool` | exact Tool or Implementation revision |
| `invocation_contract_ref` | `w.contract` | exact subject/tool/frame invocation contract |
| `use_role` | `w.role` | owned dependency/proposed-use/invocation constructor with witnessed posture when invoked |

**Operational behavior.** Record exact tool use/invocation posture without realization, conformance, ownership or authority.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Session S attempts to invoke Tool T under Contract C, but the invocation fails and transfers no ownership.

**Insufficient case.** An invocation contract for another tool revision cannot support this use.

**Useful correction.** Use the contract for this subject and tool revision; supply an attributable invocation trace only when claiming invocation.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| realization | An independent instantiation/execution witness establishes concrete realization, beyond declared contribution or method use. | `relation.uses-tool:forbidden:0` |
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.uses-tool:forbidden:1` |
| ownership | An independently governed ownership record identifies the owner, beyond production, action or impact. | `relation.uses-tool:forbidden:2` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.uses-tool:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Four branches need tool/implementation contract adapters and explicit posture mappings; failed invocation is still distinct from successful external effect.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/uses-tool.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K39-uses-tool.json)

**Exact ordered pairs (4).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | implementation | agent-action dependency/proposal/invocation of implementation under the exact invocation contract |
| agent-action | tool | agent-action dependency/proposal/invocation of tool under the exact invocation contract |
| agent-session | implementation | agent-session dependency/proposal/invocation of implementation under the exact invocation contract |
| agent-session | tool | agent-session dependency/proposal/invocation of tool under the exact invocation contract |
