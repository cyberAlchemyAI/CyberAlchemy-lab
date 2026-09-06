# Resource-bounded event-file parity result

Status: **PASS** for two fresh-process recoveries of 250,000 governed subjects
from 500,000 canonical-format event files.

The temporary fixture contained 50,000 nodes and 200,000 relations. Every
subject had one semantic event file and one exact governance event file. The
fixture occupied 690,644,470 logical bytes and 2,085,994,496 allocated
filesystem bytes. Generation completed in 112.07 seconds of process time and
peaked at 2,180,456 KiB RSS.

| Attempt | Load and validate | Calculate and rebuild | Process total | Peak RSS | Bound |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 51.625 s | 10.594 s | 63.384 s | 3,044,880 KiB | 180 s / 7,340,032 KiB |
| 2 | 52.016 s | 11.844 s | 64.667 s | 3,045,052 KiB | 180 s / 7,340,032 KiB |

Both processes reproduced the exact expected cursor, source-event count,
source-event-set digest, and rebuilt-index digest. Their normalized receipts
were identical. Adding leading whitespace to one event made the separate
control fail with `NON_CANONICAL_JSON`. The fixture was removed after evidence
capture.

The first development measurement exposed serial file loading as a scale
defect. The runtime now loads each deterministically ordered directory in
parallel and joins worker results in path order, retaining deterministic
validation and error selection. Runtime and graph suites plus strict clippy
passed after the change.

The source-bound receipt is [`validation.json`](validation.json). This result is
local synthetic evidence only. It does not establish a production service
level, representative workload capacity, canonical append acknowledgement,
durable pending-work recovery, power-loss durability, multi-writer ordering, approval,
admission, activation, publication, or cutover.
