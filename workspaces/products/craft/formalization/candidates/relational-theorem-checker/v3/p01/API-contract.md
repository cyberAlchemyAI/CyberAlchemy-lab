# V3 local checker contracts

These are candidate local Python/CLI contracts. P01 implements schema, strict decoding and catalog selection; execution becomes available through P03 and supervised use through P06. There is no HTTP service or live authority effect.

`qualify_fresh(request, context)` accepts `relational.qualification-request/v3`: an explicitly named `rich-positive-recursive-v2` source profile, the exact nested v2 recursive proposal, an explicit resource policy, a combined/staged layout, and cold/warm dependency mode. The baseline remains `relational.baseline/v2`; neither its schema nor its original profile/catalog identity is relabeled. The v3 proof manifest separately binds the v3 trusted catalog, source profile, request, proposal, baseline, toolchain and inherited profile.

`inspect_saved(request, result, context)` returns a closed inspection variant with `application_authorized=false`. It validates currentness and exact evidence correlation but emits no live replay event. `describe(request,result,query)` must inspect first and classify typed present, completed in-profile absent, outside-profile, invalid-query or incomplete outcomes. Actual application always requalifies in its current invocation and independently registers its successor.

The trusted catalog computes exact required IDs from change class. Registration requires 17 normative obligations and currently uses the stronger fresh 20-obligation rule-only identity extension. Rule-only requires all 20; richer migration requires 18 and is a different transition claim. An extension selected in the plan is not yet a qualified new profile. Caller-supplied catalogs or obligation subsets are not request fields.

The proof manifest requires exactly one combined module or exactly four ordered staged modules: data, typed, closure and expansion. Each has a source and compiled-artifact binding. General replay, projection, dependency, generated-result and generator bindings are separate mandatory fields. Shapes alone do not prove file currentness or theorem validity; P02 supplies those checks and P03 the fresh invocation.

Qualified results require completed resource reporting and explicit scoped claims, and still have `application_authorized=false` because later application must replay. Invalid, unsupported, unknown-resource, cancelled and unsupported-policy variants have no claims, no manifest, no complete closure and no application authorization. These are not semantic falsehoods. A process exit of zero means the operation completed; mapped yes/no/unknown/invalid remain typed semantic verdicts.

CLI contract: 0 completed scoped result; 2 invalid request/data; 3 unknown resource exhaustion; 4 unsupported profile or required enforcement policy; 5 stale saved evidence or publication reconciliation; 130 cancellation. Exact failure reason/stage and enforcement events are recorded. The cancellation variant is distinct from condition-status unknown.

Resource policy is required rather than given an unmeasured default. It preserves fixed early v2 work ceilings, a stage deadline at most 60 seconds, an explicit whole-run deadline, memory amount and required/advisory mode, output ceiling and one supervised worker. Required aggregate enforcement unavailable on this host returns unsupported-policy. Advisory selection explicitly reports its lack of aggregate enforcement. Numerical production recommendations await actual supervised measurements.

The strict decoder rejects duplicate keys, nonfinite/overflow numbers, unknown fields through schemas, inputs above 4 MiB and nesting above 64 before deeper processing. Expensive decoding and all following phases will run under P06 supervision. Schema bindings use tagged repository/toolchain paths with no absolute/path-traversal/backslash forms; P05 resolves them beneath pinned roots and distinguishes documentary records.

Externally supplied assessment, clock, policy/gate and condition/action truth remains assumed. IR verification and independent-checker feasibility are separately selected extensions. Existing v2 feedback is not successor feedback and does not close original v1 R06/G4. Authority effect: none.
