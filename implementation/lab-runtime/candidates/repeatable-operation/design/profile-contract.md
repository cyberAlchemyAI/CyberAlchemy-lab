# Independent source profile protocol

Status: candidate implementation protocol metadata; no canonical Source Profile type is invented.

An executable manifest identifies code. A policy core identifies permitted capture roots, exact selectors, accepted schema/profile versions, authority rules and transition rules. An independent capture pins the original-byte manifest, registry bytes, authority basis and expected source cut. Two captures may use the same executable without changing its identity.

## Capture and authority

1. Resolve immutable admission evidence before mutable lookup hints. Require complete original bytes and all selected schema dependencies.
2. Restrict paths to declared repository-relative roots; reject traversal, duplicate normalized paths, escaping symlinks and undeclared files. Schema selection is exact, including JSON Pointer selectors; never assume every identity is node_id.
3. Read the authoritative cut, capture original bytes, then reread the cut. Reject races, mismatched hashes or unavailable closure. Derived lookup and SQLite data are disposable projections.
4. Separate isolated candidate policy, signing keys, stores and journals from admitted operation. A candidate capture cannot satisfy an admitted-write gate.
5. Verify byte SHA separately from parsed meaning. Wire hashing, JCS command fingerprints and artifact byte hashing retain their distinct subjects.

## Profiles and transitions

The source-profile schema is transport/implementation metadata. It does not replace Project State, Ontology Cut or their governance. All references resolve against exact pinned bytes and dependencies.

A declaration of deterministic post-admission capture is allowed only when the reviewed policy core already covers the exact transaction consequences. Keep that stable core outside the changing capture and transaction postimage. Otherwise prepare a separately reviewed successor profile, retaining predecessor history and revalidating carried-forward inputs. Never rewrite an old profile or infer a successor admission.

## Four specified acceptance cases

| Case | Required result |
| --- | --- |
| Same executable, two distinct data cuts | Two capture identities; unchanged executable identity; each cut and original bytes verified independently. |
| Unsupported protocol | Reject before interpreting the capture or executing effects. |
| Changed lookup hint | Follow immutable authority evidence; reject a conflicting hint rather than treating it as admission. |
| Post-admission capture | Accept only declared consequence closure under the reviewed stable core; otherwise require an exact successor target. |

These are design cases. No profile loader, signature channel, original-byte capture implementation or runtime case was executed here.
