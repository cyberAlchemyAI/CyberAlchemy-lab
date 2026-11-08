export type DocSection = {
  id: string;
  eyebrow: string;
  title: string;
  summary: string;
};

export type DocsView = "overview" | "tutorial";

export type SearchEntry = {
  id: string;
  eyebrow: string;
  title: string;
  summary: string;
  terms: readonly string[];
};

export type ConstructionStep = {
  id: string;
  label: string;
  title: string;
  explanation: string;
  source: string;
};

export type SystemLayer = {
  id: string;
  product: string;
  label: string;
  title: string;
  description: string;
  outputs: readonly string[];
};

export type BackendTypeReference = {
  id: string;
  name: string;
  category: string;
  syntax: string;
  meaning: string;
  useWhen: string;
  form: string;
  requirements: readonly string[];
  compilesTo: string;
};

export type ClauseReference = {
  clause: string;
  value: string;
  cardinality: "0" | "0..1" | "0..n" | "1" | "1..n" | "2..n";
  meaning: string;
};

export const backendTypeAnchor = (syntax: string) => `type-${syntax}`;
export const supportingDeclarationAnchor = (syntax: string) => `declaration-${syntax}`;
export const diagnosticAnchor = (code: string) => `diagnostic-${code.toLowerCase().replace(/_/g, "-")}`;

export const overviewHero = {
  lead: "Build complex systems.",
  emphasis: "Keep their meaning explicit.",
  descriptionBeforeFile: "AlchLang gives people and agents a shared language for defining domain concepts, rules, permissions, workflows, and boundaries in reviewable ",
  descriptionAfterFile: " files. Craft validates that meaning and compiles it into a checked system graph and deterministic application code.",
  value: "Readable by people. Precise for agents. Compilable into code.",
} as const;

export const systemLayers: readonly SystemLayer[] = [
  {
    id: "author",
    product: "AlchLang",
    label: "Authoring language",
    title: "Write what the domain means",
    description: "Name the concepts, rules, calculations, policies, operations, workflows, interfaces, events, and lifecycle in readable .alch source.",
    outputs: ["source.alch", "source diagnostics", "derived ontology"],
  },
  {
    id: "compile",
    product: "Craft",
    label: "System compiler",
    title: "Check the system as a typed graph",
    description: "Validate the supported concepts and relationships, select exact realizations, then generate and verify a deterministic target.",
    outputs: ["typed graph", "generated target", "certificate"],
  },
  {
    id: "apply",
    product: "Your application",
    label: "Runtime boundary",
    title: "Choose when generated work may run",
    description: "Application-owned bindings provide data, infrastructure, credentials, and execution decisions without changing the authored domain meaning.",
    outputs: ["runtime inputs", "observations", "receipts"],
  },
] as const;

export const integratedJourney = [
  { step: "01", owner: "AlchLang", title: "Author", detail: "Readable .alch source keeps domain language and constraints together." },
  { step: "02", owner: "AlchLang", title: "Lower", detail: "Declarations become a typed Craft project with source provenance." },
  { step: "03", owner: "Craft", title: "Compile", detail: "The project becomes one validated graph and compilation certificate." },
  { step: "04", owner: "Craft", title: "Generate", detail: "A selected realization produces deterministic implementation files." },
  { step: "05", owner: "Application", title: "Integrate", detail: "The application supplies explicit runtime bindings and inputs." },
  { step: "06", owner: "Evidence", title: "Inspect", detail: "Receipts describe what was checked or observed without claiming deployment." },
] as const;

export const packageRoles = [
  { name: "@cyberalchemy/alchlang", status: "Core", detail: "Parser, source diagnostics, ontology projection, and Node/TypeScript build surface." },
  { name: "@domainspec-v2/cli", status: "Required for Craft builds", detail: "Craft compiler package under its compatibility identifier: typed project graph, deterministic code generation, verification, and certificates." },
  { name: "@cyberalchemy/alchlang-rust", status: "Optional", detail: "Native Rust generation and cross-target conformance for supported profiles." },
  { name: "@cyberalchemy/alchlang-local-host", status: "Experimental", detail: "Repository-bound local hosting and provisioning; not required by the core language." },
] as const;

export const artifactRoles = [
  { artifact: "source.alch", owner: "AlchLang", purpose: "The human-authored domain model." },
  { artifact: "ontology.json", owner: "AlchLang", purpose: "A source-linked semantic projection for navigation and explanation." },
  { artifact: "project/", owner: "AlchLang → Craft", purpose: "The typed compiler input produced from supported declarations." },
  { artifact: "graph + certificate", owner: "Craft", purpose: "The validated system snapshot and its bounded compilation result." },
  { artifact: "generated/", owner: "Craft", purpose: "Deterministic implementation files for the selected realization." },
  { artifact: "manifest.json", owner: "AlchLang", purpose: "The complete output inventory installed last when the build succeeds." },
] as const;

const constructionSegments = [
  `domain customer-approval "Customer approval"
owner customer-domain-owner
logic sfol-v1`,
  `entity Customer:
  customerId: identifier required
  status: string required
  amount: decimal required

actor CreditOperator`,
  `rule approved-release:
  status == "approved"`,
  `boundary credit-release-authority:
  owner customer-domain-owner

permission release-credit:
  actor CreditOperator
  action ReleaseCredit
  when approved-release
  boundary credit-release-authority`,
  `action ReleaseCredit:
  actor CreditOperator
  subject Customer
  input amount
  requires approved-release
  permission release-credit
  boundary credit-release-authority
  emits credit-released

event credit-released:
  subject Customer
  payload customerId, amount
  boundary credit-release-authority`,
];

const constructionDetails = [
  {
    id: "identity",
    label: "Start the file",
    title: "Name the domain and its logic",
    explanation: "The header gives the model a stable identity, names its meaning owner, and selects SFOL v1 as the only rule language for this file.",
  },
  {
    id: "types",
    label: "Add domain types",
    title: "Describe the facts rules may inspect",
    explanation: "The Customer entity defines typed, required facts. The actor is named explicitly so later permissions do not depend on an implicit caller.",
  },
  {
    id: "rule",
    label: "Add an SFOL rule",
    title: "Turn business meaning into a repeatable decision",
    explanation: "The rule reads only supplied typed facts. The same status value and the same formula always produce the same Boolean result—without a clock, network call, or hidden state.",
  },
  {
    id: "contracts",
    label: "Constrain authority",
    title: "Connect the rule to named contracts",
    explanation: "The boundary names the owner of authority. The permission states which actor may request which action, under which SFOL rule, without performing the action itself.",
  },
  {
    id: "action",
    label: "Complete the file",
    title: "Declare the action and observable event",
    explanation: "The action gathers its actor, input, rule, permission, boundary, and event contract. Runtime bindings may implement it later; the source remains an inspectable statement of requirements.",
  },
] as const;

