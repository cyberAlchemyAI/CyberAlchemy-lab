# Standalone Define

The independent candidate is in [implementation/define-cli/standalone](../implementation/define-cli/standalone/README.md). It has its own Python installation metadata, bundled contracts, CLI and `define.api/v1` byte interface. No Lab installation or runtime is required.

From this repository:

```bash
./define/define-standalone doctor
./define/define-standalone capabilities
```

Installed commands are `define-standalone` and `define-api`; Python callers use `from define_core import call`. The [first-use guide](../implementation/define-cli/standalone/README.md#a-first-definition-pack) shows the complete local Pack workflow. Agents author the schema-conforming request and supply selected sources; the core checks and assembles them.

[Design and work map](development/standalone-api/v1/DESIGN.md) · [Two-round critique](development/standalone-api/v1/DISTILL.md) · [Historical implementation baseline](development/standalone-api/v1/IMPLEMENTATION.md) · [Current release qualification](development/standalone-release/v2/RELEASE.md).

V3 generic reuse preserves exact source meaning with unverified standing. It is a different contract from the existing v2 Lab workflow, which remains available through `define-v2`. Native Lab review requires an explicit compatible mapping and independently qualified owner route. The current `0.3.0rc2` candidate passes its recorded standalone Linux qualification. Apache-2.0 is selected for the standalone distribution. Public stable release awaits the stable-version cut and publication described in the release report. It has not been adopted as the repository's default runtime.
