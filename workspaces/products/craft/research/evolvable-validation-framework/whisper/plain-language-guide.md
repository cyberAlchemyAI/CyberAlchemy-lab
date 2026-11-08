# How DomainSpec turns a graph into a composability proof

Imagine a map made of boxes and arrows. Each box is a thing in a software system, and each arrow says how two things are related. That map is a **graph**. DomainSpec is the set of structured notes that describes this graph before or while the software is built.

The goal is not merely to draw a map. The goal is to check that the map makes sense, that the arrows correspond to real code behavior, and that the checks leave behind evidence someone else can inspect.

## The small glossary

**Node:** one box in the map. Examples are `Rule`, `Operation`, `Entity`, and `Event`.

**Edge:** one arrow between two boxes. `Rule --enforces--> Operation` is an edge.

**Relationship signature:** the rule that says which kind of box may point to which other kind. For example, DomainSpec currently allows a `Rule` to `enforces` an `Operation`. It does not allow an `Operation` to `enforces` a `Value Object`.

**Validator:** a checker that answers a narrow question, such as “does this edge use a legal signature?”

**Obligation:** a written promise to perform one check. “This operation must call its enforcing rule” is an obligation.

**Test case:** one executable attempt to check an obligation. It has an input, an expected result, and a reason for existing.

**Binding:** the link between an abstract obligation and the real code symbols that should satisfy it. It tells the test which operation and which rule to call.

**Evaluator:** the thing that performs a check. A table-walk validator is one evaluator. A graph query engine or a runtime test is another.

**Receipt:** a small evidence record describing what was checked, against which input, by which evaluator, and with what result. A receipt is evidence; it is not a new source of truth.

**Composability:** whether the boxes and arrows can work together in the way the relationship promises. A legal arrow is only the beginning. The target code must actually use the source code in the expected direction.

## One complete example

Start with this authored statement:

```text
MaxAmountRule --enforces--> ProcessPayment
```

Here is what the proof path means in ordinary language.

### 1. Read the source

The authored DomainSpec files say that `MaxAmountRule` is a rule and `ProcessPayment` is an operation. The relationship file says that `Rule --enforces--> Operation` is allowed.

At this point we have a claim written by a person. We have not proved that the code behaves this way.

### 2. Build the normalized graph

The compiler reads the authored files and produces a machine-friendly graph: a list of nodes and a list of edges. It also keeps a source path and digest so we can trace a generated graph item back to the file that created it.

The generated graph is a convenient working copy. We do not edit it and then pretend it was the authored source.

### 3. Check the shape

The structural validator checks simple facts:

- both nodes exist;
- each node has one declared kind;
- the edge name is active;
- the endpoint kinds match the relationship signature;
- IDs, scope, and multiplicity are valid.

If this passes, we know the arrow is legal on paper. We do **not** yet know that payment code calls the rule.

### 4. Derive an obligation

The test-derivation engine turns the graph into a checklist. For our edge it creates something like:

```text
obligation: ProcessPayment must call MaxAmountRule before accepting payment
source: the authored enforces edge
rule type: composability
```

The obligation gets a stable ID. Running the same graph through the same rule set should produce the same ID and the same checklist. If the engine cannot understand a rule, it must say `needs_formal` or `coverage_gap`; it must not invent an answer.

### 5. Bind the obligation to code

The binding says which real functions represent `ProcessPayment` and `MaxAmountRule`. The code-composability checker then looks for the expected call direction: the operation must call its enforcing rule.

This is where a graph arrow becomes a code-level claim. If the checker cannot find the symbols or the call, the result is a failure or an explicit coverage gap—not a silent pass.

### 6. Generate and run the test

The engine creates a test case from the obligation and binding. The test runs the real operation with a valid payment and an over-limit payment. It should show that the rule is consulted and that the invalid payment is rejected.

Generated tests must point back to the obligation and source edge. Expected values must come from the authored rule or formal expression, not from running the implementation first and copying its answer. If a test needs a human decision or a missing runtime fixture, it remains an honest skipped case with a reason.

### 7. Check relationships that involve many edges

Some questions cannot be answered by checking one edge at a time. For example:

- does a chain of relationships create a forbidden cycle?
- can an event reach the operation that should consume it?
- do two rules demand contradictory states?

Those are **cross-graph** questions: questions about several boxes and arrows together. They need a graph evaluator such as a bounded Datalog, Cedar, or FOL query. The evaluator must return a query ID, an input scope, a witness or counterexample, and a bounded claim. The current cycle example in the research findings is only a design example; the repository does not yet have this runnable evaluator.

### 8. Write the receipt

The final receipt should say:

```text
graph digest: which graph was checked
obligation: which promise was checked
binding: which code symbols were used
evaluator: which checker or test ran
result: pass, fail, counterexample, or coverage_gap
witness: the useful detail that supports the result
claim limit: what this result does not prove
```

That last line matters. A passing table check proves shape. A passing runtime test proves an observed behavior for its fixture. A bounded graph query proves only the property within its stated scope. None of these automatically proves every possible future graph.

## What is already real

The current repository has a working structural foundation:

- a relationship validator has passed a six-edge fixture against 30 current signatures;
- the key-and-door compiler fixture produces a deterministic graph with four nodes and three edges;
- the test engine derives stable, content-addressed obligations;
- generated test output distinguishes real assertions from honest coverage gaps;
- typed-negative fixtures reject malformed endpoints, generated inverse edges, and wrong relationship directions.

These are meaningful survivors. They prove that the map can be parsed, checked, and turned into a deterministic checklist.

## What is still missing

The complete composability proof is not finished. We still need:

1. one end-to-end fixture that goes from edge to obligation to bound test to executed result to typed receipt;
2. code-realization coverage for every relationship included in the claim, not only the small subset the current checker understands;
3. a runnable cross-graph evaluator for cycles, reachability, or another explicitly chosen graph law;
4. a coverage matrix showing which relationships are structurally checked, code-realized, runtime-tested, and globally evaluated;
5. a decision about the open `Saga` versus `Workflow` orchestration mismatch;
6. clear treatment of bounded Alloy/TLA results as evidence, never as unbounded proof.

## The practical starting point

Do not begin with every relationship in the repository. Pick one profile and one small relationship family. Use the `enforces` example above. Make the whole path work once:

```text
source edge
→ valid graph
→ derived obligation
→ code binding
→ generated test
→ executed result
→ receipt
```

Then add one typed-negative case, such as reversing the edge or using the wrong endpoint kind. Once that small path is replayable and its evidence is clear, expand the same pattern to the next relationship.

That is the difference between “the graph looks valid” and “we have evidence that this part of the graph composes.”

## Sources and boundary

This guide is a plain-language explanation of [the accepted research findings](../findings.md). It is a candidate teaching artifact, not a new DomainSpec definition, engine contract, relationship authority, or Inventory authority.
