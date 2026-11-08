"""Disposable native append of the 88 inert T13 technical successors."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import types


ROOT = Path(__file__).resolve().parents[4]
PREPARATION = ROOT / "implementation/lab-runtime/local-host/t13-event-materialization-0001/materialize.py"
PREPARATION_SHA = "f14f67f355b9bba2bb541726a817870628b93f6e54a78e865762a90a274c8f7f"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value, message):
    if not value:
        raise ValueError(message)


def selected_preparation():
    raw = PREPARATION.read_bytes()
    need(sha(raw) == PREPARATION_SHA, "selected T13 preparation changed")
    module = types.ModuleType("_cal_t13_selected_preparation")
    module.__file__ = str(PREPARATION)
    exec(compile(raw, str(PREPARATION), "exec", dont_inherit=True), module.__dict__)
    return module


def native_call(m, action, *args):
    # The preparation's exact executable and installation receipt are checked
    # afresh before every native call.
    m.exact(m.NATIVE, m.NATIVE_SHA)
    m.exact(m.INSTALL, m.INSTALL_SHA)
    result = subprocess.run([str(m.NATIVE), action, *map(str, args)],
                            capture_output=True, check=False, timeout=120)
    return result


def write_input(path, value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    with path.open("xb") as stream:
        stream.write(raw)
    path.chmod(0o600)
    return sha(raw)


def append_batch(m, semantic_dir, governance_dir, body, temp):
    path = temp / "native-input.json"
    write_input(path, body)
    try:
        return native_call(m, "append", semantic_dir, governance_dir, path)
    finally:
        path.unlink()


def fresh_read(m, semantic_dir, governance_dir):
    result = native_call(m, "read", semantic_dir, governance_dir, 88)
    need(result.returncode == 0 and not result.stderr, "native cold read refused")
    value = json.loads(result.stdout)
    need(value["result"] == "PASS" and value["checkpoint_parity"] == "PASS" and
         value["authority_effect"] == "none" and
         len(value["semantic_events"]) == 88 and len(value["governance_events"]) == 176,
         "native cold read count or parity differs")
    return value


def run():
    m = selected_preparation()
    account = m.parse(m.exact(m.ACCOUNT, m.ACCOUNT_SHA))
    snapshot = m.parse(m.exact(m.ARCHIVE, m.ARCHIVE_SHA))
    original = m.archive_events(snapshot)
    drafts, rows = m.prepare(account, snapshot)
    successors, canonical_bodies, aggregate_sha = m.native_seal(drafts)
    need(len(successors) == len(canonical_bodies) == len(rows) == 88,
         "technical successor count differs")
    original_batch = {
        "semantic": [original["semantic"][i] for i in range(1, 89)],
        "governance": [original["governance"][i] for i in range(1, 89)],
    }
    successor_batch = {"semantic": [], "governance": successors}
    with tempfile.TemporaryDirectory(prefix="cal-t13-native-append-", dir="/tmp") as name:
        temp = Path(name)
        need(not temp.resolve().is_relative_to(ROOT.resolve()),
             "temporary native root entered repository")
        temp.chmod(0o700)
        semantic_dir = temp / "semantic"
        governance_dir = temp / "governance"
        semantic_dir.mkdir(mode=0o700)
        governance_dir.mkdir(mode=0o700)
        first = append_batch(m, semantic_dir, governance_dir, original_batch, temp)
        need(first.returncode == 0 and not first.stderr,
             "original frozen native bootstrap append refused")
        need(len(list(semantic_dir.iterdir())) == len(list(governance_dir.iterdir())) == 88,
             "original bootstrap file count differs")
        bootstrap = sorted((p.name, sha(p.read_bytes())) for p in governance_dir.iterdir())
        changed = copy.deepcopy(drafts)
        changed[0]["previous_event_digest"] = "0" * 64
        bad_successors, _, _ = m.native_seal(changed)
        bad = append_batch(m, semantic_dir, governance_dir,
                           {"semantic": [], "governance": bad_successors}, temp)
        need(bad.returncode != 0 and b"GOVERNANCE_EVENT_CHAIN_BROKEN" in bad.stderr and
             bootstrap == sorted((p.name, sha(p.read_bytes())) for p in governance_dir.iterdir()),
             "wrong predecessor did not refuse without effect")
        second = append_batch(m, semantic_dir, governance_dir, successor_batch, temp)
        need(second.returncode == 0 and not second.stderr,
             "technical successor native append refused")
        cold = fresh_read(m, semantic_dir, governance_dir)
        need(cold["semantic_events"] == original_batch["semantic"],
             "cold native semantic event bodies differ")
        for i, (original_governance, successor) in enumerate(zip(original_batch["governance"], successors), 1):
            need(successor["previous_event_digest"] == original_governance["event_digest"] and
                 successor["stream_id"] == original_governance["stream_id"] and
                 successor["governance_cursor"] == 88 + i,
                 "technical successor lineage differs")
            need(cold["governance_events"][i - 1] == original_governance and
                 cold["governance_events"][88 + i - 1] == successor,
                 "cold native event body differs")
        before = sorted((p.name, sha(p.read_bytes())) for p in governance_dir.iterdir())
        duplicate = append_batch(m, semantic_dir, governance_dir, successor_batch, temp)
        need(duplicate.returncode != 0 and b"GOVERNANCE_CURSOR_NOT_CONTIGUOUS" in duplicate.stderr and
             before == sorted((p.name, sha(p.read_bytes())) for p in governance_dir.iterdir()),
             "duplicate successor append changed native state")
        after = fresh_read(m, semantic_dir, governance_dir)
        need(after == cold, "negative append changed cold native view")
        receipt = {
            "schema_version": "lab-T13-disposable-native-append/v1",
            "result": "PASS-bounded-disposable-native-append",
            "original_accounting_sha256": m.ACCOUNT_SHA,
            "original_archive_sha256": m.ARCHIVE_SHA,
            "selected_preparation_sha256": PREPARATION_SHA,
            "selected_native_executable_sha256": m.NATIVE_SHA,
            "native_aggregate_successor_seal_sha256": aggregate_sha,
            "original_semantic_events_appended": 88,
            "original_governance_events_appended": 88,
            "technical_successor_governance_events_appended": 88,
            "cold_semantic_events": len(cold["semantic_events"]),
            "cold_governance_events": len(cold["governance_events"]),
            "cold_checkpoint_parity": cold["checkpoint_parity"],
            "wrong_predecessor_refused_without_effect": True,
            "duplicate_refused_without_effect": True,
            "temporary_native_root_removed_on_return": False,
            "original_event_bytes_written_to_private_temporary_storage": True,
            "original_event_bytes_in_public_receipt": False,
            "owner_decisions_created": False,
            "authority_effect": "none",
            "T13_complete": False,
            "claim_ceiling": "All 88 inert technical successors appended after exact frozen predecessors in disposable native storage; no original adoption, owner Decision, current live head or repository effect.",
        }
    need(not temp.exists(), "temporary native root remained after run")
    receipt["temporary_native_root_removed_on_return"] = True
    receipt["runner_sha256"] = sha(Path(__file__).read_bytes())
    return receipt


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
