# Candidate migration definitions

These are local prototype terms; no canonical ontology admission is claimed.

| Term | Agent-facing definition | Plain meaning | Test obligation |
|---|---|---|---|
| Additive state migration | A source-contract-bound structural extension whose new scalar is computed by a DomainSpec Mapping | Add one field to every selected stored record | Existing values, keys and versions unchanged; default present |
| Storage generation | A fresh function-owned provisioned root selected with the revision in one registry transaction | Keep the old database while preparing its successor | No pre-switch writes to the old state; selected generation restored on restart |
| Migration rehearsal | Apply and validate the exact generated mapper on an online SQLite backup | Check a copy before draining | Failure leaves the old revision usable |
| Migration receipt | Source, mapper and snapshot hashes plus preservation checks | Explain exactly what was transformed | Bind evidence to bytes and avoid claiming operational approval |

Open questions: [README](README.md#open-questions).