export const constructionSteps: ConstructionStep[] = constructionDetails.map((step, index) => ({
  ...step,
  source: constructionSegments.slice(0, index + 1).join("\n\n"),
}));

export const sections: DocSection[] = [
  {
    id: "quickstart",
    eyebrow: "Start here",
    title: "Five-minute quickstart",
    summary: "Install the core package, validate canonical source, and generate deterministic application code.",
  },
  {
    id: "workspace",
    eyebrow: "Try it",
    title: "Run a mini workspace",
    summary: "Edit an in-memory AlchLang file and exercise check, build, and guarded run commands in a browser sandbox.",
  },
  {
    id: "model",
    eyebrow: "Mental model",
    title: "One source, explicit layers",
    summary: "Keep logical meaning, domain contracts, infrastructure bindings, runtime work, and operational evidence distinct.",
  },
  {
    id: "integration",
    eyebrow: "AlchLang + Craft",
    title: "Follow meaning into implementation",
    summary: "See which product owns each stage, package, artifact, and validation boundary from .alch source to generated code.",
  },
  {
    id: "source",
    eyebrow: "Source format",
    title: "Author canonical .alch files",
    summary: "Use plain UTF-8 source, explicit ownership, one SFOL profile, typed fields, indentation, and causal source errors.",
  },
  {
    id: "sfol",
    eyebrow: "Language",
    title: "Express rules with SFOL",
    summary: "Use one bounded formula kernel across rules, query filters, permissions, guards, and policy cases.",
  },
  {
    id: "contracts",
    eyebrow: "Typed backend",
    title: "Shape reads and decisions",
    summary: "Queries, Calculations, Mappings, and Policies compile into typed, inspectable contracts.",
  },
  {
    id: "backend-types",
    eyebrow: "Local language surface",
    title: "Use all 13 backend types",
    summary: "Author Value Object, Enum, Operation, Workflow, Interface, State Machine, and the complete 13-type Craft backend alphabet.",
  },
  {
    id: "type-selection",
    eyebrow: "Choose a construct",
    title: "Select the type that owns the meaning",
    summary: "Compare neighboring declarations before choosing identity, value, behavior, boundary, transformation, or lifecycle semantics.",
  },
  {
    id: "lexical-reference",
    eyebrow: "Lexical reference",
    title: "Read tokens and source structure",
    summary: "Look up identifiers, comments, strings, numbers, lists, indentation, file containers, and scalar field types.",
  },
  {
    id: "declaration-reference",
    eyebrow: "Declaration reference",
    title: "Inspect every declaration contract",
    summary: "Read the meaning, use criteria, canonical form, semantic validation, and compilation surface for every supported declaration.",
  },
  {
    id: "formal-grammar",
    eyebrow: "Formal grammar",
    title: "Read the closed language grammar",
    summary: "Use the notation legend, top-level production index, SFOL precedence, and documented grammar-versus-validation boundary.",
  },
  {
    id: "domainspec-target",
    eyebrow: "Craft compiler",
    title: "Compile with Craft 1.0.0",
    summary: "Lower supported AlchLang declarations into the Stable 1.0 typed graph, generator, verification, and certificate boundary.",
  },
  {
    id: "compiler",
    eyebrow: "Compiler",
    title: "Inspect deterministic artifacts",
    summary: "Follow local compilation and explicit Craft 1.0.0 lowering, ontology bindings, TypeScript output, migration limits and digest manifests.",
  },
  {
    id: "actions",
    eyebrow: "Action runtime",
    title: "Run guarded actions",
    summary: "Require declared actors, facts, SFOL guards, permissions, authority grants, and explicitly selected adapters before execution.",
  },
  {
    id: "effects",
    eyebrow: "Operation patterns",
    title: "Resolve effects and bindings",
    summary: "Discover generatable operation patterns and close an Effect against its exact binding, guarantee, provider, and failure continuation.",
  },
  {
    id: "outbox",
    eyebrow: "Durable runtime",
    title: "Operate the transactional Outbox",
    summary: "Commit state and messages atomically, dispatch with leases and retries, recover dead letters, and consume through an idempotent inbox.",
  },
  {
    id: "evidence",
    eyebrow: "Operations",
    title: "Close the evidence loop",
    summary: "Runtime observations flow into ORODI evaluation without collapsing source validation into operational proof.",
  },
];

export const implementationCoverage = [
  { capability: "integrated-alch-domainspec-journey", section: "integration", evidence: "domainspec-cli.ts + domainspec-project-writer.ts + Craft public API" },
  { capability: "domainspec-exact-uint64-lowering", section: "compiler", evidence: "domainspec-profile.ts + lower-domainspec.ts + domainspec-project-writer.ts" },
  { capability: "canonical-source-loader", section: "source", evidence: "source-file.ts" },
  { capability: "sfol-parser-and-evaluator", section: "sfol", evidence: "predicate-parser.ts + runtime.ts" },
  { capability: "query-calculation-mapping-policy", section: "contracts", evidence: "typed-backend.ts" },
  { capability: "value-object-and-enum-contracts", section: "backend-types", evidence: "parser.ts + model.ts + render-typescript.ts" },
  { capability: "full-operation-contract", section: "backend-types", evidence: "declared reads + writes + effects + guards + outcomes" },
  { capability: "workflow-interface-and-state-machine-contracts", section: "backend-types", evidence: "parser.ts + validate.ts + lower.ts" },
  { capability: "complete-declaration-syntax-reference", section: "declaration-reference", evidence: "parser.ts + predicate-parser.ts + validate.ts" },
  { capability: "closed-meta-type-extension-boundary", section: "formal-grammar", evidence: "closed parser declaration grammar + canonical Craft profile" },
  { capability: "validate-lower-render-write", section: "compiler", evidence: "validate.ts + lower.ts + render-typescript.ts + writer.ts" },
  { capability: "guarded-action-adapters", section: "actions", evidence: "runtime.ts + adapters.ts" },
  { capability: "operation-pattern-registry", section: "effects", evidence: "pattern-registry.ts + registry-compiler.ts" },
  { capability: "sqlite-outbox-generator", section: "effects", evidence: "sqlite-outbox-generator.ts" },
  { capability: "durable-transactional-outbox", section: "outbox", evidence: "durable-outbox-runtime.ts" },
  { capability: "confirmed-http-transport", section: "outbox", evidence: "outbox-integrations.ts" },
  { capability: "idempotent-inbox", section: "outbox", evidence: "outbox-integrations.ts" },
  { capability: "operational-evidence-boundary", section: "evidence", evidence: "runtime receipts + ORODI handoff" },
] as const;

