# Business input and profile selection

Status: versioned v1 and v2 candidate construction contracts. Profile engine implementation and installed qualification are tracked by the PE tasks; this contract alone is not a release claim.

Craft checks the domain's entities, relationships and behavior. AlchLang expresses that behavior in source files. A profile supplies supported technical choices such as transport, component ownership, routes and error serialization. The user supplies business sources and explicit public-operation/external-read intents, then selects a profile package. External API wire contracts and operator values are necessary inputs as described below.

For the one-entry, zero-function application path, use [business-only applications](BUSINESS-APPLICATIONS.md). That v2 carrier supplies explicit business meaning/definitions/owner decisions and generates its own empty-effects settlement. The v1 function-service and application_calls compatibility rules below remain distinct. [Create a v2 profile](PROFILE-PACKAGES.md#create-a-v2-api-prefix-profile-without-compiler-changes) using finite rules and locked assets.

## What the user writes

The closed `craft.profile-project/v1` input references relative domain `.alch` sources, distinct public intents, external reads, formal claims, external contract configuration and selected packages. Domain source contains the existing business declarations: domain/owner/logic, entities, schemas, calculations, rules, mappings, policies and result behavior supported by the selected lowering adapter. It does not contain generator profile selection, technical endpoint/service declarations, native imports, transport/runtime choices, environment slots, routes, execution/interpretation companions or native code. Unsupported required declarations reject explicitly rather than being ignored.

Each public intent identifies its source, input/output schema and result, plus explicit public access or a named supported business authorization policy. It classifies each authored output status as success or business rejection; profiles map those classes to HTTP status conventions. No HTTP status is handwritten in the business contract. Authentication mechanism defaults never grant permission. A policy reference must resolve to checked business behavior; unsupported authorization rejects. Every generated entry must originate in an authored intent and reach that checked behavior. Initial service-v1 supports 2–32 entries: one-entry input is unsupported until a separately qualified core change. Extra generated health/description endpoints and aliases presented as independent intents are forbidden.

An external read names a business dependency, expected output schema and requested input fields. It grants no network access during generation. Its result binding, guard, calculation and named business failures stay in business source. Formal claims name exact source selectors and statements; authored claims remain unproved until separate evidence supports a stronger state. A model cannot label its own claim proved or admitted.

## External API configuration and operator values

`craft.integration-configuration/v1` binds an authored read to an exact wire schema/version/digest, GET operation/location reference and supported typed field projection/rename. It specifies missing/extra-field policy and value compatibility. It cannot compute prices, convert units, grant permission, run custom code, retry/write remotely or reinterpret business failure meaning. Such behavior must be expressed in checked business source using supported primitives, or generation rejects it.

The location reference is declarative integration configuration. Profiles derive environment slot names; operators supply actual destinations and secrets later. URLs/tokens/environment values never enter the source fixture or generated evidence. Public access is explicit in this example; future selected authentication mechanisms cannot change it silently.

## Illustrative quote contract and semantic expectations

[test/profile-engine/fixtures/quote-business](/home/vlad_/projects/cyberAlchemy-v2/craft/projects/domainspec-v2/impl/cli/test/profile-engine/fixtures/quote-business) provides an independent business example, not a user's live inventory contract. `requestQuote` reads inventory and returns exact price × quantity when stock suffices; otherwise total is zero and status unavailable. Requested quantity is 1–100 and returned SKU must match. `describeQuotePolicy` returns those business bounds and unavailable-total convention. Both operations are explicitly public, independently authored and independently tested. The oracle defines success, insufficient stock, zero price, quantity boundaries, mismatched SKU and policy behavior before generator implementation.

Coverage identities include every selected business declaration/clause, validated public intent/access policy, integration field binding, formal claim and required generated role. Each maps to retained checked behavior/artifact, explicit unsupported rejection, or formal claim residue with reason. Linked/generated/static-checked/finite-observed/proved/admitted states remain separate. Generated technical defaults are recorded independently from authored constraints; conflicts reject. Existing fully technical Alch service examples are compatibility fixtures rather than evidence of this new authoring contract.

## Contract rejection names

Validators use stable names: `PROFILE_TECHNICAL_SOURCE_FORBIDDEN` for authored technical clauses, `PROFILE_PUBLIC_INTENT_UNKNOWN_REF` for unresolved intent schemas/results, `PROFILE_AUTH_POLICY_UNSUPPORTED` for unresolved or unsupported required authorization, `PROFILE_WIRE_CONTRACT_REQUIRED` for an unbound external read, and `PROFILE_BUSINESS_CONSTRAINT_CONFLICT` when a technical default conflicts with authored constraints. Schema validation rejects extra input properties, missing policies, invented proof fields and one-entry envelopes. PE02/04 implement these runtime diagnostics; this contract defines their meaning.

## Supported and unsupported roles

| Role | Initial target | Unsupported requirement behavior |
|---|---|---|
| Domain policy/calculation/mapping | Existing checked declarative primitives | Reject unsupported syntax/relationship; no native feature glue |
| Public entry | Two distinct intent-linked Node HTTP entries | Reject invented entries, one-entry input or unresolved policy |
| External dependency | One-shot read-only supported HTTP wire contract | Reject custom executable mappings, writes, arbitrary providers |
| Architecture | Registered entry-local/shared-port recipe vocabulary | New primitives require core changes, not per-profile dispatch |
| System/bridge view | Derived checked plan, origins and coverage | No new canonical ontology or admission |
| Operational expectation | Optional ORODI declaration contract | No inference of live observation/accounting/eligibility |

## Open Questions

PE01 owns actual callable compatibility, PE04 lowering, PE08 final checker coverage and PE09 denominator validation. [The supported profile vocabulary](PROFILE-PACKAGES.md#open-questions) owns broader feasibility. Local hosting, TDE, EVF and publication remain deferred. User-facing packaging will retain local public links rather than private research pointers.

## Profile package and trace contracts

`craft.profile-package/v1` pins package ID/version, engine contract, exact dependency references/digests, role descriptor/recipe mappings, resource budgets, declarative rules, owned asset digests and a fixed reject-on-conflict policy. Rules are finite select/project/join/traverse/require-one/defaults/emit forms. Values use literals, field paths and bounded string concatenation; no arbitrary functions, expressions, recursion, evaluator JavaScript or package build commands are accepted.

Template assets declare identifier/string/JSON/import-path holes and owned includes; native runtime assets cannot declare template holes/includes. Include cycles, unowned includes and unsupported signatures reject. Native assets are not loaded as compiler/evaluator plugins. Their later controlled qualification does not certify arbitrary native code as sandbox-safe.

The role catalog distinguishes exact existing generator descriptors (`declarative-function-v1`, `service-v1`, `typescript.bound-operation/v1`) from candidate engine-owned entry/shared-port/read/environment/expectation roles. A descriptor ref is not an implemented recipe or factory admission. Exact supported descriptor/recipe pairs are required; new primitives/role contracts need core qualification. Missing mappings cannot be repaired with fabricated admitted refs.

`craft.profile-lock/v1` binds sources, core/tools and every package/asset closure. `craft.profile-composition/v1` records component roles, unique owners, acyclic dependencies, origins and contracts. `craft.profile-coverage/v1` records business obligations, public intents/access policies, integration bindings, generated roles and formal claim residue. Shape validation never produces a registered checked graph/current plan. Required behavior cannot become claim residue; generation input cannot label itself proved/admitted. Actual current-object reconstruction and closure rechecks remain separate generation stages.

Global captured-data limits are 100,000 nodes, depth 64 and 16 MiB of strings/keys; arrays are dense/bounded and objects inert. Getters, proxies, symbols, classes and non-finite/unsafe numeric representations reject. Per-package operation/row/join/depth/byte budgets bound evaluation separately. Data snapshots are immutable and canonical identities sort object keys while retaining array order. The versioned schemas and typed validators define this initial vocabulary; package loading, evaluation and executable generation are later PE03–12 work.

## Working tutorials

[Generate and verify a service](PROFILE-GENERATION.md), then [author a supported package](PROFILE-PACKAGES.md). The existing application adapter preserves whole-application Mapping/Operation contracts; its compatibility carrier includes explicit existing technical companions.
