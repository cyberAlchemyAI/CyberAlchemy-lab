# Lab history to an optional analytical report

## Source and target

Exact Lab ontology cut and review references -> Disposable RDF view and inert returned evidence.

## Direction and contract

Proposed: versioned export mapping, explicitly selected checks, result retained for Lab review.

Recommendation only: keep canonical history and approvals in the Lab. The analytical adapter must not write events, infer authorization or promote local edges to global connections.

## Testing and evidence

Version/digest substitution, unsupported qualifier, wrong kind pair, changed source cut and attempted effect escalation.

Retain: Lab cut/review binding, mapping/profile/tool identity, result bytes, omissions and no-effect posture.

Sources: [claim-preservation checks](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/projection_entailment.rs#L1); [consequence-change analysis](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/conservativity.rs#L1).

## Known gap

This adapter is not implemented. A faithful representation of Lab identities, lifecycle and global relation semantics still needs design and verification.
