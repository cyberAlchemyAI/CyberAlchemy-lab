<!-- MINT-BASELINE BACKFILL (2026-07-01) for domainspec-v2 — cast from templates/definition-localization-route.md
     (Tier-2 addition #9, SWU-9), which post-dates v2's 2026-06-29 first mint. INTERNAL/private.
     Inherited whole (meta route); localizes nothing structural — the domain applies it to its own terms. -->

# DomainSpec v2 Definition Localization Route

Status: active local route
Owner: definitions-governance (domain-local)
Staging: [reviews/](./reviews/) (pre-canonical review area)

## The route (inherited)
```text
harvested / cited term (posture: imported)
  -> represented locally (posture: represented — a local card citing the source as provenance)
  -> reviewed in definitions/reviews/ (pre-canonical)
  -> owner canonicalizes (posture: canonical — indexed in DEFINITIONS-INDEX, tracked by DRIFT-AUDIT)
```
No arrow is automatic. A term can stay `represented` indefinitely; only the owner promotes to `canonical`.

## Local-posture vocabulary (inherited)
- `imported` — cited from a source; **not** local authority (provenance only).
- `represented` — a local card exists that cites the source; the meaning is being localized.
- `canonical` — owner-canonicalized; indexed; the only posture that counts as domain definition authority.

## Reviews staging
`reviews/<term>.md` holds a term while it is pre-canonical. A `represented` term used as authority before
canonicalization is a drift defect ([DRIFT-AUDIT](./DEFINITION-DRIFT-AUDIT.md) flags it).

## Worked example (v2)
`domainspec-v2-D3` (Edge-Law Admissibility) is a completed run of this route: cav2 `CAV2-D22/D29/D16` entered
as **imported** provenance (cited in the card's Evidence), the local card localized the meaning
(**represented**), and the owner canonicalized it as a build-from-owned card (**canonical** — indexed, no
cav2 authority transferred). The harvested cav2 IDs stay provenance, never the resolution path (Obs-B).

<!-- Meta route (inherited whole): the domain applies it to its own terms; cav2 terms enter only as
     `imported` provenance, never `canonical`. -->
