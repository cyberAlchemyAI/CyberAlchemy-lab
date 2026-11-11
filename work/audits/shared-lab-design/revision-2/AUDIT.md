# Shared Lab design revision 2 audit

Revision 2 improves the individual field comparisons. It still needs a design round for the handoff between verification and planning. The same receipt can accompany a changed structured value when the planner checks a narrower binding than the effect or decision consumes.

| Prior finding | Re-audit |
| --- | --- |
| A01 Publication | Open. AdmissionSnapshotMatches leaves the index outside its comparisons. Bundle authorization can remain identical while the proposed index changes. Historical receipt handling also needs a verified envelope for the entire observed operation. |
| A02 Compatibility | Open. CarrierCompatibility compares selected and observed schema to each other. The fidelity observation binds the body and scope. Replacing both schema references together leaves the fidelity observation valid to the planner. Bind carrier, original schemas and generators, exact edge manifest and mapping to the same assessment. |
| A03 Lifecycle | Partial. Intent, predecessor, successor and operation comparisons improve the plan. The closure observation binds the proposal while consumer_manifest and closure_receipt are presence checks. Bind the complete declared universe, exact closure and permission proposal to the same decision. |
| A04 Recovery | Open. AssessJoinTransition proves refusal only for ObserveRefusal. ObserveNativeCommit can advance from NativeUnknown with an Unknown outcome. Specify the admissible evidence and outcome for every transition and for terminal observations. |
| A05 Construction | Open. EntryBound checks the entry ID and internal coverage. ResultsCover compares results to specifications supplied with that ID. Changing a specification and its result together leaves the entry and independent assessment receipts usable. Bind the immutable specification manifest and complete result manifest to their receipts. |
| A06 Atomic admission | Sound boundary choice, incomplete handoff. The selector CAS can expose a complete snapshot only if its expected selector, immutable snapshot membership, and all declared consequences travel together in the verified plan. The changed-index witness applies here too. |
| A07 Meta types | Closed for the audited role issue. Review and native outcome alternatives are Policies. ChooseDecision remains a result constructor. |
| A08 Join identity | Partial. The numeric operation key and historical read improve persistence design. BeginJoinPlan checks the receipt against its own subject and a run reference. Define a verified key assignment that binds both numeric keys, the workspace, the run and the original operation. Require replay of the exact immutable command tuple. |
| A09 Ports and registry | Partial. Typed wire signatures exist. Define the checked conversion from each verified port result to each planner input. In particular, a RegistryAssessment names predecessor and postimage while the planning observation checks a registry subject alone. Specify the relation between the receipt bytes, decoded members, and the plan. |
| A10 Selection and trace | Partial. The compact partition checks membership, uniqueness and disjointness within the submitted lists. The complete-selection observation binds a separate selection reference. Specify how exact members, obligations and check specifications derive from the verified manifest and reach the planner together. |

## What to settle before implementation

1. Define one exact verified representation for each decision. Decode the original receipt and its referenced manifests, validate the full proposition, and pass that verified value through a single typed projection. Avoid combining a verified binding with independently supplied copies of its members.
2. Document which comparisons belong to the verifier, which belong to AlchLang, and how the interface enforces that division. Rename or document Verified as a binding comparison. Its equality checks alone establish neither issuer authority nor proof validity.
3. Complete the transition table with outcome, event type, revision, run and original operation for each edge. Require a committed or replayed observation for commit signals and an actual selected-snapshot observation for publication.
4. Retain the 80 existing planning checks. Add substitutions where both sides of a local comparison change while the authoritative receipt stays fixed. Require rejection either at the checked projection or at the planner. Cover valid replay and failure cases before enabling persistence or publication.

The existing definitions remain sufficient for this audit. The missing work is the contract and projection that preserves their meaning across the port and planner boundary. The five pending definitions retain their owner review status.

The witness runner uses synthetic observations and the original checked candidate model. It tests planning outcomes. Real authorization and effects require a separate qualification.
