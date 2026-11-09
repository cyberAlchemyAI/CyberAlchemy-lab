# DomainSpec v2 User Guide (Pre-release)

## Start here

DomainSpec helps a team make a **checked map of a software feature**.

**DomainSpec is the system that performs this work. A DomainSpec specification is the
project description a team creates with it.** An application framework is different:
it supplies code structure or runtime services. DomainSpec does not replace that
framework and does not run the application.

Suppose a game team says:

> A player can unlock a door when they have the right key.

That sentence sounds clear, but developers still need answers:

- What identifies the player?
- Where does the “has the key” decision live?
- Which action changes the door?
- What records a successful unlock?
- Which code is expected to implement each part?
- What evidence would show that the code matches the description?

DomainSpec gives those answers stable names, types, and connections.

```text
Player -------- performs -------> UnlockDoor -------- produces -------> DoorUnlocked
                                     ^
                                     |
                                  enforces
                                     |
                                 HasKeyRule
```

This checked map is useful, but it has limits. It does not prove that the game is fun,
that the player really has a key at runtime, or that the application is ready to ship.

### What DomainSpec does

DomainSpec helps a team:

1. write down the important parts of a feature;
2. assign each part a clear role;
3. connect the parts using allowed relationships;
4. reject malformed descriptions;
5. generate readable views and focused checks from supported inputs;
6. compare selected expectations with evidence from code; and
7. record exactly what a result proves and where it stops.

### What DomainSpec does not do

DomainSpec does not:

- guess missing business meaning;
- generate a complete application from prose;
- prove that a written requirement is correct;
- turn every generated check into a test execution;
- approve an implementation;
- authorize a release or deployment; or
- replace the people responsible for those decisions.

For the complete system map, see [ARCHITECTURE.md](ARCHITECTURE.md).

### A useful analogy: grammar for a system description

Think of DomainSpec as a grammar checker for a system map:

- concepts are the vocabulary;
- meta-types are the roles each word plays;
- relationships are directed verbs; and
- the typed graph is the complete sentence map.

The analogy stops at truth. A grammar checker can reject a malformed sentence, but it
cannot prove that the sentence is true. DomainSpec can reject some malformed system
descriptions, but it cannot by itself prove the business meaning or running software.

## Learn one idea at three levels

The same idea stays constant at every level:

> Write the intended meaning, check its structure, gather evidence, and keep the final
> decision separate from the evidence.

### Level 1: one decision and one action

The player may unlock the door only when the player has the required key.

```text
HasKeyRule -- enforces --> UnlockDoor
```

| Concept | Type | Plain meaning |
| --- | --- | --- |
| `HasKeyRule` | Rule | Gives a yes-or-no decision. |
| `UnlockDoor` | Operation | Changes the state of the game. |

This shows where the decision belongs and what it controls.

It does **not** show whether code enforces the rule.

### Level 2: one complete feature

Add the actor and the recorded result:

```text
Player -------- performs -------> UnlockDoor -------- produces -------> DoorUnlocked
                                     ^
                                     |
                                  enforces
                                     |
                                 HasKeyRule
```

Now DomainSpec can check that:

- `Player` is an Entity with an identity field;
- `HasKeyRule` is a Rule with a boolean result;
- `UnlockDoor` is an Operation that changes state;
- `DoorUnlocked` is an Event about something that already happened; and
- all three connections point in allowed directions to existing nodes.

This shows that the feature description follows the selected structural rules.

It does **not** run the game or prove the business rule is correct.

### Level 3: compare the feature with code

The target end-to-end path adds implementation evidence:

```text
feature source
  -> checked graph
  -> focused obligations
  -> checks against exact code
  -> evidence from several providers
  -> independent review
  -> owner decision
```

A TypeScript provider might report:

```text
expected: HasKeyRule guards UnlockDoor
observed: UnlockDoor calls HasKeyRule before changing state
result:   supported for these exact files and tool versions
```

If the provider cannot understand an indirect framework call, it must report
`unsupported`. It may not convert uncertainty into PASS.

This shows how evidence can support a narrow implementation claim.

It does **not** describe a complete current pipeline. The selected JSON source does not
yet feed the general obligation engine directly, the general factory-to-EVF join is not
complete, and release still requires a separate owner decision.

## The current product boundary

This guide describes private, pre-release repository tooling.

| Available now | Not available yet |
| --- | --- |
| Experimental JSON source profile | Stable external installation |
| Internal compiler and contract tests | Released public CLI |
| Private 13-type, three-profile instantiation and static-conformance CLI | Published package and production runtime proof |
| Generated graph and source manifest | Complete JSON-to-obligation bridge |
| Generated Markdown view and build receipt | General end-to-end EVF receipt |
| Legacy Markdown derivation engine | Production monitoring and deployment |
| Bounded local conformance experiments | Production authorization |

