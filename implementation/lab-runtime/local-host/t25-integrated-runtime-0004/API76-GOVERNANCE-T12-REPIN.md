# API76 current T12 governance selection

The final0003 `member:action-governance` diagnostic stopped before an API call.
The selected governance v4 fixture tried to capture the historical
`runtime-byte-custody-v3` profile, whose pinned Project State lookup differs
from the current T12 specialist-owner lookup. The failed final0003 originals
remain retained; they are not retried or relabeled.

The existing `api-governance-integration-v5-current-t12-0001` successor uses
the source8-current-fixture engine-v3 at its true repository origin. Its source
manifest binds 986 unique input files, including 45 native engine inventory
rows and a profile selecting the current T12 history cursor 7. API76 code
constructor `prepare_api76_code_0003.py` changes only the staged
`integration-members.json` governance directory and exact source SHA. The
governance contract profile SHA and three operation names remain the same.
`package_view_api76.py` installs the v5 manifest and every bound input byte,
rejects conflicting package rows, and includes those bindings in the generated
API source/profile file sets.

Focused v5 source checks and API76 selection checks passed 7/7. A disposable
native v5 fixture accepted `checkpoint.resolve` and refused a foreign
authenticated context with `unauthorized`; its native head did not change and
its private `/tmp` fixture was removed. These checks exercise the governance
member directly. The API76 common dispatcher and all three governance
operation pairs still require fresh final0004 native qualification.

The private test receipts are under
`/home/vlad_/.local/share/cyberalchemy-lab/final-local-product-20261026-0003/governance-v5-selection-0001/`:

- `RESULT.json` SHA-256 `ae4043be71908dd446fd56291253c20057ae7e912c35bfcae4e1438607f36f3a`.
- `NATIVE-PROBE.json` SHA-256 `6b2e4aee2384fb37859b7f769555cb4e27889fbb118c9d9bc74e656be46c802e`.

No canonical authority write, human owner outcome, repository admission, or
external activation is claimed by this repin.
