# Local candidate CLI and outcome contract v1

The executable integration belongs to R04. This document freezes the interface
it must implement. Existing standalone inference CLIs remain predecessor tools;
their `accepted` fields are adapted into this richer result, never treated as
aggregate readiness. No HTTP server or governance admission is provided here.

| Command | Inputs and exact identities | Supported scope | Result and failure behavior |
| --- | --- | --- | --- |
| `relation-checker check-instance REQUEST [--profile ID]` | Strict JSON request bytes, captured registry/source/profile and toolchain hashes. | Accepted F0 three-kind semantics, or explicitly selected registry structure. | Return checker findings and scoped obligations. Structural coverage of 41 kinds does not imply their full semantics. Malformed input is not-run; unsupported semantics remain unsupported. |
| `relation-checker check-extension PROPOSAL [--bundle BUNDLE]` | Before/after registry, graph and rule identities, complete independently generated policy, optional source-bound evidence bundle. | Named L2 structural profiles and the G3 captured fresh-head/old-body rule profile. | Compute obligations even when evidence is missing. Distinguish selected-data compatibility, invariant preservation and model conservativity. Missing/stale/unsupported obligations prevent readiness. No G2 pass substitutes for G3 rule evidence. |
| `relation-checker check-proof SUBMISSION` | Exact obligation ID, trusted required statement and definition closure, submitted theorem ID/source bytes, toolchain/import/isolation policy. | Proof-language and theorem environments explicitly selected by R02. | Independently check the full required type and transitive axioms. A compiling proof of another statement is invalid evidence; it does not disprove the required theorem. Replay failure is unknown. |
| `relation-checker replay-evidence BUNDLE` | Exact bundle bytes, selected proposal/baseline/profile, proof/model/checker artifacts and full semantic/runtime dependencies. | R03 independently verified bundles with complete required obligations. | Recompute identities and replay checks before aggregation. Edited labels, omitted obligations and changed dependencies cannot inherit readiness. A later timestamp does not repair stale bytes. |

All paths refer to local approved workspace artifacts. Resolve roles and actual
bytes independently; do not fetch arbitrary URLs or accept an upload label as
proof authority. Input parsing rejects duplicate JSON keys, nonfinite numbers,
invalid UTF-8 and unpaired surrogates. Unknown fields and versions are rejected
at the applicable profile boundary. Original bytes determine file digests.

Each command emits one UTF-8 JSON outcome to stdout. Human explanations identify
the cause, relevant input location, obligation and next corrective action.
Provider logs remain separate artifacts. Diagnostics must not substitute raw
stack traces for explanations or expose unrelated environment/credential data.

The outcome separates these dimensions:

1. **Execution:** completed, not-run, timeout, unavailable or provider-error.
   Completed means the operation ran, not that its obligation passed.
2. **Currentness:** current, stale or unresolved, determined by actual dependency
   comparison before and after execution. Client `current: true` is not evidence.
3. **Evidence:** verified-checker, kernel-proof, checked-model-witness,
   bounded-search or none. Every obligation retains its own method; an aggregate
   may contain several methods. Finite witnesses cannot discharge a universal
   conservativity theorem. No-witness search cannot become a theorem.
4. **Obligation verdict:** satisfied, violated, unknown, unsupported or not-run,
   against an independently selected complete required statement and scope.
5. **Readiness:** ready-for-review, blocked, unresolved or not-applicable.
   Only completed, current, allowed evidence satisfying every hard obligation can
   yield ready-for-review. No outcome performs an actual authority transition.

All reported hard obligations must belong to the independently generated set.
Readiness aggregation checks exact IDs, uniqueness, missing and unresolved IDs,
not merely the entries a submitter chose to provide. The JSON schema prevents
several inconsistent labels; it cannot establish mathematical truth or compute
the policy inventory. R02/R03 must perform those independent semantic checks.

The three compatibility dimensions are always distinct fields:
`selected-data-compatibility`, `invariant-preservation`, `model-conservativity`.
For commands where a dimension is irrelevant, use not-applicable. An extension
ready-for-review requires all three verified-for-named-scope, with general
theorem evidence where required. Rule conservativity also retains its separate
required I06 statement and model interpretation boundary.

Exit codes are a CI summary; the JSON outcome is authoritative for the separate
dimensions. Use this precedence when several conditions apply:

| Code | Meaning |
| --- | --- |
| 2 | Invalid input; command not run. |
| 6 | Provider timeout; obligation remains unknown. |
| 5 | Required provider or isolation environment unavailable. |
| 8 | Provider/internal execution failure. |
| 7 | Relevant baseline, proof or semantic dependency stale. |
| 3 | Selected meaning/profile unsupported. |
| 1 | A completed supported check shows a violated requirement. |
| 4 | Required evidence missing or unresolved. |
| 0 | Completed/current allowed checks satisfy the selected required inventory. |

Code 0 for check-instance or check-proof means scoped validation, with readiness
not-applicable. Code 0 for an extension/bundle review requires ready-for-review.
Ready-for-review is a bounded candidate recommendation, not admission approval.

The frozen draft `provider-result`, `obligation-result` and `review-report`
contracts already distinguish execution, currentness, method and verdict. This
local successor adds command/profile identities, local file bindings, explicit
compatibility dimensions and not-run execution. An adapter maps local bindings
to artifact-store exact references only after checking actual bytes/roles.
Historical theorem-only FormalClaim/evidence bindings retain their meaning:
use explicit successor/adapter records for finite model or bounded-search
evidence. Never relabel either as a universal theorem or silently modify legacy
ownership. R02 defines the concrete accepted proof language and isolation.

Retained trust includes source meaning, parsing/hashing, host runtime and OS,
toolchain and independently supplied assessment truth. The unary Conforms
projection and candidate epoch from I06 remain scoped abstractions. All 263
inherited source-semantic obligations remain visible outside the named claim.
