# Candidate application ontology compiler

DomainSpec owns `src/application/compiler.ts`: semantic validation, core project
compilation and application artifact generation. The shared input schema is
`domainspec.application-ontology/v1-candidate`, with profile `bound-application-v1`,
declarations, source hashes, embedded core project files and authority_effect none.
JSON input is authored intent; it is not a signed semantic equivalence receipt.

The native commands are `application-check <absolute-json> --root <absolute-root>`
and `application-build <absolute-json> --root <absolute-root> --target-root
<absolute-output>`. Build rejects existing output and requires the authored output
path. The API exports loadApplicationOntology, checkApplicationOntology and
buildApplicationOntology. Neither the backend nor native CLI imports AlchLang.

Supported declarations: application, model, record, enum, adapter, operation,
route, request, query, normalization, lifecycle, projection, storage, configuration, view, ui and assurance.
Closed clauses, references, auth policies, routes, lifecycle states, storage field
coverage, source hashes, path containment and embedded core files are checked.
Core models are compiled with the existing DomainSpec compiler, then generated.

Artifacts include domain types/enums, HTTP dispatch/authorization calls, buffered
JSON request parsing and success-response guards, lifecycle/redaction functions, UI route/view/default
configuration, bound UI assets, raw ontology, compiled view and a hash manifest.
HTTP guards validate text and Buffer JSON before flushing deferred writeHead calls.
Streaming adapters are outside this buffered-response contract. Nested record and
unknown types retain their explicitly declared open content semantics.

Storage declarations bind existing schemas and migrations; no DDL is synthesized.
JSON request shape and bounded byte limits are generated from request declarations,
validated after authorization and cached for adapters. OAuth, crypto, persistence
IO, remaining domain-specific rules and rendering remain adapters.
Normalization declarations bind one request operation to text trim/truncate/minimum
length or optional positive-integer field rules. Unknown fields, incompatible
types, unknown rules, duplicate bindings and invalid bounds fail compilation.
Named nested records validate recursively; explicit record/unknown fields remain open.
Operation effects and assurance/test bindings are declarations, not automatic
execution, proof or authority. The existing frozen core catalog is unchanged.

The Body War v2 consumer tests byte-equivalent native/frontend output, live model
mutations, malformed/stale inputs, unit/API, PostgreSQL, browser and assurance flows.
Its evidence retains the complete obligation denominator and operational gaps.

Query declarations bind a GET operation to closed integer fields with authored
bounds and defaults. Unknown/duplicate parameters reject before handler calls.
Numeric conversion uses Number and requires a safe integer inside the interval.
Scalar unions allow explicitly named alternatives in record fields. Query/body
input conflicts, incomplete field coverage and invalid bounds fail compilation.

## Open Questions

Which application semantics should be promoted beyond this candidate profile?
Which remaining adapter effects, request/stream contracts and proof providers
should receive stronger executable bindings?
