# Sustained ingestion protocol

1. Validate `requirements.json` against its Draft 2020-12 schema.
2. Build `cal-sustained-ingestion-prototype` once with the locked release
   dependency graph; compilation is outside attempt timing.
3. Start each attempt from an independently generated empty calculated cut.
4. Create 500 ordered one-node calculated batches and an independently rebuilt
   final model.
5. Start the ingestion worker paused, enqueue exactly 16 batches, and prove the
   next batch returns retryable `INGESTION_QUEUE_FULL` without advancing either
   accepted watermark.
6. Start four readers, resume the worker, retry the rejected batch, and submit
   the remaining batches. Retry only explicit overload outcomes.
7. Wait for the final accepted sequence, drain the queue, and compare the final
   graph to the independently rebuilt target.
8. Preserve raw stdout/stderr, one evidence record per attempt, a timestamped
   report, a latest pointer, and a source-bound validation receipt.

The channel capacity bounds queued batches. One batch may concurrently be in
the projection worker, so the declared pending-work bound is capacity plus one.
Elapsed time and projection latency are observations, not deterministic fields.
