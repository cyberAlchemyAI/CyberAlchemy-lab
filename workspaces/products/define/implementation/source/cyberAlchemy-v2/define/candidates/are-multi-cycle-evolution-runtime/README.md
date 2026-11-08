# ARE multi-cycle evolution runtime candidate

Status: candidate. Authority effect: none.

This package defines the proposed ARE runtime boundary for coordinating several
different evolution cycles through JSON while the runtime owns state, evidence,
generated data, accounting, receipts, recovery, and navigation.

Start with:

1. [Definition Pack](ARE-MULTI-CYCLE-EVOLUTION-RUNTIME-DEFINITION-PACK.v1-candidate.json)
   for the complete candidate vocabulary, relationships, sources, owners,
   boundaries, and open questions.
2. [Architecture](ARCHITECTURE.md) for the shared-kernel and versioned-cycle
   structure, managed evidence store, JSON interaction boundary, cycle taxonomy,
   reconstruction model, and architectural acceptance conditions.

The proposal extends the existing ARE evolution runtime conceptually. It does
not create a second runtime and does not authorize implementation. Benchmark
research is one cycle type alongside research learning, engine improvement,
interaction learning, and controlled upgrade.

## Open Questions

The cross-cycle architecture gates are closed. A per-cycle definition audit is
now active before implementation planning. For `benchmark-research/v1`, BR-01
is resolved: one immutable improvement objective guides and identifies the
lifecycle, while candidate hypotheses and bounded attempts remain subordinate
to it. BR-02 is also resolved: primary metrics decide success under a frozen
logical rule, guardrails may block success, and diagnostics cannot change the
decision. BR-03 and BR-05 establish one iterative portfolio of independently
attributable hypotheses within the objective cycle; hypotheses may yield many
candidates, experiments, and attempts but never become child cycles. BR-04
replaces E0-E10 runtime identifiers with semantic operations and events; the
numeric labels remain historical aliases only. BR-06, concerning deterministic
cycle stopping conditions, is resolved with objective-driven bounded
continuation. BR-07 resolves hypothesis admission through agent proposal and
runtime validation. BR-08 resolves work selection by reusing the inspected
research ontology, Research DAG, Research Work Plan replay, and scheduler:
dependencies and readiness are derived, the agent chooses among ready work, and
automatic dispatch remains disabled. BR-09, concerning comparison-reference
modes and fresh controls, is resolved by an immutable per-objective selection.
BR-10 resolves experiment freeze, successor, retry, and attempt identity. BR-11,
resolves typed evidence-bound hypothesis outcomes. BR-12 resolves launch
authorization through a user-approved bounded cycle envelope and a separate
runtime admission for every frozen experiment. BR-13 keeps deterministic
validation as the normal path and has the runtime send flagged output and its
evidence bundle to a distinct evaluation agent. That agent returns a review
receipt but cannot write state or grant authority. The currently identified
benchmark-research gates are therefore closed. RL-01 establishes one immutable
research question, intended learning outcome, and declared use as the identity
of a research-learning cycle, with multiple hypotheses beneath it. RL-02 adds
typed question dispositions derived from the complete verified evidence
portfolio; a supported hypothesis or technique candidate cannot automatically
complete the cycle. RL-03 freezes evidence sufficiency, counterevidence,
confidence, applicability, resources, and stopping rules before admission.
RL-04 admits typed multimodal evidence with provenance, quality, independence,
limitations, and claim ceilings; experiments are question-specific rather than
universal. RL-05 defines an immutable, non-authorizing Research Finding Bundle
that a receiving cycle must explicitly accept. RL-06 closes the currently
identified research-learning gates with DAG-derived readiness, agent task
selection, and runtime launch admission inside a bounded envelope. EI-01
establishes one immutable measurable objective as engine-improvement cycle
identity, with multiple techniques and variants beneath it. EI-02, concerning
terminal decisions and activation separation, establishes a recommend-only
output. EI-03 establishes content-addressed isolated workspaces, strict mutation
boundaries, one writer, and successor identity for changed bytes. EI-04,
establishes a frozen staged comparison and selection contract with independent
confirmation. EI-05 establishes exact retention with recomputed currentness and
stale frontier re-entry. EI-06 closes the currently identified
engine-improvement gates with one user-approved envelope and distinct runtime
admissions for construction and comparison. IL-01 establishes one immutable
scoped learning objective as interaction-learning cycle identity. IL-02,
admits attributed, minimized, policy-eligible corrections, approvals, observable
outcomes, deterministic checks, and scoped application outcomes while excluding
hidden reasoning, secrets, unauthorized private content, unverified inference,
and model self-assessment. IL-03 derives lessons only from sufficient admitted
evidence and applies them only after deterministic scope and policy matching;
current user instructions take precedence and expiry or revocation blocks new
applications. IL-04 adds typed application outcomes, portfolio-derived lesson
standing, predefined recurrence or replication, and evidence-bound terminal
dispositions. IL-05 adds a user-approved bounded operating envelope and an
immutable, non-authorizing Interaction Learning Bundle, closing the currently
identified interaction-learning gates. CU-01, concerning controlled-upgrade
identity, establishes a minimal immutable binding of candidate, target, and
serving predecessor/rollback point. CU-02 establishes one user approval over
the exact binding and bounded execution policy, with deterministic retention or
rollback and no repeated phase approvals. CU-03 establishes the minimum final
readiness recheck and atomic predecessor comparison. CU-04, concerning
deterministic canary settlement, retains only on a frozen pass and otherwise
rolls back at failure or deadline. CU-05 adds journal replay, observed-state
reconciliation, and idempotent recovery. This closes the currently identified
controlled-upgrade and per-cycle definition gates. Under NX-01, the user
selected a cross-cycle consistency and implementation-readiness review before
separately routed implementation planning; all 54 existing
predecessor-runtime tests passed. CR-01, concerning the separation of aggregate
cycle state from subordinate record and executable work state, selects three
derived projections over one event authority. CR-02 selects a shared kernel
mechanism for cycle-specific envelopes and admissions, closing the cross-cycle
semantic review. NX-02 asks whether to begin a separately routed
implementation-planning phase.

The benchmark-research, research-learning, engine-improvement,
interaction-learning, and controlled-upgrade definition audits are closed.
Exact schemas, validators, archive realization, the H-EN
import manifest, and process protocols remain downstream design work. The
Definition Pack owns the current decisions and open questions.
