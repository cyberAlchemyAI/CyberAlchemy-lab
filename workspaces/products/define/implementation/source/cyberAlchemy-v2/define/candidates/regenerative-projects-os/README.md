# Regenerative Projects OS Define adapter

Status: private candidate; no authority effect.

This is a CyberAlchemy Define consumer adapter for the project-owned RPOS
definitions package at `../../../fit-farms/definitions/`. It intentionally does
not copy or redefine the domain definitions. Fit Farms owns the semantic source;
this candidate records how Define consumes the exact package bytes.

Fit Farms now vendors its selected Lab semantic foundation locally, so this
adapter depends only on the RPOS package and its bound vendor manifest—not on a
live CyberAlchemy Lab checkout. The adapter checks the three formalization
postures and semantic-test presence while leaving their meanings project-owned.

The package uses the current Define concepts—goal, intent, context, consumer,
source references, one disposition per concept, open questions, and claim
ceilings—without inheriting the blocked `cav2.define` parent package or either
of its incompatible Definition Pack runtime schema identities.

## Architecture boundary

```text
Fit Farms definitions
  -> Fit Farms validator
  -> this Define adapter
  -> Fit Farms Lab-v4 ontology manifest
  -> universal Node/Relation events and derived Context views
```

This adapter cannot promote RPOS meaning, write ontology state, qualify ARE,
or authorize implementation and external action.

## Validate

From the CyberAlchemy v2 repository root:

```bash
python3 define/candidates/regenerative-projects-os/validate.py
```

Set `RPOS_PROJECT_ROOT` only when Fit Farms is not a sibling of this repository.

## Improvement handoff

The RPOS consumer exposed reusable Define gaps around per-concept subject,
goal, use cases, structured open questions, receipt integrity, distinction
checks, semantic dependency closure, formalization posture, and portable
foundation snapshots. See `SEMANTIC-IMPROVEMENT-HANDOFF.md` and its
machine-readable JSON.
This is a semantic candidate, not a construction handoff.
