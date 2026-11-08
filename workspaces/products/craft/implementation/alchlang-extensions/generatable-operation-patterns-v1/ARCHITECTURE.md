# Generatable Operation Pattern Registry architecture

## Observed architecture

The AlchLang compiler currently lowers explicit domain declarations into
target-neutral TypeScript and JSON artifacts. `Operation` is an admitted
DomainSpec meta-type. The local CLI already generates an operation port, while
provider runtime implementation remains open.

## Candidate extension

This package adds a registry between language meaning and code generation:

```text
meta-type + integration binding + generator + conformance
                         |
                         v
              derived availability
                         |
                         v
                    AlchLang CLI
```

The registry reports availability. It does not promote a pattern, select a
provider, or authorize an effect.

## Layers

1. Product meaning: `product-capability.json`.
2. Business meaning: `business-ontology.json`.
3. Pattern inventory: `operation-patterns.json` and its schema.
4. System model: `domainspec/specs/operation-pattern-registry`.
5. Runtime projection: `implementation/src/pattern-registry.ts` and CLI.
6. Evidence: tests, exact binding and independent conformance.
