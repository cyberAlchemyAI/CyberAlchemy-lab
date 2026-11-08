# Whole-application review slice (candidate)

Goal: let a reviewer inspect one complete authored AlchLang `application-v1`
source, its exact companion inputs, the generated TypeScript application, and
repeatable behavioral evidence in one local directory.

## Dependency DAG

```text
R1 Author the composed commerce application and exact companions
  -> R2 Check, build, and verify with the public AlchLang CLI
    -> R3 Exercise the generated request handler and signed HTTP loopback
      -> R4 Reject a tampered generated artifact and verify the original again
        -> R5 Review the source, application graph, code, results, and limitations
```

## Review of the plan

- R1 uses the existing deterministic synthetic whole-application fixture with
  source-authored Realizations. It does not invent provider credentials or
  present test-only values as production decisions.
- R2 is a real `application-v1` build, not a hand-written substitute for the
  compiler output. It retains the source, companion manifest, selected inputs,
  generated code, graph, and exact output manifest.
- R3 tests business-flow outcomes separately from adapter startup: no matching
  order rolls back, one matching identity commits, and a mismatched read
  identity rolls back. The signed loopback tests the generated HTTP adapter
  boundary.
- R4 mutates only a disposable copy. The retained generated application stays
  verifiable, and repeat runs do not rewrite it.
- R5 is a human review surface, not product approval. PostgreSQL, NATS,
  outbound delivery, business completion, and production behavior remain
  unobserved.

The dependency graph is acyclic. Runtime observations cannot be inferred from
R2; the scenario must run independently at R3. The historical P03/L4X
candidate remains a separate frozen handoff and is not refreshed by this slice.

## Acceptance evidence

`review/whole-application-v1/` must contain authored inputs, `generated/`, a
review guide, and a self-contained local test command. `check`, `build`, and
`verify` must pass. The generated handler and loopback outcomes must match
their explicit oracles. Tampering must fail verification; the original must
still verify. No release, deployment, authority, or product-approval claim is
made.

## Open Questions

- A later product-owner review may decide whether this synthetic application
  is sufficient for product acceptance or whether a different domain is needed.
- Live-provider and production evidence require separately scoped work.
