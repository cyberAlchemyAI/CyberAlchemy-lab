# L5 local active ontology runtime plan

Status: implementation candidate  
Route: `CA2-ROUTE-IMPLEMENT`  
Predecessor: admitted L4 state-bearing sandbox adapter  
Candidate: `cal.prototype.rust-local-active-ontology-runtime/epoch-004`

## Product frontier

Build one process-local runtime that calculates the exact W7 ontology projection
from canonical events, remains active across operator commands, exposes status
and projection output, and stops only through explicit `stop`, stdin EOF, or the
drop safety net.

## Runnable product work

1. Bind the exact L4 product approval and adapter-admission digests.
2. Replay the exact 47-event semantic and governance histories at cursor 47.
3. Persist the calculated projection inside the adapter-owned sandbox.
4. Keep the runtime and projection inspectable across repeated commands.
5. Restore and remove the complete sandbox on stop, EOF, failure, or drop.
6. Run formatting, Clippy, the complete Rust suite twice, the command process,
   mutation probes, and deterministic report generation.
7. Freeze one product candidate and prepare one approval decision at the end.

## Operational lane

| Task | Owner | Affected later stage | Product-lane effect |
| --- | --- | --- | --- |
| Choose a service transport | Runtime owner | Post-product live service | Does not block stdin prototype. |
| Bind credentials | Security owner | External target | Credentials remain forbidden. |
| Select production event store | Product and operations owners | Live deployment | Does not block canonical fixture runtime. |
| Author migration/cutover | Governance and operations owners | External-effect stage | Not part of this product. |

## Done criteria

- all eight invariants pass twice;
- the runtime prints `ready`, serves repeated `status` and `projection`
  commands, and prints a verified `stopped` receipt;
- cursor, event count, subject count, and event-set digest match the exact W7
  corpus;
- predecessor digests remain current;
- no Cargo target or sandbox root remains;
- the product-approval packet is ready, but no approval is inferred.
