# Direct-Rule successor contract (U0)

Contract-only implementation at C01. Core owns `contracts/business-spec-v2.schema.json` and `src/profile-engine/business-authoring-protocol-v2.ts`; Alch has a generated data-only mirror. This does not register a parser/resolver/selection, native generator or genuine checked handle yet.

The source starts with `source-contract alchlang.business-spec/v2-candidate`. A domain `version` remains business version, not syntax dispatch. The v1 parser/source contract retains its meaning. The explicit header dispatches to the successor only after U01 integration.

The exact zero-claim contract source is `test/profile-engine/fixtures/u0-v2/business.alch`. Its DTO is a schema witness; the actual parser must reproduce source facts and selectors at U01. It has one two-field Entity (exact UInt64 identity and Bool flag), one Rule, one guarded identity-return/no-effect Operation and one public logical entry. The Rule's required `condition item.verified` supplies execution. `requirement` links its declared business intent; a missing condition is never filled from a claim or fixture.

The v2 Operation retains the explicit `requires`, `returns`, `on-rejection` and `effects none` clauses. An entry uses `invokes`, `public-name`, and `permission public`. Permissions remain with the entry. Protected/resource/service/event entry realizations are later qualified work. A transport binding is derived separately from the entry and profile.

`definition` and existing `formal-claim` clauses are optional in v2. Optional claim syntax retains the established v1 finite FOL profile/interpretation clauses and adds one or more `subject RuleOrOperationId` lines, represented as `subject_refs`. They are captured assurance data only; they never supply executable Rule meaning or bypass review. Missing/unsupported native formal output rejects only when selected as required. TDE/EVF and U1 formal-language projection/format validation are outside C01 and remain deferred/unselected.

The closed schema rejects old claim-ref Rules, omitted conditions, extra executable hooks, protected entry assertions, nonempty effects and result paths other than the entire input. Dynamic declaration/type/field/parameter/reference correspondence is checked independently by Core at U03/L02. JSON Schema validation alone does not satisfy those obligations or authenticate custody. Neither an `accepted` flag nor a matching digest forms a registered handle.

The executable projection includes model identity, requirement context/examples/boundaries, Entity shape, Rule input/condition/requirement, Operation guard/result/rejection/effects and logical-entry permission. Definitions/claims have their own assurance projection. Exact captured source/tool/profile bytes and later native realization identities are separate. C02 fixes canonical field/order/currentness contracts. Source/prose changes recapture and invalidate old handles even when some executable fields compare equal.

## Open Questions

C02/C03/C04/J00 close exact stage identities, native ABI, output/coverage contracts and schema/export integration. U01/U03 implement actual parse/check owners. The first U0 cell does not claim broader meta-types, arbitrary expressions, protected access, effects or hosting. All future source/version transitions must preserve exact v1 semantics.
