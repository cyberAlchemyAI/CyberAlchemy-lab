# Package transfer v1 candidate calculation

Pure groundwork for package.export and package.import. Original public request
schemas remain unchanged. The five new schemas are closed internal controls and
archive structure; they are not canonical Definitions, Artifact Types or APIs.

Export retains each original JSON byte sequence, including whitespace, as base64.
It verifies hashes and complete reachable dependencies, allows bounded cycles,
and rejects dangling bindings, duplicate identities/references, unreachable extras,
incomplete ordered request closure, incomplete privacy review and private content.
Independent selected Actor/cut/control values must match; dataclasses do not
authenticate them. Source admission basis bytes survive as provenance, but this
calculation cannot verify signatures or transfer authority into the target.

Archive verification rechecks original controls and rebuilds the exact complete
metadata/content structure. Import accounts for every source artifact and retains
all nonartifact dependency bindings. Exact copy versus explicit adaptation must
match actual bytes; retain/exclude cannot conceal a candidate target. Every target
has a separate bound body, current selected scope and identity without collision.

The import plan explicitly leaves target model validation pending. Its host must
validate every original carrier/schema, full prospective model, typed relations,
mapping semantics, current preimages and complete generated Decision core before
exposing a Change Proposal. It must also verify source admission by actual replay.
No generalized validity is inferred from target hashing or source admission.

Integration still required: independently authenticated export/import policies,
actual current source and source replay, exact owned output scope, strict clocks
and budgets, durable operation claims, managed generation/recovery, target model
validation and complete real public tests. No public handlers are added yet.
Fixtures are synthetic pure values; no real user usefulness or admission is claimed.


## v2 successor

Raw text and binary dependencies have explicit encoding declarations covered by
the complete privacy review. Artifact bodies remain original JSON for later
carrier validation. Exact raw dependency bytes survive archive verification;
neither parsing nor rendering rewrites them. Binary labeling cannot bypass the
JSON credential/Session checks, and PEM key markers are refused in every encoding.
The actual host remains responsible for a genuine privacy review of every raw
dependency; a byte scan is not proof that an arbitrary binary contains no secret.
Source basis duplicates are refused. Complete import output is bounded at 1 MiB.
Archive and privacy-review internal schemas are explicit v2 successors; original
public request schemas and all 50 original test assertions remain unchanged.


## v3 successor

Controls, API requests, import mapping/disposition, target bodies and resulting
plans retain their original 1 MiB budget. Individual source materials are capped
at 32 MiB, aggregate originals at 40 MiB and encoded archives at 64 MiB, further
limited by the independently selected export contract. These limits allow a
complete selected 23.5 MB replay snapshot without dropping its dependencies.
Archive/v3 and export-contract/v2 are explicit internal schema successors.

Text/binary labels cannot hide JSON objects, arrays or strings: structured-looking
bytes must pass the bounded strict decoder and recursive privacy checks.
Duplicate keys, malformed or invalid UTF-8 structured bytes are refused. Ordinary
text and binary bytes remain exact. Independent source/privacy review is still
required for arbitrary nonstructured data; this calculation supplies no authority.
Archive verification now checks its frozen source both before and after work.
All 61 predecessor assertions are retained; no public handler is added here.
