# Build and change an application with Craft and AlchLang

**AlchLang** lets you write a domain model in readable source. **Craft** validates
its structured form and generates selected native modules. You supply application
implementations and explicit adapters for databases, messaging and transport.
The useful working loop is: declare meaning, check bindings, generate, execute a
small example, change the model, then regenerate and verify.

## Start from a complete example

Install both selected archives into a separate consumer project using the public
quickstart. The [tutorial](TUTORIAL.md) introduces the commands. Copy complete
example directories, including their fixtures and companion files: a source
excerpt alone cannot carry all the declared identities and meanings.

| Your immediate goal | Start here |
| --- | --- |
| Understand and run all 13 meta-types | Installed `examples/meta-types` and Craft `examples/reconciled-commerce` |
| Filter, map, reduce, sort or compute with bounded loops | [Pure computation](COMPUTATION.md) and `examples/computation` |
| Expose a typed API or call one | [API connections](API-CONNECTIONS.md) and `examples/api-connections` |
| Form a larger application with selected explicit bindings | [Application examples](../examples/application-v1/README.md) |
| Understand source syntax and profiles | [Language reference](LANGUAGE.md) |

## Decide what each declaration means

An Entity identifies a domain object; a Value Object describes an owned value;
an Enum provides explicit alternatives. Rules describe predicates. Calculations
compute values. Mappings project values. Queries describe reads. Operations
describe actions. Policies select among declared alternatives. StateMachines
propose state transitions and intents. Events describe declared event values.
Workflows coordinate declared steps. Interfaces describe public boundaries.

Write the meaning and types before connecting these roles. A Calculation is the
right owner for a pure aggregate. An Operation is the right place to bind an
external action. An Interface supplies the public contract; your HTTP or other
transport adapter connects that contract to a service implementation.

## Check before generating

For the additive pure computation path:

```sh
./node_modules/.bin/alchlang computation check "$PWD/computation/summary.alch"
./node_modules/.bin/alchlang computation build "$PWD/computation/summary.alch" \
  --out "$PWD/generated-summary"
./node_modules/.bin/alchlang computation verify "$PWD/computation/summary.alch" \
  --out "$PWD/generated-summary"
```

For a complete existing application-v1 source, use the application commands and
its selected companion instead:

```sh
./node_modules/.bin/alchlang check "$PWD/application/commerce.alch" \
  --application-bindings commerce.alch.application.json
./node_modules/.bin/alchlang build "$PWD/application/commerce.alch" \
  --out "$PWD/generated-application" \
  --application-bindings commerce.alch.application.json
```

The companion is resolved relative to the source. Copy the entire application
example directory into `application`, including fixture and input subdirectories.
Keep the selected profile and explicit provider bindings visible; formation or
verification of artifacts is not execution of a provider pack.

## Run a witness you can understand

Use known small inputs and a fixed expected result. For the summary calculation,
the two accepted orders yield count 2 and total 1250. Compare generated native
execution with the independent reference result. Then test an empty input and a
repeated item so the order and seed behavior are visible.

For API integration, use the shipped in-memory transport example against freshly
generated native Interface modules. Its known request yields exact values
`id=1`, `net=93`, `fee=5`. Invalid input must fail before service or transport
invocation. The API guide explains how to attach that tested adapter shape to
your own host without treating an Interface as a server.

## Change meaning and implementation together

Change a declared expression and its authored meaning, refresh its exact
companion bindings, and generate into a fresh directory. The computation chapter
includes a count-by-two edit whose output changes to count 4 with the same input.
Keep that changed result as evidence that the model affected the generated
program. Verification rejects outputs from the previous model and detects a
modified generated module.

Keep source, companions and expected examples under your version control. Keep
credentials in your own approved configuration mechanism. Generated manifests
record the exact inputs and artifact bytes; they do not prove that your domain
meaning is correct or that an external service ran.

## Author and edit a pure computation

Use [the complete computation recipe](COMPUTATION.md#create-your-own-calculation)
to write a Calculation, draft a new companion with the installed
`examples/computation/draft-companion.mjs`, review its authored meaning and owner,
adopt the companion, and check/build/verify/compile/run it. The guide creates a
sum producing 5, then edits both expression and meaning to produce 10 while
preserving version1. A proposed companion establishes syntax and binding
coverage; `alchlang computation check` adds Craft's type/reference/purity/cycle
checks. Neither step approves the domain meaning.

Generate into a new artifact directory and compile into a sibling native directory.
Companion identities bind exact saved bytes, so changing formatting or source
requires current bindings and fresh artifacts. Keep API/operation effects in the
application transport bindings described in [API connections](API-CONNECTIONS.md);
the standalone computation remains pure.

## Open Questions

The [computation guide](COMPUTATION.md#open-questions) and
[API guide](API-CONNECTIONS.md#open-questions) own their remaining scope questions.
Public preview publication is still held. Local hosting, TDE and EVF remain
deferred; durable recovery expansion is a separate planned chapter.
