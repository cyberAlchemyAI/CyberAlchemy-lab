# Contextual Framings capability ontology

Status: private candidate package. Authority effect: none.

## Purpose

This package defines the candidate Agent Reasoning Engine capability for
turning source-bound knowledge into a purpose-specific framing that a person
can understand and use with less cognitive effort.

A framing is not merely a summary. It selects a perspective for one consumer,
objective, and context. It may use an analogy, but it must preserve the source
provenance, salient constraints, uncertainty, excluded detail, analogy limits,
and the condition under which the framing expires.

## Capability boundary

The candidate capability accepts a bounded framing request and source-bound
knowledge. It returns one or more framing candidates plus an explicit fit and
limitation assessment. It does not modify model weights, establish truth,
replace source material, authorize an action, or prove improved cognition or
productivity.

## D65 construction state

| Stage | State |
| --- | --- |
| Product Capability definition (`CAV2-D67`) | source-bound canonical type |
| Contextual Framing meaning | package-local candidate |
| Product Capability | candidate |
| Capability-local business ontology | candidate |
| DomainSpec authored source | not authored |
| Compiled graph and system ontology | not evaluable |
| Implementation binding | not evaluable |
| Conformance evidence | not evaluable |

The missing successor stages are recorded in `residue.jsonl`. File presence
does not advance any stage.

## Files

- `product-capability.json` owns the candidate product outcome and boundary.
- `nodes.json` and `relations.json` own the business-domain ontology.
- `sources.json` binds the exact selected inputs.
- `schemas/framings.schema.json` and `scripts/validate.py` define deterministic
  structural and source-currency validation.
- `residue.jsonl` preserves construction gaps.

## Validation

From the repository root:

```text
python3 cyberAlchemy-v2/agent-reasoning-engine/framings/scripts/validate.py
python3 cyberAlchemy-v2/agent-reasoning-engine/framings/scripts/validate.py --write-receipt
```

Check-only mode does not write. Receipt mode creates an append-only receipt for
the exact current material digest.

## Open Questions

- Which independently reviewed DomainSpec profile should own the future system
  ontology?
- What user study can measure lower cognitive effort without confusing brevity
  with comprehension?
- Which runtime component may propose framings, and which owner accepts a
  framing for consequential use?

## Claim ceiling

This package defines candidate product meaning and a capability-local business
ontology only. It does not implement the capability in a language model,
modify model weights, admit a DomainSpec profile, prove conformance, promote a
definition, authorize an effect, publish, release, or deploy anything.
