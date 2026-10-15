# Original-byte custody integration into the full Lab API

Status: implementation analysis for the next integration successor. Authority effect: none. The standalone storage primitive does not close the API workflow.

## Preserve the selected current engine

The current API independently selects corrections-v1/engine-next and the fresh-participation source. This engine already owns `lab-runtime-proposal/v2-candidate`: its proposal binds a correction profile and each target's reference correction binding. Its scoped configuration/v3 and approval/v2 bind configuration, correction profile and authorized domain scope. Endpoint mapping and historical schema/endpoint rules are also independently selected. The bare frozen-v2 writer is not a substitute for these obligations.

The storage candidate uses distinct `lab-runtime-original-json-proposal/v1-candidate` and `lab-runtime-original-json-transaction/v1-candidate`. Before composition, preserve both original families and add an explicitly named combined contract with the exact correction/reference fields and original-content entries. A composed proposal must not drop those fields to satisfy the older bare writer.

## Prepare and review

1. Recover each actual original target byte body from the authenticated private Vault. Recheck its existing header, media type, byte hash, length, carrier, identity, discriminator, schema and privacy gates.
2. Wrap that same byte body in the custody entry; never reconstruct it from the parsed object. Preserve binary evidence/package inputs separately under their own media and content contract.
3. Bind every new schema's original bytes independently from the inherited descriptor schema encoding SHA256. Keep semantic equivalence out of original-byte claims.
4. Build the exact combined proposed target, including correction binding and original entry. Regenerate the stable Decision core and proposal digest for that actual target before review. Earlier preparation cores over v1 targets are historical evidence, not authority for a changed package.
5. Preserve all source/capability/action/owner/reference and typed connection closure. A storage protocol cannot confer these permissions.

## Admit and retrieve

1. Verify current source, independent grant, exact review/checkpoint/owner closure, original byte identity, expected HEAD and recovery state before applying a complete proposal.
2. Publish transaction and embedded originals through the existing single HEAD commit. Retain all independent Decision cores and deterministic consequences.
3. Update the successor original-source reader: decode the original entry through its explicit content selector; compare its raw SHA256 and parsed structural value against the replayed record; preserve the enclosing transaction's original byte digest separately.
4. Update artifact headers and body retrieval to use the original SHA256 for custody entries. The current artifact_model unconditionally re-encodes selected values and is not suitable for these entries without a successor.
5. Populate the complete existing SQLite projection with exact raw BLOBs; retain privacy exclusions, all metadata, typed connection checks, watermarks, original semantic gaps and independent source cut. The small custody BLOB cache is evidence for storage parity, not a replacement for that complete projection.
6. Preserve context and ontology source bindings. Ontology representation history stays independently governed; neither decoded raw content nor a cache row creates ontology authority.

## Export, files and recovery

Exact exports return approved original bytes. Rendered files bind renderer/template/input/output independently. Managed-path ownership, symlink/traversal/collision protections, complete package manifests, binary material custody, installation policy and recovery remain original API conditions. Delete cache generations and verify fresh canonical replay without promoting them into input authority. Cold retry of a completed request returns its recorded result; uncertain pending effects require reconciliation.

## Validation and final review

Run the full original 34-handler contracts and relevant source/schema/session/transaction/ontology/package regressions after composition, with real owned positive/negative journeys. Retain all prior source/proof bytes. Add exact original-content protocol schemas, codec and composed publisher/source reader to S02's scoped review members. Record original/structural/approval/event digests separately. R08 remains the one actual final owner checkpoint; this analysis supplies no outcome.
