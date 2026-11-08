# Quantity-price construction record

## Product construction

Current frontier: bounded local product candidate ready for review after current
module, compiler regression, and upstream repository tests. No product approval
is recorded. No construction blocker remains within the selected prototype scope.

| Stage | Artifact / result |
| --- | --- |
| Prototype definitions | `definitions.json`: snapshots, requests, tiers, exact USD, quote and subtotal |
| Agent navigation scaffolds | `product-ontology.json`, `business-ontology.json`; unregistered prototypes |
| Product prototype | Pure quote API with quoted, no-price, and ambiguous outcomes |
| Business prototype | Cheapest eligible base price; quote is not a sale commitment |
| DomainSpec prototype | `quantity-price.alch` and exact source-bound ontology sidecar |
| Compiled system | `evidence/application/bundle/project`: five nodes, two edges |
| Implementation prototype | Generated TypeScript query/calculation plus explicit USD adapter |
| Product tests | 23 module tests; 120 actual Medusa repository comparison cases; AlchLang regression suite |
| Exact candidate | `candidate.json`; check with `node verify-candidate.mjs` |
| Product approval | Not recorded; owner decision must bind the tested candidate digest |

Runnable construction work is complete for this slice. Any next scope extension
(taxes, price lists, fractional quantities, currencies, or live lookup) requires
its own contract and test cases, not an expanded interpretation of this result.

## Operational support

| Task | Owner | Affected stage | State |
| --- | --- | --- | --- |
| Install pinned oracle dependencies | This task | Product tests only | Done locally; lockfile retained, node_modules ignored |
| Temporary PostgreSQL setup and cleanup | Oracle harness | Product tests only | Done; own container removed |
| Live-shop credential and snapshot integration | Future integration owner | No current stage | Deferred; no live system touched |
| Publication / deployment | Repository and product owners | No current stage | Deferred; separate explicit scope required |

No operational-support residue blocks the runnable prototype. The oracle owns
only its uniquely named temporary container and explicitly selected output.
The downloaded image and installed local dependencies remain available for reruns.

## Open questions

[README.md](README.md#open-questions) owns the remaining product questions.
Previous exact-UInt64 candidates and the old-profile blocked commerce trial remain
historical evidence; this module does not rewrite their records or claim approval.
