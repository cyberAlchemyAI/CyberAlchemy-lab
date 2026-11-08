# Bound application AlchLang frontend

`profile bound-application-v1` accepts `.alch` modules with JSON-valued clauses.
The frontend parses imports and lowers digest-bound core models. It delegates all
application semantic checks and generation to the selected DomainSpec package.
There is no separate AlchLang application generator.

`check <root.alch>` checks through DomainSpec. `ontology <root.alch>` emits the
shared JSON compiler input. `build <root.alch> --out <new-output>` sends that input
to the same backend used by the native DomainSpec application-build command.
Build requires the output path authored by the application and an absent target.
Missing backend exports require rebuilding the explicitly selected package.

Backend contract: [DomainSpec APPLICATION.md](../cli/APPLICATION.md).
The historical Body War v2 reference consumer is not part of the selected Craft
source and is therefore not a current checkout dependency.
The consumer tests byte-equivalent output and runtime effects of route, permission,
response and lifecycle changes, and records its current assurance limits.

## Open Questions

Owned by the backend contract and the reference consumer's README.
