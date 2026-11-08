# T06 current composite successor rehearsal

The current API33 composite SDK and branch driver select a fresh task-local
dependency installation at `working/installation-0001`. The staging script
copies the exact 1,010 public files selected by the pinned T07 dependency
manifest, verifies every selected byte and a closed 1,011-file inventory, and
leaves unselected generated caches behind. It preserves the historical
`installation.json` as provenance and checks its exact bytes, size, mode, and
owner during staging and every runtime installation check.
`working/INSTALLATION-0001.json` records the new copy and its checks. The generated installation is ignored by Git and can
be rebuilt with `PYTHONDONTWRITEBYTECODE=1 python3 -B stage_installation.py`
after removing only this task-local disposable installation and receipt.

The SDK and branch producer are separately versioned under `product/` and
`docs/plans/`. Their manifests pin executable rows. The selected sixth API33
contract profile now includes those exact rows and binds its current local
integration-member file; independent cold `software_guard()` accepted the
profile and task-local installation. This package currently proves source
closure and launcher reachability with an
intentionally absent configuration; it does not establish a Base, Action, or
Governance branch startup or a 34-operation qualification.