export const domainSpecTarget = {
  version: "1.0.0",
  install: `npm install ../domainspec-v2-cli-1.0.0.tgz`,
  commands: `mkdir -p build
npx alchlang domainspec --version
npx alchlang check workspace.alch --profile domainspec-1.0.0
npx alchlang emit-domainspec workspace.alch --out "$PWD/build/order-project"
npx alchlang build workspace.alch --backend domainspec --language typescript --out "$PWD/build/order-build"`,
  usage: `import {
  evaluateMapping,
  selectPolicy,
} from "./build/order-build/domain.js";

const normalized = evaluateMapping("normalize-order", facts);
const selectedTarget = selectPolicy("fulfillment-policy", normalized);

// The application decides whether and how selectedTarget may run.
return { normalized, selectedTarget };`,
  exactCommands: `npx alchlang check workspace.alch --profile domainspec-1.0.0-exact-uint64-v1 --bindings ./typed-commerce.bindings.json
npx alchlang build workspace.alch --backend domainspec --language typescript --profile domainspec-1.0.0-exact-uint64-v1 --bindings ./typed-commerce.bindings.json --out "$PWD/build/commerce-exact"`,
  supported: "String/Bool records, identifier fields, Boolean equality rules, safe input-free UInt64 constants, concrete mappings and ordered policies selecting those constants.",
  bindings: "The companion <source>.domainspec.json binds the source SHA-256, owner, declaration and property meanings, ontology selectors, Entity identity and Value Object Rule invariants. Use --bindings to choose another file.",
  outputs: "project/, generated/, domain.ts, source and binding snapshots, trace.json, certificate.json, compiler-files.json and manifest.json. The manifest is installed last as the completion marker.",
  migration: "The existing typed-commerce application also needs queries, integer records, parameterized arithmetic and threshold comparisons. It currently rejects with DS_UNSUPPORTED. The new exact profile supports that unchanged source; the original profile still rejects it.",
} as const;

export const quickstart = `mkdir alchlang-quickstart && cd alchlang-quickstart
npm init -y
npm install ../cyberalchemy-alchlang-0.4.0-candidate.0.tgz
npx alchlang --version

# Save the maintained workspace example as workspace.alch, then:
npx alchlang check workspace.alch
npx alchlang build workspace.alch --out "$PWD/generated/customer-approval"`;

export const sourceExample = `# Plain UTF-8 source; no Markdown fence.
domain inventory "Inventory"
owner inventory-domain-owner
logic sfol-v1

entity Item:
  item_id: identifier required
  quantity: integer required
  label: string optional`;

export const sfolExample = `domain typed-commerce "Typed commerce"
owner typed-commerce-owner
logic sfol-v1

entity Order:
  order_id: identifier required
  amount: integer required
  status: string required

rule OpenOrder:
  status == "open"`;

export const actionExample = `operation CommitOrderWithOutbox:
  state-change yes
  actor OrderService
  subject OrderOperation
  input operationId, orderId, outboxMessageId, occurredAt, payload
  reads OrderOperation
  writes OrderOperation, OutboxMessage
  effects PersistOrderWithOutbox
  requires operation-pending
  permission commit-order-with-outbox
  boundary order-transaction-authority
  emits outbox-message-recorded
  performs PersistOrderWithOutbox \\
    using sqlite-transactional-outbox`;

export const typedBackendExample = `query OpenOrders:
  source Order
  where status == "open"
  order amount desc
  limit 2
  project order_id, amount

calculation ApplyFee:
  inputs amount
  expression add(amount, 5)
  rounding reject

mapping SummarizeOrder:
  source Order
  target OrderSummary
  total true
  field summary_id <- order_id
  field total <- amount

policy FeePolicy:
  inputs amount
  case amount > 100 -> ApplyFee
  default KeepAmount`;

