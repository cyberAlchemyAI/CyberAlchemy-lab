"""Effect-disabled, exact-byte proposal for a fresh local Docker chain.

This imports the frozen T35 *constructor*, never generated roles. Nothing here
creates a family, container, signer, grant, store, or output package.
"""
from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[4]
T35_PARENT = REPO / "implementation/lab-runtime/candidates/runtime-completion-0001"
TRUSTED_T35 = {
    "role_stage.py": "8f8235588e2a62c973b25115af5e4b6080a301632db7098be4604d0c47d55fe8",
    "phase_rebind.py": "e5435311b3021baa2c1c952ac3e8401181283b689aa3e2f4d146c161a5ad7f74",
    "hardener.py": "b1d11bba6c4df68bf3a4aa69f801cafd5554aebccba8c215510185d9984c7bad",
    "path_contract.py": "9b77ff713c937495f9a5e3fe36d413a45e7185c98de1fed4b8c30b45c108f765",
}
T35_KEY_FILES = {
    "constructor": "role_stage.py",
    "phase_rebind": "phase_rebind.py",
    "hardener": "hardener.py",
    "path_contract": "path_contract.py",
}
T35_MODULES = {
    "constructor": "t35_external_v1.role_stage",
    "phase_rebind": "t35_external_v1.phase_rebind",
    "hardener": "t35_external_v1.hardener",
    "path_contract": "t35_external_v1.path_contract",
}
for _name, _digest in TRUSTED_T35.items():
    _path = T35_PARENT / "t35_external_v1" / _name
    if _path.is_symlink() or hashlib.sha256(_path.read_bytes()).hexdigest() != _digest:
        raise RuntimeError("T35 constructor code changed before import: " + _name)
sys.path.insert(0, str(T35_PARENT))
from t35_external_v1 import phase_rebind, role_stage  # noqa: E402

