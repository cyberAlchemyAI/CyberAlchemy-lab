# AlchLang syntax and meaning

The [step-by-step Craft guide](../../COMPLETE-GUIDE.md) shows how AlchLang declarations connect inside Customer Success. Use this page to look up the syntax after seeing that application. The same `module`, `value-object`, and `rule` shapes also appear in the complete [ReviewDesk Rule](../guide/alchlang.md#start-with-one-rule) and the larger [ReviewDesk API](../../implementation/alchlang/examples/generic-http/business.alch). This reference covers that **generic application path**. The compiler and selected profile decide exact acceptance, limits, and diagnostics. The [Core generic guide](../../implementation/cli/docs/GENERIC-APPLICATIONS.md) describes cumulative features. The older `application-v1` `domain`/`owner` file format has a [separate reference](../../implementation/alchlang/docs/LANGUAGE.md). Do not combine their headers or profile formats.

## File shape

```alch
module CustomerSuccess version 1

value-object AccountSnapshot:
  accountId UInt64
  licensedSeats UInt64
  activeSeats UInt64

rule HasLicensedSeats:
  input account AccountSnapshot
  expression account.licensedSeats > 0
```

`module` qualifies names, such as `CustomerSuccess.HasLicensedSeats`. Top-level declarations end in `:` and their clauses are indented. The separately checked [technical profile source](../../implementation/cli/examples/technical-profile-source/architecture-shared.alch) shows `use Profiles.Library.Node, Edge` for names from another source file. An import needs that file in the checked source closure.

The working examples keep one declaration or clause per line, use two-space indentation for bodies, and use `#` for full-line comments. Names such as `CustomerSuccess.ReviewRenewalEntry` identify an Entry in a module; a `use` declaration resolves a checked name from another source. In expressions, strings are quoted, Boolean literals are `true` and `false`, and enum values are named symbols. The parser checks syntax first; semantic checks then resolve names, types, required clauses and profile support.

## Types and values

| Form | Meaning | Example |
| --- | --- | --- |
| `Bool`, `UInt64`, `String` | Checked scalar types. Generic generated JSON carries `UInt64` as a decimal string. | `accountId UInt64` |
| `value-object` | A value made from its fields. | `value-object AccountSnapshot:` |
| `entity` | A stored object with declared identity; needs a stateful profile. | `identity accountId` |
| `enum` | A finite choice. Supported forms include values and typed variants. | `value Renew`; `variant Reject reason ReviewRejection` |
| `optional<T>` | A value or absence. | `optional<AccountSnapshot>` |
| `List<T,N>` | Bounded collection. | `List<Activity,16>` |

The Customer Success source also declares a validated string:

```alch
value-object Text:
  carrier String
  utf8-bytes 0..4096
  unicode-scalars 0..1024
```

The selected profile must admit the required value and collection features. Its bounds cannot silently change authored source constraints.

The [ReviewDesk decision source](../../implementation/alchlang/examples/generic-decision/business.alch) also uses `pattern "^[a-z0-9]{1,16}$"` on a bounded string and `invariant amount > 0` on a value object. These are checked when values are decoded or constructed. Its `outcome<ApprovalState,Bool,0>` is the typed zero-intent result of a state proposal, not a stored transition.

## Expressions and calls

Working generic source uses field paths (`account.activeSeats`), literals, comparisons (`>`, `<=`, `==`, `!=`), Boolean operators (`and`, `or`, `not`), arithmetic, typed calls, and bounded collection functions. Calls name inputs: `HealthScore(account=account)`. The Customer Success source uses `length`, `filter`, `map`, `fold`, and `all-unique-exact`. The exact supported operator and type combinations belong to the selected compiler/profile pair; arithmetic can fail instead of silently overflowing.

```alch
calculation HealthScore:
  pure
  input account AccountSnapshot
  result UInt64
  rounding floor
  expression account.activeSeats * 100 / account.licensedSeats + fold(account.activities,0,total:UInt64,item:Activity => total + item.adoptionPoints)
```

The separate `AccountNumbersValid` Rule requires a positive `licensedSeats` before the intended call path divides by it.

## Declaration index

| Declaration | Purpose | Typical clauses |
| --- | --- | --- |
| `value-object`, `enum`, `entity` | Values, choices, and stored identities. | Fields, `value`, `variant`, `identity` |
| `rule` | Reusable Boolean condition. | `input`, `expression` |
| `calculation` | Pure typed computation. | `pure`, `input`, `result`, `rounding`, `expression` |
| `policy` | First matching ordered case and fallback. | `result`, `ordered-cases`, `when`, `otherwise` |
| `mapping` | Construct a target value. | `target`, `total true`, `field ... <- ...` |
| `query` | Read and project a declared source. | `source`, `where`, `project`, missing/unavailable handlers |
| `operation` | Check, read, call, return, or perform admitted effects. | `requires`, `enforce`, `read`, `call`, `transaction`, `return` |
| `entry` | Callable boundary and access requirement. | `invokes`, `interaction`, `access` |
| `state-machine`, `workflow` | State proposal or supported workflow. | See [ReviewDesk decision](../../implementation/alchlang/examples/generic-decision/business.alch) and [Workflow guide](../../implementation/cli/docs/GENERIC-APPLICATIONS.md#open-a-generated-workflow-through-the-public-api). |

The broader backend concept set also names **Interface** and **Event**. Technical source profiles use an `interface Family:` declaration to state their boundary, as the [shared-port source](../../implementation/cli/examples/technical-profile-source/architecture-shared.alch) shows. Other application profile paths may use Event and Workflow declarations. Their available clauses and execution depend on that path's selected backend; use the [compatibility declaration reference](../../implementation/alchlang/docs/LANGUAGE.md#declaration-clause-index) and the matching example rather than assuming they are supported by the generic Rule profile.

The generic path is cumulative: the small ReviewDesk example admits a Rule, the decision example adds pure computation and state proposal, and the HTTP example adds protected Entries and storage. A declaration existing in the language does not mean every profile can execute it.

### Rules, policies, and mappings

```alch
rule AccountNumbersValid:
  input account AccountSnapshot
  expression account.accountId > 0 and account.licensedSeats > 0 and account.activeSeats <= account.licensedSeats

policy SuggestedAction:
  input account AccountSnapshot
  result RenewalAction
  ordered-cases:
    escalated when account.openEscalations > 0 -> Support()
    underused when account.activeSeats * 2 < account.licensedSeats -> Adoption()
    otherwise -> Renewal()

mapping ToRenewalReview:
  input account AccountSnapshot
  input request ReviewRequest
  target RenewalReview
  total true
  field reviewId <- request.reviewId
  field accountId <- account.accountId
  field healthScore <- HealthScore(account=account)
```

The policy takes the first matching case. `otherwise` is its fallback. `total true` requires a complete target. The Rule and Mapping above are shortened teaching examples; the [full source](../../implementation/cli/examples/technical-profile-source/customer-success-example/business.alch) contains the complete conditions and assigns every target field.

### State proposals

The [ReviewDesk decision](../../implementation/alchlang/examples/generic-decision/business.alch) defines a guarded state machine and calls it from a pure Calculation:

```alch
state-machine Approval:
  state ApprovalState
  input ApprovalSignal
  initial Draft
  terminal Approved
  transition Draft Submit when CanApprove(state,event) -> Approved
  transition Draft Submit when true -> Review
  transition Approved Hold -> Approved
  otherwise stay

calculation ProposeApproval:
  pure
  input request Request
  result outcome<ApprovalState,Bool,0>
  expression Approval.propose(request.state,request.signal)
```

Guards run in source order. `otherwise stay` handles unmatched inputs. The returned proposal does not persist the new state; an admitted Operation and stateful profile would be needed for a write. A Workflow is a separate capability with its own source and runtime contract; see the [generic Workflow guide](../../implementation/cli/docs/GENERIC-APPLICATIONS.md#open-a-generated-workflow-through-the-public-api).

### Queries, operations, and transactions

```alch
query ReadAccount:
  input accountId UInt64
  source stored StoredAccount
  output optional<AccountSnapshot>
  where stored.accountId == accountId
  project stored.value
  on-missing return none
  on-unavailable fail account-unavailable

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

`reject` is a business rejection; `fail` denotes a failure such as unavailable storage or unknown commit. `EvaluateRenewal` enforces eligibility before this write. The stateful profile supplies the transaction implementation and command replay. A pure profile cannot execute this operation just because its syntax parses. See the [complete source](../../implementation/cli/examples/technical-profile-source/customer-success-example/business.alch) and [generic transaction guide](../../implementation/cli/docs/GENERIC-APPLICATIONS.md#commit-the-decision-atomically-c08-candidate).

### Entries and access

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

An Entry is callable; its Operation remains business behavior. These are authored access requirements. The selected profile chooses a supported Auth bridge, and the host must supply its real Auth resource. An HTTP route maps to the Entry but grants no access by itself.

## Compatibility file format

The older `alchlang check` / `build` path uses a different document header. The [compatibility reference](../../implementation/alchlang/docs/LANGUAGE.md) documents its lexical rules, top-level grammar, clause cardinalities and 13 backend concepts. A compatibility file begins with `domain` and `owner`, and a canonical `application-v1` source selects that profile. Historical `legacy-sfol-v1` source also uses `logic sfol-v1`. Those clauses are **not** the header for the generic `module CustomerSuccess version 1` examples above. A source file should follow the syntax and selected profile of one command path.

## Files around the source

Business source, computation bounds, application capability profile, HTTP profile, and technical source envelope are separate inputs with versioned schemas. [Profiles and profile creation](../guide/alchlang-profiles.md) explains them. The [AlchLang overview](../guide/alchlang.md#choose-the-command-path) maps command families.
