#!/usr/bin/env python3
"""Retain two original output producer episodes and exact later consumers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import subprocess
import sys

from inventory import ROOT, check_output_set, digest, inventory


HERE = Path(__file__).resolve().parent
TRANSITIONS = {
    "engineering": "transition:engineering:assessed",
    "research": "transition:research:evaluated",
}
OUTPUTS = {
    "engineering": (("workflow/work-outcome-assessment.json", "cal.artifact-type.work-outcome-assessment/v1"),),
    "research": (("finding.json", "cal.artifact-type.finding/v1"),
                 ("evaluation.json", "cal.artifact-type.evaluation/v1")),
}
CATALOG = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-transitions-0001/carrier-catalog.json"
CATALOG_SHA256 = "b2709686d7a34ff704ebaa4c7dc78c18281208adfe2daeedf84fc5a0705e6ed8"
CONTRACTS = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v30/workflow_output_contracts.py"


def canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def original_carriers():
    raw = CATALOG.read_bytes()
    if digest(raw) != CATALOG_SHA256:
        raise ValueError("selected original carrier catalog changed")
    module = runpy.run_path(str(CONTRACTS))
    catalog = module["parse"](raw)
    documents = {path: (ROOT / path).read_bytes() for row in catalog["rows"]
                 for path in (row["schema_path"], row["artifact_path"])}
    return module["OriginalCarriers"](raw, CATALOG_SHA256, documents)


def link_episode(kind: str, output: Path, selected: dict) -> dict:
    observed = output / kind
    workflow = json.loads((observed / "workflow-run.json").read_bytes())
    events = json.loads((observed / "transitions.json").read_bytes())
    row = next(item for item in selected["transitions"] if item["transition_ref"] == TRANSITIONS[kind])
    if workflow["workflow_type_ref"] != f"workflow:{kind}:v1-candidate" or workflow["state"] != row["to_state"]:
        raise ValueError("original WorkflowRun type or state differs")
    event = events[-1]
    if event["from"] != row["from_state"] or event["to"] != row["to_state"]:
        raise ValueError("observed terminal transition differs")
    event_sha = digest(canonical(event))
    if workflow["event_bindings"][-1]["sha256"] != event_sha:
        raise ValueError("WorkflowRun does not bind observed event")
    originals = []
    for relative, carrier in OUTPUTS[kind]:
        path = observed / relative
        raw = path.read_bytes()
        body = json.loads(raw)
        identity = body["node_id"]
        header = {"scope_ref": body["scope_ref"], "identity_ref": identity,
                  "version_ref": identity + "@" + body.get("version", "candidate.1"),
                  "carrier_ref": carrier, "byte_sha256": digest(raw)}
        originals.append((header, raw))
    headers = check_output_set(row, originals)
    carriers = original_carriers()
    for header, raw in originals:
        carriers.output(header, raw, scope_ref=header["scope_ref"])
    work_path = observed / ("workflow/work.json" if kind == "engineering" else "work.json")
    work = json.loads(work_path.read_bytes())
    if {header["scope_ref"] for header in headers} != {work["payload"]["project_ref"]}:
        raise ValueError("observed outputs and later Work project scope differ")
    output_refs = work["payload"]["output_refs"]
    if not all(header["version_ref"] in output_refs for header in headers):
        raise ValueError("later Work materialization did not consume every output")
    if kind == "engineering":
        if workflow["outcome_assessment"] != headers[0]:
            raise ValueError("WorkflowRun did not link the exact observed Work assessment")
    elif workflow["outcome_assessment"] is not None:
        raise ValueError("research hypothesis evaluation was misreported as Work satisfaction")
    return {"transition_ref": TRANSITIONS[kind], "workflow_run_sha256": digest((observed / "workflow-run.json").read_bytes()),
            "event_sha256": event_sha, "output_artifact_refs": headers,
            "output_original_paths": [str((observed / relative).relative_to(output)) for relative, _ in OUTPUTS[kind]],
            "later_consumer": {"path": str(work_path.relative_to(output)), "sha256": digest(work_path.read_bytes()),
                               "field": "payload.output_refs"},
            "claim": "isolated original candidate producer output and later candidate Work materialization"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new run directory; must not exist")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(ROOT / "authority"):
        raise ValueError("new task-local run directory outside authority required")
    selected = inventory()
    output.mkdir(mode=0o700, parents=False)
    (output / "INVENTORY.json").write_text(json.dumps(selected, indent=2, sort_keys=True) + "\n")
    links = []
    for kind in TRANSITIONS:
        command = [sys.executable, "-B", str(HERE / "worker.py"), kind, str(output / kind)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=360, check=False)
        (output / f"{kind}.stdout").write_text(result.stdout)
        (output / f"{kind}.stderr").write_text(result.stderr)
        if result.returncode:
            raise RuntimeError(f"{kind} original episode failed ({result.returncode}); inspect task-local stderr")
        summary = json.loads(result.stdout)
        if summary["event_count"] != 3 or (kind == "engineering" and summary["source_correction"] != "completed"):
            raise ValueError(f"{kind} original phase sequence or producer effect differs")
        if kind == "research" and summary["replay_stdout_count"] != 6:
            raise ValueError("six observed original research replay children required")
        links.append(link_episode(kind, output, selected))
    report = {"schema_version": "lab-T31-local-output-episode/v1", "inventory": {"workflows": 10, "transitions": 28},
              "observed_terminal_output_transitions": links, "observed_count": len(links),
              "remaining_transition_count": 28 - len(links), "zero_output_substitute_accepted": False,
              "source_or_authority_effect": "none", "native_output_journal_or_all28_qualified": False,
              "w03_regression": "NOT-RUN; candidate assessment unsupported",
              "claim_ceiling": "Two isolated original candidate producer paths with original bytes and later Work references. The 26 other output-bearing transitions, signed current Source8 cut, native output journal and final T31 qualification remain open."}
    (output / "RESULT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": "PASS-local-candidate-output-paths", "observed": len(links),
                      "remaining": 28 - len(links), "receipt": str(output / "RESULT.json")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
