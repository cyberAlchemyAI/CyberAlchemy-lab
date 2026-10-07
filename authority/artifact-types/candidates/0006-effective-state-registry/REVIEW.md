# Step 4 — Artifact Type effective-state registry

- Status: `candidate-owner-review-open`
- Authority effect: `none`

## Result

The registry inventories all `56` descriptor files across `46` identities and `49` declared references and `51` resolved references. It resolves `33` admitted contracts, `2` duplicate candidates, and every remaining candidate without reading admission from the embedded descriptor status.

The candidate also supplies `cal.artifact-type.artifact-type-registry/v2`. The v2 contract succeeds the candidate v1 contract because v1 can represent admitted entries only. V2 additionally represents every visible descriptor, historical state, duplicate resolution, semantic rebind obligation, activation posture, exact overlay, and discriminator path.

Candidate.2 closes every nested registry structure. Descriptor, admitted-contract, current-lookup, duplicate-resolution, lineage, overlay, inventory, discriminator, digest, and source-direction values now have explicit schemas. Seven hostile cases prove that empty descriptors and malformed contract, lookup, overlay, resolution, inventory, and lineage values are rejected.

The 56 count is the repository preimage being resolved, including the now-admitted Coordination Context/v2 successor. The Artifact Type Registry/v2 contract is staged inside this candidate and does not enter that preimage by implication.

## State counts

- `admitted-current`: `21` descriptors
- `admitted-historical`: `5` descriptors
- `candidate-unadmitted`: `28` descriptors
- `resolved-duplicate`: `2` descriptors

The registry also contains seven current embedded foundation contracts that share an Artifact Type descriptor file. This produces `28` admitted-current and `5` admitted-historical contract entries from `21` current and `5` historical descriptor files. Shared files are resolved by `(path, digest, Artifact Type ref)` rather than by path and digest alone.

## Step 3 semantic rebinding

| Artifact Type | Current effective state | Required action | New primary Definition |
| --- | --- | --- | --- |
| `cal.artifact-type.capability-realization-binding/v1` | `admitted-current` | `admitted-successor-required` | `cal.definition.capability-realization-binding@1.0.0-candidate.1` |
| `cal.artifact-type.context-profile/v1` | `candidate-unadmitted` | `candidate-rebind-required` | `cal.definition.context-profile@1.0.0-candidate.1` |
| `cal.artifact-type.measurement-method/v1` | `candidate-unadmitted` | `candidate-rebind-required` | `cal.definition.measurement-method@1.0.0-candidate.1` |
| `cal.artifact-type.measurement-result/v1` | `candidate-unadmitted` | `candidate-rebind-required` | `cal.definition.measurement-result@1.0.0-candidate.1` |
| `cal.artifact-type.model-instance-binding/v1` | `candidate-unadmitted` | `candidate-rebind-required` | `cal.definition.model-instance-binding@1.0.0-candidate.1` |

## Content audit

The effective-state audit answers **which exact contract is current**. The companion content audit answers **whether each contract's declared content is complete and current enough for its lifecycle state**. It checks all 56 descriptors against their schemas, Definition bindings, receipts, validators, fixtures, source direction, integrated contract sections, and reference-shaped relation fields.

The content audit finds:

- 12 admitted-current descriptors whose declared content is verified by this audit;
- 9 admitted-current descriptors needing review or remediation through immutable successors or refreshed evidence;
- 5 admitted-historical descriptors that remain preserved as history;
- 18 candidate descriptors whose declared content is verified and await admission review;
- 5 candidate descriptors requiring revision;
- 5 non-effective candidate records and 2 resolved duplicates that are not promotion targets.

The five candidate revisions are the four Step 3 semantic rebinds plus Ontology Package/v1, whose `CAV2-D19` binding is neither present in the admitted Definition registry nor resolvable at its declared path.

The nine current-contract obligations consist of legacy integrated-section review across older admitted contracts, two stale validation receipts caused by their pinned Definition registry digest, and the Capability Realization Binding immutable-successor requirement. The former Coordination Context/v1 mismatch is now historical and its v2 successor is admitted-current. No admitted bytes are rewritten by this audit.

Every resolved schema exposes at least one reference-shaped field. The audit inventories 521 paths for explicit mapping review against the 23-kind candidate Relation model. Those mappings remain review-only until Relation Kinds and their carriers are admitted.

## Real-like example

The Product Identity/v1 descriptor still says `candidate-unadmitted`, but the decision chain first admitted it and later moved it to `admitted-historical`. Product Identity/v2 is `admitted-current`. The migration Product/v1 descriptor was never admitted; its duplicate-resolution overlay points to Product Identity, whose effective current version is v2. No descriptor bytes are rewritten. The registry exposes all four facts and their exact decisions.

Capability Realization Binding/v1 is admitted-current, but Step 3 introduced its positive Definition after that admission. The registry therefore marks the current carrier `admitted-successor-required`; it does not rewrite the admitted contract or pretend the new Definition binding is active.

For a content example, Coordination Context/v1 says both `project_ref` and `goal_ref` are required semantic fields, while its admitted schema permits either field to be absent. Coordination Context/v2 closes that mismatch with explicit nullable fields and is now admitted-current; the v1 bytes remain admitted-historical.

For an evidence example, Bounded Context/v2 still validates its schema, fixtures, projections, and admitted Definition binding. Its current receipt is `FAIL` only because it pins an older digest of the mutable Definition registry. That requires a refreshed receipt or a validation design that binds the relevant Definition entry instead of the whole registry; it does not invalidate existing Bounded Context instances.

## Decision boundary

This candidate resolves the effective state of all 56 visible Artifact Type descriptors and 33 admitted contract entries and records a separate content audit over those descriptors. Admitting Step 4 would admit only the Registry/v2 contract and its exact initial registry instance. It would not collectively admit, revise, or repair the audited Artifact Types, admit an instance or semantic rebind, activate a consumer, or run a runtime.