The current JSON profile supports only four types and three relationships:

```text
Types:         Entity, Rule, Operation, Event
Relationships: performs, enforces, produces
```

DomainSpec's full language is larger. A type being active in the language does not mean
the current JSON profile can author it.

This guide has `authority_effect: none`. It explains the system but cannot change a
definition, approve a code form, or authorize release.

## Walk through Key and Door

The walkthrough follows six decisions. The first four define the feature. The last two
control what the result means and how later changes are handled.

| Decision | Concrete choice in Key and Door | Consequence | Current or target? |
| --- | --- | --- | --- |
| Scope | Keep actor, permission, state change, and recorded result | The feature contains four concepts | Current checked fixture |
| Identity | Use `player_id` to identify the Player | `Player` forms as an Entity | Current checked fixture |
| Permission | Put the yes/no key decision in `HasKeyRule` | The Rule `enforces` the Operation | Current checked fixture |
| Outcome | Change the door through `UnlockDoor` and record `DoorUnlocked` | Operation and Event have separate jobs | Current checked fixture |
| Evidence | Claim only structural formation and generation | Runtime and release stay unsupported | Current build-receipt boundary |
| Revision | Change source, regenerate, and review again | The old receipt remains bound to old bytes | Current manual workflow; guided difference inbox is target design |

Each decision answers one question. None is consent to approve the feature or release
the implementation.

### Step 1: choose the feature boundary

The game also has combat, maps, inventory, quests, animation, and sound. The team does
not need to model all of that to define one door mechanic.

For this feature, the boundary contains:

- the actor;
- the permission check;
- the state-changing action; and
- the recorded result.

```text
Player + HasKeyRule + UnlockDoor + DoorUnlocked
```

The phrase **feature boundary** is teaching language in this guide. It is not a
DomainSpec meta-type.

**Reader decision:** model the whole game, only presentation details, or the four parts
of the unlock mechanic? The checked example chooses the four-part mechanic. The current
repository can check that fixture; a guided authoring screen remains target design.

### Step 2: identify the player

The player's health, location, and inventory can change while the game still recognizes
the same player. The stable value is `player_id`.

That makes `Player` an **Entity**: something whose identity continues while other data
changes.

**Reader decision:** use the room, carried key, or `player_id` as the continuing
identity? The checked source chooses `player_id` because rooms and inventory can change.

```json
{
  "kind": "Entity",
  "body": {
    "fields": [
      { "name": "player_id", "type": "string", "identity": true }
    ]
  }
}
```

The current profile checks that an Entity has at least one identity field. It does not
check whether `player_id` is globally unique in the running game.

### Step 3: place the key decision

Before the door changes, the game needs a yes-or-no answer:

```text
Does the player have the required key?
```

That makes `HasKeyRule` a **Rule**. A Rule allows or blocks behavior.

**Reader decision:** place the key check in the actor, success event, or a Rule that
controls the action? The checked source chooses a Rule. The current compiler checks its
shape and direction; it does not evaluate live inventory.

```json
{
  "kind": "Rule",
  "body": {
    "formal_return_type": "boolean"
  }
}
```

The Rule controls the action through a directed relationship:

```text
HasKeyRule -- enforces --> UnlockDoor
```

Reversing the arrow would make a different and invalid statement.

### Step 4: describe the state change

Immediately before success, the door is locked. Immediately after success, it is
unlocked.

That makes `UnlockDoor` an **Operation**: a business action that changes state.

**Reader decision:** describe permission only, record success only, or include the
actual state-changing action? The checked source includes the Operation because the
door must change.

```json
{
  "kind": "Operation",
  "body": {
    "state_change": "yes"
  }
}
```

The player performs the Operation:

```text
Player -- performs --> UnlockDoor
```

### Step 5: record what happened

After a successful unlock, the game records `DoorUnlocked`.

That makes it an **Event**: a statement about something that already happened.

```json
{
  "kind": "Event",
  "body": {
    "temporal": "past"
  }
}
```

The Operation produces the Event:

```text
UnlockDoor -- produces --> DoorUnlocked
```

### Step 6: review the complete story

```text
Player -------- performs -------> UnlockDoor -------- produces -------> DoorUnlocked
                                     ^
                                     |
                                  enforces
                                     |
                                 HasKeyRule
```

Review the feature by asking:

1. Is every important concept present?
2. Does each concept have the right type?
3. Does each type contain the information its formation rule requires?
4. Are connections directed correctly?
5. Does every connection point to an existing node?
6. What does the check prove, and what remains untested?

**Evidence decision:** a passing build supports structural formation, resolution,
provenance, and repeatable generation for the exact fixture. It does not support a
runtime or release claim.

## Work with the current source files

