# Event-file parity resource protocol

The parity harness builds the locked binaries outside the timed region and then
checks current memory, filesystem bytes, and inode headroom. It refuses to
allocate the fixture when any preflight minimum is missing.

The generator and each recovery process run under GNU `time` and an inherited
virtual-memory limit. The harness records maximum resident set size, process
wall time, internal load/rebuild phases, page faults, filesystem I/O counters,
logical event bytes, and allocated fixture bytes.

Two recoveries must return the same normalized receipt and exact independently
derived source and index digests. A separate leading-whitespace control must
return `NON_CANONICAL_JSON`. The harness then removes its temporary fixture.

No measured field grants authority or selects a persistence design.
