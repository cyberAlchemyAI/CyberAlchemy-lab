# Shared Context

Status: pass

## Core Paths

- Tower root: `projects/domainspec-v2/research/alloy-tla-modeling/`
- Invoke plan root: `projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/`
- Examples: `projects/domainspec-v2/research/alloy-tla-modeling/examples/`
- DCB saga toy: `projects/domainspec-v2/research/dcb-saga-correctness/`

## Source Anchors

- `../BRIDGE-DECISIONS.md`: tool-lane decisions.
- `../levels/L2-closure-plan.md`: validation slices.
- `../examples/README.md`: evidence requirements for examples.
- `../../dcb-saga-correctness/toy-run-result.md`: bounded witness result.
- `../../dcb-saga-correctness/toy-harness/`: TypeScript fixture source.

## Local Environment Snapshot

- WSL/Linux x86_64.
- `apt`, `apt-get`, `curl`, `wget`, `sha1sum`, `shasum` available.
- `java`, `alloy`, `tlc`, local `tla2tools*.jar`, and local Alloy jars not found at planning time.

## Tool Source Anchors

- Alloy 6.2.0 homepage/release:
  - `https://alloytools.org/`
  - `https://github.com/AlloyTools/org.alloytools.alloy/releases/tag/v6.2.0`
- TLA+ tools:
  - `https://github.com/tlaplus/tlaplus`
  - `https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4`
