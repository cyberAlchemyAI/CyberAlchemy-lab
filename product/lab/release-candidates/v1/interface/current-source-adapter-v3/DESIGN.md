# Bounded source construction successor

Status: authored; not frozen, executed, selected or qualified.

The measured API35 source replay spent 499.15 seconds under passive profiling.
Its source adapter ran 35 guards and its eligibility collection ran 30 guards.
This identifies repeated verification as a measured cost in that replay. It
does not establish the cause of the Machine errors or unprofiled API latency.

This successor validates the complete selected record set under original source
guards at entry and exit. Each record retains its exact header, original byte
hash, schema, semantic kind, revision witness and privacy checks. Individual
public `get` calls retain their source guard. No clock, permission, callback,
Assignment period or Session duration is replaced or extended.

All 17 original test methods are unchanged. Three additional actual source
cases cover complete-set validation and mutated-record/source-cut refusal.
These cases have not run.

The original producer binds its Implementation to adapter2's exact reader.py.
Adapter3 therefore requires a separately constructed candidate producer4 with
an exact declared adapter3 entrypoint. Its base.py selects that missing producer
explicitly. It must not substitute adapter3 under producer3's Implementation.
No candidate construction, public integration or qualification may be claimed
from this authored package alone.

Next: construct and freeze the exact producer/Implementation successor; freeze
adapter3's complete dependencies; run all 20 cases and the independent original
adapter audit. Qualified mapper, Context and API successors require their own
exact source selection and full original verification before use.
