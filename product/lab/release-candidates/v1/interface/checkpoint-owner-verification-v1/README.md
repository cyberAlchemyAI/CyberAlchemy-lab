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
No wildcard or alias is inferred. Nonempty claim limitations and unknown boundary
period descriptions require an independent semantic adapter and fail closed.

A consistent join still returns `authority_basis_verified: false` and
`live_authority_verified: false`. It reports the original assignment and claim
basis references for later resolution. Current artifact presence and possession
of a configured key do not prove that those original basis Decisions grant the
requested live effect. In particular, this package does not change the Role
Assignment schema's candidate status or turn local candidate source eligibility
into canonical authority.

The 38 checks use original schemas and synthetic authority records, plus real
temporary private files. They qualify those joins and file checks. They do not
qualify a successful native owner-source journey, a public `checkpoint.resolve`
handler, human identity, conversation interpretation or an actual owner outcome.
Operator signatures still use the preceding checkpoint rules kernel. Conversation
and existing-exact-authority provenance adapters, original basis-Decision
resolution, policy integration, durable outcome recording, retry/recovery and
Validation Report generation remain required before public handler qualification.
