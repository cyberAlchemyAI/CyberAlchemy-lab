# Candidate represented-subject adapter

Status: O02 partial implementation. Canonical admission and signed transaction mapping remain open.

## Contract

The raw carrier and the represented subject are distinct. The exact C14 proposal maps Project Identity/v1 to the Project endpoint and Product Identity/v2 to the Product endpoint. Method uses its separately selected candidate carrier. All other subjects keep their carrier semantic kind. The adapter has no inferred aliases, string-prefix mapping or label-based identity.

Each view preserves the original carrier bytes, exact revision, identity selector, current signed carrier contract, schema bytes, mapping proposal and represented kind. The signed C12 archive supplies independently replayed catalog contracts. Workflow postimages are unadmitted prospective inputs; a catalog contract does not admit an instance.

The selected candidate cut is closed. An unchanged signed input retains its independently replayed admission posture and original byte digest; candidate postimages stay unadmitted. Duplicate revisions, committed-subject overwrite, out-of-cut endpoints, edited views, historical carriers and original-byte drift are rejected. Separate workflow cuts remain separate even when their proposed revision strings collide. The adapter requires an open verified replay handle and rejects caller catalog metadata or altered catalog/mapping indexes.

The frozen runtime's actual relation validator is invoked on a private represented-subject view, preserving exact ordered pairs and qualifiers. This checks candidate compatibility. It does not implement signed transaction persistence, install a mapping into a registry, create a confirmed global Edge, authorize an ontology event or establish an owner outcome.

## Remaining O02 work

Translate the rich Node/v2 contract to Rust semantic state with independently resolved definition selector digests, components, use obligations and forbidden collapses. Map exact Lab source effects to separate ontology events; join governance through exact event identity, digest and cursor. Keep retire, remove and source withdrawal separate. Demonstrate deterministic reconstruction and challenge-only semantic-byte preservation.

The current Rust reducer admits only `test-empty-profile/v1` with empty typed properties. Node/v2 permits rich profiles and typed properties. A separately declared candidate profile/runtime extension needs implementation and exact review; deleting properties or relabeling that profile would lose meaning. O03 supplies ontology event admission; O05 supplies closed coupling reconciliation; R03 supplies transaction/API integration. W08/S02/R08 review exact new mapping, implementation and effects. W07 remains incomplete until those actual integration obligations have evidence.
