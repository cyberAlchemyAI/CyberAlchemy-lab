# Product and research policy set

Status: **candidate and unissued**. The [policy index](index.json) contains fourteen Lab Policy/v2 candidate records, 46 source-bound [Policy Clause](../carriers/policy-clause/v1/request.json) records, one [Retention Schedule](retention-schedule.json) and one [Assistance Permission Matrix](assistance-matrix.json). The latter three use local candidate Artifact Type Requests. No owner has issued these policies; a schema-valid record is not operational permission.

| Policy | Purpose and current open choice |
| --- | --- |
| [POL-01 Purpose, basis and notice](records/POL-01/policy.json) | Controller, jurisdiction, lawful basis and participant wording. |
| [POL-02 Retention and deletion](records/POL-02/policy.json) | Ten data classes, expiry clock, durations, vendor/backup deletion and exceptions. |
| [POL-03 Assistance and integrity signals](records/POL-03/policy.json) | Participant-visible allowances, research arms and no punitive inference from browser events. |
| [POL-04 Administration and recovery](records/POL-04/policy.json) | Pinned case/timer and the existing [draft Administration Policy](../recovery/administration-policy-candidate.json). |
| [POL-05 Accessibility and alternative modes](records/POL-05/policy.json) | Supported modes, accommodation and non-punitive failures. |
| [POL-06 Case release and exposure](records/POL-06/policy.json) | Reviewed forms, exposure limits, retirement and replacement bank. |
| [POL-07 Scoring and feedback](records/POL-07/policy.json) | Evidence, independent review, correction and display gates. |
| [POL-08 Research recruitment and assignment](records/POL-08/policy.json) | Cohort, allocation, protocol amendments, precision and stopping. |
| [POL-09 Research data use, export and training](records/POL-09/policy.json) | Purpose eligibility, export lineage, withdrawal and model-training separation. |
| [POL-10 Access, security and incidents](records/POL-10/policy.json) | Principal/role guards, exceptional access, containment and notification route. |
| [POL-11 Vendor and dependency governance](records/POL-11/policy.json) | Processor identity, region/terms, package license/version and data route. |
| [POL-12 Rights and feedback contest](records/POL-12/policy.json) | Access, correction, withdrawal, deletion and evidence challenges. |
| [POL-13 Claims and employment use](records/POL-13/policy.json) | Bounded public claims and separate named-role validation before selection use. |
| [POL-14 Integration reconsideration](records/POL-14/policy.json) | The existing [Challenge Contract](../lab-records/integration-choice-challenge-contract.json) and change grounds. |

The [retention schedule](retention-schedule.json) has ten separate data classes and deletion/derivative routes. **Every duration is null**, and the controller, jurisdiction and approval are unset. Those are owner and legal decisions before any real collection, followed by deletion and restore tests. A queued deletion job or written schedule does not prove deletion.

The [assistance matrix](assistance-matrix.json) proposes the same baseline for all three sessions: personal scratch notes and accessibility tools allowed; live internet, IDE/code assistants, generative AI and human coaching disallowed during the timed answer. General preparation before the specific case is allowed. These are **candidate values**, not participant rules. The exact matrix must be reviewed, published before case exposure and pinned to an Administration Policy. E09 research arms can have their own disclosed, assigned allowances. Focus/visibility events alone never establish rule violation or lower a score.

Each Lab Policy/v2 record links to candidate clauses with condition, action, enforcement point, required evidence, exception route, owner and open parameters. Specialized [Recovery Rules](../recovery/index.json), [Access Permission entries](../concrete-records/index.json), Study Protocols and the future Decision Policy retain their own carriers. The policy set constrains them when issued; it does not replace their operational state or owner Decisions.

The order for a pilot is: name principals and jurisdiction → resolve purposes, notice, retention, assistance and vendors → reconcile administration, access and rights handling → freeze study/case/scoring policies → run enforcement, deletion, accessibility and incident rehearsals → issue exact policy versions and link them to the pilot release. [External source review](EVIDENCE-REVIEW.md) explains why these domains were included. [Validation](../../tools/validate_policy_records.py) proves source, schema and link consistency only.
