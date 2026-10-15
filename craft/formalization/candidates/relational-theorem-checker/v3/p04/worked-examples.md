# Query and relation explanations

The public `describe` API first inspects the exact saved source/witness evidence. This is recorded-current inspection, not a fresh replay or application authorization. Both actual combined and staged layouts use the same API. The combined and wrong-scope test envelopes adapt exact historical v2 qualifications; they do not issue new fresh qualifications.

## Exact positive relation

`ContractReady(capability:reviewer@v1)` follows from `ContractReview` and its exact rule substitution. Its two source leaves are `ConformsTo(capability:reviewer@v1, contract:review@v1, static)` and `TargetKind(contract:review@v1, contract)`. The conformance leaf retains its member assertion and assessment token; the kind leaf retains the target node. Accepted assessment truth is supplied. See [the staged trace](positive-explanation.json). The older unary Conforms fact loses target and scope, so it cannot select this contract/scope by itself.

## Absence and typing

The wrong-scope case asks for other-scope, which is in the finite domain but has no matching conformance observation. Its unseeded positive cycle does not derive ContractReady. [The explanation](wrong-scope-explanation.json) says absent-in-complete-profile. The new theorem proves that this diagnostic entails AtomValid, completed closure and nonmembership. Given closure adequacy, it excludes derivation from these fixed supplied facts. It does not assert falsity in every generic model, which may contain extra truths.

Unknown predicate identity/version/digest or an undeclared domain value is outside-profile. A known predicate with wrong arity/sorts or a malformed atom is invalid-query. An exhausted computation is incomplete and never proves absence. Trace rendering can be truncated while the inspected closure remains complete; omitted indices stay visible. Output overflow instead emits an incomplete rendering result without an absence/application claim.

## Mapped semantic relations

[Unknown condition](unknown-potential-explanation.json) retains a potential inherited norm but activates none. [Positive condition](active-origin-explanation.json) activates the exact norm and retains its binding/contract/subject/scope origin. Activation does not establish fulfillment or admission. Active require/forbid conflicts have separate paired origins; they do not enable arbitrary conclusions.

[Expired direct delegation](expired-delegation-explanation.json) returns no at epoch 10 for period [0,10). Its exact agent, principal, delegation revision, action and scope remain visible. The profile does not implement chains.

The mapped reader regenerates the exact concrete checked witness and checks current source/compiled dependencies. It does not render ancillary typed transport certificate fields that the witness does not bind. Supplied roots, condition evaluations and policy/gate truth remain explicit assumptions. No same-kernel replay is an independent checker, and no explanation changes readiness.
