# Formal Tooling

This directory is the tracked command surface for the Alloy/TLA+ research tower.

## Tracked

- `formal-tools.env.example`: optional environment overrides.
- `install-formal-tools.sh`: idempotent local installer for the pinned JRE, TLA+ jar, and Alloy jar.
- `run-tla-check.sh`: wrapper for SANY and TLC.
- `run-alloy-check.sh`: wrapper for the Alloy CLI.
- `validate-examples.sh`: first-pass example validation runner.
- `lib/formal-tools-common.sh`: shared path and receipt helpers.

## Ignored

Downloaded tools stay under `.formal-tools/` at the repository root. This checkout excludes that path through `.git/info/exclude`; do not commit downloaded jars, archives, extracted runtimes, solver caches, or generated native binaries.

Default local paths:

```text
.formal-tools/jre/current/bin/java
.formal-tools/tla/tla2tools-1.7.4.jar
.formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar
```

## Receipts

Receipts belong under `projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/`.

Known receipts:

- [Toolchain smoke](../invoke-plan/run-results/toolchain/swu-fmt-001-smoke-clean.md)
- [Toolchain provenance](../invoke-plan/run-results/toolchain/toolchain-receipt.md)
- [Wrapper validation](../invoke-plan/run-results/toolchain/swu-fmt-003-wrapper-validation.md)

Generated model-run receipts should use:

```text
invoke-plan/run-results/tla/
invoke-plan/run-results/alloy/
```

## Commands

Install or repair local tools:

```bash
projects/domainspec-v2/research/alloy-tla-modeling/tooling/install-formal-tools.sh
```

Run a TLA+ parse check:

```bash
projects/domainspec-v2/research/alloy-tla-modeling/tooling/run-tla-check.sh --sany \
  projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.tla
```

Run a TLA+ model check:

```bash
projects/domainspec-v2/research/alloy-tla-modeling/tooling/run-tla-check.sh --tlc \
  projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.tla
```

Run an Alloy command:

```bash
projects/domainspec-v2/research/alloy-tla-modeling/tooling/run-alloy-check.sh commands \
  projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.alloy
```

Run the first-pass examples:

```bash
projects/domainspec-v2/research/alloy-tla-modeling/tooling/validate-examples.sh
```

## Environment Overrides

All wrapper paths may be absolute or repository-root-relative. Use [formal-tools.env.example](formal-tools.env.example) as the template.

Supported variables:

```text
FORMAL_TOOLS_HOME
JAVA_BIN
TLA_TOOLS_JAR
ALLOY_JAR
FORMAL_RUN_RESULTS_ROOT
```

## Checksum Policy

The TLA+ release publishes an upstream SHA-1 for `tla2tools.jar`, and this tower records it in the [toolchain receipt](../invoke-plan/run-results/toolchain/toolchain-receipt.md). The Alloy release did not expose an upstream checksum in the release metadata checked for this work-pack, so Alloy receipts must label their checksum as local-only.
