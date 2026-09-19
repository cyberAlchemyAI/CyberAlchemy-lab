# Authority Model carrier

Authority kind + posture -> requested operation -> intended effect -> responsible owner + required gate.

An Authority Model describes what may count for which purpose, who owns the next decision, and which checks must precede it. This candidate binds the reconstructed Authority Model meaning from D41 and closed-kind invariant from D49, while preserving both normalized source selectors.

A kind is a category of authority. A posture is its declared state, such as candidate. An operation names a requested move; its effect is what that move would change or permit. Each routing rule partitions the declared effects into allowed and blocked uses, and names the owner route, gate, validation surface and boundaries that prevent one authority layer from overriding another.

Unknown kind -> blocked until an owner amends the model. Unknown posture, operation or missing routing rule -> blocked. An operation whose declared effect differs from the requested effect -> blocked. Matching modeled use -> requires owner gate. A model or scope mismatch -> not applicable.

The checker rejects duplicate operations, overlapping kind/posture rules, effects both allowed and blocked, missing effect coverage and kinds without an owner rule. It never resolves conflicts by choosing whichever rule appears first.

The example allows candidate definitions and evidence to be routed for review and blocks admission effects. This is an illustrative model, not a replacement for the Lab's current governance. A matching route is not a gate verdict, authenticated claim or authority grant. The supplied claim is a preview input, not the still-unbuilt Authority Claim carrier.

This bounded profile uses exact scope, kind, posture and operation identities. It does not implement delegated authority, nested scope precedence, lifecycle transitions, actor authentication, verdict verification or execution. Route and validation references remain opaque; non-collapse statements are recorded text.

Run from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0015-authority-model-carrier/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/candidates/0015-authority-model-carrier/check.py evidence/migrations/cyberalchemy-v2-to-lab/candidates/0015-authority-model-carrier/artifact-types/authority-model/v1/fixtures/valid/authority-model-record.json evidence/migrations/cyberalchemy-v2-to-lab/candidates/0015-authority-model-carrier/examples/ready.json
```

CLI status 0 means a route requiring an owner gate was found, 1 means blocked or not applicable, and 2 means invalid input. Status 0 does not authorize an action.

Validation passes 16 behavioral tests and 8 invalid contract fixtures. It verifies 27 Definition dependencies and their 25 source sections, both normalized D41/D49 selectors, eight inherited source-lineage residues and the existing narrow D53 binding. Generated files reproduce and the predecessor snapshot remains unchanged.

The 195-target ledger now has 13 admitted targets, 89 constructed candidates and 93 remaining scaffolds. Next: `type.authority-claim`.

The user's `next` authorizes construction and testing. A later model adoption would approve a particular set of kinds, ownership routes, effect boundaries and required gates in its named scope. This candidate grants no adoption or action authority.