export const backendTypes: readonly BackendTypeReference[] = [
  {
    id: "DS-D1.1", name: "Entity", category: "Structural", syntax: "entity",
    meaning: "An identity-bearing object whose facts and lifecycle can change over time.",
    useWhen: "Use an Entity when two otherwise equal records are still distinct domain objects, or when state must be tracked across operations.",
    form: `entity Order:
  order_id: identifier required
  amount: integer required
  note: string optional`,
    requirements: ["Each field uses one supported scalar type.", "Fields are required unless explicitly marked optional.", "The domain owner becomes the owner of every declared fact."],
    compilesTo: "A typed domain interface and the fact model used by rules, queries, events, mappings, and operations.",
  },
  {
    id: "DS-D1.2", name: "Value Object", category: "Structural", syntax: "value-object",
    meaning: "A value defined by its typed contents rather than an independent identity.",
    useWhen: "Use a Value Object for money, addresses, ranges, coordinates, or other values whose equality is structural.",
    form: `value-object Money:
  value: decimal required
  currency: string required
  equality value, currency`,
    requirements: ["At least one typed field is required.", "An equality clause must name one or more fields from the object.", "Equality field names must be unique and resolvable."],
    compilesTo: "A readonly TypeScript contract plus its explicit equality-field metadata.",
  },
  {
    id: "DS-D1.3", name: "Enum", category: "Structural", syntax: "enum",
    meaning: "A closed vocabulary of named values, each carrying an authored description.",
    useWhen: "Use an Enum when the legal values are finite and do not themselves transition.",
    form: `enum OrderStatus:
  value pending "Accepted but not committed"
  value committed "State and event committed"`,
    requirements: ["At least one value is required.", "Every value needs a quoted description.", "Value identifiers must be unique inside the Enum."],
    compilesTo: "A string-literal union and a readonly array of the allowed values.",
  },
  {
    id: "DS-D1.4", name: "Operation", category: "Behavioral", syntax: "operation",
    meaning: "The complete write-side contract: inputs, reads, mutations, effects, guards, permissions, and outcomes.",
    useWhen: "Use an Operation for a state-changing domain capability whose mutation and effect boundaries must be reviewable.",
    form: `operation CommitOrder:
  state-change yes
  actor OrderService
  subject Order
  input order_id
  reads Order
  writes Order, OutboxMessage
  effects PersistOrder
  requires PositiveAmount
  permission commit-order
  boundary order-authority
  emits order-committed
  performs PersistOrder using sqlite-outbox`,
    requirements: ["state-change yes and a nonempty writes set are mandatory.", "The effects set must exactly match the effects named by performs.", "Every Effect write must also appear in the Operation write set.", "Actors, subjects, facts, rules, permissions, boundaries, effects, bindings, and events must resolve."],
    compilesTo: "An operation contract and runtime port; execution still requires an explicit adapter or Integration Binding.",
  },
  {
    id: "DS-D1.5", name: "Query", category: "Behavioral", syntax: "query",
    meaning: "A deterministic read contract over rows supplied by the caller.",
    useWhen: "Use a Query to filter, sort, limit, and project an Entity collection without granting or performing data access.",
    form: `query OpenOrders:
  source Order
  inputs status
  where status == "open"
  order amount desc
  limit 20
  project order_id, amount`,
    requirements: ["source must resolve to an Entity.", "project is mandatory, nonempty, unique, and limited to declared facts.", "where is optional but must be Boolean SFOL.", "order is optional and uses asc or desc; limit is a positive safe integer."],
    compilesTo: "A typed Query contract and a pure evaluator over caller-supplied rows.",
  },
  {
    id: "DS-D1.6", name: "Calculation", category: "Behavioral", syntax: "calculation",
    meaning: "A bounded, side-effect-free UInt64 arithmetic term.",
    useWhen: "Use a Calculation when a numeric result must be repeatable, range checked, and independent of runtime providers.",
    form: `calculation ApplyFee:
  inputs amount
  expression add(amount, 5)
  rounding reject`,
    requirements: ["Inputs must be unique declared integer facts and appear before expression.", "Terms are UInt64 literals, inputs, or nested add, subtract, multiply, and divide calls.", "rounding is floor, ceil, or reject.", "Nesting beyond 64 levels, range errors, underflow, overflow, and division by zero fail causally."],
    compilesTo: "A typed Calculation contract and checked pure evaluator.",
  },
  {
    id: "DS-D1.7", name: "Rule", category: "Behavioral", syntax: "rule",
    meaning: "A named Boolean statement in the bounded SFOL kernel.",
    useWhen: "Use a Rule for reusable business truth shared by guards, permissions, transitions, and policies.",
    form: `rule PositiveAmount:
  amount > 0 and status != "cancelled"`,
    requirements: ["Exactly one indented formula line is allowed.", "Fact references must resolve and comparison operand types must agree.", "The complete formula must produce Boolean."],
    compilesTo: "A normalized SFOL formula and a deterministic Boolean evaluator.",
  },
  {
    id: "DS-D1.8", name: "Policy", category: "Behavioral", syntax: "policy",
    meaning: "An ordered decision table that selects one declared target.",
    useWhen: "Use a Policy when several SFOL conditions choose among Operations, legacy Actions, or Calculations.",
    form: `policy FeePolicy:
  inputs amount
  case amount > 100 -> ApplyFee
  default KeepAmount`,
    requirements: ["At least one ordered case and one default target are required.", "Every case predicate must be Boolean SFOL.", "Inputs must be declared facts; targets must resolve to an Operation, Action, or Calculation."],
    compilesTo: "A pure selector that returns a target identifier; selection does not execute or authorize it.",
  },
  {
    id: "DS-D1.9", name: "Workflow", category: "Behavioral", syntax: "workflow",
    meaning: "An ordered orchestration contract spanning multiple domain steps.",
    useWhen: "Use a Workflow when the business outcome requires a visible sequence of Operations rather than one atomic write contract.",
    form: `workflow FulfilOrder:
  scope intra-feature
  steps CommitOrder, ConfirmOrder`,
    requirements: ["scope is exactly intra-feature or cross-feature.", "At least two ordered steps are required.", "Every step must resolve to a declared Operation or supported legacy Action."],
    compilesTo: "Static workflow metadata; durable scheduling and compensation remain runtime-provider responsibilities.",
  },
  {
    id: "DS-D1.11", name: "Interface", category: "Connective", syntax: "interface",
    meaning: "A named internal or external boundary over exposed domain capabilities.",
    useWhen: "Use an Interface to state which Operations, legacy Actions, or Queries cross a system boundary.",
    form: `interface OrdersApi:
  kind external
  exposes CommitOrder, OpenOrders`,
    requirements: ["kind is exactly internal or external.", "At least one exposure is required.", "Every exposure must resolve to an Operation, Action, or Query."],
    compilesTo: "A typed interface contract; no network server, protocol, authentication, or authorization is implied.",
  },
  {
    id: "DS-D1.12", name: "Event", category: "Behavioral", syntax: "event",
    meaning: "A named observable domain outcome with a typed payload and authority boundary.",
    useWhen: "Use an Event to describe what other components may observe after an accepted domain transition.",
    form: `event order-committed:
  subject Order
  payload order_id, amount
  boundary order-authority`,
    requirements: ["Payload entries must resolve to declared facts.", "A named boundary must resolve when present.", "An Event describes an outcome; it does not publish itself."],
    compilesTo: "An event payload contract consumed by operation outcomes and effect declarations.",
  },
  {
    id: "DS-D1.13", name: "Mapping", category: "Connective", syntax: "mapping",
    meaning: "An explicit field-by-field transformation between two Entity shapes.",
    useWhen: "Use a Mapping to make data-shape conversion reviewable instead of hiding it in host-language code.",
    form: `mapping ToSummary:
  source Order
  target OrderSummary
  total true
  field summary_id <- order_id
  field label default string "unlabelled"`,
    requirements: ["source and target must resolve to Entities.", "At least one uniquely targeted field clause is required.", "Copied fields and typed defaults must match the target fact type.", "total is true or false; current total coverage still requires separate review."],
    compilesTo: "A typed Mapping contract and pure object transformation.",
  },
  {
    id: "DS-D1.14", name: "State Machine", category: "Lifecycle", syntax: "states",
    meaning: "The legal states and guarded transitions of one Entity.",
    useWhen: "Use a State Machine when an Entity has meaningful lifecycle stages and only specific transitions are valid.",
    form: `states Order:
  initial pending
  pending -> committed when PositiveAmount emits order-committed
  committed -> archived`,
    requirements: ["The header identifier must resolve to an Entity.", "A transition is from -> to with optional when Rule and emits Event clauses.", "Referenced guards and emitted Events must resolve."],
    compilesTo: "A state-machine contract containing discovered states and ordered transition metadata.",
  },
];

