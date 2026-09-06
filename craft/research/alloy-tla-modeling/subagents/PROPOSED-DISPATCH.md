# Proposed `/domainspec-subagents-strategy` Dispatch

Status: proposed-not-registered
Schema target: v0.6.0
Dispatch type: research
Working folder: `projects/domainspec-v2/research/alloy-tla-modeling/subagents/`
Final approver: parent
Max loops: 1

## Gate Note

This sheet is intentionally not appended to `telemetry/agents/subagents-dispatch.yaml` and no agents were spawned. The router requires a proposed sheet, tension gate, and explicit human confirmation before registration and run.

## P1 Trigger

Dispatch is justified if the user wants actual fan-out because:

- synthesis: Alloy, TLA+, TypeScript, DCB, and DomainSpec relationship governance must be joined;
- context protection: raw tool/language research can exceed what the parent needs;
- parallelism: graph, temporal, and alternatives lanes are independent until synthesis;
- isolation: each lane can explore a discardable model sketch without mutating canonical definitions.

## Goal

Determine the first usable Alloy and TLA+/PlusCal modeling lanes for DomainSpec v2 saga correctness work, with honest proof labels and an integration path from the existing TypeScript bounded witness.

## Context

The existing DCB saga correctness research found that TypeScript should be the first bounded witness, TLA+/PlusCal should be the formal promotion path when temporal behavior is hard, and Alloy should be the alternate formal path when graph completeness is hard. This tower needs a research dispatch shape that can deepen those lanes without rewriting DomainSpec taxonomy or relationships.

## Groups

### Group 1: Explorers

Anti-bias: methodology and source-corpus spread. The three explorers use different source corpora and ask different questions.

| Agent | Role | Angle | Initial prompt |
| --- | --- | --- | --- |
| `alloy-graph-explorer` | explorer | formal relational graph lane | Read the Alloy primary sources and local DomainSpec relationship files. Propose a bounded Alloy model shape for participants, operations, compensations, policies, interfaces, mappings, and typed edges. Name exactly what Alloy can and cannot prove for DomainSpec graph completeness. |
| `tla-temporal-explorer` | explorer | temporal behavior lane | Read the TLA+ primary sources and local saga proof obligations. Propose a minimal TLA+/PlusCal state model for success safety, failure safety, compensation ordering, retry/dead-letter, and freshness acceptance. Name exactly what TLC can and cannot prove. |
| `typescript-bridge-explorer` | explorer | local extraction lane | Read the existing TypeScript toy harness and result. Propose the JSON fixture contract that can feed both Alloy and TLA+ without overclaiming proof or mutating canonical definitions. |

### Group 2: Skeptics

Anti-bias: attack-vector spread.

| Agent | Role | Gate | Initial prompt |
| --- | --- | --- | --- |
| `overclaim-skeptic` | skeptic | definitional-soundness | Attack any claim that says Alloy, TLA, TypeScript, or DCB proves more than its evidence supports. Return wording fixes and blocked phrases. |
| `cost-skeptic` | skeptic | non-vacuity | Build the smallest concrete next task that would make each lane real. Kill any lane whose first witness is too large or not runnable in this repo. |

### Group 3: Writer

| Agent | Role | Initial prompt |
| --- | --- | --- |
| `formal-lane-writer` | writer | Synthesize the explorers and skeptics into `domainspec-subagents-findings.md`, with a verdict matrix for Alloy graph model, TLA+/PlusCal temporal model, TypeScript extractor, DCB freshness, and Lean deferral. Every load-bearing claim must cite `domainspec-subagents-research.md`. |

## Connections

| From | To | Type | Purpose |
| --- | --- | --- | --- |
| explorers | skeptics | sequential | Skeptics attack proposed lane claims after explorer returns. |
| skeptics | writer | sequential | Writer integrates surviving claims and blocked overclaims. |

## Expected Outputs If Run

- `subagents/domainspec-subagents-research.md`: verbatim per-agent returns.
- `subagents/domainspec-subagents-findings.md`: cited synthesis and verdict matrix.
- Updated `SUBAGENT-CLOSEOUT.md`: actual agents spawned, exit reason, and integration status.

## Proposed Exit Reason

`resolved` if the writer and parent accept the lane split and all overclaim/cost residues have owners.
