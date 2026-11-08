"""Read the current T12 admission successors as an exact source envelope.

The v2 engine profile ended at D75. This adapter extends that epoch through
the actual immutable successor bundles without changing authority files.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE_PROFILE = ROOT / "product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/profile.json"
LOOKUP = "authority/project-state-transitions/current.json"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "DUPLICATE_JSON_KEY_REFUSED")
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: require(False, "NONFINITE_JSON_REFUSED"))


def safe_path(repo, relative):
    require(type(relative) is str and relative == Path(relative).as_posix() and
            not Path(relative).is_absolute() and ".." not in Path(relative).parts and
            "\\" not in relative, "UNSAFE_SOURCE_PATH_REFUSED")
    path = repo / relative
    require(path.is_file() and not path.is_symlink() and
            not any(parent.is_symlink() for parent in path.parents), "SOURCE_ORIGIN_REFUSED")
    return path


def read(repo, relative, expected=None):
    raw = safe_path(repo, relative).read_bytes()
    observed = sha(raw)
    require(expected is None or expected == observed, "SOURCE_DIGEST_REFUSED " + relative)
    return parse(raw), observed


def bundle_from_state(path):
    selected = Path(path)
    require(selected.name == "project-state.json" and selected.parent.name == "instances",
            "STATE_LAYOUT_REFUSED")
    return (selected.parent.parent / "bundle.json").as_posix()


def capture(repo=ROOT, *, expected_lookup_sha256=None):
    repo = Path(repo).resolve()
    profile, profile_sha = read(repo, BASE_PROFILE.relative_to(ROOT).as_posix())
    lookup, lookup_sha = read(repo, LOOKUP, expected_lookup_sha256)
    require(lookup["replay_source"] is False and lookup["authority_effect"] == "none" and
            lookup["projection_policy"] == "generated-from-immutable-admission-bundle",
            "CURRENT_LOOKUP_SHAPE_REFUSED")
    base = profile["current_selection"]
    anchor = base["bundle_path"]
    base_bundle, base_sha = read(repo, anchor, profile["operational_roots"][-1]["sha256"])
    require(base_bundle["current_project_state_ref"] == base["state_version_ref"].split("@")[0],
            "BASE_STATE_SELECTION_REFUSED")
    cursor = lookup["admission_bundle"]["path"]
    visited = set()
    reverse = []
    while cursor != anchor:
        require(cursor not in visited and len(reverse) < 16, "BUNDLE_CHAIN_REFUSED")
        visited.add(cursor)
        bundle, bundle_sha = read(repo, cursor)
        require(bundle_sha == lookup["admission_bundle"]["sha256"] or bool(reverse),
                "CURRENT_BUNDLE_BINDING_REFUSED")
        predecessor = bundle["predecessor_state"]
        require(set(predecessor) == {"path", "sha256"}, "PREDECESSOR_BINDING_REFUSED")
        next_cursor = bundle_from_state(predecessor["path"])
        reverse.append((cursor, bundle, bundle_sha, predecessor))
        cursor = next_cursor
    require(reverse, "NO_SUCCESSOR_BUNDLE_REFUSED")
    chain = list(reversed(reverse))
    previous_state_path = base["state_path"]
    previous_state, previous_sha = read(repo, previous_state_path)
    require(base_bundle["current_project_state_sha256"] == previous_sha,
            "BASE_STATE_BINDING_REFUSED")
    summaries = []
    for bundle_path, bundle, bundle_sha, predecessor in chain:
        require(predecessor == {"path": previous_state_path, "sha256": previous_sha},
                "PREDECESSOR_CHAIN_REFUSED")
        root = Path(bundle_path).parent
        files = bundle["files"]
        names = [row["path"] for row in files]
        require(len(names) == len(set(names)), "BUNDLE_DUPLICATE_FILE_REFUSED")
        captured = {}
        for row in files:
            require(set(row) == {"path", "sha256"}, "BUNDLE_FILE_BINDING_REFUSED")
            relative = (root / row["path"]).as_posix()
            require(relative.startswith(root.as_posix() + "/"), "BUNDLE_ESCAPE_REFUSED")
            body, observed = read(repo, relative, row["sha256"])
            captured[relative] = (body, observed)
        state_path = (root / "instances/project-state.json").as_posix()
        require(state_path in captured, "STATE_NOT_IN_BUNDLE_REFUSED")
        state, state_sha = captured[state_path]
        require(state["node_id"] == bundle["current_project_state_ref"] and
                state_sha == bundle["current_project_state_sha256"], "BUNDLE_STATE_REFUSED")
        transaction_path = (root / "instances/admission-transaction.json").as_posix()
        require(transaction_path in captured, "TRANSACTION_NOT_IN_BUNDLE_REFUSED")
        transaction = captured[transaction_path][0]
        targets = transaction["payload"]["admission_targets"]
        for target in targets:
            matches = [name for name, (body, digest) in captured.items()
                       if name.startswith((root / "instances").as_posix() + "/") and
                       body.get("node_id") == target["target_ref"] and digest == target["target_sha256"]]
            require(len(matches) == 1, "ADMISSION_TARGET_REFUSED")
        for consequence in transaction["payload"]["deterministic_consequences"]:
            matches = [name for name, (body, digest) in captured.items()
                       if body.get("node_id") == consequence["consequence_ref"] and
                       digest == consequence["output_sha256"]]
            require(len(matches) == 1, "CONSEQUENCE_REFUSED")
        summaries.append({"bundle": {"path": bundle_path, "sha256": bundle_sha},
                          "state": {"path": state_path, "sha256": state_sha,
                                    "identity": state["node_id"]},
                          "target_count": len(targets),
                          "file_count": len(files),
                          "history_cursor": state["payload"]["cursor"]})
        previous_state_path, previous_sha = state_path, state_sha
    require(lookup["admission_bundle"] == summaries[-1]["bundle"] and
            lookup["current_project_state"] == {"path": previous_state_path,
                                                 "sha256": previous_sha} and
            lookup["identity_ref"] == summaries[-1]["state"]["identity"],
            "CURRENT_SELECTION_REFUSED")
    return {"schema": "cal-current-authority-source-envelope/v1",
            "base_profile_sha256": profile_sha,
            "base_bundle": anchor,
            "current_lookup_sha256": lookup_sha,
            "current_state": summaries[-1]["state"],
            "successors": summaries,
            "authority_effect": "none"}


if __name__ == "__main__":
    print(json.dumps(capture(), sort_keys=True))
