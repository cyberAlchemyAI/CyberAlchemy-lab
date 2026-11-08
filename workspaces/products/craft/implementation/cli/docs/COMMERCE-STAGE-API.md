# Original source API and source-bound semantic components

The shared `CommerceSourceOwner` API now has an internal Core implementation:
`createCoreCommerceStageSourceOwner(originalSources, originalSemantics)`.
The factory requires genuine Core owner instances. `prepare(root, path)`
captures the real declared files, checks their semantics and projects the
existing Application/Module contracts. It returns a newly registered opaque
source-stage handle backed by those exact original parents.

```typescript
const sources = createCoreCommerceSourceOwner();
const semantics = createCoreCommerceSemanticOwner(sources);
const stage = createCoreCommerceStageSourceOwner(sources, semantics);
const source = await stage.prepare(applicationRoot, 'application.alch');
const inspection = stage.inspect(source);
const modules = stage.moduleContracts(source);
const component = createCoreCommerceSemanticStageComponent(stage, source);
const checkedModule = component.checkModule(modules[0], modules);
stage.assertCurrent(source);
```

These are source APIs. The inspection's profile, native-basis and output
identities remain null. The handle is not selection, business acceptance,
early-request, checked application, generated output, native binding or runtime
custody. Public build/export/installed qualification remains a later task.

## Data checked against original source

`CommerceSemanticComponent` methods return `CommerceResult` data. This
implementation is bound to the genuine source-stage handle at construction;
supplied JSON cannot establish which source was checked.

| Method | Comparison |
| --- | --- |
| `checkModule(module, closure)` | Original module identity/imports/declarations/spans/entries/optional claims and the complete captured module contract closure. Closure array order is normalized; omission, duplication and substitution reject. |
| `checkComputation(contract)` | Exact independently reconstructed source computation, including functions, guards, rounding, value constraints and captured v2 computation limits. Caller-proposed limits cannot select a new checking scope. |
| `checkRead(plan, values)` | Original checked ReadPlan plus the complete source ValueSchema rooted at that query's output. |
| `checkEffects(plan, values)` | Original checked EffectPlan plus the complete source ValueSchema rooted at that operation's result. Control, guards, native positions, transaction and failure details survive comparison. |
| `checkWorkflow(plan, entries)` | Original checked WorkflowContract and complete checked application entry closure. Changes to permissions, recovery, resume, terminal or ownership behavior reject. |

Every call checks source/code currentness and original parent identity before
comparing inert data. Accessors, proxies, non-data objects and unexpected fields
reject. Successful comparison returns frozen data; matching JSON cannot restore
an original handle or acquire another stage's authority. Data projection helpers
are not owner factories and do not independently establish source custody.

## Source contract requirements

The ApplicationContract already requires a captured technical profile module
and Mapping, the closed v5 parameter object,1–16services,1–64entries and all
five required outputs. The adapter enforces that existing scope. A smaller
source-only fixture may still be captured by `CoreCommerceSourceOwner`; the
adapter does not invent an application profile or missing output selection.

The profile Mapping must belong to a captured technical-family module. Its
identity and parameter data describe a selection request. They do not derive
or load a native family. The closed v5 parameters retain the exact existing
wire sizes, timeout and validated table prefix. Supporting other profiles or
parameter contracts requires their original downstream implementations.

Optional formal claims retain their declared language, actual captured file
identity and exact existing meta-type target selectors. They remain optional
assurance, not execution prerequisites or discharged theorems. The component
does not invoke Lean, SMT, Alloy, TLA+, Souffle, TDE or EVF.

Disposing a source-stage handle disposes its internally created semantic and
source captures. Changing bytes, replacing files even with the same bytes,
changing a captured parameter/claim asset or replacing loaded adapter code
invalidates subsequent source inspection and component calls. New factories in
the same loaded code epoch cannot silently bless replaced code.

## Open Questions

The original integrated plan owns technical-family derivation/native production
(EC09–EC12), executable role planning/generation, selected profile/early-request/
application assembly and installed replay. Source-bound component acceptance
does not implement those joins. EC07 final acceptance/preservation and genuine
completed-source succession remain necessary before task closure. Local
hosting, TDE, EVF, publication/deployment and live identity/provider/database/
broker activation remain deferred.
