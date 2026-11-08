# AlchLang DomainSpec 1.0.0 lowering candidate

Status: implemented and locally tested product candidate. No product approval,
ontology admission, release, deployment or external authority is recorded here.

## Product construction

Current frontier: both design tracks have implementation prototypes and current
local product-test evidence. The next construction step is review of this exact
candidate against the product and business ontology scaffolds.

- Compiler self-model: `self-model/project/` compiles with 53 nodes and 45
  relationships. Four generic backend descriptions are contract-document Entities.
  `self-model/migration.json` accounts for all 50 predecessor nodes and 42 edges.
  Historical source, accepted artifacts and receipts were not edited.
- Application lowering: an explicit source-bound sidecar supplies ontology meaning,
  identity, invariants and ownership. The compiler emits real DomainSpec project
  files, invokes the public 1.0.0 compiler and optionally builds TypeScript.
- The example application emits 13 nodes. Its mappings preserve field renaming,
  missing-field behavior, defaults and totality. Policies preserve ordered first
  match and fallback and return a selected identifier without invoking the target.
- Source and binding snapshots, compiler file inventory, declaration traces,
  certificates and artifact hashes make the output inspectable and replayable.
  Output directories are exclusively created; the manifest is the final completion
  marker. This is not an atomic directory swap.

## Validation

AlchLang package `npm run typecheck`, `npm run build` and `npm test` passed;
84 tests passed, zero failed. `evidence/tests.log` records the full package run.
Tests include byte-identical builds, invalid inputs, no overwrite, CLI rejection,
self-model migration accounting, and strict compilation and execution of generated
TypeScript compared with the existing AlchLang evaluator. Mapping, policy, rule
and constant parity are exercised, including first-match overlap and fallback.

The built CLI was separately used for version checking, profile checking,
TypeScript building and successor self-model compilation. Results and certificates
are in `evidence/`. `evidence/candidate.json` pins the implementation, self-model,
definition/design antecedents and test evidence. Its scope is explicit, not a claim
that the whole repository is clean or tested.

An incidental workspace-wide typecheck failed in unrelated poker-team validation
code because `@opentelemetry/api` was unavailable (with an associated implicit-any
error). It did not reach the chained workspace build. This does not change the
passing scoped AlchLang package result.

## Profile and claim limits

The first profile supports String/Bool records and identifier fields, bounded
Boolean rules, input-free UInt64 constants representable exactly by JavaScript
Number, concrete mappings and policies selecting those constants. Other constructs
and numeric semantics reject explicitly; this is not full thirteen-kind lowering.

Each constant has a traced derived evaluation Operation because DomainSpec requires
an outgoing calculates relationship. These support nodes establish graph structure;
their generic generated operation bodies are not application runtime conformance
claims. The checked `domain.ts` entry exposes mappings and policy selection. Record
invariant references are structural bindings, not automatic runtime enforcement.

Prototype ontology selectors remain navigation scaffolds. Source hashes prove
which definitions were used, not who approved them or whether their ontology was
admitted. Compiler success and test parity do not manufacture product approval.

## Operational support

Owner: repository maintainer. Rebuild or install the exact DomainSpec 1.0.0 CLI
when changing environments; this supports the compiler-binding stage. The local
binding used for these tests is available, so there is no current causal blocker
to candidate review. Packaging/publication and broader runtime realization remain
deferred operational residue, with no release or deployment action performed.

Usage and example sidecar are documented in `../../implementation/README.md`.
