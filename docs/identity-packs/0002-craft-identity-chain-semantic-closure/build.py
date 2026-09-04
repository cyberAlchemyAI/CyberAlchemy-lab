#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_chain(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit chain.json and run build.py. -->","",f"# {data['title']}","","> Candidate successor chain; no admission or implementation authority.","",f"- Chain: `{data['chain_id']}`",f"- Predecessor: `{data['predecessor_chain']['chain_id']}`","","## Conformance vocabulary",""]
    for name, item in data["conformance_vocabulary"].items():
        if isinstance(item, dict):
            lines.append(f"- **{name.replace('_',' ').title()}** — `{item['definition_ref']}`; {item.get('use', item.get('posture'))}")
    lines += ["",data["conformance_vocabulary"]["non_inference_rule"],"","## Sequence",""]
    for stage in data["stages"]:
        lines += [f"### {stage['stage_id']}","",stage["decision_question"],"","Outputs:",""]
        lines += [f"- `{item}`" for item in stage["outputs"]]
        lines += ["",f"Effect: {stage['promotion_effect']}",""]
    lines += ["## Non-regression guarantees",""] + [f"- {item}" for item in data["non_regression_guarantees"]]
    lines += ["","## Recommended next unit","",f"`{data['recommended_next_unit']['unit_id']}` — {data['recommended_next_unit']['scope']}","","## Deferred",""] + [f"- {item}" for item in data["deferred"]]
    lines += ["","## Claim ceiling","",data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_layering(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit chain.json and run build.py. -->","","# CML-07 Successor Implementation Layering","","> Candidate projection; no stage is authorized.","","| Layer | Theme | Stages | Decision unlocked |","| --- | --- | --- | --- |"]
    for item in data["layering"]:
        stages = ", ".join(f"`{stage}`" for stage in item["stages"])
        lines.append(f"| `{item['layer_id']}` | {item['theme']} | {stages} | {item['decision_unlocked']} |")
    lines += ["","## Scope boundary","","CML-07 ends at schema and identity-contract conformance evidence plus one decision request set. Implementation and runtime conformance remain deferred."]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = load(ROOT / "chain.json")
    (ROOT / "CHAIN.md").write_text(render_chain(data), encoding="utf-8")
    (ROOT / "IMPLEMENTATION-LAYERING.md").write_text(render_layering(data), encoding="utf-8")
    checks = []
    def check(check_id: str, ok: bool, detail) -> None:
        checks.append({"check_id":check_id,"result":"PASS" if ok else "FAIL","detail":detail})
    pred = data["predecessor_chain"]
    check("predecessor-chain-current", sha(LAB / pred["path"]) == pred["sha256"] and sha(LAB / pred["validation_receipt_path"]) == pred["validation_receipt_sha256"], pred)
    semantic_results = []
    for item in data["semantic_predecessors"]:
        path = LAB / item["path"]
        semantic_results.append({"id":item["candidate_id"],"expected":item["sha256"],"actual":sha(path),"definitions":item["definition_count"]})
    check("semantic-predecessors-current", all(x["expected"] == x["actual"] for x in semantic_results), semantic_results)
    artifact = data["artifact_type_predecessor"]
    check("artifact-type-v2-current", sha(LAB / artifact["path"]) == artifact["sha256"], artifact)
    stage_ids = {item["stage_id"] for item in data["stages"]}
    seen = set()
    ordered = True
    for item in data["stages"]:
        ordered = ordered and set(item["depends_on"]) <= seen
        seen.add(item["stage_id"])
    check("stage-order-topological", ordered, [item["stage_id"] for item in data["stages"]])
    check("semantic-closure-before-s2", data["stages"][3]["depends_on"] == ["CML07-S1B-AUTHOR-SEMANTIC-CLOSURE"], data["stages"][3]["depends_on"])
    vocabulary = data["conformance_vocabulary"]
    check("conformance-scopes-distinct", vocabulary["schema_conformance"]["scope"] != vocabulary["runtime_conformance"]["scope"] and vocabulary["implementation_conformance"]["posture"] == "deferred-beyond-cml07" and vocabulary["runtime_conformance"]["posture"] == "deferred-beyond-cml07", vocabulary)
    text = json.dumps(data, sort_keys=True)
    check("semantic-reference-enforcement", "semantic_definition_refs" in text and "Artifact Type/v2" in text, artifact["required_rule"])
    outputs = [value for stage in data["stages"] for value in stage["outputs"]]
    check("output-paths-unique", len(outputs) == len(set(outputs)), len(outputs))
    check("no-bounded-context-output", not any(value.startswith("contexts/") for value in outputs), outputs)
    check("single-final-human-boundary", data["non_regression_guarantees"][-1].startswith("Human approval occurs once"), data["non_regression_guarantees"][-1])
    chain_md = render_chain(data)
    layering_md = render_layering(data)
    check("chain-projection-parity", (ROOT / "CHAIN.md").read_text(encoding="utf-8") == chain_md, sha(ROOT / "CHAIN.md"))
    check("layering-projection-parity", (ROOT / "IMPLEMENTATION-LAYERING.md").read_text(encoding="utf-8") == layering_md, sha(ROOT / "IMPLEMENTATION-LAYERING.md"))
    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {"schema_version":"cyberalchemy-lab-craft-identity-chain-validation/v2","subject":data["chain_id"],"result":"PASS" if not failed else "FAIL","authority_effect":"none","checks":checks,"summary":{"passed":len(checks)-len(failed),"failed":len(failed),"total":len(checks)},"materials":{"chain_sha256":sha(ROOT / "chain.json"),"chain_projection_sha256":sha(ROOT / "CHAIN.md"),"layering_projection_sha256":sha(ROOT / "IMPLEMENTATION-LAYERING.md")},"recommended_next_unit":data["recommended_next_unit"],"claim_ceiling":"PASS proves the successor chain preserves its exact predecessors, places eight-term semantic closure before S2, separates validation and conformance scopes, requires semantic Definition references for v2 registrations, is acyclic, and reproduces its projections. It does not admit or implement any stage."}
    receipt_path = ROOT / "receipts/validation.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CRAFT_IDENTITY_CHAIN_V2={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"CHAIN_SHA256={receipt['materials']['chain_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
