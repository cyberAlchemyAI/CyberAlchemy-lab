# Distilled Knowledge

Status: pass

## Smallest Coherent Concept

DomainSpec should treat Alloy and TLA+ as two different formal lenses over the same extracted saga fixture:

```text
DomainSpec artifacts
  -> TypeScript SagaSpec extractor and bounded witness
  -> fork by hard class
     -> Alloy: bounded graph-completeness counterexample search
     -> TLA+/PlusCal: temporal execution model checking
  -> DCB: freshness guard around accepting model evidence, waivers, and receipts
```

## Why This Is The Right Split

Alloy is relational first. It is strongest when the question is about the existence or absence of a structure in a bounded world: missing participant, missing compensation link, invalid typed edge, or graph shape that should be impossible.

TLA+ is behavior first. It is strongest when the question is about all possible execution traces in a finite model: success cannot be accepted after a failed shipment, compensation eventually follows a failed later step, a retry policy reaches a terminal state, or a stale waiver forces claim rejection.

TypeScript is proximity first. It is strongest when the repo needs a quick fixture, bounded witness, and extraction shape that can later feed both formal lanes.

DCB is acceptance first. It is strongest when the question is whether a model verdict, receipt, waiver, or correctness claim is still fresh enough to accept.

## Minimal Workflow

1. Build or update `SagaSpec` in TypeScript.
2. Classify the hard class:
   - graph completeness -> Alloy;
   - temporal behavior -> TLA+/PlusCal;
   - deterministic local sanity -> stay in TypeScript;
   - non-rerunnable proof acceptance -> DCB freshness.
3. Generate a tool-specific fixture.
4. Run the tool and capture the exact command, version, scope/model config, and result.
5. Accept or reject the result through `AcceptSagaProofFreshnessClaim` only when freshness matters.

## Operator Reminder

The phrase "formal proof" is too wide here. Prefer:

- "bounded TypeScript witness"
- "bounded Alloy counterexample check"
- "TLC finite-model check"
- "TLAPS proof" only if TLAPS is actually used
- "DCB freshness acceptance" for read-set guarded acceptance
