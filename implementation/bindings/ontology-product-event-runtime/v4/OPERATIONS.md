# Operational support — preparation only

Owner: runtime owner for activation/cutover and rollback; source ontology owners
for meaning and admission; repository owner for publication. Authority effect none.

Current construction is independent of these operational tasks.
The two governance adapters use the governance-model owner as the proposed
coordination route. This is not a newly granted authority or an owner decision.
The import retains each source's declared authority posture and unresolved
questions rather than resolving them by changing a status.

## Proposed cutover prerequisites

After one exact tested Product is approved, select the exact runtime build,
manifest, target, consumer list and rollback envelope. Each consumer change
needs an explicitly owned scope. Do not replace the current v2 or v3 stores.
No current consumer list or live cutover decision is claimed here.

## Proposed rollback

Keep original source documents and old event stores read-only and available.
For a future consumer switch, first record its exact previous binding. On a
verified failure, stop that consumer's new writes and restore only its previous
binding under the separately authorized envelope. Preserve all v4 transactions
for diagnosis; do not delete history or replay v4 events into v2.

## Deferred residue

Admission and source interpretation: source owners; stage post-Product approval.
Live cutover: runtime/consumer owners; stage activation; requires exact consumers.
Publication: repository owner; no construction stage; not requested.
Source retirement: source owners; migration administration; not requested.
None is a causal blocker for runnable prototype implementation or tests.
