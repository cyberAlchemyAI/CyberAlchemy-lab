# Open Ontologies: repository map and useful ideas

Open Ontologies is a Rust tool for working out what a knowledge graph means,
what a proposed change would affect, and which results another program can
check. It also includes data-import tools, assistant interfaces, and a desktop
application.

For CyberAlchemy, its strongest value is as a source of **better checks around
ontology changes and agent views**. Our recorded history, exact versions, and
owner decisions should continue to provide the foundation. An isolated export
of a Lab view could become input to its reasoning tools.

## Start here

- [Repository map](REPOSITORY-MAP.md): parts, flows, all top-level areas, and
  the limits of the current implementation.
- [What we can use](REUSE-ASSESSMENT.md): ranked opportunities, what already
  overlaps with the Lab, and a small proposed first experiment.
- [What our proof work already covers](LAB-PROOF-COMPARISON.md): the focused
  comparison with the implemented definition and relation checkers.
- [Every Rust module](MODULE-MAP.md): all 107 source files, grouped by purpose.
- [Architecture index](ARCHITECTURE.md): focused reading paths and reusable
  concept and relationship cards.
- [Verification record](VALIDATION.md): what was inspected or run in this review.

## Most useful ideas

1. Check whether an agent's smaller view still supports the claims its task
   needs. Losing a few triples can matter more than retaining most of a graph.
2. Preview changes in consequences, as well as added or removed concepts.
3. Let a search engine propose a result, then check its evidence separately.
4. Give each reasoning run one fixed input and explicit version/time scope.
5. Keep generated schema suggestions as hypotheses with their observed evidence.
6. Make CI distinguish checks that ran from checks skipped for missing tools.

These are proposed transfers, not implemented Lab integrations. Their source
evidence and limits are in the [reuse assessment](REUSE-ASSESSMENT.md).

## Important limits

Its HTTP sessions share one live graph. Stable reads do not mean independent
agent branches. Its plan/apply path does not bind a plan to the exact reviewed
base graph; risk reports are partly advisory and a full apply is not one
atomic operation. Some checks have narrow logical coverage. We should not copy
those assumptions into Lab authority or history handling.

See [stable graph reads](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/graph.rs#L1245), [stored plan fields](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan.rs#L670), [plan application](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan.rs#L571), and [batched graph writes](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/plan.rs#L647).

## Review scope

Reviewed on **2026-11-02**, at commit **`c7fd75f9491253c56e4d4f408ceac179de343e48`**.
The temporary clone is `/tmp/cal-open-ontologies.ANeAQC/repo`.

The structural inventory covers **2,924 tracked paths**, **107 Rust source
files** and **244 top-level Rust integration-test files**. Three mapping agents
traced runtime/storage, reasoning/evidence, and interfaces/data; their findings
were checked and synthesized here. This is a full structural map with selected
deep source traces, not a line-by-line audit or a claim that every feature works.

The review ran three existing browser-install tests successfully and read Cargo
metadata offline. It did not build the engine, run the complete suite, rebuild
formal proofs, launch services, or change Lab runtime behavior.

The engine is published under the [MIT license](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/LICENSE#L1). Imported data can have separate terms;
[example dataset licensing](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/case-studies/skills-england-esco-crosswalk/README.md#L1) is one example. No upstream implementation was copied into
the Lab by this review.
