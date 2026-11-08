# P07: isolate runs and anchor cache authority

## Problem and intended behavior

P06 now owns each process group and gives each job a unique directory. Its saved files are still ordinary mutable files, and its inherited cache checks acquire their expected binary hashes from the cache manifest itself. P07 will make accepted output read-only under the mediated API and independently bind cache metadata to the already accepted P02 report. Cache reuse remains byte reuse; every successful qualification still recompiles the exact actual witness and performs the fresh general replay.

## Implementation order

1. Define closed owned-run and execution-state schemas. State separates required outstanding tasks, selected optional outstanding tasks, and resolved optional tasks. A task can be resolved as not-needed only if it was actually unselected; all seven extensions in this run remain selected.
2. Implement an independent cache anchor. Verify the accepted P02 receipt, its bound layout-equivalence report, and that report's inherited_dependency_binding before opening the cache. Verify every source and compiled dependency, pinned compiler and kernel, catalog, generator, and layout policy. Canonicalize those values into a cache key. Do not let a replacement cache self-certify its new hashes.
3. Add a fixed P07 worker that retains the accepted P06 proof recipe and resource boundary. Record owned phase observations inside the supervised group. Use exclusive writes and owner metadata; a second run cannot reuse an existing run directory.
4. Publish the final owned-run record only after exact proof inspection and supervisor completion. Bind all run-specific outputs, the original raw request, source/policy inputs, actual resource report, and phase records. Apply private permissions and remove API write permission from finalized files. This is mediated immutability, with byte verification on reread; it does not exclude a same-privilege external writer.
5. Resume only after validating the original request bytes, policy, source closure, phase records, and outputs inside a supervised worker. Allocate a new run and rerun fresh qualification; preserve the original phase provenance rather than calling cached computations fresh proof. Interrupted or conflicting output stays diagnostic evidence.
6. Produce cleanup proposals with exact owner/run bindings. Do not delete historical accepted runs or unrelated directories. Reject another run, escaped paths, and any accepted evidence.
7. Review two actual rich runs sharing the same anchored cache, phase interruption and fresh resume, stale metadata, transplanted output, conflicting run identity, and optional-status normalization. Compare accepted earlier bytes before and after the warm run.

## Evidence required for acceptance

The review must distinguish tests of owned metadata from actual fresh kernel qualifications. Successful resume must retain provenance to the old phase record while creating a distinct new fresh run. Read-only permissions are measured on the files created with umask 077. Every cache-control failure must come from an independently pinned expected binding rather than the substituted file's own metadata.

This document prepares the next unit; it does not accept P07 or bypass its P05/P06 dependencies. No cleanup or external publication is authorized by this plan.
