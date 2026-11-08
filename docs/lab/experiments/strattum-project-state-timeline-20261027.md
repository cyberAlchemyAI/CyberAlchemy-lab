# Strattum feature-gap / Paperclip autonomy experiment

Date: 2026-10-27 UTC. This is a local feature and autonomy experiment, not a
Lab release or canonical Project admission.

## Feature selected

[Strattum Chat](https://www.strattum.ai/en/plataforma/chat) describes retrieval
at the version applicable on a requested date, ACL filtering before ranking,
exact source citations, and a question/access/answer trail.
[Memory Graph](https://www.strattum.ai/plataforma/memory-graph) describes entity
timelines. The current Lab `artifact.query` can read exact verified historical
source cuts, but it does not accept an effective date or apply per-record ACLs,
and its query result is not a cited readable answer with a durable read audit.

The initial [fixture candidate](../../../product/lab/release-candidates/v1/interface/project-state-timeline-v1/README.md)
tests four related capabilities together: synthetic effective-time selection,
per-record fixture filtering, byte/field/version citations, and a private read
receipt. It copies two real `project-state/v2` records byte for byte; the
effective dates, readers, and assessment findings are authored fixture data.

## Working local result

From the repository root:

```bash
python3 -B product/lab/release-candidates/v1/interface/project-state-timeline-v1/demo.py
python3 -B -m unittest discover -s product/lab/release-candidates/v1/interface/project-state-timeline-v1 -p 'test_*.py' -q
```

The demo returns the specialist-owner Project State for `vlad` at the synthetic
interval boundary, with the exact repository-origin state citation and an
explicitly fixture-authored assessment citation. The same-time `lab-agent`
query returns `no-accessible-state` without a hidden state identity. Both
paths commit private read receipts. The final suite has **14/14 PASS**,
including boundary, denied, tampered, ambiguous, malformed, audit-failure,
and post-read-mutation cases. Fixture manifest SHA-256:
`7c96f68515d3d1da35c3b192c67f2a727be38af30413b57519798108e12ac969`.

## Paperclip execution

An isolated Paperclip `2026.1023.0` instance is healthy at
`http://127.0.0.1:3101`; the historical Paperclip pilot was not reused.
Company `eafa0d57-b4ea-4a57-8b02-56fbce44a6d3` contains Project
`636b4dd3-bbc0-47e4-96d7-9bf3109f3622`.

| Issue / run | Observed result |
| --- | --- |
| CYB-1 `2da65987-30f7-4442-ba5e-3c9228eb5a93` | Fixture CLI slice complete; issue description was narrowed to the actual implementation. |
| CYB-2 `602bdf61-7257-4d18-a236-0bca2027bab4` | Independent subagent code review and Paperclip fixed validation recorded; done. |
| CYB-4 `80384a42-045a-45fe-a3bb-7f47e04d66a1` | Done. Genuine AI review through Paperclip process adapter succeeded in run `3028a9a0-944e-48fd-94b4-62e8a5ed10ba` on the preceding 11-test source. It found three issues, all repaired in the final source. A prior AI run `6061e998-d994-4de3-9f60-b134f73e8032` timed out at 180 seconds with no verdict. |
| Fixed validator `dca3b099-7a95-4e8f-9f86-76b284889541` | Final 14-test source: exit 0, demo/citations/receipts PASS, source unchanged, stdout SHA-256 `319cccaa2664396f7ccab09c86a77a3361dce3bc4444744516754f2910f2b97a`. |
| CYB-3 `ce82752d-244f-4483-8d7d-bba6ce9f296b` | Backlog: authenticated Lab API integration, trusted effective time/signed cut, graph/object policy, and broader query audit. |

The native `codex_local` Paperclip adapter failed lifecycle verification on
this host and produced no heartbeat. The successful AI review used a bounded
`process` adapter invoking the host Codex CLI in read-only mode. Paperclip
orchestrated the Project, issues, and review/test runs; implementation and
repairs were performed by the parent agent. This experiment does not show
autonomous implementation or complete Lab runtime qualification.

## Review findings and disposition

The first direct AI review found that a malformed pinned manifest could leave
only a `started` audit intent. The Paperclip AI review then found three more
cases: a fallback read exception could leave that intent unfinished, hidden
entry validation could reveal an error, and removal of `origin_path` could
downgrade state citation integrity. The final code completes bounded refusal
receipts for malformed/unexpected reads, validates dates and shape only after
fixture visibility selection, and requires a repository origin for selected
Project State records. Regression tests cover all four. An independent
subagent separately checked audit ordering, symlink paths, forged sources,
post-read mutation, and fixture provenance, then rechecked the final 14-test
source and found no remaining P1/P2 issue within the fixture contract.

## Boundary of this result

The principal is supplied on the CLI, and the fixture manifest is locally
readable. Its date assignments are synthetic, and the Lab's signed source cut
has no signed effective timestamp. The `assessment` finding is fixture-authored.
That fixture candidate is not an authenticated Lab API endpoint, a production ACL, a
signed historical Project State answer, or a Strattum parity claim. CYB-3 is
the concrete next implementation task for those capabilities.

## Authenticated signed-cut feature slice

The [signed-cut answer candidate](../../../product/lab/release-candidates/v1/interface/signed-cut-project-state-v1/README.md)
now uses the selected installed API75 Reader for exact historical
`artifact.query` followed by `artifact.inspect`. The read-only bridge is
`implementation/lab-runtime/local-host/strattum-api-bridge-0001/`. It selected
two distinct signed cuts (0 and 2) and one Project State at each. Capture-0002
SHA-256 is `513899d217ede516d84e4e6f28c560735c187e19bb00a134a5600ca7d54309a2`.
The out-of-scope query returned `unauthorized` without a state reference.

The private capture retains the disposable Reader's public policy, challenge,
proof, request/reply pairs, cuts and a completed receipt; it retains no private
Reader key. `verify_capture.py` checks the proof against the retained policy
key, pins the selected API75 source/profile digests, checks exact call/message
hashes and Reader context, and cold reads the repository-origin Project State.
With the pinned private `branch.snapshot`, it also verifies the local
transaction original bytes, decoded Project State and native original-body
SHA. A forged signature, mixed context, missing provenance, forged repository
origin SHA, and forged private transaction SHA were each refused in disposable
negative probes. The installed Reader owns signed-source verification; this
offline verifier does not independently replay its source chain.

The product `run_product.py` composed two different cited answers from the
retained authenticated capture. Current answer-0005 SHA-256 is
`1d932f8d44a65b201c92afc966c25dd91b6f5d5b333bac135f7785a95a2976c4`.
Each answer cites source locator, original content digest, provenance,
Project State version and exact pointers for name, identity, project and state
digest. The result explicitly says `API30 discrepancy assessment pending`.
The pure composer has **27/27 synthetic tests PASS** and both real captured
query/inspect pairs PASS. The fresh one-command live run passed: capture SHA-256
`7a45c06ecc813d43d5349fca77ed75b39c9015bcb0c201c7665852dbe80e45a8`,
answer SHA-256 `bd0692e9baaba455e22650167be633ba178fd7e7e6dc50bc6b9ad540a5d3ddd8`.
Cold verification of that capture and the answer receipt passed; the private
run directory and files have 0700/0600 modes. Independent final review found
no P1/P2 issue in this bounded feature.

## Paperclip autonomous coding test

Paperclip ran the coding agent in isolated Git worktrees with no parent-checkout
write access. CYB-6 generated the first composer (14 synthetic tests PASS),
but its Paperclip wrapper falsely failed the file allowlist because it stripped
Git porcelain's leading status space. CYB-7 then succeeded (18 synthetic tests
PASS), but both actual Lab captures were rejected because it assumed the wrong
binding shape and field names. CYB-8 succeeded (21 synthetic tests PASS) but
still assumed `decoded_artifact.artifact_type`; actual API75 uses `carrier_ref`.
The parent integrated only the reviewed CYB-8 source and repaired the real
response shape, Reader/actor, body identity/project, query scope and essential
citation checks. This is a **measured partial autonomy result**: Paperclip
scheduled and ran genuine isolated coding, while independent real API evidence
and human-supervised integration found defects its synthetic tests missed.
CYB-10 ran a separate read-only Paperclip AI review against the integrated
answer. It found that malformed nested request shapes, unusable essential
values and silent citation truncation could pass. The candidate now checks the
exact selected nested request fields, requires a nonblank state name and valid
state digest, and marks long citation previews with their full-value hash.
The three cases have focused negative tests. CYB-11's single exact-pin
Paperclip closure heartbeat `f9792d3e-bd02-4e2f-a769-d8e22a8bd732` passed:
27/27 tests, private capture proof and wrong-scope refusal, two real answer
recompositions, and answer-0005 receipt match. An independent subagent also
replayed malformed nested requests, blank/invalid essential fields, and long
citation values against the final code and found no P1/P2 issue within this
bounded feature.

The authenticated signed-cut slice is separate from the synthetic calendar
timeline. Cut 0 shows the specialist-owner state and cut 2 the local transaction
state; those are not the fixture's January/February states. There is no signed
business-effective date mapping, and a wrong-scope denial does not establish
per-record ACL filtering across Lab reads. Full Strattum parity and API30
diagnosis are not claimed.

## Separate local Project creation experiment

The fresh API76 package in
`/home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/api76-build-0003/`
passed native construction and the installed API cold check. Its archive SHA-256
is `0bbfe5e9b2aa098e95ed23f54b2200fa069eb933190e50a26686809ba55edec9`;
the package manifest SHA-256 is
`e4d30e95c73aa6a537f0bb922008955414aabea9d49bc472b395e2d43c350c6e`.
This qualifies that isolated installation, not the full regression suite, a
Docker run, or a live Session.

An initial attempt to create `project:lab-strattum-feature-gap-pilot` through
that installed API's `checkpoint.resolve` refused with `integrity-failed`
before `admission.apply`. The retained Store has no operation journal entry and
remains at genesis transaction 0. It has no observed Project admission. The
installed governance adapter assumes every target body has `node_id`, while
the current ProjectIdentity/v1 contract uses `project_id` as its signed identity
field. The failed Store and its reconciliation receipt are retained; the same
checkpoint call was not retried.

A separately reviewed attempt through that installation's native Store did
commit a signed local transaction for
`project:lab-strattum-feature-gap-pilot@1.0.0-candidate.1`. Its first result
was a refusal during receipt construction because the 1,980,014-byte native
transaction exceeded the API parser's 1 MiB input budget. The effect was not
retried. A read-only recovery cold replayed the retained Store and an exact
private copy, verified the signed approval, current ProjectIdentity subject,
original record, scope evidence and transaction, and wrote
`/home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/native-recovery-0001/RECOVERY-RESULT.json`
(SHA-256 `d273d655983e45bbe766628b7bd451a270b6822810be28c1ca9419655956be3d`).
An independent reviewer replayed the copied Store and verified its approval
signature, transaction and original bytes, single current ProjectIdentity,
source-to-copy hashes, private file modes, and unchanged prior refusal. The
focused native pilot and recovery suites passed **8/8** tests; no P1/P2 finding
remained within this local claim.
The recovered result is one **local native ProjectIdentity artifact**. The
governed API checkpoint/admission path remains unqualified; the generated
Project State still belongs to the existing migration Project. There is no
separate Project runtime or canonical repository authority change.
