# First Lab workspace model candidate

Status: **Define-prepared candidate with explicit remaining gaps**, 5 November 2026. Authority effect: **none**. No existing Craft source, identity, shared installation, selected runtime, admitted Definition, registry, store or folder layout is changed by this package.

This package makes the first proposed Lab workspace model concrete. It uses current admitted artifact contracts for a new scoped Workspace Definition, a reusable operating-model record, canonical manifests and a Craft model-instance binding. The local workspace schema is a proposal implementation contract, not a newly admitted Artifact Type.

## Read and inspect

| Need | Record |
| --- | --- |
| Actual corrective Define CLI result, all concept dispositions and source meanings | [Define result](define-process/RESULT.md), [process checks](define-process/process-check.json) |
| Proposed Workspace meaning, formal conditions and intuition | [Definition](definition/lab-workspace/DEFINITION.md), [machine source](definition/lab-workspace/definition.json), [candidate-only index](definition/INDEX.json) |
| Reusable eight-area operating model | [Native model record](model/model.json), [operating profile](model/operating-profile.json), [rules](model/rules.json), [local profile schema](model/workspace.schema.json) |
| Shared operations, optional specialization and runtime placement | [Shared-runtime model](SHARED-RUNTIME.md), [policy](model/runtime-policy.json), [Craft selection](craft/runtime-selection.json) |
| Craft's proposed workspace boundary and exact adopted-model references | [Workspace profile](craft/workspace.json) |
| Parent model versus local instance authority and extension scope | [Model Instance Binding](craft/binding.json) |
| Project duplicate and Product revision selection | [Reconciliation](craft/reconciliation.json) |
| Exact current functional anchors and retained representations | [Source selection](craft/selection.json) |
| Independently owned proposal integration homes | [Craft package](craft/PACKAGE.md), [product](craft/homes/product/PACKAGE.md), [project](craft/homes/project/PACKAGE.md), [work](craft/homes/work/PACKAGE.md), [authority](craft/homes/authority/PACKAGE.md), [ontology](craft/homes/ontology/PACKAGE.md), [architecture](craft/homes/architecture/PACKAGE.md), [implementation](craft/homes/implementation/PACKAGE.md), [documentation](craft/homes/docs/PACKAGE.md) |
| Exact current carrier selections | [Contract bindings](contracts.json) |
| Explicit design decisions | [Decisions](DECISIONS.md) |
| Source-bound authoring request and candidate-only Decision representation | [Intent evidence](review/operator-intent.json), [Decision candidate](review/decision.json) |
| Creation/succession scenario and limits | [Scenario](SCENARIO.md) |
| Open work and claim boundaries | [Residue](RESIDUE.md) |
| Current executed package checks | [Validation receipt](receipts/validation.json) |

## Verification

From the Lab repository root:

```sh
python3 docs/proposals/0012-lab-workspace-model/render.py --check
python3 docs/proposals/0012-lab-workspace-model/validate.py
```

After deliberately editing this candidate's canonical records, regenerate its human projections with `render.py`. `validate.py --write-report` writes only this package's current receipt. The default validator reads source and uses disposable temporary directories for its profile fixture; it does not write permanent runtime state.

The executed scenario creates an isolated candidate-profile generation, publishes a compatible fixture successor, restarts its reader, verifies predecessor bytes/journal and restores the retained reader. This exercises the authored profile interpreter and filesystem fixture. It does **not** install or upgrade the native Craft application or prove whole-Lab operational qualification.

The shared-runtime fixture resolves two workspace scopes to one synthetic target and checks optional specialization and dedicated placement, with 11 refusal cases. It creates no runtime and executes no native operations. See [shared-runtime model](SHARED-RUNTIME.md).

## Exact selection boundary

The Craft manifest homes in this proposal own **selection descriptors and candidate integration records**, not copied or newly admitted Craft Product, Project, authority or runtime sources. Referenced source stays in `craft/` and its original legacy homes. The selection covers current model/profile/component entrypoints across the eight areas; it does not claim a complete compiler/build source closure.

Craft's current Project record is selected as the proposed profile input; the byte-identical coordination copy is retained. Product Identity/v2 proposal is selected for the local profile while the earlier v1 record remains exact and unsuperseded. ORODI Goal reverse membership retains `candidate-reverse-link-not-applied`. Parent and local owner routes grant no new assignments or permissions.

The preceding [workspace boundary map](../../../architecture/workspace-model-mapping/WORKSPACE-BOUNDARIES.md) and [prerequisite audit](../../../architecture/workspace-model-mapping/MODEL-GAPS.md) remain planning context. This package captures a fresh current-source selection rather than silently updating their older evidence snapshots.

## Define process correction

The original package was authored directly against artifact schemas and validated by its local harness. It had **not** gone through Define CLI. The original [pre-Define validation receipt](receipts/pre-define-validation.json) remains evidence only for those earlier checks.

The corrective scripted workflow now records actual default CLI/native-context reads, Define v3 Lab snapshot capture, preparation, inspection, complete Definition/v2 materialization, exact reconstruction and a later-use observation. Revision 3 preserves revisions 1 and 2, adds your shared-runtime correction, and retains your explicit answer: **Lab Workspace** denotes the durable scope; **runtime instance** denotes execution.

There are 16 reused source meanings, the proposed Workspace meaning, local terminology and shared-runtime conventions, and two open concepts. The operating model and Craft binding are now candidate revision 2. Shared operations are the default; behavior specialization can remain on shared execution, and dedicated execution is a separate explicit option. The materialized Workspace body remains byte-identical to the pre-Define draft, with all 103 field leaves attributed mechanically. This does not constitute independent semantic-fidelity acceptance.

The actual owner-review use observation is **blocked**, because a local snapshot does not establish current native authority. Formal-symbol fit and semantic-owner acceptance remain open. No private operator was provisioned, and no signing, native review/application or canonical admission was performed. The Pack's frozen readiness is not rewritten after materialization to imply permission.