### Files people edit

The current Key and Door fixture has six editable files:

```text
project.json
specs/key-and-door/feature.json
specs/key-and-door/nodes/player.json
specs/key-and-door/nodes/has-key-rule.json
specs/key-and-door/nodes/unlock-door.json
specs/key-and-door/nodes/door-unlocked.json
```

| File | What it controls |
| --- | --- |
| `project.json` | Project ID, selected profile, registry digests, features, generated folder |
| `feature.json` | Feature ID and the complete list of node files |
| `nodes/*.json` | One concept's identity, type, intent, required body, and outgoing connections |

Study the checked source directly:

- [Project record](impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/project.json)
- [Feature record](impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/specs/key-and-door/feature.json)
- [Player](impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/specs/key-and-door/nodes/player.json)
- [HasKeyRule](impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/specs/key-and-door/nodes/has-key-rule.json)
- [UnlockDoor](impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/specs/key-and-door/nodes/unlock-door.json)
- [DoorUnlocked](impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/specs/key-and-door/nodes/door-unlocked.json)

### Files DomainSpec generates

```text
.domainspec/generated/graph.json
.domainspec/generated/source-manifest.json
.domainspec/generated/SPEC.md
.domainspec/generated/markdown-view.json
.domainspec/generated/build-receipt.json
```

| Generated file | Question it answers |
| --- | --- |
| `graph.json` | Which normalized concepts and connections did the compiler build? |
| `source-manifest.json` | Which source file and digest produced each graph record? |
| `SPEC.md` | How can a person read the normalized graph? |
| `markdown-view.json` | Which graph, Markdown bytes, and generator version belong together? |
| `build-receipt.json` | Which profile, registries, source files, outputs, and generator were checked? |

Generated files are read-only. If the meaning changes, edit the source and regenerate
all bound outputs.

### A complete Rule node

The checked fixture stores `HasKeyRule` like this:

```json
{
  "schema_version": "minted-node/v1",
  "node_id": "key-and-door.HasKeyRule",
  "feature_id": "key-and-door",
  "kind": "Rule",
  "intent": "Allow the unlock operation only when the player holds the key.",
  "body": {
    "formal_return_type": "boolean"
  },
  "connections": [
    {
      "edge_id": "key-and-door.edge.has-key-rule-enforces-unlock-door",
      "type": "enforces",
      "to": "key-and-door.UnlockDoor"
    }
  ]
}
```

Read it as six answers:

| Field | Answer |
| --- | --- |
| `node_id` | What stable name does this concept have? |
| `feature_id` | Which feature owns it? |
| `kind` | What job does it perform? |
| `intent` | What does the team mean by it? |
| `body` | Which information must every Rule provide? |
| `connections` | What does this Rule control? |

The structural check can confirm the required shape and allowed connection. It cannot
decide whether the game design is right or inspect the game's code.

### Change the requirement safely

Suppose the team decides that a master key should also work.

**Revision decision:** edit generated Markdown, keep using the old result, or change
owned source and build a new result? Only the third choice preserves traceability.

Use this sequence:

```text
change project-owned source
  -> regenerate every bound output
  -> inspect the new graph and receipt
  -> review the changed meaning
```

Do not edit generated `SPEC.md`. Do not reuse the old receipt. Both belong to the old
source revision.

## The two repository paths

Two working paths exist, but they do not yet connect into one general workflow.

### Selected JSON source path

```text
project.json -> feature.json -> node files
             -> graph + source manifest
             -> generated SPEC.md + view record
             -> build receipt
```

This path checks the current consumer-source package. It tests schemas, paths, profile
bindings, relationship endpoints, determinism, provenance, and stale generated bytes.

It does not generate general test obligations from the selected graph yet.

### Legacy Markdown derivation path

```text
legacy aspect documents or explicit normalized SPEC.md
  -> parsed graph
  -> deterministic derivation rules
  -> stable obligation IDs
  -> test specifications and structural tests
```

An **obligation** is one named item that later checks or evidence must account for.

Example: a declared state transition can produce a positive transition test. An
explicitly invalid transition can produce a rejection test.

The engine does not invent business behavior missing from the source. It uses no
language model and no network during derivation.

For maintainers in a prepared checkout:

```bash
npm --prefix projects/domainspec-v2/impl run validate:content
npm --prefix projects/domainspec-v2/impl run validate:rels
npm --prefix projects/domainspec-v2/impl run validate
```

These are repository commands for the legacy validation surface. They are not a stable
external CLI for the selected JSON package.

### The unfinished bridge

The future machine route is:

```text
selected JSON -> verified machine graph -> obligations -> generated checks
```

It must not read generated Markdown as source or silently fall back to the legacy
engine. Until this bridge is implemented and independently checked, a successful JSON
build does not mean obligation derivation ran.

