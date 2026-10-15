K02 owned qualifier lookup — captured meaning and remaining trust boundary

This package implements revisioned Intent Resolution qualifier lookup and canonical
addressing-role lookup from independently captured binding catalogs. The executable
check pins the complete resolved Resolution to the projected source, the resolved
Role to the typed claim and owned Selection, and both binding captures and Selection
to the exact full frame. The complete source decoder and authentic provider are
still separate unfinished work.

A binding record retains its own revision, source-kind label, token, complete typed
target, frame, original binding-record bytes and owner-review reference. Catalogs
retain records and separately issued roots. Independent CatalogMeaning requires
exact root membership, nonempty tokens, matching fixed record kind/frame, immutable
binding-record revisions, functional token-to-value mapping and immutable target
values at each target revision key within that typed target catalog. The checker
is proved equivalent to this predicate rather than used to define it.

Multiple distinct approval records for one token are permitted if they resolve to
the same complete target. Identical retries and consistent aliases are permitted.
The lookup returns the target value, so choosing an earlier consistent approval
cannot change the result. Conflicting aliases, changed target digest/body, conflicting
binding bytes and stale/missing roots refuse. This avoids requiring one approval
record per token when the intended meaning only requires one unambiguous value.

Resolution and role bindings have two fixed candidate record kinds. The joint guard
embeds complete binding records into a tagged union and checks their canonical
revision keys across both catalogs, including roots. A revision cannot name both
kinds with different token/target/body/bytes/review data. A concrete regression shows
both individual typed catalog checks can pass while their joint revisions conflict;
the composed qualifier checker refuses. This guard concerns binding-record identity.
It does not require the targets' semantic reference values to be unequal, and a
positive control preserves that distinction. Authentic full source/entity catalog
correspondence remains an explicit policy/provider requirement.

For roles, the raw addressing_role token must equal the owned canonical role code,
matching the existing Addresses and SourceInterpretation contract. Resolution aliases
are supported. A different role-token alias is currently unqualified even when its
binding reaches the same Role. Supporting role-code normalization would require a
reviewed contract/profile revision, not silently weakening the exact-code join.
This is a candidate profile limit, not a mathematical prohibition on aliases.

Successful lookup yields independently stated captured resolution/role meanings,
nonempty tokens, exact endpoint kind, owned Selection role and full frame. Candidate
ResolutionTokenMeaning and AddressingRoleMeaning additionally require independently
supplied catalog-authenticity propositions. The checker cannot produce those proofs.
These are structural interpretations under captured roots, not an authenticated
realization of the nineteen SourceInterpretation policies. An arbitrary authenticity
predicate could be vacuous; no such concrete realization is supplied or accepted.

Four positive cases cover the original token, an alias, two distinct consistent
approvals and identical retries. Nineteen controls cover missing roots/tokens, empty
tokens, wrong kind/frame/role, alias and revision conflicts, source-body substitution,
role-code mismatch, changed Selection role, cross-catalog conflicts and shared target
reference values. Seven synthetic typed branch cases cover all six allowed source
kinds and refusal of other. They reuse fixture references with assigned typed kinds;
they do not prove actual entity kinds from prefixes or authenticate the World.

Limitations: binding-record byte parsing and byte/body correspondence are unproved;
synthetic binding bytes and review roots are used by the fixture. Root authenticity,
typed World/Selection capture, schema/lifecycle/evidence/challenge/successor/companion/
claim policy realization, public unknown/unsupported diagnostics, complete source
composition, complete-rule effect closure, complete-theory countermodels and mandatory
independent checking remain open. This component takes a Projected input; it does not
itself decode and authenticate that input from original source bytes. The public source
checker must compose the verified metadata/payload projection before using this join.

All seven K02 inherited IDs and all 263 successor pending IDs remain pending. The
nineteen source policy obligations are not replaced by these captured consistency
proofs. Original 90 discharges and R06/G4 acceptance retain their original scope.
K04 remains the current one-at-a-time meaning review; no new owner acceptance is
recorded. Only fresh pinned compilation/replay plus matching-phase import audits
qualify this package for the candidate proof index. No independent checker is implied.

Verification result: all 45 new declarations pass 66 fresh pinned compiler/replay
invocations, 500 declaration axiom inspections including imported dependencies,
and all 66 matching-phase import-resolution audits. The total includes eleven
generic/joint catalog lemmas, four checker/bridge lemmas, four positive fixtures,
nineteen controls and seven branch cases. Total compiler time was 294.085 seconds;
the slowest module took 34.653 seconds. These are compilation/elaboration timings,
not a supported runtime envelope. Preparation failures and the stopped run before
the joint binding revision guard are preserved under repair-attempts and contribute
no registered evidence. Authenticated policy realization, whole-source refinement,
independent checking and inherited discharges remain unproved.
