# Lesson selection through the Lab API

Status: candidate implementation contract. Public handler integration and runtime
qualification remain pending. This package supplies no governing Definition,
owner outcome, operational scope grant or admitted Artifact Type.

## Original contract

`lesson.select` consumes the original Context Query and returns the original
Lesson Selection. It selects lessons for a bounded Assignment, resolves the active
Session through authenticated transport, and reports selected, omitted and blocked
revisions with reasons. Selection supplies no Application or effectiveness claim.

The existing W06 implementation checks exact reviewed lesson bytes, source head,
scope, expiry, family, source version, exclusions, current instruction precedence,
counterevidence and incompatible influences. Its source repair example is a
specific controlled use. Its hardcoded retention policy, review disposition and
repair family do not define every future Lab lesson.

## Composition

1. Select the actual Service and MachinePeer through the existing authenticated
   transport. Independently select its live Agent/Session resource, Assignment,
   accountable Principal, original source cut and disposal hook. A request Actor
   or reconstructed Session record cannot replace those objects.
2. Add a declared successor read policy for `lesson.select`. Preserve all old
   policy variants and their exact operation sets. The new policy independently
   selects the owned routing object. A Machine peer may inherit this read only
   when its actual parent policy explicitly includes it; its action budget stays
   zero. Typed candidate mutation remains a separate permission obligation.
3. Resolve the original Context Query through current signed source facts and
   existing eligibility rules. Compare Assignment, Work, Coordination Context,
   Actor, exclusions, current cut, expiry and budgets. This read neither renews an
   Assignment nor restores an expired or disposed Agent.
4. Enumerate the complete current signed Lesson catalog through declared carrier
   semantics as well as projected kinds. Resolve exact original record bytes and
   carrier contracts. An unresolved current Lesson blocks closure; an empty result
   is valid only when the verified complete inventory contains no current Lessons.
5. Select each exact review, applicability rule, retention and counterevidence
   witness through independent owned routing bindings. Require a bijection with
   the complete inventory. Explicit null records a missing review or rule; it
   blocks that lesson and supplies no substitute evidence. Validate exact Lesson
   revision, original body digest, scope and source cut; no wildcard, caller rule
   or candidate shadow is accepted.
6. Evaluate existing W06 selection conditions through an explicit successor
   domain profile. Retain the original controlled profile and all its tests. A
   general profile declares its supported statuses, retention and reviewed-use
   postures explicitly. Unresolved applicability or expiry blocks selection;
   expired and explicitly excluded lessons are omitted. Conflict pairs block
   both otherwise applicable influences. Evidence and counterevidence persist in
   Project State even when the lesson is omitted.
7. Produce the unchanged Lesson Selection and exact check evidence. Complete
   original source and live permission exit guards before exposing the result.
   Evidence materialization, when needed, is confined to the authenticated owned
   workspace and gives no domain admission or Application. Preserve the branch
   head, source archives, original records and actual Session memory boundary.
8. Dispose all transient rule/selection working state with the Session. Durable
   continuity consists of Project State exposed through Context and Ontology
   Views, original lesson/review evidence and source provenance.

## Verification obligations

Retain every W06 condition and original test. Qualify the actual API transport and
source composition with an empty catalog and a nonempty signed catalog. Cover
selected, expired, excluded, unresolved, instruction-conflicting and mutually
conflicting lessons; counterevidence and exact review/source identity changes;
missing/extra routing witnesses; source or permission changes at either boundary;
Actor spoofing, foreign Assignment/Session, revocation, expiry and disposal.

The existing current source has no current Lesson. Its empty result alone cannot
qualify the nonempty path. Synthetic applicability tests supply no genuine owner
review or causal benefit. Actual controlled fixtures and their scope remain
distinct from genuine R05 participant evidence and the final R08 outcome.

## Internal contracts

The routing, applicability and domain profile schemas are closed candidate runtime input
contracts. They are not new public API schemas or new canonical Artifact Types.
Their content identities must be selected by the actual read policy and verified
against current source facts before use. Schema validity grants no authority.
