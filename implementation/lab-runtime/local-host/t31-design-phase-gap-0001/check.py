#!/usr/bin/env python3
"""Cold, bounded causal check of the two unobserved W08 designed transitions."""

from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FILES = {
    "engineering_source": ("implementation/lab-workflows/candidates/v1/workflows/engineering.py", "91eb2420596cd0ece48bfdec749342c0ebfaf0df0f6d06171e3e295e1255569f"),
    "research_source": ("implementation/lab-workflows/candidates/v1/workflows/research.py", "20f1749ef038c5153f293615126151a87c21794dd39b52338bc0f59c3c7be8ad"),
    "research_selection": ("implementation/lab-workflows/candidates/v1/examples/research/packages/0007/selection.json", "9ea324cf32469efa00d32c522bdf9baeab710e4463b5bc0ba69aba9d2996f148"),
    "research_design_input": ("implementation/lab-workflows/candidates/v1/examples/research/packages/0007/experiment-design.json", "fbecd82653bcf60d12dc25382d1f8af74e1370eb6c6e07e1d27ab3dcfb57018a"),
    "engineering_events": ("implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/engineering/transitions.json", "c2219189e89361014a4082b432331281e00eb065c17cb30a8f70e959005b2ce8"),
    "research_events": ("implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/research/transitions.json", "27698ef6038aa960d856093012d635cd4b770e98b8ad4f320bf0f06b9b462a2e"),
    "engineering_workflow": ("implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/engineering/workflow-run.json", "21d82f6ce3766dcb9324877ebba18e4965952130572d17b006f69bdc074823e0"),
    "research_workflow": ("implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/research/workflow-run.json", "bd2f746854fac130e355425bbb34a9c1e9644c650daa4649445cc1a81ed1db5e"),
    "predecessor": ("implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/RESULT.json", "c9f85acd1b9316489d26eb1bbbb3e43d617f2903b7e627b74b86983c2c9e1445"),
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def source(root: Path, key: str, *, exact_phase: bool = True) -> bytes:
    relative, expected = FILES[key]
    root = root.resolve(strict=True)
    path = root
    for segment in Path(relative).parts:
        path = path / segment
        mode = path.lstat().st_mode
        require(not stat.S_ISLNK(mode), f"{key}: symlinked ancestor or file")
    require(path.is_relative_to(root) and stat.S_ISREG(path.stat().st_mode),
            f"{key}: unsafe selected file")
    raw = path.read_bytes()
    if expected and (exact_phase or key not in {"engineering_events", "research_events", "engineering_workflow", "research_workflow"}):
        require(sha(raw) == expected, f"{key}: changed bytes")
    return raw


def canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def phase(root: Path, kind: str, *, exact_phase: bool) -> dict:
    events = json.loads(source(root, kind + "_events", exact_phase=exact_phase))
    workflow = json.loads(source(root, kind + "_workflow", exact_phase=exact_phase))
    require(len(events) == len(workflow["event_bindings"]) == 3, f"{kind}: three event bindings required")
    first = events[0]
    require((first["from"], first["to"], first["authority_effect"]) == ("prepared", "designed", "none"),
            f"{kind}: designed phase changed")
    require(workflow["event_bindings"][0]["sha256"] == sha(canonical(first)),
            f"{kind}: WorkflowRun event binding changed")
    return first


def diagnose(root: Path = ROOT, *, exact_phase: bool = True) -> dict:
    # Source byte pins make the phase interpretation refer to these original producers.
    engineering_source = source(root, "engineering_source").decode()
    research_source = source(root, "research_source").decode()
    require("'proposed_output_sha256':self.manifest['output_source_sha256']" in engineering_source and
            "self.implementation_bytes=self.tool.output.read_bytes()" in engineering_source and
            "require(self.state=='assessed'" in engineering_source,
            "engineering design/execute/materialize sequencing changed")
    require("self.transition('prepared','designed'" in research_source and
            "design=records[selection['design_ref']]" in research_source and
            "require(self.state=='evaluated'" in research_source,
            "research selected-input/design/materialize sequencing changed")
    engineering = phase(root, "engineering", exact_phase=exact_phase)
    research = phase(root, "research", exact_phase=exact_phase)
    require(set(engineering["detail"]) == {"work_ref", "source_sha256", "proposed_output_sha256",
            "declared_connections", "satisfaction_obligations"} and
            engineering["detail"]["proposed_output_sha256"] != engineering["detail"]["source_sha256"],
            "engineering first event is not a proposal-only design")
    selection = json.loads(source(root, "research_selection"))
    design_raw = source(root, "research_design_input")
    rows = [row for row in selection["records"] if row["kind"] == "experiment-design"]
    require(len(rows) == 1 and rows[0]["path"] == "experiment-design.json" and
            rows[0]["sha256"] == sha(design_raw) and rows[0]["version_ref"] == selection["design_ref"] == research["detail"]["design_ref"],
            "research design must be a preselected input")
    require(set(research["detail"]) == {"method_ref", "procedure_sha256", "design_ref", "samples", "ratio_threshold"},
            "research first event output claim changed")
    previous = json.loads(source(root, "predecessor"))
    require(previous["cumulative_count"] == 4 and previous["remaining_transition_count"] == 24,
            "selected predecessor count changed")
    return {"schema_version": "lab-T31-designed-causality-diagnostic/v1",
            "result": "NO_NEW_OUTPUT_TRANSITIONS",
            "predecessor_result_sha256": FILES["predecessor"][1],
            "diagnostic_code_sha256": sha(Path(__file__).read_bytes()),
            "selected_phase_bindings": [{"path": FILES[key][0], "sha256": FILES[key][1]}
                                        for key in ("engineering_events", "research_events", "engineering_workflow", "research_workflow")],
            "examined_refs": ["transition:engineering:designed", "transition:research:designed"],
            "engineering_reason": "Designed event records proposed output digest; actual corrected bytes arise in execute and GeneratedOutput is materialized after assess.",
            "research_reason": "ExperimentDesign is a SHA-pinned selection input before design; designed event only references it.",
            "cumulative_observed_count": 4, "remaining_count": 24,
            "claim_ceiling": "Causal refusal for these two retrospective attributions only; no new output transition, native journal, or T31 qualification."}


if __name__ == "__main__":
    print(json.dumps(diagnose(), sort_keys=True, indent=2))
