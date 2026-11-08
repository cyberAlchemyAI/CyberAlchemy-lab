"""Generate one exact current-authority profile for the disjoint v3 engine."""

import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
ADAPTER = HERE.parent / "current_authority_adapter.py"
spec = importlib.util.spec_from_file_location("cal_source8_current_authority_adapter", ADAPTER)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def profile():
    selected = adapter.capture()
    old = json.loads(adapter.BASE_PROFILE.read_bytes())
    state = selected["current_state"]
    state_body = json.loads((ROOT / state["path"]).read_bytes())
    old["operational_roots"] += [row["bundle"] for row in selected["successors"]]
    old["current_selection"] = {
        "bundle_path": selected["successors"][-1]["bundle"]["path"],
        "history_base": str(Path(state["path"]).parent),
        "history_cursor": len(json.loads((ROOT / Path(state["path"]).parent /
                                         "project-semantic-event-history.json").read_bytes())["payload"]["events"]),
        "lookup": {"path": adapter.LOOKUP, "sha256": selected["current_lookup_sha256"]},
        "state_path": state["path"],
        "state_version_ref": state["identity"] + "@sha256." + state["sha256"],
    }
    old["admission_as_of"] = state_body["payload"]["cursor"]
    return old


def main():
    value = profile()
    path = HERE / "profile.json"
    raw = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
    print(json.dumps({"profile": str(path), "sha256": adapter.sha(raw),
                      "successor_bundles": len(value["operational_roots"]) - 1}))


if __name__ == "__main__":
    main()
