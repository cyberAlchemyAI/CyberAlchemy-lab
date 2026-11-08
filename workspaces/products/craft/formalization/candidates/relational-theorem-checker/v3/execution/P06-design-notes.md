# P06 implementation decisions from current execution

This is a design note for the next dependent unit. It is not P06 acceptance or an enforcement result.

## Observed boundaries

The host exposes unified cgroup membership `0::/init.scope` and memory/pids controllers, but `/sys/fs/cgroup` is not writable by the executing user. A required per-run aggregate memory policy must return unsupported-policy on this host. Advisory execution can report sampled descendant RSS, but neither sampling nor per-process RLIMIT_AS establishes an aggregate memory ceiling.

The original P03 CLI general replay reached 60 seconds and returned unknown-resource without claims. A later probe reached the same limit while compiling the expansion module. Successful prior actual expansion compilations ranged from 21.4 to 37.8 seconds. These observations show local variation; they do not determine numerical defaults or prove the source of that variation. The 60-second policy remains unchanged.

## Supervised boundary

A dedicated trusted worker must own request decoding, normalization, finite evaluation, dependency preparation, witness compilation, general replay and saved inspection. It starts in a new process group. The supervisor continuously drains bounded output, applies a whole-run monotonic deadline, monitors cancellation and tears down/reaps descendants after incomplete outcomes. A cooperative lock prevents concurrent expensive runs against one execution root.

The result is returned only after the entire worker exits successfully and policy accounting completes. A saved intermediate qualified file is not a completed supervised qualification. Cancellation, timeout, output overflow, forced termination and unsupported required enforcement return empty claims and cannot publish.

A writable delegated cgroup backend must set memory.max and pids.max before releasing a waiting worker, verify effective values, observe memory.events, kill the group on failure and remove only its own emptied per-run group. Missing delegation stays explicit. Advisory mode must never claim cgroup enforcement.

## API integration review

P03 deliberately refuses required memory mode. The supervisor must not patch its global qualifier or silently rewrite a required request to advisory. A supported required backend needs a separate trusted qualification entry point with an explicit enforced-policy capability, the original request identity and the same exact proof construction/inspection requirements. That bridge requires its own binding and hostile substitution controls. On the current host no such capability can be issued.

No optimization or witness change is inferred from these timing results. P10 selects defaults and optimization only after cold/warm measurements under the final supervisor.

## P07 cache follow-up

P03 currently checks source/compiled hashes from the fixed existing cache location. P07 must independently anchor that cache metadata to P02's accepted `layout-equivalence-report.json` field `inherited_dependency_binding`, rather than acquiring authority from a mutable cache's own manifest. The accepted P02 report already pins the exact dependency manifest digest. Include every source and compiled dependency in the context's currentness checks; reject metadata changes that retain source hashes while substituting compiled bytes. This strengthens the planned cache boundary before shadow publication.