## Choose the right concept type

A **meta-type** is the role a concept plays.

### Quick decision tree

```text
Does it describe data?
  +-- Keeps identity while changing? --------------------> Entity
  +-- Equal when every field is equal? ------------------> Value Object
  +-- Fixed list of names? ------------------------------> Enum
  +-- Owns legal state transitions? ---------------------> State Machine

Does it describe behavior?
  +-- Changes state? ------------------------------------> Operation
  +-- Reads without changing state? ---------------------> Query
  +-- Calculates a value? -------------------------------> Calculation
  +-- Allows or blocks? ---------------------------------> Rule
  +-- Selects a strategy? -------------------------------> Policy
  +-- Coordinates several ordered actions? -------------> Workflow

Does it connect parts?
  +-- Exposes callable behavior? ------------------------> Interface
  +-- Records a past fact? ------------------------------> Event
  +-- Converts one data shape to another? ---------------> Mapping
```

### Active backend types

The **formation rule** is the minimum information a declaration must contain to count
as that type.

| Type | Concrete example | Required formation rule | Current JSON profile? |
| --- | --- | --- | --- |
| Entity | `Player` | Typed fields; at least one identity field | Yes |
| Value Object | `Money` | Typed fields, no identity, explicit equality rule | No |
| Enum | `DoorState` | Non-empty fixed value set | No |
| Operation | `UnlockDoor` | `state_change = yes` | Yes |
| Query | `GetDoorStatus` | `state_change = no` | No |
| Calculation | `DamageAmount` | `formal_return_type = value` | No |
| Rule | `HasKeyRule` | `formal_return_type = boolean` | Yes |
| Policy | `RetryPolicy` | `formal_return_type = strategy` | No |
| Workflow | `PlayerOnboarding` | `scope = intra-feature` or `cross-feature` | No |
| Interface | `DoorAPI` | `interface_kind` is present | No |
| Event | `DoorUnlocked` | `temporal = past` | Yes |
| Mapping | `DoorResponseMapping` | `direction` is present | No |
| State Machine | `DoorLifecycle` | `has_transitions = yes` | No |

Only Entity, Rule, Operation, and Event have bodies in the current experimental JSON
profile. Do not invent JSON bodies for the other nine.

### UI types are not active backend types

The registry also tracks UI proposals:

- candidate: Page, Layout, Component, View Model, Hook, Form, Action, Guard, Binding;
- deferred: Adapter and State Indicator; and
- superseded: Saga, replaced by Workflow.

Candidate means “worth testing,” not “approved.” Deferred means the distinction is not
settled. Superseded means the old ID remains only for history.

For exact formation rules and maturity, use
[meta-types.md](definitions/meta-types/meta-types.md) and
[meta-types.yml](definitions/meta-types/meta-types.yml).

## Choose the right relationship

A relationship is a directed, checked connection between typed concepts.

The current JSON profile supports:

| Connection | Meaning |
| --- | --- |
| `Entity --performs--> Operation` | The actor initiates the action. |
| `Rule --enforces--> Operation` | The decision allows or blocks the action. |
| `Operation --produces--> Event` | Successful action records a past fact. |

The full registry contains 31 active signatures: 17 backend, 8 UI, and 6 UI-to-backend.
The UI connection verbs may be active while their endpoint UI types remain candidate or
deferred. Relationship status and type status are separate.

<details>
<summary>Reference: all 31 active relationship signatures</summary>

#### Backend relationships: 17

| Connection | Plain meaning |
| --- | --- |
| `Entity --performs--> Operation` | An actor initiates an action. |
| `Operation --produces--> Event` | Successful behavior records a past fact. |
| `Operation --produces-for--> Entity` | An action writes or creates a view for another feature. |
| `Operation --creates--> Entity` | An action owns creation of an Entity type. |
| `Event --triggers-cross--> Operation` | A fact in one feature activates behavior in another. |
| `Rule --enforces--> Operation` | A yes/no Rule gates an action. |
| `Calculation --calculates--> Operation` | A calculation supplies a value to an action. |
| `Event --transitions--> State Machine` | An Event advances a lifecycle. |
| `Interface --exposes--> Operation or Query` | A boundary makes behavior callable. |
| `Workflow --orchestrates--> Operation[]` | A Workflow coordinates ordered actions. |
| `Policy --applies--> Operation or Calculation` | A Policy selects behavior. |
| `Mapping --maps--> Entity or Interface` | A Mapping converts a shape. |
| `Entity --contains--> Value Object` | An Entity embeds a complete value. |
| `Query or Operation --reads--> Entity` | Behavior depends on Entity data. |
| `Entity --emits--> Event` | An Entity is the subject of an Event. |
| `Entity --owns--> Entity` | The source owns lifecycle, custody, or writes. |
| `Entity --belongs-to--> Entity` | The source is assigned to the target. |

