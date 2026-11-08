"""Cold readback of the selected T29 local continuity receipt."""
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
CODE_SHA = "de40654882c0351a50dc6b5cf96fecea54ff5ae8d24a5663261eaed52328b569"
RECEIPT_SHA = "e61db562b2b24540f79d142699ceb19adab8e07bac276e912b362b74b23b75d3"


def selected(path: Path, expected: str) -> bytes:
    state = path.lstat()
    if not stat.S_ISREG(state.st_mode) or path.is_symlink():
        raise ValueError("unsafe T29 selected file")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("T29 selected byte changed")
    return raw


def verify() -> dict:
    selected(HERE / "continuity.py", CODE_SHA)
    receipt = json.loads(selected(HERE / "RUN-0002.json", RECEIPT_SHA))
    consumed = receipt["consumption"]
    if not (receipt["schema_version"] == "lab-t29-installed-continuity/v1" and
            receipt["result"] == "PASS" and receipt["local_t29_check_passed"] is True and
            receipt["original_scope_complete"] is False and receipt["task_complete"] is False and
            receipt["original_admitted_operation"] is False and
            receipt["api40_installed_replay"] is False and
            receipt["repository_authority_effect"] == "none" and
            receipt["external_effects"] == 0 and
            receipt["fixture_manifest_sha256"] ==
                "1e00e6fd7f1baf7f8cfcd0c0ae7c11ab66649e05cc9575705bee968117ae0346" and
            receipt["fixture_release_sha256"] ==
                "a8cfacd9e15b65184c1b87a284a699475850b8a783a354102301f50ccbe9cb3e" and
            receipt["installed_fixture_verified"] is True and
            receipt["fresh_restart_replay"] is True and
            receipt["foreign_residue_preserved"] is True and
            receipt["retained_candidate_replay_before_cleanup"] is True and
            receipt["owned_temp_root_removed"] is True and
            receipt["signed_local_work_sequence"] == 1 and
            receipt["fresh_process_operations"] == 15 and
            receipt["rolled_back_head"] != receipt["signed_local_work_head"] and
            consumed["head"] == receipt["signed_local_work_head"] and
            consumed["session_lease_seconds"] == 120.0 and
            consumed["bounded_input_consumed"] is True and
            consumed["session_closed"] is True and
            consumed["work_version"] == "work:lab-runtime:t29-local-work@candidate.1"):
        raise ValueError("T29 receipt claim/lineage mismatch")
    return {"result": "PASS", "continuity_code_sha256": CODE_SHA,
            "selected_receipt_sha256": RECEIPT_SHA, "local_t29_check_passed": True,
            "original_scope_complete": False, "api40_installed_replay": False}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True, indent=2))
