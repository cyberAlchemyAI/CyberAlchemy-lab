# Complete Value family

This candidate-local family proves a portable Value Object construction contract from
an owner-authored definition and denominator. It checks exact component protocol
identity and digest, base-before-extension validators before formation, structured
failure with no object, complete normalized tuple equality, equal-tuple hash
congruence, recursive owned immutability, nested protocol delegation, and
additive-validation-only acyclic factory extension.

The family uses an independently issued construction observation. A provider cannot
write or replace the denominator, expected findings, observer identity, or its own
evidence. The current real target lane is deliberately expected-red until later
target/provider SWUs supply observations.

The claim is transport-only: it does not prove a native TypeScript, Python, or Rust
implementation, cross-language hash bytes, collision freedom, promotion, or
authority. `authority_effect` remains `none`.
