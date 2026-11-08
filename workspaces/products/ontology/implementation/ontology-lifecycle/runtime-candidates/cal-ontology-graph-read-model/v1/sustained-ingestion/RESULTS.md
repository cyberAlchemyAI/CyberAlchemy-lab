# Sustained ingestion results

The source-bound `sustained` profile passes its local synthetic quality bar in
two independent release-process attempts.

| Attempt | Batches | Ingestion time | Throughput | Maximum projection latency | Overload rejections | Reader observations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 500 | 2.875 s | 173.90 batches/s | 325.98 ms | 7,522 | 6,575,518 |
| 2 | 500 | 2.778 s | 179.96 batches/s | 216.07 ms | 7,441 | 6,542,003 |

Each attempt filled a 16-slot paused queue, rejected the next batch as retryable
`INGESTION_QUEUE_FULL`, resumed, retried without loss, and drained all 500
accepted batches. Maximum pending work was 17: the 16 queued batches plus one
batch in the projection worker. Final semantic and governance lag was zero.

All 13,117,521 concurrent reader observations saw a complete immutable
generation. The final graph digest
`93a061f57cbcf2cc94237eecf2ed0329521e6f86fbb53d7b8ab0065af56074bc`
matched the independently rebuilt calculated cut in both attempts. Old snapshot
generation zero remained readable after final publication.

The evidence proves only a local synthetic single-ingress calculated-batch
projection prototype. It does not prove canonical event append, durable queue
storage, restart recovery of accepted-but-unprojected batches, multi-writer
ordering, power-loss durability, production service levels, approval,
admission, or activation.
