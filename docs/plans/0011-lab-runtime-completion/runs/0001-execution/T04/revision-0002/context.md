# T04 revision0002 exact raw-frame context

Root review identified an exactness gap: previous inspection planning did not compare the original request bytes against its independently selected digest. This correction creates new caller/adapter/tests and evidence in revision-0002 only; all previous code/receipt/report/input hashes are retained in prior-revision-bindings.json.

Require captured immutable raw bytes, verify their SHA256 before parsing, reject changed parsed controls (including nested Actor/budget/profile/deadline), and derive only a read plan. Whitespace remains in the actual raw digest. Duplicate fields, non-finite JSON and invalid raw framing are refused. No API17, production callbacks, clocks, original receipts or live/private state change.

Focused tests use actual retained envelopes/journal snapshots plus explicitly derived raw-frame branch fixtures; the missing historical worker12 request is not fabricated. Its uncertainty/inspection lineage remains observable, while new planning of that missing wire frame is refused. No runtime reauthentication or source lifetime is claimed. Use pinned R02 interpreter -B and fresh code/input/preservation guards entry/exit.
