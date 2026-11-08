"""Build an inert, source-checked G04 worksheet; never select a route or grant."""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat


ROOT = Path(__file__).resolve().parents[6]
MATRIX = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json"
SELECTION = "product/lab/release-candidates/v1/release-validation/0001/final-materializer-selection-0276.json"
OUT = "docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U10-02/scope-decision-preparation-0002.json"
EXPECTED = {
    MATRIX: "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628",
    SELECTION: "c5f290c5f5bebbbf3b8572a9b3457d265e9ab632a35e6b4cc5a4a78dd2f99465",
}
PROJECT = "project:cyberalchemy-v2-to-lab-migration"


def _open_parent_dirfd(path):
    """Hold each directory from / through the target parent without aliases."""
    path = Path(path)
    if not path.is_absolute() or any(part in (".", "..") for part in path.parts):
        raise ValueError("unsafe absolute path")
    parts = path.parts
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for part in parts[1:-1]:
            next_fd = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=fd,
            )
            os.close(fd)
            fd = next_fd
        return fd, parts[-1]
    except BaseException:
        os.close(fd)
        raise


def read_binding(binding, root=ROOT):
    rel = binding["path"]
    p = PurePosixPath(rel)
    if p.is_absolute() or not rel or any(x in ("", ".", "..") for x in rel.split("/")):
        raise ValueError("unsafe source path")
    try:
        parent_fd, name = _open_parent_dirfd(Path(root) / p)
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd)
            with os.fdopen(fd, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ValueError("source is not a regular file")
                data = stream.read()
        finally:
            os.close(parent_fd)
    except OSError as error:
        raise ValueError("source alias or unreadable path") from error
    if hashlib.sha256(data).hexdigest() != binding["sha256"]:
        raise ValueError("source drift")
    return data


def selected_rows(matrix, selection, root=ROOT):
    routes = matrix["routes"]
    members = selection["members"]
    if len(routes) != 230 or len(members) != 363:
        raise ValueError("original inventory changed or omitted")
    seen = set()
    rows = []
    for route in routes:
        index = route["selection_index"]
        if not isinstance(index, int) or index in seen or not 0 <= index < len(members):
            raise ValueError("duplicate or invalid selection index")
        seen.add(index)
        member = members[index]
        axes = member["axes"]
        required = {
            "member_ref": member["member_ref"],
            "body_binding": axes["body_binding"],
            "body_scope_ref": axes["original_body_scope_ref"],
            "carrier_ref": axes["carrier_ref"],
            "category": axes["category"],
            "operation": axes["operation"],
            "decision_ref": axes["decision_ref"],
            "version_ref": axes["version_ref"],
        }
        if any(route.get(k) != v for k, v in required.items()):
            raise ValueError("route differs from original selection")
        if route["operation"] != "admit" or route["category"] != "artifact-instance":
            raise ValueError("unexpected original operation")
        if route["body_scope_ref"] == PROJECT:
            raise ValueError("route no longer requires domain disposition")
        body = json.loads(read_binding(route["body_binding"], root))
        if body.get("scope_ref") != route["body_scope_ref"]:
            raise ValueError("body scope differs from original selection")
        if body.get("node_id") != axes["identity_ref"]:
            raise ValueError("body identity differs from original selection")
        for key in ("consumer_code_binding", "producer_preparation_binding", "review_packaging_code_binding", "descriptor_binding", "schema_binding"):
            read_binding(route[key], root)
        for binding in route["original_body_origin_bindings"]:
            read_binding(binding, root)
        correction = route["correction_eligibility"]
        read_binding(correction["profile_binding"], root)
        if correction["eligible"] is not False:
            raise ValueError("historical correction eligibility changed")
        roles = route["owner_roles_required"]
        if roles != member["proposed_owner_roles"]:
            raise ValueError("role selector drift")
        scope = route["body_scope_ref"]
        rows.append({
            "selection_index": index,
            "member_ref": route["member_ref"],
            "original_identity_ref": body["node_id"],
            "version_ref": route["version_ref"],
            "operation": "admit",
            "direction": "original body -> original native O.prepare artifact-instance target",
            "body_scope_ref": scope,
            "body_binding": route["body_binding"],
            "original_body_origin_bindings": route["original_body_origin_bindings"],
            "carrier_ref": route["carrier_ref"],
            "schema_binding": route["schema_binding"],
            "descriptor_binding": route["descriptor_binding"],
            "decision_ref": route["decision_ref"],
            "producer_preparation_binding": route["producer_preparation_binding"],
            "review_packaging_code_binding": route["review_packaging_code_binding"],
            "consumer_code_binding": route["consumer_code_binding"],
            "original_correction_profile_binding": correction["profile_binding"],
            "original_correction_eligible": False,
            "original_correction_refusal_reasons": correction["reasons"],
            "visibility": route["visibility"],
            "proposed_owner_roles": roles,
            "candidate_alternatives": [
                {"id": "exact-domain-native-consumer", "scope_ref": scope, "condition": "independent domain grant, governing owner role and current source/cut/schema/consumer evidence"},
                {"id": "retain-refusal", "scope_ref": None, "condition": "no eligible current domain route or owner authority"},
                {"id": "separate-reviewed-correction", "scope_ref": scope, "condition": "new individually reviewed narrow correction contract and grant; original correction profile is ineligible"},
            ],
            "candidate_actor_alternatives": [
                {"id": "proposed-role-holder", "role_refs": roles, "condition": "actual current governing assignment, member scope and period independently proven"},
                {"id": "separately-appointed-domain-owner", "role_refs": [], "condition": "actual governing appointment and exact member/domain grant independently proven"},
                {"id": "none-retain-refusal", "role_refs": [], "condition": "no eligible current actor proven"},
            ],
            "accountable_questions": [
                f"For {route['member_ref']}, is {scope} the intended unchanged body scope and which producer/source cut is current?",
                f"Which actual consumer, configuration, principal and governing owner are authorized for {scope}, this carrier and admit operation during the selected period?",
                "If no exact-domain route is authorized, should this item remain refused or receive a separately reviewed narrow correction?",
            ],
            "selected_alternative": None,
            "selected_direction": None,
            "selected_consumer_endpoint": None,
            "selected_actor_alternative": None,
            "selected_principal": None,
            "current_grant_binding": None,
            "current_owner_decision_binding": None,
            "operational_result": "not-run",
            "authority_effect": "none",
        })
    if len(seen) != 230:
        raise ValueError("route omission")
    return rows


def build(root=ROOT):
    matrix = json.loads(read_binding({"path": MATRIX, "sha256": EXPECTED[MATRIX]}, root))
    selection = json.loads(read_binding({"path": SELECTION, "sha256": EXPECTED[SELECTION]}, root))
    rows = selected_rows(matrix, selection, root)
    return {
        "schema_version": "lab-u10-02-inert-scope-decision-preparation/v1",
        "authority_effect": "none",
        "task_complete": False,
        "selected_scope_dispositions": 0,
        "actual_successful_operational_routes": 0,
        "original_matrix_binding": {"path": MATRIX, "sha256": EXPECTED[MATRIX]},
        "original_selection_binding": {"path": SELECTION, "sha256": EXPECTED[SELECTION]},
        "original_consumer_rule": "proposal scope equals provisioned config scope; absent eligible correction, body scope equals proposal scope",
        "route_count": len(rows),
        "rows": rows,
    }


def validate_preparation(value, root=ROOT):
    if value != build(root):
        raise ValueError("worksheet differs from exact inert original-source preparation")
    return {"route_count": 230, "selected_scope_dispositions": 0, "authority_effect": "none"}


def write_new(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    parent_fd, name = _open_parent_dirfd(path)
    try:
        fd = os.open(
            name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o644,
            dir_fd=parent_fd,
        )
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(parent_fd)
    finally:
        # A failed write leaves its owned partial file for explicit inspection;
        # path-based cleanup could unlink a different inode after a swap.
        os.close(parent_fd)


if __name__ == "__main__":
    write_new(ROOT / OUT, build())
    print("LC-U10-02 inert worksheet: 230 rows, zero selected routes")
