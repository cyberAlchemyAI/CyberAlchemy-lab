# Retained reviewed predecessor carrier for exact reference corrections

Status: proposed candidate semantic contract. Canonical authority: none. Actual owner outcome: absent.

An exact corrective revision may retain its admitted predecessor's historical carrier when the selected correction profile enumerates that exact revision and an independently provisioned store grants its unchanged record domain. The runtime must independently bind and validate:

1. The exact current admitted predecessor, original record bytes and source provenance.
2. The complete reviewed postimage and successor identity/version.
3. A closed set of missing endpoint version selectors, with all other fields unchanged.
4. The exact original eligible carrier, descriptor and schema, with the complete postimage validating against that schema.
5. The original declared Relation Kind, axis, endpoint pair and qualifier contract.
6. Both exact eligible admitted endpoint revisions and their original source/schema/admission witnesses. Historical eligibility is explicit; withdrawn revisions are refused.
7. The selected correction profile and record domain grant in the signed configuration, proposal and independent Decision core.
8. An independent exact approval for the final complete transaction and atomic application/recovery evidence.

This candidate's closed membership is precisely the ten bindings in engine-next/write-profile.json. Its permitted category is Typed Relation, permitted operation is revise, and selectors are only `/payload/source/version_ref` and `/payload/target/version_ref`. It cannot revise a carrier declaration, Relation Kind, endpoint identity/kind, qualifier or record scope. It cannot use an unreviewed historical revision, substitute a latest revision, or authorize an ordinary write with historical carriers.

The unchanged malformed predecessor becomes historical after the correction commits. Its original unresolved reference remains inspectable as historical residue. A read projection must not erase it or present it as a successfully closed historical relation.

This rule is independently scoped in the final review. A runtime implementing it is evidence of candidate behavior. Canonical use requires exact R08 admission of the rule and its downstream publisher/validator integration; no such outcome has been recorded.