export const supportingDeclarations = [
  { name: "Actor", syntax: "actor", form: `actor OrderService`, detail: "Names a caller role. Actor declarations have no indented body." },
  { name: "Authority boundary", syntax: "boundary", form: `boundary order-authority:\n  owner order-domain-owner`, detail: "Names a non-effectful authority boundary. Its owner must equal the file owner." },
  { name: "Permission", syntax: "permission", form: `permission commit-order:\n  actor OrderService\n  action CommitOrder\n  when PositiveAmount\n  boundary order-authority`, detail: "Associates declared actors and actions through a Rule and boundary. It does not grant itself." },
  { name: "Action", syntax: "action", form: `action InspectOrder:\n  actor OrderService\n  subject Order\n  input order_id\n  requires PositiveAmount\n  permission inspect-order\n  boundary order-authority\n  emits order-inspected`, detail: "Compatibility write/read action. Use Operation when the complete write-set and effect-set contract is required." },
  { name: "Effect", syntax: "effect", form: `effect PersistOrder:\n  pattern transactional-outbox\n  binding sqlite-outbox\n  writes Order, OutboxMessage\n  emits order-committed\n  guarantee atomic-state-and-outbox\n  on-failure rollback\n  boundary order-authority`, detail: "Declares pattern, binding, writes, events, guarantee, failure continuation, and boundary. The current concrete guarantee is atomic-state-and-outbox with rollback." },
  { name: "Example", syntax: "example", form: `example positive-order:\n  kind positive\n  expected accepted\n  rules PositiveAmount`, detail: "Adds a test obligation with an authored kind, expected interpretation, and affected Rule identifiers." },
] as const;

