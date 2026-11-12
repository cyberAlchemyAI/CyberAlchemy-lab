# Craft, from one decision to an application

This guide follows one question all the way through: **should a customer account be recommended for renewal, and can a reviewer save that decision?** We will start with the business example, meet the meta types as they become useful, see their AlchLang declarations, then run the generated application in a local test. The [source files](implementation/cli/examples/technical-profile-source/customer-success-example/README.md) are part of this workspace.

## 1. Start with the result we want

The Customer Success example has an account with **8 active seats out of 10 licensed seats**. Two recorded activities contribute **5 and 10 points**. The authored score is therefore `80 + 5 + 10 = 95`. With no open escalation, the authored policy suggests **Renew**. A reviewer may approve that recommendation for account version **3**; an attempted review of version **2** must be rejected as stale.

The review request also carries a short discussion and references to its source material. The local [review cases](implementation/cli/examples/technical-profile-source/customer-success-example/fixtures/business-cases.json) provide that context; the connected cited-answer path has additional provenance checks. These are teaching rules, not a prediction or an industry standard. The point is that every result has a named input and a rule we can inspect. The [account fixture](implementation/cli/examples/technical-profile-source/customer-success-example/fixtures/account.json) contains the account values.

## 2. What Craft does

Craft helps a team keep **business meaning**, **application construction**, and **observed behavior** connected:

1. The team writes the account shape, validity conditions, score, recommendation, review action, and access requirements.
2. Craft checks those declarations and combines them with selected profiles for supported storage, HTTP, and Auth behavior. It generates an application candidate.
3. A local exercise runs that candidate with named account and review inputs. The result tells us what happened for those inputs.

Craft does not choose the renewal policy for the team. The generated application also needs a real host and resources before production use. In this guide, Auth and SQLite resources are local test fixtures.

## 3. Meta types give each part a job

A **meta type** says what role a declaration has in an application. For example, an account snapshot is a value, a saved account has an identity, a Rule answers yes or no, and an Operation performs an action. This vocabulary lets Craft check connections instead of treating every declaration as an arbitrary class or function.

The Customer Success application uses these nine of the 13 active backend meta types:

| Meta type | Plain meaning | Customer Success part |
| --- | --- | --- |
| **Value Object** | A value described by its fields. | `AccountSnapshot`, `Activity`, `ReviewRequest`, `RenewalReview` |
| **Enum** | One choice from a named set. | `Renew`, `AdoptionReview`, `SupportReview` |
| **Entity** | A stored thing with a stable identity. | `StoredAccount`, `StoredRenewalReview` |
| **Rule** | A yes-or-no condition. | `AccountNumbersValid`, `CitedContextWellFormed` |
| **Calculation** | A typed value computed from inputs. | `HealthScore` |
| **Policy** | A decision selected from ordered cases. | `SuggestedAction`, `RenewalEligibility` |
| **Mapping** | A translation into a target value. | `ToRenewalReview` |
| **Query** | A declared read of stored information. | `ReadAccount` |
| **Operation** | A declared action and result. | `EvaluateRenewal`, `ReviewRenewal` |

The other four backend meta types are useful in other applications: an **Interface** describes an exposed boundary, an **Event** names something that happened, a **State Machine** describes legal state changes, and a **Workflow** coordinates ordered work. They are part of the model, but this Customer Success business file does not need to declare them. Availability in generated code still depends on the selected profile. The [plain-language glossary](docs/reference/concepts.md) covers all 13; UI meta types have separate candidate standing.

An AlchLang **Entry** is the named callable boundary for an Operation or Query. It carries an access requirement. An Entry is not a fourteenth backend meta type. A **profile** is also separate from the meta types: it selects *how supported declarations are built and run*.

## 4. Connect the parts into an application

Follow one review request from the outside in:

