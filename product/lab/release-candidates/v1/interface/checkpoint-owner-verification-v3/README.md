# Checkpoint owner verification candidate

This component supplies an independently selected owner/key configuration,
original current-source resolution through API59, and exact authority joins.
It is a construction candidate and grants no effects.

The host selects a private file and its exact digest during construction. Public
request fields cannot select a signer key, owner mapping, authority sources or
time window. The file is read through no-follow directory descriptors; its
owner, mode, link count, byte hash and file/directory identities are checked.
Every call reads its actual bytes and the real clock again. Changed, expired,
revoked or ambiguous selections fail. Private signing keys are never accepted.

`API59Sources` requires the actual frozen API59 Service, ReaderChannel and Vault.
It verifies the complete native host source, authenticated operator Principal,
scope and current signed cut. Each authority record is resolved by its exact
five-field artifact header from the selected current source, with original body
bytes, carrier, native validation and privacy checks. Source and selection guards
run before and after reads. Unadmitted and historical sources are refused.

The join keeps five concepts distinct: active human Principal, active Role
Assignment, Authority Claim, Authority Boundary and Decision Scope. An assignment
binds the Principal's exact stable subject to the Role. Separate claim/boundary
permissions must select the exact effect; exclusions win. The boundary must bind
that exact Principal, Role and scope and be recognized by the Principal. Every
target identity/version, kind and operation must fit the Decision Scope.
No wildcard or alias is inferred. Claim limitations are retained as unresolved constraints; no live authority is
verified. Unknown boundary period descriptions fail closed.

A consistent join still returns `authority_basis_verified: false` and
`live_authority_verified: false`. It reports the original assignment and claim
basis references for later resolution. Current artifact presence and possession
of a configured key do not prove that those original basis Decisions grant the
requested live effect. In particular, this package does not change the Role
Assignment schema's candidate status or turn local candidate source eligibility
into canonical authority.

The 49 checks use original schemas and synthetic authority records, plus real
temporary private files. They qualify those joins and file checks. They do not
qualify a successful native owner-source journey, a public `checkpoint.resolve`
handler, human identity, conversation interpretation or an actual owner outcome.
Operator signatures still use the preceding checkpoint rules kernel. Conversation
and existing-exact-authority provenance adapters, original basis-Decision
resolution, policy integration, durable outcome recording, retry/recovery and
Validation Report generation remain required before public handler qualification.


The v1 failed run is retained: five errors, no failed assertions, in 38 cases.
The fixture wrongly removed mandatory limitations/exclusions and attempted to
validate an external Source Cut reference without its original storage resource.
Version2 retains nonempty original-schema limitations and exclusions, reads the
exact original storage Source Cut contract, and reports the limitations as
unresolved. No original schema is changed. Thirty-seven original test bodies
remain unchanged. The limitations test now checks retained constraints and
withheld authority. Five extra checks validate the original fixture before any
mutation, Source Cut hashes, hard links, directory privacy and duplicate keys.
Negative joins assert that they reach their intended semantic checks instead of
passing accidentally at an earlier unrelated schema refusal.


Version3 separates the artifact header's storage scope from the Role Assignment's
authority domain. Principal registry, claim, boundary and Decision Scope bodies
may retain their own semantic domains. The independent owner selection names the
storage scope and each assignment domain explicitly. Each selected target must
belong to that assignment domain; authority does not spread across domains merely
because targets share a storage namespace. All 43 prior test bodies are unchanged;
six cases check these distinctions. Exact target-to-core/package coupling still
requires composition with the checkpoint rule kernel; selected target text alone
does not authorize anything. Version2's passing evidence remains preserved.
