# Public managed file export candidate

`files.materialize` implements the unchanged proposal 0008 contract and proposal
0007 request/receipt schemas. All 34 operation contracts remain in the catalog.
Handler support is 13; complete current Agent qualification remains separate.

## Permission

The new `lab-local-export-candidate-policy/v1-candidate` branch permits the eight
existing metadata operations and `files.materialize`. It binds the exact current
development authorization and a distinct owned Principal. Agent, Assignment and
Session context remain null. The existing metadata grant stays at eight
operations; original v4 participation grants stay at twelve. The expired original
Assignment and signer are preserved.

The host independently selects the complete artifact/path list, source cut,
privacy review, renderer, output scope and limits. The output root is its private
owned workspace's `exports/` directory. Its exact manifest and device/inode are
pinned in the authenticated policy. Both path checks and the opened directory
descriptor must match this binding. No client path chooses the filesystem root.

## Export and retry

Actual artifact bytes come from the original selected signed-source reader with
full parent and prefix checks. A managed generation has original-byte or rendered
files, a provenance manifest, receipt and durable publication marker. It confers
no admission or canonical replay authority. Source guards, current permission,
deadline, output budget, selection and privacy checks precede publication.

The generation quota is checked under a nonblocking private root lock. Partial
reservations count toward the quota. Concurrent lock contention after an operation
claim reports recovery required; it never silently reruns the claimed operation.

The existing operation vault pins each effect to an authenticated namespace and
exact JCS fingerprint. Exact retries reauthorize the current host, source,
selection and output scope. A published result then uses a read-only kernel path:
the generation must already exist and all manifest/receipt/marker/output bytes
must match. Missing or changed files never cause recreation. Changed fingerprints
conflict. Pending keys and incomplete generations require inspection/reconciliation.
`operation.inspect` reports an indeterminate domain receipt as requiring
reconciliation even when the receipt itself was durably recorded.

The public receipt binds the exact original API message bytes. Private export
evidence retains the kernel receipt and its semantic request binding so the
original wire message, selected source bytes and rendered output remain distinct.

## Verification scope

The selected suite retains 86 metadata/read/preparation cases and all 24 original
file-kernel cases, plus 24 public-export cases. Public cases cover real byte and
rendered exports, nonce authentication, stdio, exact retries, conflicts, inspection,
grant/actor/scope mismatch, paths, privacy, output and generation budgets, lost or
changed outputs, pending generations, root identity, revoked permission, deadline
and Session refusal. Full original Session source methods remain retained; a new
bounded episode and its relevant complete Session regressions still remain.

All checks use newly owned temporary fixture policies, keys, output directories
and source replays under the existing development authorization. They establish
no current canonical owner authority, human decision or production release.
