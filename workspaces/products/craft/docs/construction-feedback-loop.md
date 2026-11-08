# Craft's Construction Feedback Loop

Status: candidate explanatory companion
Visibility: private
Meaning owner: Craft Product owner
Authority effect: none
Thesis: [Craft Product Thesis](../product/PRODUCT-THESIS.md)

## Product Promise

Craft is the current name of the DomainSpec v2 Product lineage. Its promise is
to carry typed Product intent and domain meaning into a working system, compare
independent evidence with expected behavior, and make the next construction or
evolution choice without losing meaning, recovery obligations, or owner control.

The Craft Product owns that proposition. The Craft Project coordinates its
development; the Craft Method owns the repeatable building discipline. This
explanation keeps those identities separate and adds no canonical terms or
runtime record schemas. The thesis's ten first-order principles remain intact.

## From Meaning To Evidence And Back

```text
Product intent + domain meaning + observable expectations
                           |
                           v
              DomainSpec + exact realization selection
                           |
                           v
              deterministic construction of a candidate
                           |
                           v
         independent conformance + bounded runtime evidence
                           |
                           v
                  compare with expectations
                           |
         +-----------------+-----------------+----------------+
         v                 v                 v                v
      continue           repair            revise            stop
         |                 |                 |                |
         +-----------------+-----------------+----------------+
                           |
                           v
             retain evidence + recovery obligations + owner
                           |
                           v
             next permitted step, handoff, or parked work
```

Product context explains why the system matters. Shared meaning and DomainSpec
make its obligations explicit enough to construct and check. Exact realization
selection identifies the architecture and language-profile choices used for
this candidate. A generator must not silently supply an unresolved owner choice.

Deterministic construction makes the selected inputs and resulting artifacts
reproducible within a declared environment and dependency boundary. Reproducing
an artifact establishes repeatability; correctness needs separate evidence.
Independent conformance checks the declared obligations without simply repeating
the constructor's assumptions. Runtime observations add evidence for behavior
that static checks cannot establish, within stated conditions and limits.

Comparison preserves three possibilities: supported, contradicted, or unknown.
A missing runtime observation leaves its claim unknown. A structurally valid
specification can still express the wrong meaning; a passing test covers only
the behavior and conditions actually tested.

## What Feedback Can Change

Continue when evidence supports the current step and further useful work is
within scope. Repair a defective realization when the intended behavior remains
clear. If evidence instead challenges the meaning, expectation, or Product
proposition, return that question to its responsible owner for revision.
Stop when the objective is achieved, ended, or has no further permitted action;
record the reason so stopped work is not mistaken for a successful result.

The location of a failure matters. A generated implementation defect does not
automatically disprove the Method. A test that shares a generator's defective
assumption does not independently support it. Repeated failures across distinct
realizations can motivate a broader investigation, with attribution and
counterevidence retained before drawing a systemic conclusion.

Feedback supports a choice; it grants no new effect. Changing acceptance-bound
bytes produces a new candidate requiring current tests and product approval.
Product approval still precedes separate operational authority decisions.

## Example: A Booking Feature

Suppose a Product owner wants a temporary reservation to expire unless confirmed.
The selected meaning distinguishes reservation from confirmed booking, states
the expiration condition, and leaves any unresolved capacity policy visible.
This is an illustrative scenario, not a completed Craft construction result.

DomainSpec expresses those obligations. The selected realization identifies how
the target represents state and time, and construction produces one candidate.
Independent checks exercise confirmation and expiry at their declared boundary;
bounded runtime evidence examines what happens after an interruption or retry.

If a retry confirms an expired reservation, preserve the failing input, exact
candidate, observed transition, and expected behavior. Repair the realization
if it violated clear meaning. If the expiry boundary itself is ambiguous, the
domain owner must resolve it before the affected construction can proceed.
Independent construction work with sufficient meaning can continue.

Recovery needs its own evidence: after interruption, does the system resume in
a permitted state, and are any compensation or rollback obligations satisfied?
A happy-path booking test cannot answer that. The next owner receives the
candidate, checks, failure or repair evidence, unresolved policy, and recovery
obligations. Preparing the handoff does not establish receipt or acceptance.

## Retaining Evidence Through Evolution

Keep the selected meaning, realization, input and output identities, applicable
conditions, observed outcomes, corrections, and unresolved work attributable.
Later feedback must identify which candidate it concerns. Historical success
cannot establish that a changed candidate or dependency still behaves correctly.

Retained evidence lets a receiving owner understand what was tried and what
remains owed. It also supports comparison when replacing construction or
validation machinery. It does not imply permanent storage of every interaction,
automatic reuse of every correction, or autonomous learning and code upgrades.

## Testing The Promise

Use one bounded Product Feature and declare expectations before constructing it.
Check continuity from meaning to implementation, deterministic replay,
independent conformance, bounded runtime behavior, and recovery or migration
where applicable. Compare owner, builder, operator, and reviewer burden with a
declared baseline, including modeling, checking, and handoff costs.

Test missing observations, stale evidence, interrupted work, conflicting meaning,
and defective realizations. Hidden choices, repeated defects shared by builder
and checker, unusable handoffs, or greater total burden are counterevidence.
Repeated no-gain results should change or stop the tested approach. A successful
trial supports its bounded claims; it does not prove market value or the thesis.

## Construction Frontier And Operational Support

The current product-construction frontier is this draft thesis explanation and
its matching machine projection. Reviewing the loop, example, and claim limits
is runnable now. This prose revision implements no runtime and produces no
product-test evidence; implementation stages retain their separate work owners.

Operational support is limited to deferred source-binding or projection review
by the owners of any affected consumers; none is refreshed in this change.
No runtime stage is affected by this documentation edit, and no operational
prerequisite is asserted as a blocker. Publication and deployment remain outside
scope. Exact selected consumer bindings, if any, still need separate inspection.

## Open Questions

- Which first Product Feature can exercise construction, recovery, and handoff?
- Which observations independently test its domain expectations and runtime limits?
- How will delayed evidence reopen the relevant candidate assessment?
- What minimum burden reduction justifies the added modeling and checking cost?

## Source Basis

This develops the [Craft thesis](../product/PRODUCT-THESIS.md) under the
[Product Thesis document contract](/home/vlad_/projects/cyberAlchemy-v2/product/PRODUCT-THESIS-DOCUMENT-TYPE.md) and the
parent [CyberAlchemy thesis](/home/vlad_/projects/cyberAlchemy-v2/product/PRODUCT-THESIS.md) and
[work-loop explanation](/home/vlad_/projects/cyberAlchemy-v2/product/CYBERNETIC-WORK-LOOP.md). ARE's
[reasoning-and-learning explanation](/home/vlad_/projects/cyberAlchemy-v2/agent-reasoning-engine/REASONING-AND-LEARNING.md)
informs the distinction between feedback, retained evidence, and tested engine
changes; it does not prove that Craft's integrated construction loop exists.
