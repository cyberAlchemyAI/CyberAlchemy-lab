# Candidate checker API v2

These are local Python APIs and CLI transports. There is no HTTP server or deployed authority service. Run commands from the repository root. The v1 transports remain unchanged.

```bash
python3 craft/formalization/candidates/relational-theorem-checker/v2/s05/projection-adapter.py REQUEST.json --output RESULT.json
python3 craft/formalization/candidates/relational-theorem-checker/v2/s06/recursive-runtime.py PROPOSAL.json --output RESULT.json
python3 craft/formalization/candidates/relational-theorem-checker/v2/s07/delegation-adapter.py REQUEST.json --output RESULT.json
python3 craft/formalization/candidates/relational-theorem-checker/v2/s07/inheritance-adapter.py REQUEST.json --output RESULT.json
python3 craft/formalization/candidates/relational-theorem-checker/v2/s08/explain.py RESULT.json --proposal PROPOSAL.json
```

| Call | Contract | Result and scope |
|---|---|---|
| `s05.adapter.project(request)` | [Projection request](../s05/request.schema.json), immutable [baseline](../s15/baseline.schema.json), [profile](../s15/profile.schema.json) | Kernel-checked F0 source observations and exact support inventory. Projection alone is not readiness. |
| `s06.runtime.qualify(proposal)` | [Recursive proposal](../s06/rule-bundle.schema.json) | Fresh general theorem replay plus actual typed, producer, lineage, complete closure and structural extension witnesses. Exact generated inventory: [catalog](../s15/obligation-catalog.json). |
| `s06.runtime.validate_receipt(proposal,result)` | Exact saved result and proposal | Structural currentness only. Does not replay evidence or authorize application. |
| `s07.stress_adapter.evaluate(request)` | [Interpretation envelope](../s07/interpretation.schema.json) | One explicitly mapped source assertion. Direct delegation or fixed inherited norm query; potential/active/conflict separate. |
| `s08.explain.describe(result,proposal,query)` | Bound result and actual checked source | Source/supplied-truth leaves, exact rule substitution and query scope. Does not upgrade readiness. |

Python modules are loaded through their local directories, as shown in the task runners. CLI JSON is strict: duplicate keys, nonfinite numbers, unknown fields and stale profile/catalog/source identities are rejected. Requests are capped at 4 MiB and 64 levels of JSON nesting; the [resource envelope](../s17/preflight-bounds.json) defines additional conservative work ceilings. Rich source observations require all exact reference, scope and kind literals in the declared finite domain.

Main v2 CLI exits: **0** for a completed scoped result; **2** invalid transport/data; **3** unknown resource exhaustion; **4** unsupported recursive profile. Explanation exits **5** for stale/mismatched evidence. Stress mapping exits **0** when it returns a scoped typed verdict (`yes`, `no`, `unknown`, or `invalid`), **2** for rejected envelope/mapping, and **3** for operational exhaustion. A successful process exit is not a `yes` verdict. No live authority effect is available.

The profile supports positive rules with fresh ordinary derived heads, including recursion. Old graph, domain, roots, facts, interpretation and context remain fixed in a rule-only proposal; existing rules can be nonempty. Richer append migrations have a distinct `InitialViewRelation` witness and can grow the domain and source observations. They do not claim every-old-model expansion. Mixed edits, old-head changes, negation, functions, fresh roots, overrides and redelegation chains remain unsupported.

JSON decoding and source-to-Lean generation are tested boundaries. The kernel checks the generated pure values/proofs and exact trusted statement definitions. Replay uses the same pinned Lean kernel, with `propext`, `Classical.choice`, and `Quot.sound` as allowed foundational axioms; it is not a second independent kernel. Accepted assessments, root receipts, policy/gate decisions and condition evaluation truth remain externally supplied. An inherited or active norm does not establish fulfillment, conformance, or admission.
