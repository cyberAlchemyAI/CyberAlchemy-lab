# T22 API30 episode-0005 local inspection successor

This disjoint successor repairs the first local cut's metadata-only view. The
selected [RUN-0003.json](RUN-0003.json) contains a bounded **7,887-byte view**
whose Project State section carries the selected body's actual payload:
project identity, cursor, state digest, 15 decision refs, 57 artifact refs,
and semantic/governance history refs. The view also binds the selected State
body digest and the compact payload digest. A freshly generated, 120-second
local technical Session consumed those exact view bytes once, recorded their
digest and size, and zeroed its held view and nonce buffers on close. The
report derives its cursor, counts, role-assignment refs and payload digest
from that consumed projection.

The engineering finding remains specific: frozen API30 pins the old
`authority/project-state-transitions/current.json` SHA-256 `8ba8ee25...`,
while current bytes are `12937950...`; the currently selected specialist
Project State body `cccf18d2...` is absent from API30's source inventory.
Both conditions refuse a claim that frozen API30 selects this current State.
The underlying State content is displayed as observed data, not adjudicated
as correct or incorrect. All four input bytes (API30 manifest, current lookup,
selected State body and lookup-selected admission bundle) are pinned and read
without following symlinks. The 105-row protected Source8 family, native
contest and later Lesson outcomes are separate.

The first package at `t22-api30-episode-inspection-0001` and its two run
receipts remain intact. This Session is an executable **technical fixture**,
not native Lab API `context.get` or `session.open`, and it has no admitted
Source8 permission. Its self-issued technical signature checks receipt
integrity; it does **not** establish independent historical Session provenance.
Neither this cut nor the first cut completes original T22. A native episode
still requires a Source8 Work/Context family explicitly binding API30, current
permissions and a native view/Session consumption receipt.

Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002 -p test_episode.py -v`, repeat with `python3 -O`, and cold replay with
`PYTHONDONTWRITEBYTECODE=1 python3 implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/episode.py --verify`.
Nine tests include an in-run check of exact projected bytes in Session memory
followed by zeroing; changed State/API30/lookup bytes; symlinked ancestor;
expired, duplicate and wrongly bound consumption; and a coherently re-signed
changed projection and report.
