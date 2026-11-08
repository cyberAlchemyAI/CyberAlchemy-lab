# Testing alignment

Every available pattern must prove:

- schema-valid registry material;
- registry/runtime parity;
- deterministic generated files;
- positive selection through the CLI;
- negative selection for every open or missing prerequisite;
- target compilation and executable behavior where the pattern has effects;
- no undeclared read, write, event or external destination.

Current evidence covers registry parity and fail-closed CLI selection.
Transactional Outbox executable behavior is intentionally missing and therefore
the pattern remains blocked.