#### UI relationships: 8

| Connection | Plain meaning |
| --- | --- |
| `Page --renders--> Component[]` | A Page renders Components. |
| `Layout --wraps--> Page[]` | A Layout wraps Pages. |
| `Component --composes--> Component[]` | A Component contains child Components. |
| `Component --consumes--> Hook` | A Component uses reactive behavior. |
| `Form --submits--> Action` | A Form delegates submission. |
| `Adapter --shapes--> View Model` | A deferred Adapter shapes display data. |
| `Guard --protects--> Page` | A Guard controls UI access behavior. |
| `Component --displays--> View Model` | A Component displays screen-shaped data. |

#### UI-to-backend relationships: 6

| Connection | Plain meaning |
| --- | --- |
| `Binding --fetches--> Query` | A Binding retrieves data. |
| `Binding --mutates--> Operation` | A Binding invokes a state-changing action. |
| `State Indicator --reflects--> State Machine` | A deferred indicator shows lifecycle state. |
| `View Model --derives--> Entity` | Display data comes from Entity fields. |
| `Form --contracts--> Interface` | A Form aligns with a callable boundary. |
| `Guard --mirrors--> Rule` | A client Guard mirrors, but does not replace, a backend Rule. |

</details>

Generated, postponed, and retired connections remain separate:

- `owned-by` is generated reverse navigation for `owns`; authors never write it.
- `depends-on` is postponed because no concrete example yet requires distinct checks.
- Operation-to-Value-Object return remains a property, not a separate relationship.
- Event publisher/payload separation remains postponed.
- `enforces-cross` is retired; `enforces` already records cross-feature endpoints.

### When a connection deserves its own relationship

A connection needs a DomainSpec relationship type only when removing it changes a
real result, such as:

- an allow/reject decision;
- a derived obligation;
- a generated projection;
- a composition path;
- an owner route; or
- a generated artifact.

An import, field reference, diagram arrow, or convenient reverse link is not enough.

Examples:

```text
NoDuplicateRule -- enforces --> GenerateSettlement
DealSplitCalculation -- calculates --> GenerateSettlement
GenerateSettlement -- creates --> SettlementTransaction
GetSettlementPreview -- reads --> SettlementTransaction
```

The full machine registry is
[relationships.yml](definitions/relationships/relationships.yml). Use the
[relationship guide](definitions/relationships/relationships.md) for readable details.

## When the language is not enough

Most projects need a new **concept**, not a new meta-type.

- `HasKeyRule` is a new project concept using the existing Rule type.
- `Page` would change the shared DomainSpec vocabulary for many projects.

Before proposing a new meta-type:

1. Try every nearby active type.
2. Give a concrete example that those types model incorrectly.
3. State which validation or generated result would change.
4. Write valid and deliberately invalid examples.
5. Define allowed relationship roles.
6. Test the distinction in more than one real setting.
7. Send the evidence to the definitions owner.

### Example: Page versus Component

A Page owns a route, primary content, layout, and access context. A Component is a
reusable visual unit with no route of its own.

That sounds like a useful distinction, but Page remains a candidate because its evidence
has not yet been independently reproduced across routing frameworks.

A candidate schema can show that the distinction is testable. It cannot activate the
type, add it to every profile, approve a code form, or authorize release.

## From the specification to code evidence

Consider this claim:

> `HasKeyRule` guards `UnlockDoor` in the implementation.

Supporting that claim requires several different records:

| Record | Concrete question |
| --- | --- |
| Business source | Who decided that the key is required? |
| Specification | Which exact source files state the Rule, Operation, and connection? |
| Checked graph | Did the compiler resolve them correctly? |
| Obligation | What must the implementation preserve? |
| Generated check | Which executable probe represents that obligation? |
| Code binding | Which function or module implements each concept? |
| Observation | What did the named tool see in the exact code? |
| Receipt | What follows from the evidence, and what remains unsupported? |

None can replace another.

The [implementation-conformance architecture](development/implementation-conformance/ARCHITECTURE.md)
designs the pure comparison layer between admitted expectations and already collected
code facts. It is an admitted Design, not a completed runtime package. The conformance
factory below is implemented bounded experiment machinery; the two must not be confused.

### The conformance factory

The [architecture-conformance factory](impl/architecture-conformance/factory/README.md)
runs bounded local code-evidence experiments.

One run:

1. names every input, dependency, and tool;
2. records exact versions and digests;
3. copies locked inputs into a private snapshot;
4. runs checks in dependency order;
5. repeats semantic work in separate processes;
6. rejects different semantic results;
7. keeps process details separate from semantic meaning; and
8. publishes only a complete verified run.