1. `CustomerSuccess.ReviewRenewalEntry` receives a request and requires the declared review permission.
2. Its `ReviewRenewal` Operation reads the actual stored account through `ReadAccountEntry` and the `ReadAccount` Query.
3. `EvaluateRenewal` enforces the `RenewalEligibility` Policy. That Policy uses Rules to check the account and cited context, checks the account version, compares the proposed action with `SuggestedAction`, and requires an explicit approval choice.
4. `ToRenewalReview` maps the accepted request and account into a `RenewalReview`. It calls `HealthScore` and `SuggestedAction` for two of its fields.
5. `ReviewRenewal` atomically creates `StoredRenewalReview` and returns the saved value.

The connection is the important part: a score alone does not save a review, and an HTTP route alone does not decide whether a review is allowed. The [full business source](implementation/cli/examples/technical-profile-source/customer-success-example/business.alch) declares these links. The selected profiles and local host complete the application around them.

## 5. Write those parts in AlchLang

AlchLang is the `.alch` language used to author this supported business model. Its first line names a module and version. The following excerpts are from the [actual Customer Success source](implementation/cli/examples/technical-profile-source/customer-success-example/business.alch); each section shows one connection, while the full file contains every required field and handler.

### Give the account a shape and a stored identity

```alch
module CustomerSuccess version 1

enum RenewalAction:
  value Renew
  value AdoptionReview
  value SupportReview

value-object Activity:
  sourceId UInt64
  version UInt64
  adoptionPoints UInt64

value-object AccountSnapshot:
  accountId UInt64
  version UInt64
  licensedSeats UInt64
  activeSeats UInt64
  openEscalations UInt64
  activities List<Activity,16>

entity StoredAccount:
  accountId UInt64
  value AccountSnapshot
  identity accountId
```

`RenewalAction` limits the suggested result to three named choices. `AccountSnapshot` is the account value supplied to the decision. `StoredAccount` says how a saved copy is identified and later found. `List<Activity,16>` makes the activity collection bounded. The source's `rule AccountNumbersValid:` declares `input account AccountSnapshot` and a Boolean `expression` that checks IDs, versions, seat counts, and activities before storage or review.

### Calculate a score and choose an action

```alch
calculation HealthScore:
  pure
  input account AccountSnapshot
  result UInt64
  rounding floor
  expression account.activeSeats * 100 / account.licensedSeats + fold(account.activities,0,total:UInt64,item:Activity => total + item.adoptionPoints)

policy SuggestedAction:
  input account AccountSnapshot
  result RenewalAction
  ordered-cases:
    escalated when account.openEscalations > 0 -> Support()
    underused when account.activeSeats * 2 < account.licensedSeats -> Adoption()
    otherwise -> Renewal()
```

The Calculation produces **95** for the fixture. The Policy checks cases in order and selects **Renew**. The source also declares `RenewalAction` and the small `Support`, `Adoption`, and `Renewal` Calculations that return its enum values.

### Require a valid review, then build and save it

```alch
operation EvaluateRenewal:
  input account AccountSnapshot
  input request ReviewRequest
  output RenewalReview
  enforce RenewalEligibility(account=account,request=request)
  return ToRenewalReview(account=account,request=request)

query ReadAccount:
  input accountId UInt64
  source stored StoredAccount
  output optional<AccountSnapshot>
  where stored.accountId == accountId
  project stored.value
  on-missing return none
  on-unavailable fail account-unavailable
```

`RenewalEligibility` is a Policy, not an approval flag: it rejects a stale account version, an action different from `SuggestedAction`, invalid cited context, or a declined review. The `Mapping` declaration connects accepted inputs to a complete result:

```alch
mapping ToRenewalReview:
  input account AccountSnapshot
  input request ReviewRequest
  target RenewalReview
  total true
  field reviewId <- request.reviewId
  field accountId <- account.accountId
  field accountVersion <- account.version
  field healthScore <- HealthScore(account=account)
  field action <- SuggestedAction(account=account)
  field discussion <- request.citedContext.answer
  field citations <- request.citedContext.citationIds
  field evidence <- request.citedContext.evidence
```

`total true` requires every field of `RenewalReview` to be provided. The [complete declarations](implementation/cli/examples/technical-profile-source/customer-success-example/business.alch) also show the eligibility policy and its Rules.

