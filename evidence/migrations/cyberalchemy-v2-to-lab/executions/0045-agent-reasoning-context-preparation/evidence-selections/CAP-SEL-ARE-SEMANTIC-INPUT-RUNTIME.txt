# Semantic Input Runtime (candidate)

This package is the production-shaped bridge from a verified Context Envelope
and an exact semantic-domain binding to the evaluator's frozen request. It owns
source selection, exact-byte provider verification, observation admission, and
structural entry eligibility. The semantic evaluator continues to own reduction
and `ReasoningReceipt` assembly. A new caller supplies a verified immutable
`are.runtime-journal-cut/v1`; the runtime seals its cut digest and sequence
range into the evaluator request. The legacy inline journal input remains only
for historical fixture byte compatibility.

Public operations:

- `loadSemanticInputProfile(profilePath, repositoryRoot)`
- `selectSemanticDomain(requestContext, routeDecision, profile)`
- `materializeSemanticRequest(input)`
- `composeSemanticLifecycle(input)`

Profiles and provider paths are explicit. The runtime performs no repository
discovery, model summarization, catalog construction, durable persistence, or
effect. A missing domain is `not-applicable`; ambiguous domains, stale exact
sources, missing ownership, or malformed providers block before evaluator
execution. Context definitions and ontology meanings remain bound context and
never become admitted observation facts.

The Codex wrapper owns and cuts the journal. Provider-supplied journal fields
are rejected, preventing observation providers from replacing lifecycle
evidence. Journal replay remains deterministic and external-call-free; no cut
or replay grants authority.

This candidate adopts no production semantic-domain catalog and grants no
admission, conformance, publication, deployment, or external-effect authority.
