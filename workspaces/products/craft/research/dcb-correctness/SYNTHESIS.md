# DCB Correctness Synthesis

## Main Finding

DCB is not a replacement for DomainSpec validators. It is a freshness guard for
validator-derived correctness claims.

Validators answer:

```text
Is this snapshot structurally valid?
```

DCB-style correctness boundaries answer:

```text
Was this correctness claim accepted against the same relevant facts it read?
```

That distinction is the center of the design.

## Cross-Lane Tensions

### Tension 1: Static Validity vs Temporal Validity

Static layer:

- code-tag validators can check concept IDs, spec refs, relationship edges, and
  drift;
- registry generation can materialize current docs;
- work-pack and test audits can check coverage.

Temporal layer:

- a correctness decision may be made after a validator report was generated;
- another spec/code/evidence fact may change before promotion;
- a stale PASS can look valid if the old report is treated as current truth.

Resolution:

Keep static validators. Add DCB-style read sets only around decision acceptance.

### Tension 2: Authoring Benefit vs Authoring Weight

Benefit:

- specs get better when high-risk rules name what they depend on and what
  invalidates them.

Risk:

- every rule table could become too heavy if boundary metadata is mandatory
  everywhere.

Resolution:

Make Correctness Boundary annotations selective. Require them for cross-feature
rules, generated-code contracts, promotion gates, source-backed evidence claims,
async projections, and other stale-evidence risks.

### Tension 3: DCB Infrastructure vs DCB Discipline

Infrastructure-heavy option:

- introduce event storage, live projections, append conditions, and tag indexes.

Discipline-first option:

- use existing source refs, checksums, code tags, validator verdicts, registry
  snapshots, and evidence receipts as correctness facts;
- simulate append conditions over a small ledger.

Resolution:

Start with the discipline-first option. Only introduce event-store mechanics if
the toy proof shows repeated value.

### Tension 4: Existing Tags vs Correctness Tags

Existing DomainSpec has several tag-like surfaces:

- markdown/frontmatter tags;
- code tags;
- registry concept IDs;
- signal categories;
- test source refs.

Risk:

- a DCB layer could overload these and create another ambiguous vocabulary.

Resolution:

Define a small correctness tag vocabulary that references existing IDs rather
than replacing them.

## Recommended Pilot Boundary

First pilot should model:

```text
AcceptSpecCodeCorrectnessClaim
```

Scope:

- one feature;
- one operation or projection;
- one spec fact;
- one code or projection fact;
- one validator verdict;
- one stale mutation;
- one rejected correctness claim.

## Viability Decision

Verdict: viable as a toy and likely viable as a DomainSpec v2 discipline.

Not yet viable as:

- production event-store infrastructure;
- mandatory template-wide requirement;
- replacement for drift comparison, code-tag validation, or registry checks.

## First Implementation Hypothesis

A JSONL ledger is enough for the first proof:

```json
{"event":"SpecFactObserved","tags":["feature:knowledge-graph-visualization","concept:DefinitionPointer"],"marker":"m1"}
{"event":"ProjectionSnapshotGenerated","tags":["feature:knowledge-graph-visualization","projection:S1"],"marker":"m2"}
{"event":"CorrectnessClaimProposed","claim_id":"c1","read_marker":"m2","read_tags":["feature:knowledge-graph-visualization","concept:DefinitionPointer","projection:S1"]}
{"event":"SpecFactChanged","tags":["feature:knowledge-graph-visualization","concept:DefinitionPointer"],"marker":"m3"}
{"event":"CorrectnessClaimRejected","claim_id":"c1","reason":"matching fact changed after read_marker"}
```

If that proof is compelling, promote the pattern into a feature pack.
