# Typed module-input mappings

A module integration can use a named Alch Mapping as its input:

```alch
mapping ShippingRequest:
  target Shipping.Request
  field request_id = pricing.request_id
  field option_id = input.shipping.option_id
  field country = input.shipping.country
  field weight_grams = input.shipping.weight_grams
  field requires_tracking = input.shipping.requires_tracking
  field note = input.shipping.note

mapping ShippingInput:
  target Shipping.Envelope
  field request = ShippingRequest
  field snapshot = input.shipping_snapshot

integration ShippingPrice:
  transport module-local
  module Shipping
  input ShippingInput
  output Shipping.ShippingResponse
  timeout-ms 10000
  max-bytes 262144

result QuoteCheckout:
  bind pricing from ItemPrice
  bind shipping from ShippingPrice when HasPrice
  # Remaining assertions and result cases follow.
```

This fragment comes from the [complete checkout examples](../../alchlang-extensions/module-input-mappings-v1/README.md).
The same Mapping works with `module-http`; configure URL and token environment
references in the integration declaration. Existing `input input.path` bindings
retain their original behavior.

## Compilation

`input MappingName` must name a Mapping without an explicit argument. Its target
must be the imported module's exact input record, such as `Shipping.Envelope`.
Nested mappings construct nested records using ordinary Alch field expressions.
DomainSpec owns their type checking and generated Node/Rust code.

Bindings retain authored order. A Mapping may read the request and earlier
bindings, but cannot read its own output or a later binding. The binding's guard
is assumed true while checking the Mapping. Reads of earlier conditional outputs
require proof from that guard or from short-circuit predicates inside the Mapping.
Other earlier guards are not assumed true.

## Runtime

Execution proceeds through guard, Mapping, imported input-schema validation, and
module invocation. Each Mapping stage uses a fresh memoization scope. A false
guard skips both mapping and transport. Input mapping errors stop execution before
module-start. A mapped value that violates imported bounds, patterns, constants
or nullability fails with `FUNCTION_MODULE_INPUT_SCHEMA`; its type name alone
does not prove these runtime constraints.

The generated Node and Rust boundaries both validate mapped input before local
or HTTP invocation. Optional absent fields are omitted; explicit null is preserved
only where the imported schema permits it. HTTP POST bodies contain the mapped
input. This permits earlier results to supply values without ambient state.

Mapping observations retain their declaration/source information. `binding-input`
marks a validated argument; `binding-input-error` records mapping/schema failure.
A skipped binding has neither Mapping starts nor input-readiness events.

## Derived ontology

The result's typed binding records include the mapping name and imported input
type. An `input-mapping` reference connects the integration to the Mapping; normal
Mapping dependencies connect it to the source records and declarations it reads.
These remain compiler-derived scaffolds, without ontology admission.

Open questions: [candidate specification](../../alchlang-extensions/module-input-mappings-v1/SPEC.md#open-questions).