HERE = Path(__file__).resolve().parent
INPUT = HERE / "selection.json"
SCHEMA = "lab-docker-chain-proposed-selection/v2-effect-disabled"
PIN_ORDER = (
    "source_source", "source_package", "reader_adapter_source",
    "mapped_source", "mapped_package", "context_source", "context_package",
)
EXPECTED_BLOCKERS = (
    "SOURCE_ENV_PYTHON_3_14_4_VS_IMAGE_3_12",
    "SOURCE_WRITES_UNDER_READ_ONLY_WORKSPACE",
    "SOURCE_ROOT_DERIVATION_REQUIRES_REBINDING",
    "NATIVE_ELF_HOST_TMP_PATH_ABSENT_IN_CONTAINER",
    "CONTEXT_ORIGINAL_OUTPUT_SCHEMA_UNPROVED",
    "FRESH_AUTHORIZATION_AND_ENGINE_SELECTION_ABSENT",
    "FUTURE_SIGNED_SOURCE_AND_MAPPED_PACKAGES_ABSENT",
    "BUBBLEWRAP_OR_DIRECT_NATIVE_PATH_NOT_SELECTED",
    "CONTAINER_FD_LIMIT_AND_SCRATCH_CAPACITY_UNPROVEN",
)
EXPECTED_FEASIBILITY = {
    "container_ready": False,
    "source_effect_ready": False,
    "image_python": "3.12-slim-bookworm",
    "source_exact_python": "3.14.4",
    "image_packages": {"jsonschema": "4.23.0", "cryptography": "46.0.5"},
    "native": {"format": "ELF64", "machine": "x86-64", "abi": "GNU/Linux glibc",
               "interpreter": "/lib64/ld-linux-x86-64.so.2",
               "needed": ["libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2"],
               "container_load_verified": False},
    "workspace_mount": "/workspace:ro",
    "scratch": "/tmp:512m-tmpfs",
    "scratch_capacity_verified": False,
    "fd_limit_verified": False,
    "native_execution_path_selected": False,
    "bubblewrap_available_in_image": False,
    "blockers": list(EXPECTED_BLOCKERS),
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def load_closed(raw: bytes) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    require(type(value) is dict, "closed object required")
    return value


def checked_bytes(binding: dict, *, executable: bool = False) -> bytes:
    require(type(binding) is dict and set(binding) == {"path", "sha256"}, "closed input binding")
    name, digest = binding["path"], binding["sha256"]
    require(type(name) is str and name and not name.startswith("/") and "\\" not in name and
            "//" not in name and all(p not in ("", ".", "..") for p in name.split("/")),
            "unsafe input path")
    require(type(digest) is str and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
            "invalid input digest")
    path = REPO / name
    require(path.is_file() and not path.is_symlink() and
            all(not ancestor.is_symlink() for ancestor in path.parents if ancestor != REPO) and
            path.resolve().is_relative_to(REPO),
            "selected input absent or unsafe: " + name)
    if executable:
        require(path.stat().st_mode & 0o111 == 0o111, "native executable mode differs")
    raw = path.read_bytes()
    require(sha(raw) == digest, "selected input bytes changed: " + name)
    return raw


def checked_t35_selection(inputs: dict) -> None:
    """Join caller-labelled bindings to the four independently pinned modules."""
    for key, filename in T35_KEY_FILES.items():
        expected_path = (T35_PARENT / "t35_external_v1" / filename).relative_to(REPO).as_posix()
        expected = {"path": expected_path, "sha256": TRUSTED_T35[filename]}
        require(inputs[key] == expected, "selected T35 code provenance differs: " + key)


def checked_imported_closure() -> None:
    """Reject preloaded/redirected modules with a different path or byte digest.

    This remains a quiescent-process construction check, not an immutable
    import-custody mechanism for later effectful execution.
    """
    for key, module_name in T35_MODULES.items():
        module = sys.modules.get(module_name)
        require(module is not None and type(getattr(module, "__file__", None)) is str,
                "selected T35 module absent after projection: " + key)
        expected = T35_PARENT / "t35_external_v1" / T35_KEY_FILES[key]
        actual = Path(module.__file__)
        require(actual == expected and not actual.is_symlink() and
                hashlib.sha256(actual.read_bytes()).hexdigest() == TRUSTED_T35[T35_KEY_FILES[key]],
                "imported T35 module path/bytes differ: " + key)


def apply_inverse(projected: bytes, patch: list[dict]) -> bytes:
    """Reconstruct the preimage solely from projected bytes and recorded edits."""
    lines = projected.splitlines(keepends=True)
    cursor = 0
    reverse = bytearray()
    for edit in patch:
        require(type(edit) is dict and set(edit) == {"op", "j0", "j1", "projected_sha256",
                                                      "original_sha256", "old_base64"}, "closed inverse edit")
        op, j0, j1 = edit["op"], edit["j0"], edit["j1"]
        require(op in ("equal", "replace", "delete", "insert") and
                type(j0) is int and type(j1) is int and cursor == j0 and j0 <= j1 <= len(lines),
                "inverse patch order differs")
        span = b"".join(lines[j0:j1])
        require(sha(span) == edit["projected_sha256"], "projected span differs")
        if op == "equal":
            require(edit["old_base64"] is None, "equal inverse edit carries replacement")
            old = span
        else:
            require(type(edit["old_base64"]) is str, "missing inverse replacement")
            try:
                old = base64.b64decode(edit["old_base64"], validate=True)
            except ValueError as error:
                raise ValueError("invalid inverse replacement") from error
        require(sha(old) == edit["original_sha256"], "inverse replacement differs")
        reverse.extend(old)
        cursor = j1
    require(cursor == len(lines), "inverse patch did not cover projected bytes")
    return bytes(reverse)


def inverse_diff(original: bytes, projected: bytes) -> dict:
    """Emit an exact inverse edit script and test reconstruction from projection."""
    patch = []
    old_lines = original.splitlines(keepends=True)
    new_lines = projected.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for opcode, i0, i1, j0, j1 in matcher.get_opcodes():
        old_span = b"".join(old_lines[i0:i1])
        new_span = b"".join(new_lines[j0:j1])
        require(opcode != "equal" or old_span == new_span, "equal edit changed")
        patch.append({"op": opcode, "j0": j0, "j1": j1,
                      "projected_sha256": sha(new_span), "original_sha256": sha(old_span),
                      "old_base64": None if opcode == "equal" else base64.b64encode(old_span).decode("ascii")})
    recovered = apply_inverse(projected, patch)
    require(recovered == original, "inverse diff failed")
    return {"patch": patch, "patch_sha256": sha(canonical(patch)),
            "inverse_recovered_sha256": sha(recovered), "operation_count": len(patch)}


def prepare(selection: dict) -> dict:
    require(set(selection) == {"schema_version", "layout", "episode_proposal", "inputs",
                               "preimages", "expected_projections", "pin_order", "future_pins", "feasibility"},
            "closed selection shape differs")
    require(selection["schema_version"] == SCHEMA, "selection schema differs")
    layout_row = selection["layout"]
    require(set(layout_row) == {"family", "snapshot", "instance"}, "closed layout")
    layout = role_stage.DisposableLayout(family=PurePosixPath(layout_row["family"]),
                                         snapshot=PurePosixPath(layout_row["snapshot"]),
                                         instance=layout_row["instance"])
    require(str(layout.family) == "/tmp/" + layout.instance and str(layout.snapshot) == "/workspace",
            "local fixture layout differs")
    episode = selection["episode_proposal"]
    require(set(episode) == {"identity_prefix", "principal_ref", "assignment_version_ref",
                             "period_ref", "not_before", "expires_at", "scope_ref",
                             "authority_effect", "authorization_state"}, "closed episode proposal")
    prefix = "completion-" + layout.instance
    require(episode["identity_prefix"] == prefix and
            episode["principal_ref"] == "principal:" + prefix and
            episode["assignment_version_ref"] == "agent-assignment:" + prefix + "@1.0.0-candidate.1" and
            episode["period_ref"] == "protocol:" + prefix + "-period/v1" and
            episode["scope_ref"] == "scope:" + prefix and
            episode["authority_effect"] == "none" and
            episode["authorization_state"] == "NOT_GRANTED", "episode identity or authority differs")
    start = datetime.fromisoformat(episode["not_before"])
    end = datetime.fromisoformat(episode["expires_at"])
    require(start.utcoffset() == timedelta(0) and end - start == timedelta(hours=24),
            "fresh fixed 24-hour UTC period required")
    require(start >= datetime(2026, 10, 20, tzinfo=timezone.utc), "historical episode period reused")
    require(tuple(selection["pin_order"]) == PIN_ORDER, "acyclic pin order differs")
    require(type(selection["future_pins"]) is dict and
            set(selection["future_pins"]) == {"source_package", "mapped_package", "context_package"} and
            all(value is None for value in selection["future_pins"].values()),
            "future signed package pin fabricated")

    inputs = selection["inputs"]
    require(set(inputs) == {"constructor", "phase_rebind", "hardener", "path_contract",
                            "compose", "dockerfile", "native", "source_manifest",
                            "source_episode", "source_authorization", "source_dependencies"},
            "closed external input set differs")
    checked_t35_selection(inputs)
    for key, binding in inputs.items():
        if key == "source_dependencies":
            require(binding == role_stage.SOURCE_DEPENDENCIES, "hardcoded Source dependency pins differ")
            for row in binding.values():
                checked_bytes(row)
        else:
            checked_bytes(binding, executable=(key == "native"))
    expected_source = load_closed(checked_bytes(inputs["source_manifest"]))
    require(expected_source["environment"] == {"python": "3.14.4", "jsonschema": "4.23.0",
                                               "cryptography": "46.0.5"}, "source environment changed")
    require(inputs["native"] == {"path": str(role_stage.NATIVE_REL), "sha256": role_stage.NATIVE_SHA},
            "selected native pin differs")
    native = checked_bytes(inputs["native"], executable=True)
    require(native[:5] == b"\x7fELF\x02" and native[5] == 1 and
            int.from_bytes(native[18:20], "little") == 62 and
            b"/lib64/ld-linux-x86-64.so.2\0" in native and
            all((name + "\0").encode() in native for name in
                ("libgcc_s.so.1", "libc.so.6", "ld-linux-x86-64.so.2")),
            "selected native ELF/ABI differs")
    original_episode = load_closed(checked_bytes(inputs["source_episode"]))
    require(original_episode["authorization_binding"] == inputs["source_authorization"] and
            original_episode["expires_at"] < episode["not_before"],
            "historical authorization/period selection differs")
    require(b"FROM python:3.12-slim-bookworm" in checked_bytes(inputs["dockerfile"]) and
            b"../../..:/workspace:ro" in checked_bytes(inputs["compose"]),
            "container feasibility preimage changed")
    require(selection["feasibility"] == EXPECTED_FEASIBILITY,
            "unsafe container feasibility claim")

    expected = role_stage.entries(layout)
    preimages = selection["preimages"]
    require(type(preimages) is list and len(preimages) == 27 and
            [x["path"] for x in preimages] == [x[1] for x in expected] and
            all(set(x) == {"path", "sha256"} for x in preimages),
            "closed ordered 27-role preimages differ")
    selected = {}
    for row in preimages:
        selected[row["path"]] = checked_bytes(row)
    staged = role_stage.stage_rows(layout, lambda name: selected[name])
    checked_imported_closure()
    projections = selection["expected_projections"]
    require(type(projections) is list and len(projections) == 27 and
            all(type(row) is dict and set(row) == {"path", "sha256"} for row in projections) and
            projections == [row["output"] for row in staged],
            "selected exact AST/resource projection differs")
    rows = []
    for source, stage in zip(preimages, staged, strict=True):
        require(stage["input"] == source, "constructor input binding differs")
        projected = stage["bytes"]
        rows.append({"role": stage["role"], "preimage": source,
                     "proposal": stage["output"], "preimage_size": len(selected[source["path"]]),
                     "proposal_size": len(projected),
                     "inverse_diff": inverse_diff(selected[source["path"]], projected)})
    require(len(rows) == 27 and len({r["proposal"]["path"] for r in rows}) == 27,
            "projected role count differs")
    return {"schema_version": SCHEMA, "status": "PROPOSED_SELECTION_ONLY",
            "effect": "NOT_RUN", "layout": layout_row, "episode_proposal": episode,
            "selected_inputs": inputs, "roles": rows, "pin_order": list(PIN_ORDER),
            "future_pins": selection["future_pins"], "phase_rebind_status": "DEFERRED_UNTIL_SIGNED_PREDECESSORS",
            "feasibility": selection["feasibility"],
            "claim_ceiling": "Exact current template preimages and T35 effect-sealed projections only; no runnable Docker Source8 chain, fresh grant, signed package, installed role, host qualification, or original-task acceptance."}


def main() -> None:
    args = argparse.ArgumentParser()
    args.add_argument("--selection", type=Path, default=INPUT)
    ns = args.parse_args()
    value = prepare(load_closed(ns.selection.read_bytes()))
    sys.stdout.buffer.write(canonical(value))


if __name__ == "__main__":
    main()
