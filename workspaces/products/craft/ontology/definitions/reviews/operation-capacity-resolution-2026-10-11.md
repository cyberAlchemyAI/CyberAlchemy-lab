# Operation / capacity classification resolution

## Owner instruction

On 11 October 2026, the user approved retaining Operation as state-changing, correcting the capacity example, adding Calculation support and updating Craft and Lab documentation together.

## Resolution

The DS-D1.4 Operation criterion and DS-D1.6 Calculation criterion remain unchanged. A successful Operation owns a state change; a rejected attempt may leave state unchanged. A pure snapshot classifier belongs to Calculation. Query remains retrieval and Rule remains a Boolean condition.

The current example is `craft/impl/cli/examples/capacity-classification`. It binds the original strict WithinCapacity Rule, the typed snapshot and a payloadless Accept/Reject Enum through explicit contract references, with no authored `enforces` or `reads` edges. The historical `test/fixtures/capacity-decision` is preserved as previous compiler regression evidence, and its Operation classification is superseded for current guidance.

The compiler adds `domainspec.typed-calculation/v2` and a Calculation-rooted closure, authoring, typed dependency checks, receipt decoding, Rust/TypeScript/Python generation and in-memory execution. Numeric v1 contracts remain compatible. No relationship endpoints or frozen implementation catalogs are changed.

ReserveCapacity is the documentation's state-changing Operation example. Its live-state check and reservation must be coordinated. The successor classifier does not implement that storage transaction.

## Evidence scope

Compiler and generated artifacts are built locally. Normal checkout builds require baseline and toolchain dependencies missing after repository relocation; an isolated build uses the preserved source dependencies. Automated regression tests and formal proofs are not run in this change. Generated receipts have authority_effect=none and do not admit Lab records, adopt a realization or authorize deployment.
