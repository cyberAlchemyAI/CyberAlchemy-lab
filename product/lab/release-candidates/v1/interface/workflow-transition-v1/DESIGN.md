# Workflow transition kernel candidate

The kernel validates one exact transition from an independently selected workflow
definition and run. Schema validity and supplied authority/satisfaction reports
do not replace the actual host's independent grant or authenticated Actor.

The host grant binds the original run, definition, authority evaluation,
satisfaction report, action receipts, named obligation evidence, source cut,
principal, role, permitted transition and actual validity period. Every selected
input/reference must be current and in that exact scope. Named checks must pass
and match their independently selected original evidence. Unknown states,
terminal transitions, unbound input carriers and incomplete obligations refuse.

Planning produces a next candidate run and event. It never reports application,
completed Work, successful Product outcomes, canonical admission or activation.

## Actual coordination persistence

An explicitly created owned `/tmp` journal stores one immutable transaction
containing original next-run bytes and the transition event. A recoverable head
pointer selects the committed sequence. The exact original planned claim is
retained and checked during replay.

An exact retry returns the committed event without new writes. An interrupted
claim is never redispatched, even through another idempotency key. Recovery can
observe an already written exact transaction and repair its head pointer; it
cannot invent a missing effect. Source/authority guards run around writes.

## Current integration ceiling

This package supplies a transition kernel and owned journal, not an added public
API handler. A subsequent actual Service/ReaderChannel adapter must independently
select grants and evidence, close coordination/intent/current record semantics,
manage output producers and privacy, and construct the closed API receipt.
All 34 original operation contracts and 46 plan tasks remain requirements.

The component fixtures are explicitly isolated schema-valid witnesses. They do
not represent a current signed Lab source, actual Agent, human owner response or
production authority. Actual owned journal tests prove local persistence,
replay/retry/recovery for these witnesses only.
