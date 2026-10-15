# Package source boundary for the next host integration

## Verified facts

The current public `package.export` contract requests selected portable original
content and its complete required dependencies. Its preconditions require exact
bytes, complete closure, an independently resolved destination and exclusion of
credentials and Session memory. It does not prescribe exporting every unrelated
record in the operational branch. `package.import` separately validates source
package/provenance, mapping, disposition and target custody/privacy. Source
admission evidence never admits an imported target.

The first full-snapshot size probe used the exact API52-selected 23,542,012-byte
snapshot. Before package construction it decoded the embedded original files and
ran the strict privacy scan. The baseline contains a persisted Agent Session
descriptor in both original documents and projected subjects, and its schema has
a `session_memory` property. The descriptor has four fields:
`expires_with_session`, `selected_input_refs`, `working_record_refs` and
`unresolved_questions`. Its reference/question arrays are not all empty. This
metadata observation does not establish live RAM disclosure or justify treating
the entire descriptor as safe. Actual exit 1 is preserved.

The new transfer and filesystem kernels passed 78 pure and 33 filesystem fixture
cases respectively. Those fixtures supply no authenticated Actor, source replay,
genuine privacy review or semantic import proof. Public handlers remain 18/34.

## Recommended next implementation

1. Select a real root through the original authenticated Service and signed
   source reader. Run the full original source checks locally before and after
   reading; retain the original source cut and immutable original bytes.
2. Define and prove that root's complete portable dependency closure: original
   carrier/schema resources, exact referenced artifact revisions, represented
   typed edges, relation contracts and all declared source evidence. Do not
   equate a graph's membership in a branch with a semantic dependency.
3. For source admission claims, include the exact sufficient original admission
   basis and its verification dependencies. A source cut or receipt label is not
   an admission proof. If that sufficient basis cannot be carried safely, expose
   the gap and refuse that source posture; do not invent a witness or relabel an
   admitted source to evade this requirement.
4. Classify every included original against the declared privacy contract.
   Distinguish a public schema statement and resolved persisted metadata from
   actual Session memory using exact contracts and original source evidence.
   No generic key-name exemption, removed field, rewritten original, arbitrary
   binary claim or caller-supplied `safe` flag qualifies this distinction.
5. Exclude unrelated Session records only when the actual dependency calculation
   proves they are outside the selected closure. If a required dependency fails
   privacy, refuse export with `private-material-excluded`/`closure-missing` and
   expose the exact gap. Never silently shorten the required closure.
6. Bind independent current export/import permissions, root scope and controls.
   Perform pure preflight before a durable operation claim. Then use the managed
   generation kernel after full source exit; verify existing results read-only.
   Import must pass original carrier, reference, typed relation, stable core and
   prospective model validation before returning a Change Proposal.
7. Add actual positive and negative public cases. Preserve all original tests,
   schemas, real clocks, budgets, signatures and source callbacks. Source or
   filesystem fixture evidence does not transfer to these public cases.

A whole-branch export remains unqualified. If a particular package truly needs
the full snapshot as a dependency, the failed probe must be resolved at that
exact privacy/provenance boundary first. This recommendation changes no
canonical schema, Session lifecycle, authority or final R08 checkpoint.

## Source references

- `docs/proposals/0008-lab-api-contracts/operations/package.export.json`
- `docs/proposals/0008-lab-api-contracts/operations/package.import.json`
- `docs/proposals/0007-lab-integrated-schema-package/RUNTIME-OBLIGATIONS.md`:
  O-EXACT portable replay and original-byte obligations.
- `authority/artifact-types/agent-session/v1/schema.json`
- `product/lab/release-candidates/v1/interface/api-v52/receipts/R03-0094.json`
- This run's `package-public-source-size-failure-0001.json` and actual terminal.

Candidate design only. No permission, public qualification or admission is granted.