The final Operation connects that pure decision to a protected read and an atomic write:

```alch
operation ReviewRenewal:
  input request ReviewRequest
  output RenewalReview
  read account from CustomerSuccess.ReadAccountEntry(accountId=request.accountId)
    on-missing reject account-missing
    on-unavailable fail account-unavailable
  call accepted EvaluateRenewal(account=account,request=request)
  transaction RecordReview:
    atomic-participants StoredRenewalReview
    create stored StoredRenewalReview:
      reviewId <- request.reviewId
      value <- accepted
    on-unique-conflict reject review-already-recorded
    on-proven-rollback fail storage-rolled-back
    on-unknown-commit fail outcome-unknown
  return stored.value
```

The Entry makes this Operation callable and states its access requirement:

```alch
entry CustomerSuccess.ReviewRenewalEntry:
  invokes CustomerSuccess.ReviewRenewal
  interaction request-response
  access:
    authenticated customer
    permission renewal.review
    auth-resource renewal
    auth-action review
    auth-scope customer-success
```

The HTTP profile maps this Entry to `POST /api/renewal-reviews`. The permission stays in the authored Entry; the route does not grant it.

## 6. Supply the rest of the application

The business source describes meaning and behavior. The [application profile](implementation/cli/examples/technical-profile-source/customer-success-example/contracts/selected-profile.json) selects supported Node, SQLite transaction, command replay, limits, and Auth mechanisms. The [HTTP profile](implementation/cli/examples/technical-profile-source/customer-success-example/contracts/http-profile.json) selects methods, paths, Entries, and response Mappings. A [protected service layout](implementation/cli/examples/technical-profile-source/protected-ServiceAssembly.profile.json) groups the generated Entries. The host supplies actual Auth actors and storage.

That gives a whole local application path:

```text
account and review inputs
  → checked AlchLang declarations
  → selected application, HTTP, and service profiles
  → generated protected service and graphs
  → local Auth and SQLite fixtures
  → observed response and saved review
```

The [example project file](implementation/cli/examples/technical-profile-source/customer-success-example/example-project.json) lists the exact source/profile arguments. It is a readable container for this example, not a new AlchLang syntax.

## 7. Run the example and read the result

From the Lab root in the configured Linux environment, [build the local Craft source](implementation/README.md) once. Then run the focused portfolio test:

```sh
node workspaces/products/craft/implementation/run.mjs build
CRAFT_PORTFOLIO_LIBRARY_ROOT="$PWD/workspaces/products/craft/implementation/cli/examples/technical-profile-source" \
  node --test --test-name-pattern=generated.customer-success.domain \
  workspaces/products/craft/implementation/verification/portfolio-business-applications.test.mjs
```

This test checks and generates the Customer Success application, opens its protected local runtime, records the account, submits the review, reads the saved result, and checks rejection cases. The current focused run passed: **1 test, 0 failures**. Its [business cases](implementation/cli/examples/technical-profile-source/customer-success-example/fixtures/business-cases.json) expect score `95` and action `Renew`; a request for account version `2` is rejected with `account-version-stale` and is not saved. It also checks permission denial and command replay.

This is local behavior evidence using fixture Auth and SQLite. It does not establish a live CRM read, production identity setup, model quality, hosting, or permission to deploy. The connected cited-answer path has separate checks and source-release requirements described in the [application example](implementation/cli/examples/technical-profile-source/customer-success-example/README.md).

## Continue from here

- [AlchLang syntax](docs/reference/alchlang-syntax.md) explains types, expressions, declarations, and the different command paths in detail.
- [Profiles and creating a profile](docs/guide/alchlang-profiles.md) starts with one small editable profile, then covers reusable technical profiles.
- [Contract Workbench](implementation/cli/examples/technical-profile-source/contract-workbench-example/README.md) applies the same approach to comparing supplied contract editions.
- [ReviewDesk](implementation/alchlang/examples/generic-http/README.md) shows a smaller protected approval API.
