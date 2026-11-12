# Craft concepts in plain language

The [step-by-step Craft guide](../../COMPLETE-GUIDE.md) shows these terms working together in Customer Success. Use this page as a lookup after following that example. Its business rules are teaching inputs, not a real company's renewal policy.

| Term | Plain meaning | Customer Success example |
| --- | --- | --- |
| Product | An offering with a purpose and promised value. | Craft is the Product used to build the example application. |
| Product Feature | A piece of intended value being shaped for a Product. | Renewal review is a feature of the example application; Craft's own proposed features are separate. |
| Product Capability | A stable outcome the Product claims it can provide, subject to its standing. | Generating a supported application path is a described Craft capability; the catalog currently has proposal-only standing. |
| Authority | The responsible source of meaning, contracts, and decisions. | The business owner decides what makes an account eligible for renewal. |
| Value Object | A value described by its fields. | `AccountSnapshot` holds one account edition and its activity. |
| Enum | One named choice from a set. | `RenewalAction` can be `Renew`, `AdoptionReview`, or `SupportReview`. |
| Entity | A stored thing with a stable identity. | `StoredAccount` is identified by `accountId`. |
| Rule | A yes-or-no condition. | Whether the stored account and proposed review meet declared conditions. |
| Calculation | A value derived from inputs. | The example score of 95 from seats and activity. |
| Policy | A choice among ordered cases. | Suggest `Renew`, `SupportReview`, or `AdoptionReview`. |
| AlchLang | An authored language for supported business types and behavior in `.alch` files. | `business.alch` declares the account, score, action policy, and review operation. |
| Query | A declared read of information. | `ReadAccount` selects the account edition; its Entry requires access. |
| Operation | An action with a declared result. | Save a permitted review of the recommendation. |
| Mapping | A declared translation into a target value. | `ToRenewalReview` builds the saved review from the account and request. |
| Interface | A contract for an exposed boundary. | Not declared in the Customer Success business file; technical profile sources use Interfaces. |
| Event | A named occurrence that an application can report. | Not needed by this example's business file. |
| State Machine | The legal changes between named states. | Not needed by this example's business file. |
| Workflow | Ordered work across steps and outcomes. | Not needed by this example's business file. |
| Profile | A selected implementation recipe for supported source. | Choose the protected service, storage, and HTTP behavior. |
| Entry | A named point where a caller can request a Query or Operation. | `ReviewRenewalEntry` invokes the review Operation. |
| Protected | Requires the declared access checks before an Entry can run. | The reviewer needs the review permission. |
| Auth | The host's identity and permission service used by protected Entries. | The local exercise supplies test actors; a real host must supply its own service. |
| Source context | The material and editions used to support a result. | The saved review keeps citations and source editions with the discussion. |
| Evidence | What a check or observation showed, with its conditions and limits. | A local test shows the generated application saved and read a review for named inputs. |

Entity, Value Object, Enum, Operation, Query, Calculation, Rule, Policy, Workflow, Interface, Event, Mapping, and State Machine are the **13 active backend meta types**. Entry and Profile have different jobs in the current AlchLang path; they are explained above and in the [guide](../../COMPLETE-GUIDE.md#3-meta-types-give-each-part-a-job). UI meta types have separate candidate standing.

Craft also separates Product from the **Project** that coordinates its development and the **Work** currently being done. Its **Ontology** organizes meanings and views; **Architecture** selects system structure; **Implementation** contains the executable source. None of these replaces the business owner's decision.

The [current definitions](../../authority/definitions/README.md), [Product overview](../../product/PRODUCT.md), and [Use Craft today](../guide/current-usage.md) provide more detail behind this short explanation.

