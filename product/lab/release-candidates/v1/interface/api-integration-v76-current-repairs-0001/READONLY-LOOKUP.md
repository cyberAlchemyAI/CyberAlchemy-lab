# Read-only operation lookup

API58's full export suite found that refusal before claim still created an empty
workspace `.lock`. API59 preserves the original API58 source and evidence and
changes operation lookup to make an empty-journal observation without writing.

An authorized claim still creates the exclusive lock and rechecks the exact key,
fingerprint and prior result before any dispatch. Inspection of an existing lock
opens it without creation. A durable journal whose lock is missing is refused;
inspection and retry do not recreate it. A concurrent first claim can follow an
empty observation, and the claim's original locked recheck remains authoritative.

The host authority, original source guards, clocks, native validation, export
publisher and all public contracts remain unchanged. Actual export and recovery
checks are required on the new source; predecessor qualification does not transfer.