export const declarationClauses: Readonly<Record<string, readonly ClauseReference[]>> = {
  entity: [
    { clause: "<field-id>: <scalar> [required|optional]", value: "field identifier, scalar type, presence", cardinality: "0..n", meaning: "Declares an owned fact. Presence defaults to required." },
  ],
  "value-object": [
    { clause: "<field-id>: <scalar> [required|optional]", value: "field identifier, scalar type, presence", cardinality: "1..n", meaning: "Declares a structural value field. Presence defaults to required." },
    { clause: "equality <field-id,...>", value: "unique local field references", cardinality: "1", meaning: "Names the fields that determine value equality." },
  ],
  enum: [
    { clause: "value <id> \"<description>\"", value: "value identifier and double-quoted description", cardinality: "1..n", meaning: "Adds one unique member to the closed vocabulary." },
  ],
  operation: [
    { clause: "state-change yes", value: "literal yes", cardinality: "1", meaning: "Marks the declaration as a state-changing operation." },
    { clause: "actor <actor-id,...>", value: "Actor references", cardinality: "0..n", meaning: "Names actors that may invoke the operation." },
    { clause: "subject <entity-id,...>", value: "Entity references", cardinality: "0..n", meaning: "Names the domain objects the operation addresses." },
    { clause: "input <field-id,...>", value: "fact references", cardinality: "0..n", meaning: "Declares facts supplied as operation input." },
    { clause: "reads <entity-id,...>", value: "Entity references", cardinality: "0..n", meaning: "Declares the complete domain read set." },
    { clause: "writes <entity-id,...>", value: "Entity references", cardinality: "1..n", meaning: "Declares the state write set, including every entity written by an Effect." },
    { clause: "effects <effect-id,...>", value: "Effect references", cardinality: "0..n", meaning: "Declares the exact set later paired by performs clauses." },
    { clause: "requires <rule-id,...>", value: "Rule references", cardinality: "0..n", meaning: "Adds reusable SFOL preconditions." },
    { clause: "permission <permission-id,...>", value: "Permission references", cardinality: "0..n", meaning: "Associates permission contracts with the operation." },
    { clause: "boundary <boundary-id>", value: "Authority boundary reference", cardinality: "1", meaning: "Places the operation under one declared authority boundary." },
    { clause: "emits <event-id,...>", value: "Event references", cardinality: "0..n", meaning: "Declares observable outcomes." },
    { clause: "performs <effect-id> using <binding-id>", value: "Effect and integration-binding references", cardinality: "0..n", meaning: "Pairs each declared Effect with its exact implementation binding." },
    { clause: "allowed only when <sfol-formula>", value: "Boolean SFOL formula", cardinality: "0..n", meaning: "Creates an operation-local generated Rule precondition." },
    { clause: "requires human confirmation when <text> is <rule-id>", value: "Rule reference", cardinality: "0..n", meaning: "Creates a generated Human permission tied to the named Rule." },
  ],
  query: [
    { clause: "source <entity-id>", value: "Entity reference", cardinality: "1", meaning: "Names the shape of caller-supplied rows; it does not fetch them." },
    { clause: "inputs <field-id,...>", value: "unique fact references", cardinality: "0..1", meaning: "Names external values available to the query contract." },
    { clause: "where <sfol-formula>", value: "Boolean SFOL formula", cardinality: "0..1", meaning: "Filters supplied rows." },
    { clause: "order <field-id> asc|desc", value: "fact reference and direction", cardinality: "0..n", meaning: "Adds an ordered sort key. Authored order is significant." },
    { clause: "limit <positive-integer>", value: "positive safe integer", cardinality: "0..1", meaning: "Bounds the number of returned rows." },
    { clause: "project <field-id,...>", value: "unique fact references", cardinality: "1", meaning: "Declares the nonempty result projection." },
  ],
  calculation: [
    { clause: "inputs <field-id,...>", value: "unique integer fact references", cardinality: "0..1", meaning: "Declares the names available to the arithmetic expression and must precede it." },
    { clause: "expression <uint64-term>", value: "UInt64 literal, input, or arithmetic call", cardinality: "1", meaning: "Defines the checked arithmetic result." },
    { clause: "rounding floor|ceil|reject", value: "rounding mode", cardinality: "0..1", meaning: "Controls inexact division; omission defaults to reject." },
  ],
  rule: [
    { clause: "<sfol-formula>", value: "Boolean SFOL formula", cardinality: "1", meaning: "Defines the complete reusable proposition for this Rule." },
  ],
  policy: [
    { clause: "inputs <field-id,...>", value: "fact references", cardinality: "0..1", meaning: "Declares facts used by case predicates." },
    { clause: "case <sfol-formula> -> <target-id>", value: "Boolean formula and Operation, Action, or Calculation reference", cardinality: "1..n", meaning: "Selects the first target whose case evaluates true." },
    { clause: "default <target-id>", value: "Operation, Action, or Calculation reference", cardinality: "1", meaning: "Provides the target when no case matches." },
  ],
  workflow: [
    { clause: "scope intra-feature|cross-feature", value: "scope literal", cardinality: "1", meaning: "Declares the orchestration boundary." },
    { clause: "steps <operation-id,...>", value: "ordered Operation or legacy Action references", cardinality: "2..n", meaning: "Declares the ordered workflow steps." },
  ],
  interface: [
    { clause: "kind internal|external", value: "boundary kind", cardinality: "1", meaning: "Classifies the interface boundary." },
    { clause: "exposes <capability-id,...>", value: "Operation, legacy Action, or Query references", cardinality: "1..n", meaning: "Names the capabilities visible through the boundary." },
  ],
  event: [
    { clause: "subject <entity-id>", value: "Entity reference", cardinality: "0..1", meaning: "Names the entity associated with the outcome." },
    { clause: "payload <field-id,...>", value: "fact references", cardinality: "0..1", meaning: "Declares the observable payload fields." },
    { clause: "boundary <boundary-id>", value: "Authority boundary reference", cardinality: "0..1", meaning: "Associates the outcome with a declared boundary." },
  ],
  mapping: [
    { clause: "source <entity-id>", value: "Entity reference", cardinality: "1", meaning: "Names the source object shape." },
    { clause: "target <entity-id>", value: "Entity reference", cardinality: "1", meaning: "Names the constructed target shape." },
    { clause: "total true|false", value: "Boolean literal", cardinality: "0..1", meaning: "Requests total-clause behavior; omission defaults to true." },
    { clause: "field <target-field> <- <source-field>", value: "compatible fact references", cardinality: "0..n", meaning: "Copies one source field into one unique target field." },
    { clause: "field <target-field> default <scalar> <json>", value: "target fact, scalar type, JSON value", cardinality: "0..n", meaning: "Supplies a typed default for one unique target field." },
  ],
  states: [
    { clause: "initial <state-id>", value: "state identifier", cardinality: "0..1", meaning: "Marks the initial state when authored." },
    { clause: "<from> -> <to> [when <rule-id>] [emits <event-id>]", value: "state identifiers with optional Rule and Event references", cardinality: "0..n", meaning: "Declares an ordered legal transition and optional guard and outcome." },
  ],
  actor: [],
  boundary: [
    { clause: "owner <owner-id>", value: "the document owner identifier", cardinality: "1", meaning: "Binds the boundary to the same owner declared in the file header." },
  ],
  permission: [
    { clause: "actor <actor-id>", value: "Actor reference", cardinality: "1", meaning: "Names the subject of the permission contract." },
    { clause: "action <action-id>", value: "Operation or Action reference", cardinality: "1", meaning: "Names the capability governed by the contract." },
    { clause: "when <rule-id>", value: "Rule reference", cardinality: "1", meaning: "Supplies the Boolean SFOL condition." },
    { clause: "boundary <boundary-id>", value: "Authority boundary reference", cardinality: "1", meaning: "Places the contract under one declared boundary." },
  ],
  action: [
    { clause: "state-change yes|no", value: "state-change literal", cardinality: "0..1", meaning: "Records compatibility intent; omission defaults to no and does not establish the complete Operation contract." },
    { clause: "actor <actor-id,...>", value: "Actor references", cardinality: "0..n", meaning: "Names actors associated with the compatibility action." },
    { clause: "subject <entity-id,...>", value: "Entity references", cardinality: "0..n", meaning: "Names addressed domain objects." },
    { clause: "input <field-id,...>", value: "fact references", cardinality: "0..n", meaning: "Declares supplied input facts." },
    { clause: "reads <entity-id,...>", value: "Entity references", cardinality: "0..n", meaning: "Overrides the read set otherwise derived from subjects." },
    { clause: "writes <entity-id,...>", value: "Entity references", cardinality: "0..n", meaning: "Declares writes without the complete Operation invariant." },
    { clause: "effects <effect-id,...>", value: "Effect references", cardinality: "0..n", meaning: "Declares referenced effects." },
    { clause: "requires <rule-id,...>", value: "Rule references", cardinality: "0..n", meaning: "Adds named preconditions." },
    { clause: "permission <permission-id,...>", value: "Permission references", cardinality: "0..n", meaning: "Associates permission contracts." },
    { clause: "boundary <boundary-id>", value: "Authority boundary reference", cardinality: "1", meaning: "Places the action under one declared boundary." },
    { clause: "emits <event-id,...>", value: "Event references", cardinality: "0..n", meaning: "Declares the observable outcomes produced by the action." },
    { clause: "performs <effect-id> using <binding-id>", value: "Effect and binding references", cardinality: "0..n", meaning: "Pairs an Effect with a concrete binding." },
    { clause: "allowed only when <sfol-formula>", value: "Boolean SFOL formula", cardinality: "0..n", meaning: "Creates an action-local generated Rule precondition." },
    { clause: "requires human confirmation when <text> is <rule-id>", value: "Rule reference", cardinality: "0..n", meaning: "Creates a generated Human permission tied to the named Rule." },
  ],
  effect: [
    { clause: "pattern <pattern-id>", value: "architecture-pattern identifier", cardinality: "1", meaning: "Names the implementation pattern." },
    { clause: "binding <binding-id>", value: "integration-binding identifier", cardinality: "1", meaning: "Names the exact binding used by performs." },
    { clause: "writes <entity-id,...>", value: "Entity references", cardinality: "1", meaning: "Declares the nonempty effect write set." },
    { clause: "emits <event-id,...>", value: "Event references", cardinality: "1", meaning: "Declares the nonempty emitted-event set." },
    { clause: "guarantee atomic-state-and-outbox", value: "supported guarantee literal", cardinality: "1", meaning: "Requires atomic state and outbox persistence." },
    { clause: "on-failure rollback", value: "supported continuation literal", cardinality: "1", meaning: "Requires rollback on failure." },
    { clause: "boundary <boundary-id>", value: "Authority boundary reference", cardinality: "1", meaning: "Places the Effect under one declared boundary." },
  ],
  example: [
    { clause: "kind <id>", value: "example-kind identifier", cardinality: "0..1", meaning: "Classifies the generated test obligation; omission defaults to positive." },
    { clause: "expected <text>", value: "expected interpretation text", cardinality: "0..1", meaning: "Records the expected interpretation." },
    { clause: "rules <rule-id,...>", value: "Rule references", cardinality: "0..1", meaning: "Names Rules affected by the example." },
  ],
};

