# Commerce identity and clock components

The candidate identity component implements the eleven native producer methods
declared by the original commerce source. Business authors keep writing their
requirements and source expressions such as
`identities.commandId("payments.capture", orderId)`. The compiler resolves that
expression's signature, argument order, namespace, source location and service;
the profile supplies the finite native implementation.

The component produces data. An order ID does not prove an order exists. Event
metadata does not prove a transaction committed. A fingerprint does not establish
authentication, event delivery, or permission to perform an operation.

## From source to a native component

`createCommerceIdentityCallOwner` requires genuine current original source,
stage and computation-domain parents. Its `paths` and `bind` methods recheck an
exact Operation or Workflow plan against the captured source. Private factory
tokens retain the original expression, ordered parameters, source literals,
finite text domains, caller service and source span.

`eventFingerprint` resolves its Event type and version from the checked source
argument. The caller cannot supply a replacement qualified type or schema
version. `eventMetadata` retains checked record-event consumers and requires its
producer literal to match the source operation's target service. Caller service
identity and target service identity remain separate responsibilities.

`generateCommerceIdentityBundle` emits four TypeScript sibling files: the
source-compiled domain checks, closed value codecs, source-call identity model,
and the native `context.ts` implementation. An unknown primitive, changed ABI,
changed tuple domain or unsupported signature is rejected. Source descriptor
changes alone do not implement new native behavior.

`createCommerceIdentityComponentOwner` writes fresh component members with
exclusive creation and mode 0600, records their physical identities, and imports
the captured JavaScript with its fixed sibling dependency closure. It checks
current original source and native members around component evaluation. Its
private component and callsite tokens cannot be restored from JSON or hashes.
Failed materialization retains created files for inspection; an occupied file is
preserved.

The component API evaluates **already-bound parameter values**. It does not
evaluate the surrounding Operation, read private Customer/Worker/Service fields,
acquire a transaction, or translate component data into an authenticated context.

## Implemented producers

| Method | Identity content |
| --- | --- |
| `checkoutFingerprint` | Logical entry, customer and quote; checkout key belongs to replay scope |
| `newOrderId` | Entry/customer/checkout-key tuple, with `ord_` prefix |
| `commandId` | Source-selected command namespace and order, with `cmd_` prefix |
| `eventMetadata` | Producer/aggregate/version/ordinal occurrence, with `evt_` prefix; correlation and command remain record fields |
| `stockLinesFingerprint` | Canonical validated lines in original order |
| `stockCommandFingerprint` | Kind/order/lines and exact optional expected version |
| `captureFingerprint` | Attempt/order/amount/currency |
| `eventFingerprint` | Source-bound Event name/version and full canonical event content |
| `confirmedOrderFingerprint` | Nine immutable confirmed-order fields, excluding occurrence metadata |
| `orderActionFingerprint` | Confirm/cancel intent and exact optional cancellation reason |
| `clockEpochMs` | One checked native wall-clock observation |

Hashing uses the fixed `ordered-utf8-field-tuple/v1-candidate` encoding: the method
domain followed by each ordered field, each with a four-byte big-endian UTF-8
length. Total tuple size is bounded at 524288 bytes. SHA-256 hex is lowercase.
Unicode is neither trimmed nor normalized. Canonical JSON and UInt64 conversion
reuse the checked source value boundary; native numbers never represent UInt64.

Reserve requires an absent reservation version; allocate/release require a
present exact UInt64 version. Confirm requires an absent reason; cancel requires
StockUnavailable or PaymentDeclined. Source literals are preserved: a source call
for `payments.capture` cannot be supplied `inventory.reserve` just because both
namespaces exist in the native ABI.

The wall-clock asset captures the native `Date.now` function when loaded. Its
observation must be a safe, nonnegative integer before conversion to bigint.
No public time argument, clock callback, rounding or monotonicity guarantee is
provided. The surrounding source Operation still owns the requirement to read
once on the fresh path and skip clock capture on an accepted replay.

## Evidence boundary

`test/commerce/commerce-native-identity.test.ts` tests actual generated/captured
components and the unchanged independent EC03 identity vectors. EC09 evidence is
under `implementation/craft-alchlang-commerce-2026-10-16/evidence/EC09/`.

Internal generated data primitives are not the public
`IdentityContextNativeV1.createCommerceIdentityProducers` constructor. That shared
interface additionally requires a genuine original OperationInvocation and
checked native callsite with the actual selected profile/native epoch. This
component never manufactures those handles. The complete selected constructor
and effect integration remain required before claiming that interface works.

No hostile in-process isolation, production identity, collision-free theorem,
commit, rollback, remote delivery, or installed/public native qualification is
claimed by component success. Later persistence owners must compare the original
scoped tuple/content when a digest or ID collides; generating another key is not
a collision recovery policy.

## Open Questions

The EC09 source implementation and its genuine source/physical component
constructors are reconciled in its `CLOSURE-REVIEW-02.md`. Selected profile/native
composition and original invocation/private context owners must still join these
components without replacing them with data descriptors or callback guards.
Full installed capture is EC12; whole application observations remain
EC13/EC23/EC33. Formal claims remain optional. Local hosting, TDE, EVF and
publication stay deferred.
