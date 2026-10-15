# Exact classification rule evaluation

This pure kernel is part of the unfinished `classification.prepare` handler.
It checks exact original subject, Scheme and Value revisions, independent axes,
candidate fields, selected evidence bytes, cardinality and compatibility rules.
It produces validation evidence. The public API must separately resolve the
actual current source cut, complete existing assignments, trusted caller,
material vault, assignment schema, stable Decision core and ChangeProposal.

## Closed rule selection

Each exact declared rule string selects an explicit evaluator in `engine.py`.
An unknown string produces `not-evaluable`. A new evaluator requires a reviewed
successor with its meaning, code and evidence bound to the final package.

| Declared rule | Interpretation in this candidate |
| --- | --- |
| one-active-value-per-subject-axis | One active/candidate annotation in the exact subject revision, Scheme revision and axis slot. Different axes remain independent. |
| one-runtime-posture-per-agent-instance | One actor-kind runtime posture annotation for an Agent Instance in the exact Scheme. Its meaning on another independent axis remains not-evaluable. |
| annotation-never-grants-authority | Assignment authority effect must remain none. |
| machine-agent-requires-ephemeral-instance | The declared Agent couples to one selected Session, which couples back to that exact Agent. Agent identity cannot couple to multiple selected Sessions. |
| session-memory-expires-with-session | That declared Session's memory boundary explicitly expires with the Session. |

The last two rules validate declarations. Live resource custody, ephemeral
authentication, actual expiry and RAM disposal require the separate runtime
checks. A classification result cannot supply those observations.

## Evidence and non-collapse

Basis bindings retain actual bytes. A source can support an annotation without
establishing a cause hypothesis, effectiveness, authority or ontology truth.
Failure Occurrence, mode classification, proposed cause, impact, control and
recovery remain distinct obligations. No rule aliases one independent axis to
another.

Existing assignments are supplied by the host from the complete selected cut.
Unknown status meanings remain not-evaluable. Revisions require the final
prospective assignment set; hiding a predecessor or foreign assignment is not
a public request option.

## Readiness

The kernel's tests use retained W05 and Agent episode bytes and owned in-memory
variants for negative cases. They establish primitive behavior only. They do
not qualify the public API or admit the rule interpretations. Full current-cut
handler integration and exact ChangeProposal construction remain required.

## Successor parser correction

An actual owned in-memory probe showed that the original parser accepted
duplicate members and selected the last value. This successor rejects duplicate
JSON members at every nesting depth and nonfinite JSON tokens. All 18 original
test methods remain unchanged; three exact-byte counterexamples are added.
