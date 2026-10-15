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
