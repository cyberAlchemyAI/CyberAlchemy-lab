# Versioned phase-prefix diagnostic

The reviewed `prefix_probe.py` produced one disposable PASS, while an
independent replay returned a `ContractError` and a second independent replay
passed at the same source hash. The first failure retained no contract site.
`prefix_diagnostic_0001.py` is a disjoint copy of the prefix probe with closed
phase tags around selection, materialization, Source child, Source poststate,
Reader child, Reader poststate, and cleanup. It does not amend the successful
receipt, construction packet, or independent two-outcome review.

A failure result contains only an allowlisted stage and code, each completed
child's return code plus bounded stdout/stderr lengths and SHA-256 digests, and
post-context scratch absence when observable. It excludes raw child output,
exception text, fixture paths, private signer material, and protected inputs.
`CHILD_TIMEOUT` and `CHILD_OUTPUT_LIMIT` preserve the existing bounded runner's
124 and 125 statuses. Other nonzero child statuses, contract refusals, and
unexpected exceptions remain distinct. A successful diagnostic run must still
meet the exact 15-leaf Source/Reader prefix, 53/54-leaf poststate, wrong-pin,
read-only, and cleanup oracles in the reviewed probe.

This instrumentation diagnoses an intermittent disposable result. It is not
an effect gate, production controller, current issuer, actual WSL host
qualification, Mapper/Context phase, or unit acceptance. No further effect
run is justified until independent static review checks the new source and
normal/optimized pure tests at exact hashes.
