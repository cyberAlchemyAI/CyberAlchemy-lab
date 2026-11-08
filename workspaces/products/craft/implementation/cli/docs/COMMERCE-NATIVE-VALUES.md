# Commerce native value codecs

This candidate component generates bounded data codecs from the captured Alch
business model. The application author supplies business types and requirements;
the component reuses their compiled record invariants and collection Rules. It
does not accept an application-written validation function.

`generateCommerceValueCodecBundle(stage, source, domain, baseline)` requires
genuine, current Core stage and computation-domain parents from the same original
source capture. It emits `commerce-domain-values.ts` and
`values-and-codecs.ts`, plus their source identities and member hashes. The first
file contains direct generated functions for the source's pure declarations and
invariants. The second implements the closed data boundary. These are component
assets; a selected application/profile native capture is a separate requirement.

## Using a source type

After materializing and compiling the two sibling files, a caller can use the
generated codec factory:

```ts
import {createCommerceValueCodecs} from './values-and-codecs.js';
const codecs = createCommerceValueCodecs();
const line = codecs.schemaForType('Shop.Values.QuoteLine');
const encoded = codecs.encodeCommerceValue(line, {
  sku: 'SKU-1', quantity: 2n, unitPriceMinor: 1200n,
});
if (encoded.ok) {
  // {"quantity":"2","sku":"SKU-1","unitPriceMinor":"1200"}
  const decoded = codecs.decodeCommerceValue(line, encoded.value);
}
```

`quantity: 0n` fails the source invariant. Unknown fields, missing fields and
JavaScript numeric representations of UInt64 fail validation. A successful data
decode does not establish authentication, permissions, transaction membership,
event delivery, or trusted context ownership.

## Representations and integration

| Value | Native data | Public canonical JSON |
| --- | --- | --- |
| UInt64 | `bigint` in the inclusive 0–18446744073709551615 range | Canonical unsigned decimal string |
| Bool | `boolean` | JSON boolean |
| Optional | `{kind:'none'}` or `{kind:'some',value:…}` | `null` or the declared element |
| Nullary enum | Declared variant name | Declared wire string |
| Payload enum | `{kind:VariantName,…declaredPayload}` | `{kind:WireVariant,…declaredPayload}` |
| Record | Exactly the declared fields | Exactly the declared fields |
| Bounded list | Dense array | JSON array |

The existing computation component uses its own explicitly typed wire payload
representation, `{tag:WireVariant,fields:{…}}`. The native data codec provides
`decodeComputationValue` and `encodeComputationParameters` to bridge that boundary.
Its public canonical identity remains the flat `kind` representation fixed by
`examples/ecommerce-target-candidate/contracts/context.json`. These forms must
never be interchanged by serializing arbitrary JavaScript objects.

`schemaForCallableArguments` and `schemaForEntryArguments` derive exact argument
packs from the captured source. They validate only the declared public/business
arguments. They neither acquire operation arguments nor fabricate private
Customer, Worker, Service, transaction, or native handles.

`checkCommerceSchema` accepts only a schema with the exact original source value
universe and a supported source-derived root. Handles belong to their generating
factory; cloned handles and handles from another factory are rejected.

## Boundary and size rules

The codec rejects proxies, accessors, functions, cycles, class instances, symbol
properties, non-enumerable fields, sparse arrays and additional array properties.
It copies typed-array bytes through intrinsic accessors without calling caller
constructors. Shared buffers are rejected. The parser rejects malformed UTF-8,
BOMs, duplicate decoded member names, trailing values, malformed JSON and JSON
numbers. Input bytes, node count, depth, fields and list counts are bounded.

Encoding sorts source field names, emits UInt64 strings, and emits every C0
control as a six-byte lowercase `\u00xx` escape. Strings retain their exact Unicode
scalar sequence without normalization. Exact finite refinement patterns affect
canonical maxima; unrestricted strings include their worst-case control escapes.
Composite maxima include all field names, punctuation, list elements and variant
payloads. A root whose bound cannot fit the fixed component value budget is
unsupported. Ambiguous nested optional wire encodings are unsupported.

Data errors use the closed `InputType`, `InputBound`, `InvalidUnicode`, and
`OutputBound` failure codes with path and byte-offset fields. Contract/foreign
handle errors are separate from a value failing its declared schema. A byte
offset is precise for parsing/UTF-8 failures; failures after typed decoding use
offset zero because they concern the decoded value.

## Evidence and limits

`test/commerce/commerce-native-values.test.ts` materializes and executes the actual
source-generated components. Controls cover original source types, malformed and
hostile values, fixed bounds, collection Rules, and native calculation adapters.
EC09 evidence is under
`implementation/craft-alchlang-commerce-2026-10-16/evidence/EC09/`.

Standalone components do not continuously watch the original source tree. Their
source-bound generation and immutable member identities must be joined to the
real component/native capture before use by selected profile owners. Full
installed application capture/replay remains EC12 and whole-slice observations
remain EC13/EC23/EC33. This document does not claim those tasks are complete.

## Open Questions

The source/native identity, event and clock components are documented in
[COMMERCE-NATIVE-IDENTITY.md](COMMERCE-NATIVE-IDENTITY.md). Their genuine source
callsite and physical component custody remains distinct from a selected native
basis, original application invocation, private authentication context, commit or
delivery. Those joins and the whole application observations remain the original
later plan tasks. Codec validity cannot substitute for their owners. Local
hosting, TDE, EVF and publication stay deferred.
