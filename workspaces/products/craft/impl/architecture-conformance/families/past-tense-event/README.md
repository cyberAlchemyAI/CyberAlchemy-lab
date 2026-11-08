# Past-tense Event candidate family

This candidate-local family extends the unchanged W3 Event proof with immutable payloads, stable and reuse-resistant occurrence identity, one durable checkpoint before publication, explicit consumer/version checks, and the S1 `durable-occurrence/v1` observation handle. Its frozen S1 extension models nine orthogonal fault, delivery, recovery, decode, identity, and retry controls with explicit durable residue. Commit, publication, acknowledgement, delivery, and consumption remain separate observations; no distributed exactly-once claim is made.
