# Remaining application design for exact historical reference corrections

This is implementation analysis for the next candidate step. It does not install a write policy, authorize a store action or record an owner outcome.

## Observed constraints

The immutable coupling engine checks each authored record's `scope_ref` against the signed proposal scope. Store initialization permits its exact selected Project scope or a generated local store scope. The ten postimages retain their original `scope:cyberalchemy-lab-first-agent-episode` domain scope. Changing that scope merely to fit an existing store would add an unreviewed semantic change.

Three corrected Project endpoints are historical in the selected engineering cut. The represented-subject mapping refuses their use under the ordinary current-write policy. Historical reads explicitly allow them. A new revision's postvalidation does not automatically inherit the old revision's historical-read permission.

The other seven corrections passing endpoint validation still lack a signed, independently scoped revision application. A schema check or endpoint check alone does not complete the transaction.

## Recommended candidate implementation

Create a separate pinned write-profile successor with a declared historical reference correction target. Bind its source/record/schema dependencies, exact predecessor and correction member, endpoint witnesses, domain scope and effect in the signed proposal and resulting Decision core. Include the new profile and its independent semantic members in final S02/R08 review.

Provision exact authorized domain scopes independently from the archive read namespace and Project identity. Do not accept an arbitrary caller-provided scope or infer a grant from the record. The host must resolve the independently provisioned boundary and selected exact target scope before preparing the transaction.

A historical correction must resolve an existing admitted predecessor and prove the only changed body selectors are the reviewed endpoint version values. Each old label must be absent from the captured source cut. Each replacement must name the exact reviewed eligible original endpoint and admission witness; preserve semantic identity, endpoint kind, Relation Kind, qualifiers, body scope and other fields. Historical endpoint eligibility is an explicit property of this correction use. It does not become general authority to write against historical or withdrawn subjects.

Validate the original carrier schema, closed exact endpoint pair, qualifier contract and independently selected mapping. Bind the new version and independent Decision identity. Preserve the predecessor and original malformed source bytes as historical evidence. A correction version cannot be silently injected into a read projection or substituted under the original admitted version reference.

Exercise the declared profile in a fresh owned store with an independent fixture signer, then replay its original committed bytes cold. Verify all ten corrections, original source preservation, exact scoped consequences, current-vs-historical distinction, retry and interruption recovery. Only actual signed application receipts justify counting them as locally applied. Canonical admission and operational activation retain the final review's existing boundaries.

## Required negative cases

1. Unprovisioned or mismatched domain scope.
2. Missing, wrong or no longer current predecessor.
3. A replacement selected by latest identity rather than exact reviewed version.
4. Changed qualifier, Relation Kind, scope, semantic identity or any unreviewed field.
5. Withdrawn, wrong-kind, wrong-identity or unknown replacement endpoint.
6. Replacement bytes or admission overlay differing from reviewed witnesses.
7. Missing historical correction declaration or misuse by an ordinary revision.
8. Undeclared endpoint pair or qualifier axis.
9. Forged owner/signature, broad grant or reused independent Decision identity.
10. Source/head/profile drift after preparation.
11. Partial publication, inconsistent replay or unsafe recovery.
12. Projection-only insertion falsely claiming a committed repair.

The full 34-operation API, prospective descriptor handling, persistent projection/ontology integration and complete workflow requirements remain unchanged.
