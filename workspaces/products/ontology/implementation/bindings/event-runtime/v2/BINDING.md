# Ontology Product event-runtime binding v2

Status: test candidate  
Authority effect: none

This binding is the executable bridge from the admitted cohesive ontology root
to the existing D65 Rust lifecycle engine.

```text
exact cohesive navigation
  -> package translator
  -> canonical node events ---------+
  -> canonical relation events -----+-> EventStore replay
  -> exact governance joins --------+      |
  -> integration epoch --------------------+
                                             |
                         +-------------------+------------------+
                         |                   |                  |
                  latest snapshots    ontology cut      Context projection
                         +-------------------+------------------+
                                             |
                                  realization observation
```

The initial cut has 14 node subjects and 15 relation subjects. Each subject
gets one semantic event and one governance event, producing 29 latest subject
snapshots. A later event on a subject replaces only that subject's calculated
latest state. Snapshots and projections are rebuildable outputs; only the
event histories are runtime replay sources.

Root admission is preserved exactly. It is not copied to child ontologies, and
the implementation has `authority_effect: none`. The existing Rust runtime is
used as a replaceable test target and is not adopted or activated by this
binding.

The machine-readable contract is `binding.json`. Product candidate 0006 binds
its exact digest and supplies the current product-test evidence.
