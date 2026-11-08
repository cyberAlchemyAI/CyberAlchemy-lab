# Entity, Value Object, Enum and Mapping

These examples run the actual generated TypeScript functions. They require the
`domainspec.reconciled-typescript/v1-candidate` compilation profile selected by
`../selections/typescript.json`, module root `commerce-corpus`, and the exact
unsigned 64-bit value profile `domainspec.typescript-exact-uint64/v1`.

The source is `../source`: `domainspec.project/v1` JSON with typed node contracts.
This example qualifies that Craft invocation path. It does not claim that every
AlchLang profile exposes identical construction bindings. The old AlchLang
`domainspec-1.0.0` starter demonstrates Entity/Value Object declaration formation
and has a narrower supported surface. Generated code performs execution and
validation; these examples make no formal proof claim.

From the installed example directory, use the shared `meta-types/run.mjs` runner
when present. The component alone accepts already compiled JavaScript:

```sh
node meta-types/data.mjs /absolute/compiled-root /absolute/reconciled-commerce
```

The reusable entry point is `await runData({generatedRoot, exampleRoot})` from
`data.mjs`. The compiled root must retain `commerce-corpus/features/...` and an
ES module package envelope. The result records all 24 case groups. A failed
assertion exits unsuccessfully; it is never counted as a passing observation.

## Entity: a thing with an identity

`source/specs/commerce/nodes/customer.json` declares a Customer with required
`id: UInt64` and `name: String`. The profile selects its positive-identity Rule.
The generated module is
`commerce-corpus/features/commerce/src/domain/entities/customer.js`:

```js
const factory = createCustomerFactory();
const created = factory.create({id: '9007199254740993', name: 'Ada'});
if (!created.ok) throw new Error(created.failure_codes.join(','));
const customer = created.value;
customer.fields.id; // 9007199254740993n, preserving all digits
factory.transition(customer, {id: '9007199254740993', name: 'Updated'});
```

`create`, `reconstruct` and `transition` return a result with `ok`, `value`,
`failure_codes` and `trace`. Invalid shapes return `INVALID_FIELDS`; identity
zero fails `commerce:positive`. A transition cannot change the identity and
returns `IDENTITY_CHANGED` when attempted. `sameIdentity(other)` compares
validated snapshots by identity, even when their names differ. It does not mean
all their fields are equal.

An Order requires validated Customer, Money and Choice values for its owned
fields. In contrast, its `billing_customer_id` is an explicitly bound identity
reference to `billing:customer`. A scalar `'99'` normalizes to `99n`; construction
does not fetch a Billing Customer or verify that it exists in external storage.
Missing required fields, leading-zero/negative/fractional identities, unsafe
JavaScript numbers and unvalidated owned components are tested rejections.

## Value Object: a validated value with content equality

`source/specs/commerce/nodes/money.json` declares Money with required
`quantity: UInt64` and optional `note: String`. The selected factory binds the
`commerce:positive` invariant to quantity. The generated module is
`commerce-corpus/features/commerce/src/domain/value-objects/money.js`:

```js
const factory = createMoneyFactory();
const left = factory.create({quantity: '3'});
const right = factory.create({quantity: 3n, note: null});
left.value.equals(right.value); // true, after checking both results are ok
```

An absent note normalizes to `null`; an empty string remains a distinct value.
The factory enforces the invariant on both creation and reconstruction.
Quantity zero returns `RULE_FAIL:commerce:positive`; missing quantity and a
non-string note return `INVALID_FIELDS`. Equal normalized fields produce equal
values and hash keys. A raw object with similar fields is unowned and is not an
equal validated snapshot. The hash is an equality key, not a cryptographic
integrity guarantee. Fields and snapshots are frozen.

## Enum: a finite choice, optionally carrying a value

`priority.json` declares payload-free alternatives `Normal` and `Urgent`.
The generated `domain/enums/priority.component.js` exports
`PriorityValueComponent.fromVariant('Urgent')` and `.values.Urgent`.
Unknown names or non-string alternatives throw `INVALID_ENUM_VARIANT`.

`choice.json` declares `None` and `Some`, where Some contains validated Money.
The generated `domain/enums/choice.sum.js` exports `ChoiceValueComponent`:

```js
const none = ChoiceValueComponent.create({variant: 'None'});
const some = ChoiceValueComponent.create({variant: 'Some', payload: money});
```

The payload must be a Money snapshot from `createMoneyFactory`; a plain record
is rejected with `UNOWNED_COMPONENT`. Unknown alternatives, missing payloads,
and payloads attached to None are rejected. `.equals(a, b)` includes both the
alternative and its validated payload contents.

The examples demonstrate explicit caller serialization. A payload-free case
serializes its `variant`; a Money payload encodes `quantity` as a decimal string
and then recreates it through the Money factory when decoding. There is no
claimed automatic serializer for arbitrary snapshots or native bigint JSON.

## Mapping: explicitly project supplied inputs

The generated `application/mappings/summary.js` exports
`mappingSummary({order, net, fee})`. The inputs are ordinary typed records and
explicit scalar results, rather than factory snapshots. Passing the example
Order and net `'93'`, fee `'5'` returns `{id: 1n, net: 93n, fee: 5n}`. Swapping
net and fee swaps those results: the Mapping does not infer a hidden Calculation.
Its source uses `domainspec.typed-mapping/v3` and an explicit Interface result
binding. Missing outer arguments throw `MAPPING_INPUT`; its current reused
structured scalar normalizers report `RULE_INPUT` for malformed nested values.

`mappingIntegrationOutbound({order: '99'})` takes a scalar identity reference,
not `{id: '99'}`. It returns `{id: 99n, name: 'integration'}` without fetching an
Order. Its source uses `domainspec.typed-mapping/v2`.

Two small v2 mappings complete the partial/default examples:

- `partial-money.json` generates `mappingPartialMoney({money})`. It deliberately
  returns only `{quantity: 3n}`, even if the supplied Money record has a note.
- `default-money.json` generates `mappingDefaultMoney({money})`. A missing or
  null note becomes `'unspecified'`; an empty or present string is retained.

Both validate supplied input shapes. Partial output does not make required input
fields optional. Missing quantity and a wrongly typed note are rejected with
`MAPPING_INPUT`.

A Mapping does **not** call the target Value Object factory. Projecting quantity
zero succeeds as a shape transformation, produces an unowned record, and is
then rejected when explicitly passed to `createMoneyFactory().create(result)`.
The user must choose that construction step where domain validity is required.

## Open Questions

Installed-package integration and exact package identity are owned by the shared
`meta-types` runner and the execution qualification record. Public installation,
publication and platform claims are separately qualified. Additional AlchLang
profiles and Python/Rust targets require their own equivalent observations.
Local hosting, TDE and EVF remain deferred.
