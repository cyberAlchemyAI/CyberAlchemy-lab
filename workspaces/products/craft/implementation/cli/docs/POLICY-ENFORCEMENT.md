# Reuse an eligibility decision without hiding why it failed

A business often asks the same question in more than one place: may this contact be updated, may this article be published, or may this order proceed? A Rule answers a Boolean question. A Policy combines those questions into an ordered decision. An Operation consumes the decision when it is about to perform its work.

`enforce` connects these existing concepts. It evaluates a typed Policy result once. `Allow` continues the Operation; `Reject(reason)` ends it through the existing business-rejection channel with the declared code. The Policy itself remains a pure computation. Calling the Policy to inspect its value does not reject an Operation; enforcement is explicit at the Operation site.

## Begin with a small publication example

The complete [business module](../examples/policy-enforcement/publication.alch) declares a reason enum, an admission result, supporting Calculations, a Policy and an Operation. These are ordinary existing meta-types:

```alch
enum PublicationRejection:
  value ApprovalMissing wire "approval-needed"

enum PublicationAdmission:
  variant Allow
  variant Reject reason PublicationRejection
```

The rejection enum's explicit wire is the public failure code. Its name is meaningful to the author; renaming that name need not change the public code. Do not mix `value Allow` with `variant Reject` in the same enum: this ordinary result uses consistent variant syntax.

The two declared Calculations construct values of that result type:

```alch
calculation AllowPublication:
  pure
  result PublicationAdmission
  expression PublicationAdmission.Allow()

calculation RejectPublication:
  pure
  input reason PublicationRejection
  result PublicationAdmission
  expression PublicationAdmission.Reject(reason=reason)
```

The Policy chooses between those computations. `Approved` is explicitly declared as a Rule in the complete example; no function is implicitly created:

```alch
policy PublicationEligibility:
  input approved Bool
  result PublicationAdmission
  ordered-cases:
    approvalMissing when not Approved(approved=approved) -> RejectPublication(reason=PublicationRejection.ApprovalMissing)
    otherwise -> AllowPublication()

operation Publish:
  input approved Bool
  output Bool
  enforce PublicationEligibility(approved=approved)
  return approved
```

With `approved: false`, the Operation returns the existing `Rejected` outcome with code `approval-needed`. With `approved: true`, it continues and returns `true`. This deliberately small pure example demonstrates the language connection; it does not authenticate a user or publish a real document. In a protected application the original owners assemble trustworthy approval facts and still enforce current authorization.

## What makes an admission result valid?

The result is an ordinary named enum. Its name can be yours; it is not a new Admission MetaType. At an enforcement site, Craft checks this finite contract:

- Exactly `Allow` with no payload and `Reject` with one field named `reason`.
- `reason` names a separate finite enum of nullary values.
- Every reason has an explicit unique wire code satisfying the existing FailureCode contract: 1–128 ASCII identifier characters, `^[A-Za-z_][A-Za-z0-9_-]*$`.
- The invocation resolves to an actual checked Policy. A Bool, arbitrary Text, caller-created JSON verdict or provider action/delay result is not an admission Policy.

Craft derives the finite reason-to-code table. There is no unchecked runtime string converted into a rejection. Original value-returning Policies such as choosing an owner ID continue to use `result` and `ordered-cases` unchanged. No `decision:` block or second Policy evaluator is introduced.

## Keep the order and the point of enforcement

Cases are ordered. The first matching denial wins, and later predicates and branch actions are not evaluated. The Policy runs once per reached enforcement site, using the invocation's existing computation budget. Extra calls and constructors can consume more fuel than inline guards; identical fuel or timing is not promised.

Input decoding, refinement/invariant failure, fuel/depth exhaustion, stale source and other computation faults retain their original error channel. They do not become a business denial and never default to Allow.

The initial supported placement is a pure Operation body or supported stateful preflight before effects, including supported conditional preflight. Enforcement inside a transaction, or after an incoming path has already performed a write, event emission or commit, is rejected. A denial stops later work; it does not undo earlier workflow stages. A future transaction-body extension needs its own rollback and unknown-outcome semantics.

For example, an AI-assisted CRM can retain its existing sequence: obtain a proposal, record exact approval, evaluate contact-update eligibility, then attempt the external update. Extracting eligibility into a Policy does not move it before the proposal stage or after the write. An unknown accepted write still requires inspection by its original effect owner, even if a later authored Policy would otherwise permit another update.

## What Craft generates and what remains yours

Craft checks the source, binds the typed Policy and finite rejection table, and generates the selected Operation continuation using the original computation and rejection machinery. Source/profile capability selection must explicitly support `operation-policy-enforcement`; grammar recognition does not qualify every backend or installed package. Unsupported consumers refuse the feature rather than omit it.

The business author supplies meaningful Rules, ordered decisions, stable public rejection codes and the enforcement point. Existing Entry permissions remain beside the Entry. Operators still supply accounts, credentials and runtime resources. `Allow` grants no authorization, release capability, provider permission or durable certificate; original Auth, currentness, replay, transaction and effect checks remain active.

Formal claims are optional. No claim is needed to generate this example. A formal exporter that cannot represent the statement must report that limit instead of silently dropping it. Static graph links show which Policy and declarations implement a condition; only actual runtime observation can say which branch executed.

## Current verification boundary

The selected implementation's focused checks and final consolidated result, rather than the older pre-enforce compiler result, determine which paths are verified. The [implementation DAG](/home/vlad_/projects/cyberAlchemy-v2/goals/plans/craft-policy-enforce-2026-11-01/DAG.md) owns completion status. Local fixture success is separate from live-provider or model-quality qualification.

## Open Questions

Inside-transaction enforcement, aggregation of all rejection reasons, a shorthand admission DSL, arbitrary result adapters and direct Policy-to-Policy branch syntax remain deferred. Local hosting, TDE, EVF, deployment and publication remain deferred. This example does not change the frozen public release.
