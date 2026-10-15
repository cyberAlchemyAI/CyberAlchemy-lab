# TASK T3 — Business Ontology Dependency

Layer: L3. Status: testable candidate complete. Authority effect: none.

## Objective

Prove dependency-aware authoring by requiring an exact Product Ontology handoff
for one Business Ontology adapter while keeping independent branches available.

## Inputs And Outputs

Inputs are the accepted Product handoff protocol, Business sources and rules,
and a static Product-to-Business edge. Outputs are the Business adapter and Alch
entries, a deterministic dependency closure, candidate Business Ontology, and
no-effect receipt.

## Smallest Working Unit

Product then Business succeeds; missing, stale, substituted, or wrong-product
evidence blocks only Business.

## Ordered Rules

Resolve the selected Business entry; compute prerequisite closure; verify exact
Product candidate and receipt identities; ask Business-owned questions;
materialize, validate, confirm, and export through the common protocol; retain
the dependency receipt-set digest.

## Edge Cases And Failure Modes

Missing, stale, or substituted Product receipt; graph cycle; unrelated branch
unavailable; Business deferral; semantic conflict with prerequisite evidence;
and input-order variation.

## Verification And Completion

Dependency and localization matrices pass twice; graph order and receipts are
deterministic; an unavailable Business adapter does not alter Product output;
earlier layer guarantees remain green.

## Implementation Evidence

- The selected source is
  `language/capabilities/alchlang/define/alch-product-business-ontology-v1/business-ontology.json`.
- `BusinessOntologyQuestion` and `BusinessOntologyReadiness` compile from the
  Business `.alch` service into 61 manifest-bound files.
- The common stage port requires each prerequisite receipt to match the current
  graph digest, module-set digest, and registered prerequisite manifest.
- The Business candidate retains the exact Product candidate digest, Product
  handoff receipt digest, and dependency receipt-set digest.
- Product then Business succeeds; missing, tampered, stale, and wrong-provider
  Product evidence blocks Business while Product remains available.
- Reversed adapter and descriptor input order produces the same graph, module
  set, Business candidate bytes, and Business handoff receipt.
- Focused L3 tests passed twice at 3/3; the full Define suite passed 66/66; all
  four Alch verifier paths rebuilt byte-identically.

This evidence is local product-construction evidence only. It does not admit,
activate, publish, release, or deploy either ontology or adapter.

Open questions and blockers are owned by [the work pack](../WORK-PACK.md#blockers).
