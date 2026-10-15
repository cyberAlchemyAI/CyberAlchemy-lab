K03 — affects: semantic-owner review

Proposed meaning: admissible observations support a recorded impact link from an
exact Failure Occurrence or Incident to an exact affected subject, within an owned
scope and named evidence policy. This establishes the supported scoped observation.
It does not by itself establish causation, a severity grade, blame, or ownership.

The two source kinds are Failure Occurrence and Incident. Each may link to any of
these eleven target kinds: Agent Capability, Agent Session, Artifact Type, Generated
Output, Implementation, Ontology, Person Reference, Product, Product Capability,
Project, and Work. There are 22 declared ordered branches. This permits these
endpoint types; it supplies no observation for any branch automatically.

| Qualifier | Meaning to review |
|---|---|
| impact_scope | The exact owner-defined boundary of the observed impact. Evidence for one subject, context or period cannot silently establish wider impact. |
| evidence_posture | The exact owned evidence policy/posture and admissible provenance for this observation. A label cannot supply missing observations or successful execution. |

Example: during Incident X, admissible observation O documents a delay affecting
Work W within scope S. The owned evidence policy accepts the exact X/W/S linkage.
The root cause is unresolved, no severity assessment exists, responsibility is
unassigned, and W's ownership is unchanged. K03 can hold in that situation.
Simply seeing an incident timestamp and a late work timestamp does not itself
establish the required impact observation. A possible or predicted delay also
cannot qualify as an observed one.

Four separate conclusions require separate evidence:

- Causation: an independently justified causal model supporting dependence,
  rather than only the scoped impact observation or temporal association.
- Severity: a distinct admissible assessment under the owned severity policy.
- Blame: an independently justified responsibility assessment. Incident
  accountability alone does not assign fault.
- Ownership: an independently governed ownership record. Being affected or
  participating in an incident does not transfer ownership.

These conclusions may coexist with K03 if separately established; the relation
alone cannot establish them. Recording K03 appends its exact witnessed record
without changing those assessments or protected state. The proposed operation
must retain an identical existing revision and refuse conflicting content.

Theorem targets, not yet whole-theory discharges:

    Affects(X, T, S, P) implies SupportedScopedObservation(X, T, S, P).
    Affects alone does not entail Causation, AssessedSeverity, Blame, or Ownership.

Each of the 22 branches needs a valid meaning model and independently checked
non-entailment under the complete pinned theory. The seven inherited IDs cover
two qualifier meanings, one record effect and four excluded conclusions.

Current implementation evidence: the source audit confirms all 22 pairs against
the questioned definition and runs 13 JSON Schema boundary probes. Both artifact
schemas permit empty evidence arrays; Failure Occurrence permits prediction and
cause labels without proving observations or causes; Incident permits arbitrary
impact-summary text. The raw qualifier shape also accepts arbitrary nonempty
scope/posture strings. Those shape checks cannot replace semantic evidence.

Missing proof/integration work: independent typed impact model and complete
owned observation policy; raw-source decoding and exact reference refinement;
admissible evidence/provenance and frame/scope containment; all-branch models and
whole-theory countermodels; qualified/idempotent recording; public diagnostic
integration; independent checking. K03 is not proved or discharged by this audit.

This review asks only whether the exact proposed K03 meaning fits the owner's
intent. Other relation assessments and shared D01-D08 policies remain separate.