Example: a check for `Rule enforces Operation` may use only Rule and Operation results
verified in that same run. It cannot reuse an old Rule result from another run.

The factory proves only its named local claim. It does not approve an implementation or
prove production behavior.

### EVF combines evidence without making it stronger

The [Evolvable Validation Framework](development/evolvable-validation-framework/ARCHITECTURE.md)
is the common evidence architecture for different validators.

Example:

```text
structure provider: PASS
runtime provider:   PASS
formal provider:    UNSUPPORTED
```

EVF may report that structure and the tested runtime case are supported. It may not
claim formal coverage or return an unlimited PASS.

This is the central rule:

```text
final claim cannot be stronger than the available evidence
```

EVF has architecture and partial candidate-local evidence. No current receipt proves
the complete selected-source-to-independent-consumer path.

## Read results without overclaiming

### Six separate status questions

Do not compress everything into “complete” or “green.” Ask:

| Question | Example answers |
| --- | --- |
| Is the type part of the language? | active, candidate, deferred, superseded |
| Is a code representation proposed? | candidate-mapped, not admitted |
| Can a tool check a target language? | provider absent, bounded proof |
| Did this exact check pass? | pass, fail, expected-red, unsupported |
| May the next controlled step begin? | ready, blocked, excluded |
| Who approved use or release? | none, owner-decided, release-authorized |

### Progress states for one feature

These states answer different questions and should not be reduced to one progress bar:

| State | Concrete meaning |
| --- | --- |
| Draft | People are still editing project-owned meaning. |
| Structurally checked | The exact source passed its profile and graph checks. |
| Review needed | A person must decide whether the description says the right thing. |
| Code evidence compared | Selected implementation evidence was compared with expectations. |
| Owner decision recorded | The responsible owner made one bounded decision on exact bytes. |
| Needs update | Source, code, tools, or expectations changed after the earlier result. |

A feature can stop honestly at “Structurally checked” when no admitted code-evidence
path exists. That is useful evidence, not failure and not release readiness.

Example: Entity is an active DomainSpec type. An experiment may propose a way to
represent Entity in code and pass artificial fixtures. That does not mean a tool has
inspected real target code, that lifecycle behavior is proven, or that release is
approved.

### Common false conclusions

| Claim | Why it is wrong |
| --- | --- |
| “The class name ends in Entity, so it is an Entity.” | Identity and formation rules determine the type, not the class name. |
| “The function returns boolean, so the source must be a Rule.” | Code cannot rewrite the intended domain meaning. |
| “A generated test exists, so the application passed it.” | Test generation and test execution are different events. |
| “The test passed, so the application is correct.” | One test covers only its named input, check, and expected result. |
| “Candidate-mapped means implementation-ready.” | A proposed code representation still needs admission, tooling, targets, and evidence. |
| “Generated Markdown is the source.” | In the selected path, edit JSON source and rebuild. |
| “An active UI relationship activates Page or Guard.” | Relationship and endpoint-type maturity are separate. |
| “Saga is available because it is no longer active.” | Saga is permanently superseded; use Workflow. |

## What DomainSpec owns—and what it does not

The canonical private [product ontology package](ontology/README.md) connects the
business and system views of DomainSpec. It remains a read model: it cannot write back
into the strict source contract, activate a definition, or approve an implementation.

| Owner or surface | What it owns | What it cannot do |
| --- | --- | --- |
| DomainSpec definitions | Shared type meanings, formation rules, allowed relationships | Prove that an application behaves correctly |
| Project source | The concrete business meaning of a feature | Redefine the shared language by using a new label |
| Compiler | Structural checks and generated read-only views | Prove business correctness or runtime behavior |
| Derivation engine | Obligations from supported inputs | Prove the obligations were satisfied |
| Code-evidence provider | Observations about exact files and tools | Approve itself or expand its claim |
| EVF | Compatible evidence composition and visible gaps | Fill missing evidence or authorize release |
| Product ontology | Canonical business-system explanation and traceability | Become definition or implementation source authority, promote itself, or authorize release |
| Implementation/release owner | Acceptance, deployment, release, production decisions | Be replaced by a receipt with `authority_effect: none` |

Historical DomainSpec v1 and wider private-system documents may explain why a decision
was considered. They do not override current DomainSpec v2 authority.

## Troubleshooting

### The compiler reports a missing node

Check `feature.json` and the target named by the source node's outgoing connection. Add
or correct the project-owned source. Do not invent the missing node in generated output.

### The type is active, but the JSON profile rejects it

The full language and the current profile have different coverage. Use only Entity,
Rule, Operation, and Event in the current profile. If another type is required, raise a
profile capability proposal instead of inventing a JSON body.

### A generated file is stale

Find the source change and regenerate the entire bound output set. Do not repair
`graph.json` or generated `SPEC.md` by hand.

