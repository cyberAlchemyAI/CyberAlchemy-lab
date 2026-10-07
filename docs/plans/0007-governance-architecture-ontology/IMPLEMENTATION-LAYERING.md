# Governance architecture ontology: implementation layers

Status: proposed, 2026-10-06. Scope: Lab governance navigation and traceability. Authority effect: none.

The repository is partially implemented: admitted source contracts and instances exist; the governance module and graph technology are candidate/read-only surfaces. The primary operator needs a current explanation of Authority, Provenance, Lifecycle, and their implementation bindings.

| Layer | After this layer, we know whether… | Minimum useful result | Main cost | Exit evidence and decision |
| --- | --- | --- | --- | --- |
| **L0: real Lifecycle proof** | …one lens can traverse exact admitted subjects, histories, and implementation evidence without collapsing their status? | R0-C2, S1-S2, L0: one D71-D73 Lifecycle graph and read-only query. | Exact-state resolution, source bindings, local/global edge discipline. | Explain current Project State and its two predecessors with exact decisions and events; show missing writer and no runtime activation. Continue only if the answer is reproducible and bounded. |
| **L1: three-view understanding** | …Authority and Provenance can share the graph spine and explain one subject with Lifecycle? | A1, P1, B1, Q1: three lens roots, evidence-backed bridges, common query. | Branch evidence review and nuanced claim ceilings. | Three C1 queries return source-linked paths; bridge gaps are visible; no source-derived permission or fulfillment claim. |
| **L2: sustained currentness** | …the graph stays trustworthy as repository sources change? | F1, M1: digest checks, coverage obligations, stale reporting, deterministic refresh. | Source scanning and invalidation rules. | Identical inputs reproduce one snapshot; changed sources invalidate affected paths; coverage distinguishes files, subjects, and code symbols. |
| **L3: governed reuse** | …the exact ontology profile and graph instance are fit for governed use? | G1: separate reviews of profile, instances, any missing contracts, and evidence. Optional X1 stays outside this layer. | Owner review and admission packaging. | Explicit decisions with bounded effects; validation and runtime claims remain separate. |

Each later layer preserves exact identities, the candidate/source boundary, local/global relation separation, replay-source separation, and the explicit unknown/gap posture established in L0.

The first work item is R0. Scale work, a graph database, a daemon, automatic writes, general access-control enforcement, and ontology runtime adoption are deferred until the smaller read-only graph proves its value and a separate decision justifies them.
