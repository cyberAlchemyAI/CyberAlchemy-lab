# Candidate preparation and durable operation inspection

Status: partial R03 candidate implementation. Authority effect: none. Final owner outcome: absent.

## Operator journey

1. Authenticate a fresh local stdio channel against an independently provisioned public-key policy, exact signed source selection and private owned workspace.
2. Inspect current state/catalog/artifact content and typed connections using the retained four readers. Current and historical source cuts remain explicit.
3. Select exact candidate original content, metadata, target Decision cores, schema closure, predecessor and requested effects. Candidate input refs resolve only inside a hash-bound flat material vault.
4. Call `change.validate`. The selected runtime computes a prospective postimage and independent target cores without signing, publishing or mutating the source store. The report separates structural/core/typed checks from incomplete semantic reference closure.
5. Call `change.prepare`. The review binds actual target diffs, examples, requested consequences, private custody checks and validation evidence. Owner and operational obligations remain explicit gaps. A result envelope is not admission or Work completion.
6. After a timeout or process interruption, call `operation.inspect`. Completed outcomes retain exact result bindings. Claims without verified results remain indeterminate; retry is forbidden until scoped reconciliation.

## Example

An operator proposes a new Work revision named “Inspect a complete candidate before its final owner decision.” The target retains an explicit Project membership and declares candidate preparation state. Original content bytes, its independent Decision core, the current source cut and selected Work schema are bound separately.

The structural, core and typed declaration checks can pass. The selected cut still lacks complete Goal/input/output reference closure for the Work. The report therefore returns `not-evaluable`, lists exact requested references and retains a blocked review. This makes the missing work visible before the final owner decision.

The original source Project State, source HEAD and signed transaction history are unchanged. A simulation is not an admitted Project State successor. Private operation records contain eligible candidate evidence and invocation metadata; they do not provide Agent long-term memory. No Machine Agent Session is opened by these handlers.

## Storage and trust

- Canonical evidence remains the independently selected signed original history. SQLite remains a disposable read generation.
- The candidate workspace is a private mode-700 owned temporary root with mode-600 exact input/control/object/journal files. It is independently selected by the authentication policy; caller paths cannot select arbitrary repositories or stores.
- A durable namespace binds principal, authority scope, selected scopes, operation and key. An independent fingerprint uses the pinned RFC 8785 codec, exact source profile/cut and full inner message. Original artifact and wire byte hashes remain separate.
- Immutable allocation/claim records are retained before candidate evidence. A missing claim/result under retained allocation means uncertainty. Completed, pending and uncertain operations are never redispatched. Whole custody loss requires external reconciliation; an empty replacement directory supplies no proof that prior effects did not occur.
- Authentication, code/schema/profile pins, source freshness, actor claims, input/output ceilings, deadline and action count are checked. Outcome publication beyond a response budget points to retained inspection rather than declaring no effect.

## Remaining scope

Seven actual API handlers are selected: `lab.status`, `catalog.get`, `artifact.inspect`, `artifact.query`, `change.prepare`, `change.validate`, `operation.inspect`. Twenty-seven handlers remain unimplemented, including final `proposal.review`, Session/Agent context, transactions, actions, workflows, ontology, projections, file/package/install operations and release preparation. Full carrier-specific semantic reference validation also remains required before affected use.

The source-freeze, profile, dependency selection and real observations are final S02/R08 review inputs. The added RFC 8785 wheel is a separate dependency member; it does not modify the frozen eight-wheel R02 foundation. R05 still owes integrated tests under the final selected environment. Final operator/owner scopes and actual owner outcomes remain unresolved until the complete package.

Frozen failed api-v5, api-v6 and api-v7 attempts remain exact predecessors. This successor changes no admitted definition, canonical authority, live store, activation or external system.
