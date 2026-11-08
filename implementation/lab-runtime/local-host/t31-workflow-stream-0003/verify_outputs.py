#!/usr/bin/env python3
"""Verify W06 producer/consumer carrier closure without inventing WorkflowRun events."""

from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
T31_V2 = HERE.parent / "t31-workflow-stream-0002"
sys.path.insert(0, str(T31_V2))
from stream import artifact, check_output_set, digest, inventory, need, original_carriers  # noqa: E402

INDEX_SHA256 = "b0d75e84fafcf66aca669777f14116624f9477915161812c77b3614a7ab2354a"
T31_V2_RESULT_SHA256 = "c9f85acd1b9316489d26eb1bbbb3e43d617f2903b7e627b74b86983c2c9e1445"
OUTPUTS = {
    "lesson-prepared": ("lesson_ref",),
    "application-recorded": ("application_ref",),
    "outcome-assessed": ("outcome_ref", "improvement_signal_ref"),
}


def checked_file(root: Path, relative: str, expected: str) -> bytes:
    path = root / relative
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()),
         "missing or escaped W06 original file")
    raw = path.read_bytes()
    need(digest(raw) == expected, "W06 original file bytes differ: " + relative)
    return raw


def verify(root: Path, *, index_sha256: str = INDEX_SHA256) -> dict:
    need(digest((T31_V2 / "run-0001/RESULT.json").read_bytes()) == T31_V2_RESULT_SHA256,
         "T31 predecessor result changed")
    index_raw = checked_file(root, "episode-index.json", index_sha256)
    index = json.loads(index_raw)
    need(index["schema_version"] == "lab-W06-real-learning-episode/v1-candidate" and
         index["signed_lesson_persisted"] is True and index["actual_later_application"] is True and
         index["selection_count"] == 1 and index["applications_after_selection"] == 0 and
         index["first_Agent_invalidated"] is True and index["first_memory_erased"] is True and
         index["later_Agent_closed"] is True and index["later_memory_erased"] is True,
         "W06 actual two-Agent episode differs")
    need(index["authority_effect"] == "none" and index["actual_owner_outcome"] is None and
         index["canonical_effects_applied"] == 0 and index["lesson_promoted"] is False and
         index["general_benefit_established"] is False and index["native_domain_mapping"] is False,
         "W06 candidate claim ceiling changed")
    need(index["outcome_disposition"] == "supported-for-this-controlled-case",
         "bounded outcome differs")
    need(digest((root / "branch.snapshot").read_bytes()) == index["archive_sha256"],
         "W06 signed branch export changed")
    for row in index["original_sources"]:
        checked_file(ROOT, row["path"], row["sha256"])
    records = {}
    for row in index["records"]:
        raw = checked_file(root, row["path"], row["sha256"])
        body = json.loads(raw)
        need(body["kind"] == row["kind"] and row["version_ref"].startswith(body["node_id"] + "@"),
             "W06 record kind/revision differs")
        need(row["version_ref"] not in records, "duplicate W06 record revision")
        records[row["version_ref"]] = (row, body)
    for row in index["blobs"]:
        checked_file(root, row["path"], row["sha256"])
    selected = inventory()
    carriers = original_carriers()
    closures = []
    for name, keys in OUTPUTS.items():
        transition_ref = "transition:operational-learning:" + name
        transition = next(r for r in selected["transitions"] if r["transition_ref"] == transition_ref)
        need(len(keys) == len(transition["required_output_carriers"]), "selected W06 carrier set differs")
        originals = []
        for key, carrier in zip(keys, transition["required_output_carriers"]):
            record, _ = records[index[key]]
            raw = checked_file(root, record["path"], record["sha256"])
            header, parsed = artifact(root / record["path"], carrier)
            need(parsed == raw and header["version_ref"] == index[key], "W06 output record binding differs")
            carriers.output(header, raw, scope_ref=header["scope_ref"])
            originals.append((header, raw))
        headers = check_output_set(transition, originals)
        closures.append({"transition_ref": transition_ref, "output_artifact_refs": headers,
                         "producer_record_paths": [records[index[key]][0]["path"] for key in keys]})
    lesson = records[index["lesson_ref"]][1]
    application = records[index["application_ref"]][1]
    outcome = records[index["outcome_ref"]][1]
    signal = records[index["improvement_signal_ref"]][1]
    target = records[index["improvement_target_ref"]][1]
    need(checked_file(root, "draft/operational-lesson-335827415ca02a7697a8.json",
                      records[index["lesson_ref"]][0]["sha256"]) ==
         checked_file(root, records[index["lesson_ref"]][0]["path"], records[index["lesson_ref"]][0]["sha256"]),
         "later Agent did not import exact drafted Lesson bytes")
    source = index["lesson_from_committed_Project_State"]
    need(source["reference"] == index["lesson_ref"] and source["effective_state"] == "local-admitted-current" and
         source["source_binding"]["path"] == "transactions/0000000001.json" and
         source["source_binding"]["sha256"] == records[index["lesson_ref"]][0]["sha256"],
         "later Project State did not select exact signed Lesson")
    need(application["payload"]["lesson_revision_ref"] == index["lesson_ref"] and
         application["payload"]["application_posture"] == "applied-in-controlled-later-case" and
         outcome["payload"]["lesson_application_ref"] == index["application_ref"] and
         outcome["payload"]["disposition"] == index["outcome_disposition"] and
         outcome["payload"]["predicted_outcome"] == lesson["payload"]["predicted_benefit"],
         "later application/outcome did not consume exact Lesson")
    manifest = json.loads((root / "later/application-manifest.json").read_bytes())
    need(manifest["lesson_ref"] == index["lesson_ref"] and manifest["result"]["validated_records"] == 13 and
         manifest["original_source_unchanged"] is True and manifest["inline_only_change"] is True,
         "actual later preparation observation differs")
    need(signal["payload"]["source_refs"][-1] == index["outcome_ref"] and
         set((index["lesson_ref"], index["outcome_ref"], index["improvement_signal_ref"])) <= set(target["payload"]["basis_refs"]),
         "later improvement proposal did not consume outcome/signal")
    effect = json.loads((root / "later/unapplied-effect.json").read_bytes())
    need(effect["applied"] is False and effect["lesson_promoted"] is False and
         effect["general_benefit_established"] is False, "W06 proposed effect was misreported as applied")
    return {"result": "PASS-candidate-W06-carrier-and-consumer-only",
            "carrier_sets_corresponding_to_selected_transition_refs": closures,
            "carrier_set_count": 3, "output_artifact_count": 4,
            "native_workflow_transition_events": 0,
            "cumulative_local_candidate_transition_refs_before_W06": 4,
            "remaining_original_transition_identities_before_W06": 24,
            "source_or_authority_effect": "none",
            "claim_ceiling": "One isolated historical W06 signed candidate Lesson and later controlled application; three selected carrier sets and later references checked. No original WorkflowRun event, current Source8 cut, canonical Lesson promotion, general benefit, or T31 qualification."}


if __name__ == "__main__":
    print(json.dumps(verify(HERE / "run-0007"), sort_keys=True, indent=2))