export const typeDecisionGuide = [
  { question: "Does the concept retain identity while its facts change?", choose: "Entity", instead: "Choose Value Object when equality comes only from contained values." },
  { question: "Is this a finite vocabulary without transitions?", choose: "Enum", instead: "Choose State Machine when legal changes between states carry meaning." },
  { question: "Does it mutate domain state with explicit reads, writes, and effects?", choose: "Operation", instead: "Use legacy Action only for compatibility with the smaller action contract." },
  { question: "Does it read caller-supplied rows without performing access?", choose: "Query", instead: "Choose Interface to expose a Query or Operation across a named boundary." },
  { question: "Does it compute one checked numeric result?", choose: "Calculation", instead: "Choose Mapping when the result is a target object assembled field by field." },
  { question: "Does it state reusable truth?", choose: "Rule", instead: "Choose Policy when ordered conditions select one declared target." },
  { question: "Does a result need to be observable after a transition?", choose: "Event", instead: "Choose Effect for the responsibility that produces writes or emitted events." },
  { question: "Does work span two or more ordered operations?", choose: "Workflow", instead: "Keep one atomic mutation and its effects in a single Operation." },
] as const;

export const lexicalRules = [
  { subject: "Canonical file", syntax: "*.alch", rule: "Lowercase extension; plain UTF-8; no byte-order mark or Markdown fence.", error: "SOURCE_EXTENSION / SOURCE_ENCODING / SOURCE_CONTAINER" },
  { subject: "Legacy container", syntax: "*.md", rule: "Exactly one fenced alchlang block. New source should not use this form.", error: "SOURCE_BLOCK_COUNT / SOURCE_CONTAINER" },
  { subject: "Identifier", syntax: "[A-Za-z_][A-Za-z0-9_.-]*", rule: "Used for domains, owners, declarations, fields, and references.", error: "TEXT_SYNTAX" },
  { subject: "Comment", syntax: "# text", rule: "A full line whose first non-whitespace character is # is ignored.", error: "—" },
  { subject: "Section body", syntax: "<indent><clause>", rule: "One or more leading whitespace characters attach a row to the preceding top-level declaration; canonical examples use two spaces.", error: "TEXT_SYNTAX" },
  { subject: "Identifier list", syntax: "a, b, c", rule: "Comma-separated identifiers; declaration-specific validation controls uniqueness and resolution.", error: "UNRESOLVED_REFERENCE / duplicate-specific code" },
  { subject: "String literal", syntax: "\"text\" or 'text'", rule: "Quote canonical string operands. Enum descriptions and domain titles require double quotes.", error: "PREDICATE_SYNTAX / TEXT_SYNTAX" },
  { subject: "Number", syntax: "42 or 4.2", rule: "SFOL accepts integer and decimal literals; Calculation terms accept unsigned integer literals only.", error: "PREDICATE_SYNTAX / CALCULATION_SYNTAX" },
] as const;

export const grammarNotation = [
  { mark: "literal", meaning: "Characters shown in code are written exactly as displayed." },
  { mark: "<name>", meaning: "A named production or value supplied by the author." },
  { mark: "[item]", meaning: "An optional item that may occur zero or one time." },
  { mark: "item*", meaning: "An item that may repeat zero or more times." },
  { mark: "item+", meaning: "An item that must occur one or more times." },
  { mark: "a | b", meaning: "Exactly one of the alternatives at that position." },
  { mark: "(items)", meaning: "A grouped sequence; parentheses in code are quoted as literals." },
] as const;

export const declarationGrammar = `document     := domain-header owner-header [logic-header] declaration*
domain-header := "domain" <id> [<double-quoted-title>]
owner-header  := "owner" <id>
logic-header  := "logic" "sfol-v1"

declaration := entity | value-object | enum | operation | query
             | calculation | rule | policy | workflow | interface
             | event | mapping | state-machine
             | actor | boundary | permission | action | effect | example

section      := <declaration-keyword> <id> [":"] newline clause+
state-machine := "states" <entity-id> ":" newline state-clause+
actor        := "actor" <id>

# This compact index names accepted top-level forms. Each declaration's
# clause grammar and semantic constraints are documented in its reference.`;

export const validationBoundary = [
  { layer: "Lexing and parsing", proves: "The source uses recognized tokens, headers, declarations, clauses, and expression shapes.", doesNotProve: "That references resolve or operands and declarations are semantically compatible." },
  { layer: "Semantic validation", proves: "Required clauses, reference targets, uniqueness, type compatibility, and bounded invariants hold.", doesNotProve: "That generated code has run or an effect is authorized." },
  { layer: "Compilation", proves: "A validated model lowered into the claimed deterministic artifacts.", doesNotProve: "Runtime success, operational fitness, product approval, or deployment authority." },
] as const;

export const commonDiagnostics = [
  "SOURCE_EXTENSION", "SOURCE_ENCODING", "SOURCE_CONTAINER", "SOURCE_BLOCK_COUNT",
  "TEXT_SYNTAX", "TEXT_REQUIRED", "TEXT_FIELD", "SFOL_PROFILE", "PREDICATE_SYNTAX",
  "SFOL_FORMULA_TYPE", "UNRESOLVED_REFERENCE", "TYPE_MISMATCH", "CALCULATION_SYNTAX",
  "OUTPUT_EXISTS", "AUTHORITY_DENIED", "EFFECT_BINDING_REQUIRED",
] as const;

