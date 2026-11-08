## CAV2-D47: Interface Evidence Boundary

Status: active
Term: interface evidence boundary
Aliases: UX evidence boundary, browser-evidence boundary, UX/UI claim class boundary

### Normative Definition

Interface evidence boundary is the CyberAlchemy v2 rule that UX/UI claims must
state which kind of evidence can support them and what that evidence cannot
prove.

At minimum, UX/UI claims must be classified as one of:

- hard gate
- soft flag
- screenshot review
- human study
- not automatable

Browser automation may directly support page-load, accessibility-tree,
keyboard, layout, interaction, screenshot, trace, console/network, and DOM
measurement claims. It may prepare evidence for cognitive, attention,
perception, trust, comprehension, delight, and real-user success claims, but it
must not turn them into deterministic authority without calibrated fixtures and
owner approval.

### Formal Interpretation

For UX/UI claim `c`, let:

```text
IEB(c) = (claim_class, evidence_kind, proxy_limit, owner_route, residue)
```

The claim is valid only when `claim_class` matches `evidence_kind` and the
`proxy_limit` states what remains unproven. If the evidence class is weaker than
the claim, `CAV2-D38` requires downgrading, routing, or blocking the claim.

### Operational Interpretation

Use interface evidence boundary when writing validator specs, Playwright
reports, UI review findings, UX pattern cards, screenshot reviews, or studio
mutation handoffs. Ask whether the claim is deterministic, a risk proxy, a
visual review prompt, a human-study need, or not automatable.

### Plain-Language Intuition

A browser can show what happened on the page. It cannot by itself prove what a
human understood, trusted, felt, or preferred.

### Domain-Context Voice

In CyberAlchemy v2, this definition imports the evidence honesty model from
`ux-evidence-validator`: hard gates, soft flags, screenshot review, human
study, and not-automatable residue. It keeps UI validation useful without
collapsing browser evidence, accessibility, UX heuristics, and user research
into one false certainty.

### Boundary

Interface evidence boundary is not a validator implementation, not a complete
accessibility audit, not user research, not a universal UX score, and not a
license to block dense expert interfaces without false-positive calibration.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
- [../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md](../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md)
- [../../../arcanum/arcana/ux-evidence-validator/development/UX-EVIDENCE-CLAIM-MAP.md](../../../arcanum/arcana/ux-evidence-validator/development/UX-EVIDENCE-CLAIM-MAP.md)
- [../../../arcanum/arcana/ux-evidence-validator/development/UX-PLAYWRIGHT-VALIDATOR-SPEC.md](../../../arcanum/arcana/ux-evidence-validator/development/UX-PLAYWRIGHT-VALIDATOR-SPEC.md)
