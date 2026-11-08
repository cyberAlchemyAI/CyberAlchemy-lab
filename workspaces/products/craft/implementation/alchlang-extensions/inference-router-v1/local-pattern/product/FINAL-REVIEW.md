# Mocked workspace reference product: final review

Date: 2026-09-08. Status: review complete, qualified recommendation for the
documented local mock scope. Authority effect: none; this review does not record
owner acceptance. The separately accepted base pattern retains its existing status.

## Evidence

The current 1,462 manifest entries pass `tools/inference-reference verify`.
The manifest SHA-256 is
`6cd4925d441ff040053c1c5477524a960f835e83176b868a4ed7ef45450792e8`.
The package receipt (result record excluded), consolidated receipt, all eight suite
logs and three supplementary operator logs have matching recorded hashes.
The suite logs corroborate 214 passing tests and zero failures. These are verified
existing test results, not a fresh test execution during this review.

The [review criteria](REVIEW.md) are supported for file identity, the mock API
walkthrough and serve shutdown, protected authorization and tenant/principal
isolation, encrypted durable custody, restart/revocation behavior, and operator
documentation. The protected rehearsal includes actual new service processes and
an interrupted inference; its online introspection remains a fixture.

Alch supplies the service declarations and composition. DomainSpec supplies
contract validation and compilation. Auth Foundation supplies identity verification
and permission decisions in the protected rehearsal. The engine boundary is
exercised with local deterministic mocks. This evidence does not establish model
quality, compatibility with a real engine or operation with a live issuer.

## Findings and recommendation

No blocker was found in the demonstrated local mock inference flows. The deliverable
is a workspace reference kit; the protected rehearsal requires the paired source
checkouts and installed dependencies described in [OPERATOR.md](OPERATOR.md).

Two operator validation paths need stronger evidence before claiming comprehensive
failure handling:

- `run.mjs` forwards signals to its immediate child. The protected rehearsal runner
  itself starts nested processes with `spawnSync`. Cancellation of that whole tree
  is not covered by the saved tests; prompt descendant cleanup is unproven. The
  tested demo/serve shutdown does not establish this property for `validate` or
  `rehearse`.
- Criterion 5's successful 214-test execution and preserved logs are demonstrated.
  The validation runner has a catch path that writes a failed receipt, but the
  evidence does not include an intentionally failing suite exercising that path.
  Rejection of an existing output directory is a different check.

These findings do not invalidate the recorded successes. The next bounded
engineering task is to test failed-suite receipt behavior and nested cancellation,
then fix any demonstrated cleanup failure. Any implementation change requires a
new candidate manifest and validation evidence; preserve this reviewed candidate's
historical receipts. No runtime files or frozen candidate inputs were changed by
this review.

## Open Questions

No domain or API design decision is required for that follow-up. Process-tree
cancellation and failure receipts are outstanding verification work, not questions
for the product owner. Optional real-engine, issuer and distribution choices remain
owned by [OPERATOR.md](OPERATOR.md#open-questions).
