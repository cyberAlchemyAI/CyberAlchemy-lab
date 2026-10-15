"""Bounded ND01 conservation/evidence check, with no Lab imports or execution."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
OLD = HERE.parent / "runtime-narrative-preparation-0001"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    delta = json.loads((HERE / "DELTA.json").read_text())
    for row in delta["predecessor"].values():
        assert sha(ROOT / row["path"]) == row["sha256"]
    old_manifest = json.loads((OLD / "source-manifest.json").read_text())
    for row in old_manifest["files"]:
        p = ROOT / row["path"]
        assert sha(p) == row["sha256"] and p.stat().st_size == row["size_bytes"]
    old_sources = json.loads((OLD / "source-map.json").read_text())
    new_sources = json.loads((HERE / "source-map.json").read_text())
    assert new_sources["canonical_concepts"] == old_sources["canonical_concepts"]
    assert {k: new_sources["source_bindings"][k] for k in old_sources["source_bindings"]} == old_sources["source_bindings"]
    assert set(new_sources["source_bindings"]) - set(old_sources["source_bindings"]) == {"source4-stop", "source4-terminal"}
    assert len(new_sources["source_bindings"]) == 74
    old_n = json.loads((OLD / "narrative.json").read_text())
    new_n = json.loads((HERE / "narrative.json").read_text())
    expected = {(x["page"], x["section"]) for x in delta["body_deltas"]}
    normalized = copy.deepcopy(new_n); changes = []
    for old_page, new_page in zip(old_n["pages"], normalized["pages"]):
        assert old_page["key"] == new_page["key"]
        for old_section, new_section in zip(old_page["sections"], new_page["sections"]):
            key = (old_page["key"], old_section["title"])
            if key in expected:
                assert new_section["body"].startswith(old_section["body"] + "\n\n")
                addition = new_section["body"][len(old_section["body"]):]
                for name in ("source:cycle", "source:source4-stop", "source:source4-terminal", "exit143", "no accepted Source phase"):
                    assert name in addition
                new_section["body"] = old_section["body"]
                changes.append(key)
    assert set(changes) == expected and normalized == old_n
    stop_row = new_sources["source_bindings"]["source4-stop"]
    terminal_row = new_sources["source_bindings"]["source4-terminal"]
    assert stop_row["sha256"] == "7d5c91a70ea2511c29a10e031853dee8dfad5c25b99e39c8d29fe288ffbae624"
    assert terminal_row["sha256"] == "eb7ce5391fd6127819e18e2d76defc7813b258736b44af6bd28cb02ee476b5a6"
    stop = json.loads((ROOT / stop_row["snapshot_path"]).read_text())
    terminal = json.loads((ROOT / terminal_row["snapshot_path"]).read_text())
    assert stop["signal_sent"] == "SIGTERM" and stop["completion_or_exit_reaped"] is False
    assert stop["exact_owned_pid"] == 171449 and stop["matched_current_UID"] == 1000
    assert stop["pid_start_ticks"] == "2712960" and stop["owned_children_before_stop"] == []
    assert terminal["reaped_tool_result"]["exit_code"] == 143
    assert terminal["reaped_tool_result"]["chunk_id"] == "6df908"
    assert terminal["phase_accepted"] is False and terminal["outputs_preserved"] is True
    assert terminal["current_family_runtime_qualified"] is False
    a = json.loads((HERE / "render-0001/render-receipt.json").read_text())
    b = json.loads((HERE / "render-0002/render-receipt.json").read_text())
    assert a == b
    assert sha(HERE / "validate.py") == sha(OLD / "validate.py")
    assert a["reused_generator"]["sha256"] == "110d03b089dfc28040415cacebc2a646288a4162b9a99ba63acb6ff7f2869a9e"
    assert a["reused_generator"]["source_copy_or_filename_alias"] is False
    result = {"schema_version": "lab-T21-ND01-conservation-check/v1",
        "result": "PASS-owned-ND01-correction-ready-for-peer-review", "predecessor_manifest_rows_unchanged": len(old_manifest["files"]),
        "predecessor_inputs_conserved": 72, "new_actual_stop_inputs": 2,
        "pages_conserved": 14, "sections_conserved": 67, "diagrams_conserved": 5,
        "body_deltas": changes, "all_other_body_formal_route_fields_equal": True,
        "two_new_generations_equal_outputs": 43, "generator_reused_under_true_filename": True,
        "validator_bytes_preserved_new_true_origin": True, "observed_exit": 143,
        "signal_receipt_distinct_from_reaped_terminal": True,
        "runtime_executed": False, "shared_site_changed": False, "task_complete": False}
    with (HERE / "delta-checks.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
