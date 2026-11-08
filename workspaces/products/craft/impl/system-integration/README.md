# DomainSpec v2 system integration

This private sibling package makes the canonical D45-D49 infrastructure-binding
vocabulary machine-readable without adding DomainSpec meta types or selecting a
database, ORM, broker, dependency-injection framework, or durable runtime.

`domainspec.system-integration-profile/provider-neutral-v1` is a canonical
implementation target. It has three language profiles (TypeScript, Python, and
Rust), but the profiles are not evidence that a provider or durable dispatcher
exists. Target projects supply opaque adapter and resource references; the
compiler validates their declared relationships, canonicalizes the binding set,
and binds it to exact profile and source digests.

The package preserves these boundaries:

- dependency contracts are responsibility-specific; there is no universal
  code-level `Port`;
- a DS-D1 Interface reference is optional and only denotes a real logical
  Interface;
- Repository contracts are separate from Persistence Bindings;
- Unit of Work contracts are separate from Transaction Guarantee Bindings;
- Failure Outcome Binding classifies failures but never selects Retry;
- Durable Workflow Runtime Binding is durable-profile-only and composes, rather
  than replaces, the concern-specific bindings;
- formation and generated-source evidence prove no runtime guarantee.

Run validation with the repository Node 26 container:

```text
toolchains/node-typescript/bin/node-env run --project projects/domainspec-v2/impl -- node system-integration/validation/validate-system-integration-profile-v1.mjs
toolchains/node-typescript/bin/node-env run --project projects/domainspec-v2/impl -- node --test system-integration/tests/system-integration-v1.test.mjs
```
