# Notation Bridge

Target: Alloy and TLA+/PlusCal for DomainSpec v2 modeling.

This bridge explains the notation needed before reading the examples, glossary,
claim ledger, or final learning pack.

## Shared Notation Links

No shared notation file exists for this tower yet. Keep all source-specific
symbols here until another tower reuses them.

## Local Symbols

| Symbol | Source meaning | Plain-language reading | Shared link | Used in |
| --- | --- | --- | --- | --- |
| `sig` | Alloy signature declaring a set of atoms, optionally with fields | A typed bucket of possible domain objects | n/a | `examples/OrderFulfillmentSaga.alloy` |
| `one sig` | Alloy singleton signature | Exactly one named object exists in the bounded model | n/a | Alloy example |
| `extends` | Alloy subtype relation | A concept is a specialized kind of another concept | n/a | Alloy example |
| `set` | Alloy relation multiplicity: zero or more | A field can point to multiple targets | n/a | Alloy example |
| `lone` | Alloy relation multiplicity: zero or one | A field is optional but not plural | n/a | Alloy example |
| `some` | Alloy existential quantifier or non-empty constraint | At least one witness exists | n/a | Alloy example |
| `no` | Alloy empty-set constraint | No witness exists | n/a | Alloy example |
| `all` | Alloy universal quantifier | Every bounded candidate must satisfy this | n/a | Alloy example |
| `run` | Alloy command to find an example satisfying a predicate or constraint | "Show me a possible model" | n/a | Alloy example |
| `check` | Alloy command to search for a counterexample to an assertion | "Try to break this claim within the scope" | n/a | Alloy example |
| `Init` | TLA+ initial-state predicate | The possible first states of the saga model | n/a | TLA+ example |
| `Next` | TLA+ next-state relation | Which step can happen from one state to the next | n/a | TLA+ example |
| `[]P` | TLA+ always/box temporal operator | `P` must hold for every state in a behavior | n/a | TLA+ example |
| `<>P` | TLA+ eventually/diamond temporal operator | `P` must eventually hold along a behavior | n/a | TLA+ example |
| `/\` | TLA+ conjunction | and | n/a | TLA+ example |
| `\/` | TLA+ disjunction | or | n/a | TLA+ example |
| `=>` | TLA+ implication | if left side holds, right side must hold | n/a | TLA+ example |
| `#` | TLA+ not-equal | values differ | n/a | TLA+ example |
| `UNCHANGED x` | TLA+ variable unchanged by action | this action does not modify `x` | n/a | TLA+ example |
| `[Next]_vars` | TLA+ stuttering closure over variables | either a real next step happens or variables stay unchanged | n/a | TLA+ example |

## Reading Order

1. Read Alloy multiplicities first: `one`, `set`, `lone`.
2. Read Alloy commands second: `run` finds examples, `check` searches for counterexamples.
3. Read TLA+ state-machine shape third: `Init`, `Next`, `[]`, `<>`.
4. Read `examples/` only as sketches until a tool-run validates them.

## Notation Residue

| Symbol | Question | Status | Next route |
| --- | --- | --- | --- |
| Alloy temporal operators | Should the first graph lane use static Alloy or Alloy 6 temporal constructs? | open | Alloy validation task |
| TLA+ fairness | Which saga obligations require fairness rather than safety invariants? | open | TLA+ validation task |
| PlusCal labels | Should the first temporal model be authored in PlusCal and translated? | open | TLA+ validation task |
