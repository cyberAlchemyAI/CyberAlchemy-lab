<!-- MINT-ACT OUTPUT (L1) for domainspec-v2. Cast from templates/promotion-policy.md. INTERNAL/private.
     INHERITS the ladder + required-gates + promotion-blocks FORMAT. LOCALIZES rungs/gates/blocks.
     Obs-B: every gate resolves to THIS repo's authority/; ≥1 gate per governance is domain-originated. -->

# Promotion Policy

Status: active local policy
Owner: DomainSpec v2 owner

DomainSpec v2 promotes by evidence and owner route, not by elegance.

## Promotion Ladder

| State | Meaning | May promote to |
| --- | --- | --- |
| Source evidence | Spec/source material in its own context. | Source record. |
| Source record | Path, date, source kind, boundary captured. | Source claim ledger. |
| Source claim | A claim with evidence and local reading separated. | v2 synthesis. |
| v2 synthesis | Bounded reading with source-kind labels. | Candidate obligation, workflow witness, or open residue. |
| Candidate obligation | A proposed obligation / layer-rule / convergence-criterion v2 should preserve. | Validation request after collapse test and witness. |
| Workflow witness | A concrete feature/scenario for testing behavior. | Evidence harness or external review. |
| v2 recommendation | A source-backed proposal with risks and gates. | External owner decision (impl conforms / promote into the contract). |

## Required Gates

| Gate | Required when | Standard |
| --- | --- | --- |
| Source-kind gate | A new source is added or cited. | primary / supporting / related / analogy / inference / residue is explicit. |
| Authority gate | A claim could affect the implementation contract or policy. | Route to **this repo's `authority/`**; mark non-policy until external owner review. *(Resolves locally — never to a framework.)* |
| **Derivation gate** ⟵ *domain-originated (validation-governance)* | A typed spec node's obligations are claimed satisfied. | The engine `lint`/`derive` is CLEAN (canonical tables + every Formal cell deterministically classifiable); a `needs-formal`/`coverage_gap` blocks. Expected values read from the spec, never from running the impl. |
| **Layer-law gate** ⟵ *domain-originated (layering-governance)* | A concept is placed or a typed dependency is added. | The dependency is admissible under the layer-law + Edge-Law (a forbidden edge is unconstructible); a cross-adapter-line dependency blocks. |
| **Convergence gate** ⟵ *domain-originated (drift-governance)* | A claim asserts convergence or "drift resolved". | Backed by evidence across the relevant drift surface(s) as a trend — never a single signal; no modeling surface writes promotion-status. |

## Promotion Blocks

Block promotion when:

- a passing derived test is treated as runtime conformance or as correctness;
- a layer assignment is treated as a dependency-law verdict, or a forbidden edge is admitted;
- convergence is declared from a single drift signal, or a modeling op would write promotion-status;
- an expected value is taken from running the implementation rather than from the spec;
- the claim depends on an analogy without a bridge decision, or skips the required precedent corpus;
- the recommendation has no witness, falsifier, or audit route;
- **the promotion would resolve by traversing into a framework attachment** (no framework edge is a
  promotion path — Obs-B at the promotion level).