### `npx --no-install` cannot find `tsx`

The private checkout is not prepared. There is no approved clean-install procedure yet.
Ask the maintainer for the supported local setup; do not bypass the dependency decision
by downloading tools implicitly.

### pnpm reports `ERR_PNPM_IGNORED_BUILDS`

The workspace's allowed-build-script policy is unresolved. A setup owner must decide
which dependency scripts are permitted. Do not run `pnpm approve-builds` blindly.

### Legacy validation passes but engine lint fails

The commands check different boundaries. Content and relationship checks validate type
shapes and connections. Engine lint also checks the Markdown parser's required table and
formal-expression shapes. Report each result separately.

### A receipt contains parser rejections

A receipt records accepted, omitted, and rejected material. It is not automatically a
PASS badge. Inspect the rejection summary and the exact source references.

### `npm run validate` passed

Report the exact command. The general script does not run every engine, typecheck,
factory, experiment, browser, release, or production check.

## Extend DomainSpec carefully

### Add a project concept

Use an active type, add its required information, connect it using allowed
relationships, and check the complete graph.

### Propose a meta-type

Show a concrete distinction that active types lose. Add formation rules, valid and
invalid cases, relationship roles, and the exact validation or output that changes.
Keep the definitions-owner decision separate.

### Propose a relationship

Specify:

- source and target types;
- direction;
- allowed feature boundary;
- quantity limits;
- valid and invalid examples;
- the failure to report; and
- the check or generated result that changes.

### Add a code-evidence provider

Declare exact inputs, implementation components, tools, dependencies, generated checks,
deliberately altered cases, expected failures, replay behavior, tamper checks, and the
strongest permitted claim. Adding a provider must not make the shared runner or language
definition depend on one programming language.

## A broader legacy example

The Financial Settlement feature shows more active backend types:

| Concept | Type | Plain role |
| --- | --- | --- |
| `SettlementTransaction` | Entity | Identity-bearing settlement record |
| `SettlementResult` | Value Object | Complete result value with no identity |
| `SettlementTransactionType` | Enum | Fixed transaction categories |
| `GenerateSettlement` | Operation | Creates or changes settlement state |
| `GetSettlementPreview` | Query | Reads a preview without changing state |
| `DealSplitCalculation` | Calculation | Computes a value |
| `NoDuplicateMakeupRule` | Rule | Blocks an invalid duplicate |

```text
NoDuplicateMakeupRule -- enforces --> GenerateSettlement
DealSplitCalculation  -- calculates --> GenerateSettlement
GenerateSettlement    -- creates --> SettlementTransaction
GetSettlementPreview  -- reads --> SettlementTransaction
```

This is a useful **legacy Markdown language example**. It is not the selected
independent-node JSON source format. Use Key and Door when copying the current source
layout.

See the [legacy feature](impl/spec/features/financial-settlement/SPEC.md) and its
[generated view](impl/spec/features/financial-settlement/generated/SPEC.md).

## Current status

The repository changes frequently. Do not use an old prose snapshot as current
evidence.

For live status:

1. read [.craft/ledger.yml](.craft/ledger.yml);
2. inspect the latest same-lane receipt;
3. check the current source bytes and digests; and
4. rerun the exact validator for the claim you need.

Stable facts this guide relies on:

- DomainSpec v2 is private and pre-release.
- The current consumer profile is experimental.
- It supports four source types and three source relationships.
- The full language has 13 active backend types and 31 active relationship signatures.
- JSON compilation and legacy Markdown derivation are separate paths.
- Implementation-conformance is a Design, not a complete runtime package.
- EVF has partial evidence but no complete independently consumed vertical.
- Production authorization remains external and unsatisfied.

<details>
<summary>Historical validation snapshot: August 7–13, 2026</summary>

This snapshot is preserved so readers can see how to report bounded results. It is not
current authority. Rerun the named check before relying on it.

| Date | Observation | What it established | What it did not establish |
| --- | --- | --- | --- |
| August 7 | Two isolated runs of the fixed nine-node factory graph produced the same semantic digest on one host | Same-host repeatability for that graph and toolchain | Other hosts, full type coverage, approval, or production behavior |
| August 13 | Test Derivation Engine tests: 241 passing across 29 files | The bounded test suite passed | A clean TypeScript check or JSON-to-obligation bridge |
| August 13 | Test Derivation Engine TypeScript check: failed | Source-boundary imports and strict typing still needed repair | That passing tests should hide the failure |
| August 13 | Architecture factory TypeScript check and 69 tests across 19 files: passed | That bounded factory component passed its checks | End-to-end DomainSpec validation or release readiness |

The August 12 ontology-experiment snapshot contained both PASS and FAIL results:

