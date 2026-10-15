# Staged capture integrity correction

The helper records the selected functions' code, globals, defaults, keyword defaults and closure bindings. Each validation checks those records and the captured file digest. It also checks the actual generator behind the context-manager wrapper. Scope cleanup closes its own held descriptors directly, even when a callback is no longer eligible.

The separately captured caller companion holds the selection outside the helper and validates its selected entry code before calling it. A future source-family loader must capture both files against independent hashes, retain this contract and the companion entry code outside the helper, and check them before and after every helper invocation. The existing source/reader/mapper/Context wrappers have not yet been changed to use this companion.

The actual installed 0004 interpreter passed 24 owned-file and held-contract checks. They cover code/default selection mismatch, wrong digests, input paths, duplicate inputs, nested scopes, same-byte and different-byte leaf replacement, ancestor replacement, exception cleanup and descriptor cleanup. These controls change no production callback, clock or private state. The earlier isolated counterexample is retained separately; its mutation experiment was not rerun here.

This is a defensive integrity contract inside a trusted caller. It does not isolate Python from arbitrary privileged rewriting of every caller and trust anchor, or establish a perpetual concurrency guarantee. It retains fresh hashes and attachment checks; no trust cache or byte cache survives a verification invocation.

Before runtime use, integrate the caller into separately preserved source-family postimages, review those exact postimages and create a new independently signed native family. New helper and caller origins need complete source/profile eligibility. The old family, periods, grants and qualifications remain historical. The 24 checks do not qualify a complete learning sequence, realistic timing margin, native authority or the whole API. Required remaining integration and adversarial checks are not replaced by these component controls.