export const metaTypeExtensionSteps = [
  "Define the new semantic category and prove that none of the existing 13 types already carries that meaning.",
  "Assign a canonical Craft identity, invariants, relationships, failure behavior, and authority ceiling.",
  "Extend the carrier and normalized model with a typed representation instead of an opaque metadata escape hatch.",
  "Add parser grammar, causal validation, lowering, traceability, and deterministic generated contracts.",
  "Implement and test every claimed target-language realization and any runtime-provider boundary.",
  "Bind exact candidate bytes, collect independent evidence, and obtain the separate owner decisions required for admission.",
] as const;

export const fileGrammar = `domain <id> ["<title>"]
owner <owner-route>
logic sfol-v1

# Zero or more top-level declarations. Bodies are indented.
<declaration> <id>:
  <clause>

# Identifiers: [A-Za-z_][A-Za-z0-9_.-]*
# Lists: comma-separated identifiers
# Comments: a full line beginning with #`;

export const sfolGrammar = `formula    := disjunction
disjunction := conjunction ("or" conjunction)*
conjunction := comparison ("and" comparison)*
comparison := unary (("==" | "!=" | "<" | "<=" | ">" | ">=" | "in" | "contains") value)?
unary      := "not" unary | ("exists" | "absent") ["("] fact-ref [")"] | value
value      := fact-ref | string | integer | decimal | boolean | "(" formula ")"

# Precedence: parentheses → unary → comparison → and → or
# Calculation terms: UInt64 | input | add(a,b) | subtract(a,b) | multiply(a,b) | divide(a,b)`;

export const backendTypesExample = `value-object Money:
  value: decimal required
  currency: string required
  equality value, currency

enum OrderStatus:
  value pending "Accepted but not committed"
  value committed "State and event committed"

operation CommitOrder:
  state-change yes
  actor OrderService
  subject Order
  reads Order
  writes Order, OutboxMessage
  effects PersistOrderWithOutbox
  requires PositiveAmount
  boundary order-transaction-authority
  emits order-committed
  performs PersistOrderWithOutbox using sqlite-transactional-outbox

workflow FulfilOrder:
  scope intra-feature
  steps CommitOrder, ConfirmOrder

interface OrdersApi:
  kind external
  exposes CommitOrder, OpenOrders

states Order:
  initial pending
  pending -> committed when PositiveAmount emits order-committed`;

export const memoryRunExample = `npx alchlang run workspace.alch ReleaseCredit \\
  --actor CreditOperator \\
  --facts '{"customerId":"c-1","riskScore":600,"status":"approved","amount":100}' \\
  --grant credit-release-authority \\
  --adapter memory`;

export const effectExample = `effect PersistOrderWithOutbox:
  pattern transactional-outbox
  binding sqlite-transactional-outbox
  writes OrderOperation, OutboxMessage
  emits outbox-message-recorded
  guarantee atomic-state-and-outbox
  on-failure rollback
  boundary order-transaction-authority`;

export const patternCommands = `npx alchlang patterns
npx alchlang patterns --available
npx alchlang patterns --blocked
npx alchlang pattern transactional-outbox`;

export const outboxRunExample = `npx alchlang run outbox-operation.alch CommitOrderWithOutbox \\
  --actor OrderService \\
  --facts '{"operationId":"op-1","orderId":"order-1","status":"pending","outboxMessageId":"msg-1","occurredAt":"2026-09-03T12:00:00.000Z","payload":{"kind":"order-committed"}}' \\
  --grant order-transaction-authority \\
  --binding sqlite-transactional-outbox \\
  --database ./outbox.sqlite \\
  --effect-request-file examples/outbox-request.json`;

export const outboxOperations = `npx alchlang outbox pending --database ./outbox.sqlite
npx alchlang outbox status --database ./outbox.sqlite --status dead
npx alchlang outbox dispatch --database ./outbox.sqlite \\
  --transport stdout --worker-id local-worker
npx alchlang outbox requeue-dead --database ./outbox.sqlite \\
  --message-id msg-1 --now 2026-09-03T12:05:00.000Z`;

const section = (id: string) => sections.find((item) => item.id === id)!;

export const navGroups = [
  { label: "Start", items: [section("quickstart"), section("workspace"), section("model"), section("integration")] },
  { label: "Language", items: [section("source"), section("sfol"), section("contracts"), section("backend-types"), section("type-selection"), section("lexical-reference"), section("declaration-reference"), section("formal-grammar")] },
  { label: "Compiler", items: [section("domainspec-target"), section("compiler")] },
  { label: "Runtime", items: [section("actions"), section("effects"), section("outbox"), section("evidence")] },
];

export const docsSearchEntries: readonly SearchEntry[] = [
  ...sections.map((section) => ({ ...section, terms: [section.id] })),
  ...backendTypes.map((type) => ({ id: backendTypeAnchor(type.syntax), eyebrow: `${type.id} · ${type.category}`, title: type.name, summary: `${type.meaning} ${type.useWhen}`, terms: [type.syntax, ...type.requirements, ...declarationClauses[type.syntax].flatMap((clause) => [clause.clause, clause.value, clause.meaning])] })),
  ...supportingDeclarations.map((item) => ({ id: supportingDeclarationAnchor(item.syntax), eyebrow: "Supporting declaration", title: item.name, summary: item.detail, terms: [item.syntax, item.form, ...declarationClauses[item.syntax].flatMap((clause) => [clause.clause, clause.value, clause.meaning])] })),
  ...lexicalRules.map((item) => ({ id: "lexical-reference", eyebrow: "Lexical rule", title: item.subject, summary: item.rule, terms: [item.syntax, item.error] })),
  ...commonDiagnostics.map((diagnostic) => ({ id: diagnosticAnchor(diagnostic), eyebrow: "Diagnostic", title: diagnostic, summary: "Compiler diagnostic documented by the syntax and validation reference.", terms: [diagnostic] })),
];

export function docsViewForHash(hash: string): DocsView {
  const target = hash.replace(/^#/, "");
  return target === "tutorial" || docsSearchEntries.some((entry) => entry.id === target)
    ? "tutorial"
    : "overview";
}
