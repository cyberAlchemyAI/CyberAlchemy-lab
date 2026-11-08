# Semantic contracts, version 1

These candidate contracts extend the earlier selection without modifying authority sources or the accepted three-kind semantics. Every reference is an `(id, version)` pair. Endpoint roles are fixed by the typed record fields: agent/principal for acts-for and capability-instance/contract for inheritance. Identity strings and revision strings are opaque.

## Temporal delegation

`Delegation` is an interpreted exact revision, with agent, principal, explicit action/scope sets, half-open period `[start,stop)`, optional irrevocable revocation epoch, policy and gate references, and a redelegation flag. `ActsEdge` contains interpreted period and revocation qualifiers matching that exact revision. The legacy registry's period/state strings are not parsed automatically; a caller must supply this interpreted candidate profile. The endpoint and qualifier correspondence is the adapter's evidence obligation.

`Snapshot` has its own exact reference, epoch, and unique policy/gate assessments. Assessment values are supplied data, not authenticated evidence. A result applies only to that supplied snapshot. Reusing it at another epoch requires another evaluation; no runtime use boundary or clock authentication is implemented.

`Recorded` is membership of an edge in a supplied historical inventory. `Effective` is an independent proposition: exact edge/delegation correspondence, allowed action and scope, current epoch in the interval, no effective revocation, all required policies/gates assessed true, and a direct representation request. Expiration or revocation does not delete `Recorded`.

`checkActs` returns `invalid` for malformed or duplicate inventories; `unknown` for an unresolved delegation or policy/gate, or a permitted redelegation request whose chain is unsupported; `yes` only for `Effective`; otherwise `no`. A forbidden redelegation request returns no. No identity merging, ownership transfer or permission grant follows.

`Restricts(narrow,broad)` is independently stated using equal principals/agents, subset action/scope sets, narrower periods, a revocation time no later than the broader delegation (or broader has no revocation), and supersets of policy/gate requirements. The general restriction law uses the same snapshot and separately matching edges; it grants no permission to substitute a revision.

## Finite obligation logic

`Contract` has exact revision, exact scope and condition atom, interpreted flag, and finite norms: require(action), forbid(action), permit(action). Conditions are supplied active context labels matched by exact equality, not executable formulas or claims about external circumstances. One condition/scope applies to each contract revision in this first profile.

`Binding` has exact revision, instance, inherited contract revisions, scope, active flag and override references. `Inheritance` names that binding, instance, contract revision, scope and condition. `Matches` independently checks those identities, active state, empty overrides, interpreted contract, and scope/condition correspondence. Unresolved references/interpretations and nonempty overrides return unknown; resolved mismatches or inactive bindings return invalid for this current-evaluation request. Historical records are not removed.

`Origin(G,f)` means the fact's exact inheritance edge is in the base inventory, a matching binding and contract are present, and the norm belongs to that contract. It contains no checker result or assumed derived fact. `Derives` has exactly two constructors: propagate an origin fact, and forward the same fact. No producer of satisfaction, conformance, admission or arbitrary atoms exists. General semantic soundness and origin preservation follow by induction on derivations. Future producer rules require new proofs.

`candidateFacts` enumerates each inheritance edge paired with each contract norm. `closure` filters this finite list by `Origin` and deduplicates exact facts. The proof establishes `f ∈ closure(G) ↔ Origin(G,f)` for arbitrary finite inputs; it is a complete closure for this two-rule profile, not unrestricted rule inference. The resource budget bounds candidate enumeration plus the square of the derived fact count for conflict-pair comparisons. Exhaustion returns unknown with no complete-closure claim; a separate runtime timeout has the same claim ceiling.

Certificates use immutable numbered steps: propagate has no parent and a checked origin; forward names a strictly earlier step with the same fact. Every step is independently origin checked. This redundant check keeps replay simple and ensures a forward step cannot launder an invalid premise. Replaying arbitrary cyclic/general rule certificates is unsupported. The checker's soundness theorem establishes an origin and therefore a derivation for every accepted step.

Require and forbid are distinct positive data constructors. A conflict is a required/forbidden pair with equal instance, action, scope and condition, possibly from different contracts. Both origins remain visible. Conflict does not cause logical explosion. Conformance assessments are a separate exact-key inventory; changing them cannot change `Origin` or `Derives`. A supplied accepted assessment is not proof of runtime satisfaction, and absence in a complete request is not a claim about the wider world.

## Trust and claim ceiling

Theorems concern the typed finite input model. The JSON decoder, transport-to-Lean encoder, compiled evaluator, supplied assessments, condition interpretation, source adaptation and host execution remain trust boundaries. Integration tests exercise the adapter; no verified decoder equivalence or authenticated external authority is claimed. This is a local reference implementation with strict JSON APIs, not a network service or a globally admitted profile.
