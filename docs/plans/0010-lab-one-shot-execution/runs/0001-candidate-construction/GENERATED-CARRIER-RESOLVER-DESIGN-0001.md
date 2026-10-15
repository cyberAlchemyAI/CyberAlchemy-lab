# Selected generated carrier reference resolver

Status: implementation design; authority effect: none. This does not close a
runtime or semantic obligation. The frozen API72 candidate remains unchanged.

## Input contract

The resolver receives the actual current source view, a read facade selected by
the independently reconstructed completed producer, the exact original proposal,
and the producer's original typed input registry. These inputs must have been
verified during the current invocation under the actual host guards. A caller
cannot supply the registry, choose a different producer, or widen its permission.

Every registry entry retains its original binding, declared evidence kind and
posture, optional exact artifact header, and optional independently bound original
or receipt path. Payload locators and copied workspace object locators remain
distinct. Their correspondence comes from the verified producer reconstruction.

## Resolution rules

| Carrier | Reference | Required resolution |
| --- | --- | --- |
| Evidence Set | `payload.source_refs` | Exactly one selected original `source` entry for each reference, with its original bytes and exact artifact revision. |
| Evidence Set | `payload.item_refs` and `evidence_refs` | Exactly one selected typed original entry for each reference. Artifact revisions, Decisions and operational receipts use their own declared validation path. |
| Evidence Set | Project counterpart | Exact current Project header and separately declared `member-of` Typed Relation with matching revision, signature, axis and endpoint kinds. |
| Challenge Event | Contract | Exact independently selected current Challenge Contract revision and captured original schema. |
| Challenge Event | Challenger | Exact selected active Principal, equal to the actual authenticated producer Actor. |
| Challenge Event | Subject identity and revision | Resolve together to the producer's exact original subject header and byte binding. Historical use requires separately declared permission. |
| Challenge Event | Ground | Present in that exact Contract's allowed grounds. |
| Challenge Event | Evidence | Complete required evidence kinds and unambiguous original binding coverage; retain each entry's posture. |
| Challenge Event | Subject relation | Separately declared `challenges` Typed Relation, matching original subject revision, signature, axis, endpoint kinds and qualifiers. |
| Challenge Event | Resolution fields | Only the producer's verified open/`none`/empty-residue output is supported by this resolver. Other lifecycle states remain not evaluable. |

Missing, changed, duplicate or ambiguous selectors produce bound refusal evidence.
Unknown carriers and unsupported states retain their explicit semantic gaps.

## Output contract

Return separately bound checks and typed resolution rows, including the exact
resolver source and selected producer bindings. A passing reference check proves
only closure within these selected original bytes and source cut. It supplies no
finding of factual validity, recognized owner authority, admission or activation.

Do not change the original generic schema/core checks or declared connection
checks. Replace a carrier's generic unresolved-reference check only when every
listed obligation has a separately passing result. Preserve the original coverage
statement, limitations and unrelated review gaps.

## Qualification before use

Use a frozen successor and fresh owned fixtures. Execute original validation and
preparation with positive exact selection, plus missing receipt, substituted
source bytes, wrong evidence kind, foreign Principal, duplicate selector,
undeclared ground and unsupported resolution-state cases. Re-run the affected
inherited selections against that successor. Existing frozen failures and
predecessor runtime claims remain bound to their original sources.
