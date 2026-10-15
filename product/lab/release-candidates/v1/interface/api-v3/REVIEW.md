# Exact review members for the reader successor

Posture: candidate. Actual owner outcome: absent. Full R03: incomplete.

| Member | Why it exists | Exact review surface |
| --- | --- | --- |
| Reader contract profile | Bind the actual handler/schema/mapping implementation selected by host and client | `contract-profile.json`, `schemas/api-call.schema.json`, `schemas/api-reply.schema.json` |
| Catalog representation contract | Represent exact source declarations separately from domain instances | `schemas/catalog-envelope.schema.json`, `schemas/artifact-inspect-result.schema.json` |
| Catalog representation mapping | Select exact original descriptor or registered entry identity/body/bytes | `catalog-representations.json`, original per-row source bindings |
| Reader implementation | Enforce profile, source/header/body/cursor/SQLite parity and selective disclosure | Frozen package manifest and validation receipt |
| Ten connection correction members | Replace absent endpoint version labels with original admitted revisions | `connection-corrections/*/review-member.json` and each exact `record.json` |

These declarations belong in the final S02 closure. One conversation response may resolve independently scoped exact members under the plan's existing review rules. Candidate verification does not record that response.

## Concrete declaration example

`cal.artifact-type.owner-registry/v1` is an embedded entry in Artifact Type/v1's `registered_types` array. The old source subject retains the containing root's identity and body. The reader selects the exact entry for metadata inspection and assigns its represented catalog identity `cal.artifact-type.owner-registry`. It retains the original parent-file SHA, entry selector, selected canonical byte SHA and original instance-schema binding.

This declaration is not an Owner Registry instance. Inspecting it creates no registry, role assignment or admission outcome. The original domain instance validator remains unchanged.

## Concrete connection correction example

The admitted original `assignment-project` Typed Relation names the missing endpoint:

```text
project:cyberalchemy-v2-to-lab-migration@candidate.1
```

Its proposed successor names the original admitted endpoint:

```text
project:cyberalchemy-v2-to-lab-migration@foundation.1
```

The exact `record.json` changes only that `/payload/target/version_ref` value. Its kind, identity, Relation Kind, qualifiers, scope and all other fields are preserved. The review member binds the original D71 admission overlay and endpoint bytes. The original relation remains unchanged.

In the selected engineering cut, `@foundation.1` is historical because a signed local successor exists. Historical connection validation passes; current-write eligibility rejects that Project endpoint. Applying this correction requires a declared historical correction write profile and exact scope/owner/application evidence. Rebinding to a newer Project simply to make a current-write check pass would change the historical connection's meaning.

## Remaining work

The ten original unclosed connections remain in the authoritative captured query result. Correction candidates have no signed application receipt. Thirty API handlers, general prospective descriptor validation, persistent projection and ontology joins, remaining workflows, complete Agent/session and human pilot requirements, final review and A01-A04 remain required.
