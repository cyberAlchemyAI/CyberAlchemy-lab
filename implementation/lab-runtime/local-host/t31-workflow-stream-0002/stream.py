#!/usr/bin/env python3
"""Cold-verifiable local evidence for two additional original output transitions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREVIOUS = HERE.parent / "t31-workflow-stream-0001"
sys.path.insert(0, str(PREVIOUS))
from inventory import check_output_set, digest, inventory  # noqa: E402

PREVIOUS_RESULT = PREVIOUS / "run-0001/RESULT.json"
PREVIOUS_RESULT_SHA256 = "308cad743f9d31773a8f709a7e0804701e0622ea803627369c01031a558cb6d7"
PREVIOUS_REFS = frozenset(("transition:engineering:assessed", "transition:research:evaluated"))
CATALOG = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-transitions-0001/carrier-catalog.json"
CATALOG_SHA256 = "b2709686d7a34ff704ebaa4c7dc78c18281208adfe2daeedf84fc5a0705e6ed8"
CONTRACTS = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v30/workflow_output_contracts.py"
NEW = {
    "engineering": ("transition:engineering:implemented", (
        ("workflow/generated-output.json", "cal.artifact-type.generated-output/v2"),
        ("workflow/evidence-set.json", "cal.artifact-type.evidence-set/v1"))),
    "research": ("transition:research:executed", (
        ("experiment-run.json", "cal.artifact-type.experiment-run/v1"),
        ("measurement-result.json", "cal.artifact-type.measurement-result/v1"))),
}


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def original_carriers():
    raw = CATALOG.read_bytes()
    need(digest(raw) == CATALOG_SHA256, "original carrier catalog changed")
    module = runpy.run_path(str(CONTRACTS))
    selected = module["parse"](raw)
    documents = {path: (ROOT / path).read_bytes() for row in selected["rows"]
                 for path in (row["schema_path"], row["artifact_path"])}
    return module["OriginalCarriers"](raw, CATALOG_SHA256, documents)


def artifact(path: Path, carrier: str) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    body = json.loads(raw)
    identity = body["node_id"]
    return ({"scope_ref": body["scope_ref"], "identity_ref": identity,
             "version_ref": identity + "@" + body.get("version", "candidate.1"),
             "carrier_ref": carrier, "byte_sha256": digest(raw)}, raw)


def check_trial_ids(trials: list) -> None:
    need(type(trials) is list and len(trials) == 3 and
         [row.get("sample") for row in trials] == [1, 2, 3],
         "three distinct ordered paired sample IDs required")


def link(kind: str, run: Path, selected: dict) -> dict:
    ref, outputs = NEW[kind]
    row = next(r for r in selected["transitions"] if r["transition_ref"] == ref)
    path = run / kind
    events = json.loads((path / "transitions.json").read_bytes())
    workflow = json.loads((path / "workflow-run.json").read_bytes())
    need(len(events) == 3 and len(workflow["event_bindings"]) == 3, "original phase count changed")
    event = events[1]
    need((event["from"], event["to"]) == (row["from_state"], row["to_state"]), "observed transition differs")
    event_sha = digest(canonical(event))
    need(workflow["event_bindings"][1]["sha256"] == event_sha, "WorkflowRun does not bind middle event")
    need(workflow["workflow_type_ref"] == f"workflow:{kind}:v1-candidate" and workflow["state"] == events[-1]["to"],
         "original WorkflowRun differs")
    originals = [artifact(path / relative, carrier) for relative, carrier in outputs]
    headers = check_output_set(row, originals)
    carriers = original_carriers()
    for header, raw in originals:
        carriers.output(header, raw, scope_ref=header["scope_ref"])
    need(len({h["scope_ref"] for h in headers}) == 1, "output scopes differ")
    refs = {h["carrier_ref"]: h["version_ref"] for h in headers}
    work_path = path / ("workflow/work.json" if kind == "engineering" else "work.json")
    work = json.loads(work_path.read_bytes())
    need(work["payload"]["project_ref"] == headers[0]["scope_ref"] and
         all(h["version_ref"] in work["payload"]["output_refs"] for h in headers),
         "later Work does not bind complete output set")
    consumer_paths = [str(work_path.relative_to(run))]
    if kind == "engineering":
        generated = json.loads((path / outputs[0][0]).read_bytes())
        evidence = json.loads((path / outputs[1][0]).read_bytes())
        assessment = json.loads((path / "workflow/work-outcome-assessment.json").read_bytes())
        action = json.loads((path / "action-receipt.json").read_bytes())
        corrected = (path / "workflow/tool/registered_evaluator.py").read_bytes()
        need(action["posture"] == "completed" and action["output_sha256"] == digest(corrected),
             "actual corrected source or action receipt differs")
        need(generated["payload"]["output_digest"] == "sha256:" + digest(corrected) and
             refs["cal.artifact-type.generated-output/v2"] in work["payload"]["output_refs"],
             "generated output does not bind actual source bytes")
        evidence_ref = refs["cal.artifact-type.evidence-set/v1"]
        need(evidence_ref in assessment["payload"]["evidence_refs"] and
             evidence_ref in work["evidence_refs"], "later assessment/Work did not consume evidence set")
        checks = json.loads((path / "assessment.json").read_bytes())["checks"]
        need(len(checks) == 7 and len(evidence["payload"]["item_refs"]) == 7,
             "seven observed engineering checks required")
        for name, check in checks.items():
            need("protocol:W03-" + name in evidence["payload"]["item_refs"] and
                 digest((path / "evidence" / check["evidence_path"]).read_bytes()) == check["evidence_sha256"],
                 "engineering evidence bytes or membership differ")
        need(assessment["payload"]["disposition"] == "unsupported" and
             checks["default-regression-complete"]["result"] == "FLAG",
             "historical default regression limitation lost")
        consumer_paths.append("engineering/workflow/work-outcome-assessment.json")
        observation = {"corrected_source_sha256": digest(corrected), "assessment_disposition": "unsupported"}
    else:
        experiment = json.loads((path / outputs[0][0]).read_bytes())
        measurement = json.loads((path / outputs[1][0]).read_bytes())
        finding = json.loads((path / "finding.json").read_bytes())
        evaluation = json.loads((path / "evaluation.json").read_bytes())
        action = json.loads((path / "action-receipt.json").read_bytes())
        journal = json.loads((path / "journal.json").read_bytes())
        observed_raw = (path / "observed.json").read_bytes()
        observed = json.loads(observed_raw)
        need(action["posture"] == journal["posture"] == "completed" and
             action["evidence_sha256"] == journal["evidence_sha256"] == event["detail"]["evidence_sha256"] == digest(observed_raw),
             "six-child action/evidence linkage differs")
        check_trial_ids(observed["trials"])
        for trial in observed["trials"]:
            number = trial["sample"]
            need(json.loads((path / f"sample-{number}.json").read_bytes()) == trial and
                 set(trial["observations"]) == {"direct", "facade"}, "original paired trial differs")
            for approach, observation_row in trial["observations"].items():
                for channel in ("stdout", "stderr"):
                    need(digest((path / f"sample-{number}-{approach}.{channel}").read_bytes()) == observation_row[channel + "_sha256"],
                         "original child process bytes differ")
        experiment_ref = refs["cal.artifact-type.experiment-run/v1"]
        measurement_ref = refs["cal.artifact-type.measurement-result/v1"]
        need(experiment["run_state"] == "completed" and measurement["subject_ref"] == experiment_ref and
             measurement_ref in experiment["measurement_result_refs"] and
             measurement_ref in finding["evidence_refs"] and
             "finding:lab-research:replay-comparison@candidate.1" in evaluation["payload"]["outcomes"][0]["evidence_refs"],
             "later finding/evaluation did not consume executed output")
        need(measurement["value"] == json.loads((path / "assessment.json").read_bytes())["residue_entropy_nats"],
             "later measurement differs from actual assessment")
        consumer_paths += ["research/finding.json", "research/evaluation.json"]
        observation = {"observed_sha256": digest(observed_raw), "replay_child_count": 6,
                       "hypothesis_disposition": json.loads((path / "assessment.json").read_bytes())["disposition"]}
    return {"transition_ref": ref, "event_sha256": event_sha,
            "workflow_run_sha256": digest((path / "workflow-run.json").read_bytes()),
            "output_artifact_refs": headers,
            "output_original_paths": [str((path / relative).relative_to(run)) for relative, _ in outputs],
            "later_consumers": [{"path": relative, "sha256": digest((run / relative).read_bytes())} for relative in consumer_paths],
            "observation": observation,
            "claim": "isolated original candidate producer with phase-bound output bytes and later consumer"}


def receipt(run: Path) -> dict:
    selected = inventory()
    need(json.loads((run / "INVENTORY.json").read_bytes()) == selected, "retained original inventory differs")
    previous_sha = digest(PREVIOUS_RESULT.read_bytes())
    need(previous_sha == PREVIOUS_RESULT_SHA256, "exact predecessor result bytes differ")
    previous = json.loads(PREVIOUS_RESULT.read_bytes())
    need(previous["observed_count"] == 2 and previous["remaining_transition_count"] == 26,
         "predecessor output claim changed")
    rows = [link(kind, run, selected) for kind in NEW]
    prior_refs = [r["transition_ref"] for r in previous["observed_terminal_output_transitions"]]
    new_refs = [r["transition_ref"] for r in rows]
    all_refs = prior_refs + new_refs
    need(len(prior_refs) == 2 and set(prior_refs) == PREVIOUS_REFS and
         len(all_refs) == 4 and len(set(all_refs)) == 4 and
         set(new_refs) == {spec[0] for spec in NEW.values()},
         "four distinct selected transition identities required")
    return {"schema_version": "lab-T31-local-middle-output-episode/v1",
            "predecessor_result_path": str(PREVIOUS_RESULT.relative_to(ROOT)),
            "predecessor_result_sha256": previous_sha,
            "new_output_transitions": rows, "new_count": len(rows),
            "cumulative_observed_refs": sorted(all_refs),
            "cumulative_count": 4, "remaining_transition_count": 24,
            "source_or_authority_effect": "none", "native_output_journal_or_all28_qualified": False,
            "claim_ceiling": "Four of 28 transition identities have isolated original candidate producer/consumer evidence across two pinned local runs. The other 24, current signed Source8 native output journal and final T31 qualification remain open."}


def run(output: Path) -> None:
    need(not output.exists() and not output.is_relative_to(ROOT / "authority"),
         "fresh local run directory outside authority required")
    selected = inventory()
    output.mkdir(mode=0o700, parents=False)
    (output / "INVENTORY.json").write_bytes(canonical(selected))
    for kind in NEW:
        cmd = [sys.executable, "-B", str(PREVIOUS / "worker.py"), kind, str(output / kind)]
        process = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=360, check=False)
        (output / f"{kind}.stdout").write_text(process.stdout)
        (output / f"{kind}.stderr").write_text(process.stderr)
        need(process.returncode == 0, f"original {kind} producer failed; see retained stderr")
    (output / "RESULT.json").write_bytes(canonical(receipt(output)))


def verify(output: Path) -> dict:
    actual = json.loads((output / "RESULT.json").read_bytes())
    expected = receipt(output)
    need(actual == expected, "retained local middle-transition claim or evidence differs")
    return {"result": "PASS-local-candidate-only", "new": 2, "cumulative": 4, "remaining": 24}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "verify"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        run(args.output.resolve())
    print(json.dumps(verify(args.output.resolve()), sort_keys=True))
