K02 source interpretation contract and complete-frame join

This package specifies a candidate independent SourceInterpretation contract and
implements two executable components: a closed qualifier-object decoder and a
join from a projected source to the typed K02 claim. The contract is conditional
on semantic-policy and provider proofs. No concrete realization of those policies,
byte parser or authentic provider is supplied. Whole-source refinement remains
unfinished; the contract must not be used as evidence that those premises hold.

The qualifier object has exactly intent_resolution_ref and addressing_role, both
strings. An independent object-entry denotation is proved equivalent to decoding.
Missing, extra, duplicate and wrongly typed fields fail before token interpretation.
Unique field order may change. Empty strings can be parsed as strings; the source
contract separately requires both interpreted tokens to be nonempty. Decoding a
qualifier object does not resolve a reference or authorize a role.

The new FramedWorld pairs the previous typed World with its complete expected
frame. The previous World stores profile, context, scope, snapshot and time domain,
but no epoch. Its Addresses predicate ties the Selection's subject and target to
its endpoints and checks seven frame dimensions overall. It does not constrain
Selection.frame.epoch. The composed Joined meaning therefore requires the whole
Selection frame to equal FramedWorld.frame and checks the World's stored dimensions
against that frame. It also requires the typed claim's complete Resolution to equal
the independently projected source Resolution. This uses existing Addresses and
all six source branches without changing the previously verified fragment.

The concrete regression changes only the Selection epoch from 42 to 41 and updates
the owned Selection catalog to contain that exact changed Selection. The previous
fragment passes every check. The new composed join refuses it. This isolates the
epoch gap rather than failing because the Selection was absent from the catalog.
A matching original frame still passes.

The candidate source contract combines:

    independent metadata/payload projection meaning
    + independent closed qualifier meaning
    + complete typed source/claim/frame join
    + nonempty exact qualifier interpretation
    + nineteen explicit semantic-policy/provider obligations.

The policy interface covers authentic typed World capture, owned Selection meaning
and payload-to-World correspondence; authentic metadata and payload capture;
byte-to-AST parsing; schema revision correspondence; typed identity; owner/scope
entitlement; complete source/review provenance; lifecycle; evidence; challenge;
successors; companion relations; claim ceiling; typed payload roles; resolution
token interpretation and addressing-role interpretation. These are propositions,
not request-controlled boolean approvals. Nevertheless, an arbitrary realization
with predicates that always hold would be vacuous. No such realization is supplied
or accepted. Correct concrete policy definitions, provenance premises and their
owner assessment remain required before any whole-source or inherited claim.

All fourteen source fields are accounted for. Name remains a preserved nonempty
description in the AST/body denotation. Authority_effect is structurally constrained
to none; whole-rule protected-state preservation is still a separate requirement.
The remaining fields enter the projection or the explicit policy predicates.
No field label establishes ownership, successful execution or a physical fact.
The typed World must itself have authentic provenance: authentic metadata/payload
alone would leave room for a fabricated typed Selection or endpoint kind.

The contract proves that a complete interpretation entails successful component
checks. The converse additionally requires all policy proofs, typed-world/Selection
correspondence, nonempty token interpretations and exact role code. The executable
component checks alone cannot discharge those conditions. A synthetic rejecting
policy fixture demonstrates matching source projection, qualifier decoding and
frame join while the complete contract is false. This is a logical counterexample
to conflating structural success with full source meaning, not a deployed policy.

Limits remain: byte-to-AST translation, concrete policy realization, authentication,
owned qualifier lookup and catalog consistency, actual Selection/source refinement,
whole-theory countermodels, rule-effect closure and mandatory independent checking.
The concrete fixture covers the project branch; the join's theorem is generic over
all existing typed branches, but full source adapters for all six branches are not
implemented. The contract has not received a new semantic-owner assessment. K04 is
still the current one-at-a-time human review, and global policy review remains open.
Every inherited K02 ID and all 263 inherited successor IDs remain pending. Original
90 discharges and original R06/G4 acceptance retain their existing scope.

The verification result is authoritative only after fresh pinned Lean compilation,
separate fresh replay, per-declaration axiom inspection and matching-phase import
resolution audits pass. No independent checker is represented by these runs.

Verification result: all 30 new declarations pass 56 fresh pinned compiler/replay
invocations, 432 declaration axiom inspections including imported dependencies,
and all 56 matching-phase import-resolution audits. This includes eleven qualifier
controls and seven positive/regression/provider-boundary fixture proofs. The slowest
module took 37.675 seconds; total compiler time was 470.006 seconds, including
elaboration rather than a production runtime measurement. The initial unused-simp
warning and explicitly stopped run before the typed-world contract correction are
preserved under repair-attempts. Neither contributes registered proof evidence.
No concrete source policy realization, whole-source refinement, inherited discharge
or independent checking is claimed.
