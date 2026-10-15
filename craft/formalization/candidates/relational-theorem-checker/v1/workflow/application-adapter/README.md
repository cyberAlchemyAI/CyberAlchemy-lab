# Candidate application adapter

`candidate-adapter init --state shadow/example.json` captures the accepted
baseline in an explicit mutable shadow file. Initialization refuses to replace
an existing file. `review PROPOSAL --state STATE [--bundle BUNDLE]` performs a
complete current R03 replay and returns a bound review record.

`apply REVIEW --proposal PROPOSAL --state STATE [--bundle BUNDLE]` recaptures
the exact request, source bytes, baseline, epoch, verifier policy and evidence
dependencies. It always reruns every hard obligation before writing the
candidate snapshot. It cannot use an old ready label as application evidence.
Changed bindings reject the earlier review and require a fresh review. Changed
semantic baselines require a newly supported formal baseline; this prototype
does not silently extend its captured profile after a first shadow application.

Optional `source_inputs` in a shadow state bind explicit simulation files
inside the same shadow directory. They exercise real review-to-application
byte drift without modifying the immutable captured authority sources. They
are additional application dependencies, not newly established semantics.

All writes stay in this candidate adapter's shadow/runs directories, plus
the accepted verifier's owned candidate evidence directory. Authority stores,
runtime activation, credentials and keys are outside the write path.
`applied-to-shadow` means only a candidate state changed. Every output has
authority_effect none and human_authority_granted false. Human pilot/use review
remains separate.

A local advisory lock serializes cooperating adapters; post-replay identity
checks precede same-directory replacement. This is a simulation under ordinary
local filesystem ownership, not an adversarial distributed transaction or a
claim to protect against arbitrary noncooperating filesystem writers.
