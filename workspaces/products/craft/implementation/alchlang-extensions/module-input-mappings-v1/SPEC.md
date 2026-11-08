# Module input mappings prototype

A module integration accepts `input input.path` or `input MappingName`. A named
Mapping must take no explicit argument and target the imported module's exact
qualified input record. Its fields may use input and earlier binding outputs.

Execution order: validate endpoint input; input-only assertions; each binding's
guard; if true, evaluate its Mapping in a fresh memoization scope; validate the
result against the imported input schema; invoke the module; validate its output.
False guards skip mappings and transport. Mapping errors stop later bindings.
Input schema failures use FUNCTION_MODULE_INPUT_SCHEMA before module-start.

DomainSpec checks ordered dependencies, exact Mapping output types, and guarded
output availability. Mapping evaluation assumes the binding's guard is true; it
cannot assume that an unrelated earlier guard held. Cycles and forward references
fail compilation. Node and Rust emit Mapping code, not AST interpreters.

The derived scaffold names input-mapping references and the exact typed binding
input contract. Traces include Mapping observations, binding-input readiness, and
binding-input-error failures before module-start. No new admitted meta-type.

Product example: checkout constructs Shipping.Request.request_id from the pricing
response and combines customer shipping preferences with an optional snapshot.
Checkout still validates pricing identity and shipping business outcomes.

## Open Questions

Deferred: Mapping call arguments on the integration clause, arbitrary input
expressions, asynchronous mappings, dynamic module selection, and input creation
from late bindings. Provider identity and deployment are separate operational work.
