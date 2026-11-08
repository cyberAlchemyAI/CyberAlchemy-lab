# W0 Toolchain

Layer: L0
Status: ready

## Layer Question

After this wave, we know whether Alloy and TLA+ can be invoked locally without committing third-party binaries.

## Tasks

- [TASK-FMT-001](../tasks/TASK-FMT-001-toolchain.md)

## SWUs

- SWU-FMT-001
- SWU-FMT-002

## Promotion Evidence

- Java 11+ or OpenJDK 17 present.
- TLA+ tools help command runs.
- Alloy help command runs.
- Tool provenance receipt exists.

## Stop Conditions

- Stop if Java cannot be installed or located.
- Stop if tool binaries would need to be committed to the repo.