| Check | Captured result | Concrete reason or limit |
| --- | --- | --- |
| `validate-ontology.mjs` | FAIL | New `constructed_by` and `validated_by` connections violated the then-current no-cycle rule. |
| `validate-implementation-architecture-types.mjs` | FAIL | Stored expectations and live mapping/type counts disagreed. |
| `validate-meta-type-semantic-slices.mjs` | FAIL | The stored slice differed from repeatable extraction. |
| `validate-rmt-enum.mjs` | FAIL | Recorded hashes were stale and TypeScript status changed. |
| `validate-rmt-calculation.mjs` | FAIL | Properties and material references had changed. |
| `validate-rmt-policy.mjs` | FAIL | Recorded hashes no longer matched. |
| `validate-rmt-query.mjs` | FAIL | Recorded hashes no longer matched. |
| `validate-rmt-value-object.mjs` | FAIL | Relationship rules and accepted-file hashes had changed. |
| `validate-rmt-entity.mjs` | PASS | Synthetic structural controls passed; no real-code inspector or full lifecycle proof existed. |
| `validate-w3-effects-connections.mjs` | PASS | Only the bounded effects-and-connections experiment passed. |
| `validate-w4-orchestration-lifecycle.mjs` | PASS | Only the bounded workflow-and-lifecycle experiment passed. |

A later successful command must never hide an earlier failure. Changed bytes also do
not repair an older receipt; they require new validation and owner review.

</details>

## Source map

### Meaning and authority

- [Architecture](ARCHITECTURE.md) — whole-system map and current/target boundaries.
- [Axioms](authority/AXIOMS.md) — basic project rules.
- [Authority model](authority/AUTHORITY-MODEL.md) — what each result may decide.
- [Source spine](authority/source-spine.md) — which source owns each kind of claim.
- [Definitions](definitions/DEFINITIONS.md) — definition cards and stable IDs.
- [Meta-type cards](definitions/meta-types/meta-types.md) — type meanings and maturity.
- [Relationship registry](definitions/relationships/relationships.yml) — allowed connections.

### Source, generation, and checks

- [Supported profile registry](definitions/minted-project/supported-profiles.yml) — the
  experimental four-type, three-relationship profile.
- [Consumer-source contract](impl/spec/minted-project/INDEX.md) — editable and generated
  record roles.
- [Key and Door fixture](impl/test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door/project.json)
  — complete checked current-layout example.
- [Legacy derivation engine](impl/test-derivation-engine/README.md) — Markdown-to-obligation path.
- [Conformance factory](impl/architecture-conformance/factory/README.md) — repeatable local
  provider runs.
- [EVF architecture](development/evolvable-validation-framework/ARCHITECTURE.md) — evidence
  normalization and composition.

### Guide artifacts

- [Guide schema](COMPLETE-GUIDE.schema.json) — structure of the broader guide contract.
- [Guide manifest](COMPLETE-GUIDE.lanes.json) — reader paths, source boundaries, and
  presentation lanes for the existing guide package.
- [Interactive HTML guide](COMPLETE-GUIDE.html) — separately authored interactive
  rendering; this Markdown simplification does not silently rewrite its interface.

These guide artifacts explain the system. They do not define DomainSpec or grant
authority.

## Glossary

| Term | Plain meaning | Example |
| --- | --- | --- |
| Concept | One named part of a project | `HasKeyRule` |
| Meta-type | The role a concept plays | Rule, Operation, Event |
| Formation rule | Information required for a type | A Rule returns boolean |
| Relationship | An allowed directed connection | `Rule --enforces--> Operation` |
| Typed graph | Concepts joined by checked relationships | The Key and Door map |
| Profile | The exact language subset a source package may use | Four types and three relationships |
| Projection | A generated view of source | `graph.json` |
| Obligation | One named thing later evidence must cover | The Rule must guard the Operation |
| Provider | A bounded tool that gathers evidence | TypeScript source inspector |
| Observation | What the provider saw | A call from `UnlockDoor` to `HasKeyRule` |
| Finding | Comparison of expectation and observation | supported, failed, unsupported |
| Receipt | Exact inputs, checks, results, and limits | Factory semantic receipt |
| Claim ceiling | Strongest conclusion the evidence allows | “Supported for these files” |
| Drift | Two expected-to-match artifacts no longer agree | Old receipt versus changed source |
| Authority effect | Whether an artifact may change official state | Most experiments use `none` |

## Four questions before trusting a claim

For every DomainSpec result, ask:

1. **Meaning:** What does the concept mean, and which project source owns that meaning?
2. **Rules:** Which type, formation, and relationship rules apply?
3. **Evidence:** Which exact check ran on which exact files and tools?
4. **Decision:** Who is allowed to approve the next step?

If one answer is missing, report the gap. Do not fill it with confidence language.
