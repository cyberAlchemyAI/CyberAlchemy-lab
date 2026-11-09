# Integration decision preparation

These are **candidate design records**, not approved vendor choices or test results. [choices.json](choices.json) is the authored source for six option comparisons; [contracts.json](contracts.json) is the authored source for six prospective verification contracts. The [record index](index.json) resolves their twelve source-bound carrier instances. Both local carrier types have Artifact Type Requests and closed schemas under [carriers](../carriers/README.md).

The [component catalog](component-index.json) now gives 24 named technologies separate candidate identities, linked through each option's `component_refs`. The [stack coverage audit](STACK-COVERAGE.md) identifies the remaining unnamed software choices. An [Integration Binding carrier](../carriers/integration-binding/v1/artifact.json) is prepared for an eventual owner-selected, version-pinned release; there is no binding instance yet.

| Boundary | Option review | Verification contract | Provisional direction |
| --- | --- | --- | --- |
| Browser capture | [IG-01](records/IG-01/record.json) | [IC-01](records/IC-01/record.json) | Uppy camera UI where exact timing works; app-owned capture for processed blur. |
| Resumable transfer | [IG-02](records/IG-02/record.json) | [IC-02](records/IC-02/record.json) | Test Uppy Tus/tusd, with app-owned S3 multipart as fallback. |
| Private media store | [IG-03](records/IG-03/record.json) | [IC-03](records/IC-03/record.json) | S3 candidate pending region, cost and privacy review. |
| Speech to text | [IG-04](records/IG-04/record.json) | [IC-04](records/IC-04/record.json) | Transcribe batch candidate; faster-whisper comparator. |
| Background blur | [IG-05](records/IG-05/record.json) | [IC-05](records/IC-05/record.json) | MediaPipe browser spike with visible processed preview. |
| Assistance safeguards | [IG-06](records/IG-06/record.json) | [IC-06](records/IC-06/record.json) | Versioned reveals; visibility events only in disclosed research mode. |

Each option review records requirement context, why each option is considered, benefits, trade-offs, dependencies, failure modes, evidence maturity, source documents, decision constraints, revisit triggers and unresolved assumptions and a **provisional** preference. Each verification contract specifies an environment, fault or stimulus, acceptance condition, rejection gates, evidence requirements, threshold registration, failure route and independent reviewer route. Source and row digests tie every candidate instance to its authored source. [Validation](../../tools/validate_integration_records.py) checks parity and carrier schemas.

The intended sequence is requirement and product context → option review → verification contract → attributed synthetic run and evaluation → owner Decision → implementation and operational monitoring. The run, evaluation, Decision and implementation records have **not** been created. Acceptance values that depend on real populations, devices, costs, processor terms or jurisdiction must be registered by their owners before those tests can justify a pilot. Research involving real developers also follows separate study, consent and privacy gates.

The [candidate Lab Challenge Contract/v1](../lab-records/integration-choice-challenge-contract.json) now defines the standing route to reopen an integration choice when cost at scale, a new requirement, API changes, quality, privacy, reliability or exit risk changes the basis for that choice. Its [draft policy](RECONSIDERATION-POLICY.md) and [seven trigger clauses](challenge-triggers.json) specify eligible challengers, evidence, interim handling, response ownership and resolution. Each option review links to the contract and applicable trigger IDs. It is not active policy, an actual filed challenge or authority to replace a deployed binding. The `challenge_route` on a technical verification record remains only an independent reviewer route.
