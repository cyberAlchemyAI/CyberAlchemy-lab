#!/usr/bin/env python3
"""Build the exact collective Artifact Type admission review manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[3]
REGISTRY=ROOT/"registry.json"
DECISION_ID="CAL-DECISION-0069-COMPLETE-ARTIFACT-TYPE-MODEL-ADMISSION"


def load(path:Path)->Any:return json.loads(path.read_text(encoding="utf-8"))
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path:Path,value:Any)->None:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def major(ref:str)->int:
    return int(ref.rsplit("/v",1)[1])


def main()->None:
    registry=load(REGISTRY)
    hard=load(LAB/"authority/artifact-types/candidates/0009-step5-carrier-closure/hard-corrections-postimages.json")
    endpoint=load(LAB/"authority/artifact-types/candidates/0009-step5-carrier-closure/endpoint-carrier-postimages.json")
    legacy=load(LAB/"authority/artifact-types/candidates/0009-step5-carrier-closure/legacy-successor-postimages.json")
    meta=load(LAB/"authority/artifact-types/candidates/0009-step5-carrier-closure/metamodel-successor-postimages.json")
    relation_hardening=load(LAB/"authority/relation-kinds/candidates/0003-admission-ready-instances/carrier-postimages.json")
    repaired_paths={row["artifact_path"] for row in hard["postimages"] if row["artifact_type_ref"]!="cal.artifact-type.capability-realization-binding/v2"}
    successor_paths={next(row["artifact_path"] for row in hard["postimages"] if row["artifact_type_ref"]=="cal.artifact-type.capability-realization-binding/v2")}|{row["artifact_path"] for row in legacy["entries"]}|{row["artifact_path"] for row in meta["entries"]}
    endpoint_paths={row["artifact_path"] for row in endpoint["entries"]}|{row["artifact_path"] for row in relation_hardening["entries"]}
    superseded_before_admission={load(LAB/row["artifact_path"])["candidate_predecessor_contract"]["path"]:row["artifact_type_ref"] for row in relation_hardening["entries"]}
    lineage_predecessors={row["predecessor_descriptor"] for row in registry["candidate_lineage"] if row["posture"]=="candidate-lineage-only"}
    entries=[];excluded=[]
    for row in registry["descriptors"]:
        if row["effective_state"]!="candidate-unadmitted":continue
        path=row["descriptor_path"];current_ref=registry["current_by_identity"].get(row["artifact_type_id"])
        if path in superseded_before_admission:
            excluded.append({"artifact_type_ref":row["artifact_type_ref"],"descriptor_path":path,"reason":"superseded-before-admission","successor_ref":superseded_before_admission[path]});continue
        if path in lineage_predecessors:
            excluded.append({"artifact_type_ref":row["artifact_type_ref"],"descriptor_path":path,"reason":"candidate-lineage-predecessor-preserved"});continue
        if current_ref and major(row["artifact_type_ref"])<=major(current_ref) and path not in successor_paths:
            reason="same-version-non-effective-duplicate" if row["artifact_type_ref"]==current_ref else "obsolete-candidate-predecessor"
            excluded.append({"artifact_type_ref":row["artifact_type_ref"],"descriptor_path":path,"reason":reason,"current_ref":current_ref});continue
        artifact=load(LAB/path);schema_path=row["schema_path"];receipt_path=str((Path(path).parent/"receipts/validation.json"));receipt=load(LAB/receipt_path)
        if path in repaired_paths:group="repaired-candidate"
        elif path in successor_paths:group="immutable-successor"
        elif path in endpoint_paths:group="new-endpoint-carrier"
        else:group="existing-ready-candidate"
        predecessor=artifact.get("predecessor_contract") if group=="immutable-successor" else None
        entries.append({
            "admission_action":"successor-current" if predecessor else "new-current",
            "artifact_path":path,"artifact_sha256":row["descriptor_sha256"],"artifact_type_id":row["artifact_type_id"],"artifact_type_ref":row["artifact_type_ref"],"artifact_version":row["descriptor_version"],"group":group,
            "instance_discriminator":row["instance_discriminator"],"predecessor_contract":predecessor,
            "receipt_path":receipt_path,"receipt_sha256":sha(LAB/receipt_path),"receipt_result":receipt["result"],
            "schema_path":schema_path,"schema_sha256":row["schema_sha256"],"semantic_definition_refs":row["semantic_definition_refs"],"semantic_kind":artifact["classification"]["semantic_kind"],
        })
    entries.sort(key=lambda row:(row["group"],row["artifact_type_ref"]))
    counts={group:sum(row["group"]==group for row in entries) for group in ["existing-ready-candidate","repaired-candidate","immutable-successor","new-endpoint-carrier"]}
    counts.update({"artifact_types_to_admit":len(entries),"predecessors_to_historical":sum(row["admission_action"]=="successor-current" for row in entries),"excluded_candidate_records":len(excluded),"instance_admissions":0,"relation_kind_admissions":0,"typed_relation_admissions":0,"consumer_activations":0})
    manifest={
        "schema_version":"cyberalchemy-lab-collective-artifact-type-admission-review/v1","manifest_id":"CAL-COMPLETE-ARTIFACT-TYPE-MODEL-ADMISSION-REVIEW-0001","proposed_decision_id":DECISION_ID,"status":"candidate-exact-postimages-ready-for-owner-review","authority_effect":"none",
        "preimage":{"registry_id":registry["registry_id"],"path":str(REGISTRY.relative_to(LAB)),"sha256":sha(REGISTRY)},"counts":counts,"entries":entries,"excluded_candidate_records":sorted(excluded,key=lambda row:row["descriptor_path"]),
        "transaction_rules":["Admit only the exact artifact and schema bytes listed in entries.","Transition only the nine exact predecessor contracts named by successor entries from admitted-current to admitted-historical.","Create or replace one current_by_identity mapping per admitted entry.","Preserve every excluded candidate record and every unrelated admitted contract.","Generate and admit a new Registry/v2 postimage after the transaction; preserve prior registry snapshots.","Do not admit an ordinary artifact instance, Relation Kind, Typed Relation, ontology assertion, consumer, implementation, or runtime."],
        "realistic_examples":[
            {"example":"implementation-realizes-capability","statement":"Implementation/v1 carries executable realization identity; Product Capability carries promised product behavior; Capability Realization Binding/v2 records the governed association; relation.realizes remains a separate candidate Relation Kind."},
            {"example":"person-reference-identifies-person","statement":"Person Reference/v1 is a durable reference record; Person/v1 is the human identity endpoint; relation.asserts-identity-of remains a separately governed connection."},
            {"example":"typed-relation-in-ontology","statement":"Typed Relation/v2 carries one exact connection instance with explicit endpoint kinds, revisions, and closed qualifiers; Relation Kind/v2 carries the full semantic-axis contract; Ontology Node/v1 carries a node; Ontology/v1 carries the governed graph context."}
        ],
        "claim_ceiling":"This review manifest binds 53 exact Artifact Type candidate postimages and nine predecessor transitions. It has authority effect none and does not admit any bytes, instance, relation, ontology assertion, consumer, implementation, or runtime."
    }
    dump(ROOT/"admission-manifest.json",manifest)
    lines=["<!-- GENERATED FILE: canonical data is admission-manifest.json. -->","","# Complete Artifact Type model — collective admission review","",f"- Proposed decision: `{DECISION_ID}`",f"- Artifact Types to admit: `{counts['artifact_types_to_admit']}`",f"- Existing ready candidates: `{counts['existing-ready-candidate']}`",f"- Repaired candidates: `{counts['repaired-candidate']}`",f"- Immutable successors: `{counts['immutable-successor']}`",f"- New endpoint carriers: `{counts['new-endpoint-carrier']}`",f"- Predecessors transitioning to historical: `{counts['predecessors_to_historical']}`",f"- Excluded candidate records: `{counts['excluded_candidate_records']}`","- Authority effect before approval: `none`","","## Exact admission set",""]
    for group in ["existing-ready-candidate","repaired-candidate","immutable-successor","new-endpoint-carrier"]:
        lines += [f"### {group.replace('-', ' ').title()}","","| Artifact Type | Version | Artifact digest | Predecessor |","| --- | --- | --- | --- |"]
        for row in entries:
            if row["group"]!=group:continue
            pred=row["predecessor_contract"]["artifact_type_ref"] if row["predecessor_contract"] else "—"
            lines.append(f"| `{row['artifact_type_ref']}` | `{row['artifact_version']}` | `{row['artifact_sha256']}` | `{pred}` |")
        lines.append("")
    lines += ["## Excluded records","","| Artifact Type | Path | Reason |","| --- | --- | --- |"]
    for row in manifest["excluded_candidate_records"]:lines.append(f"| `{row['artifact_type_ref']}` | `{row['descriptor_path']}` | `{row['reason']}` |")
    lines += ["","## Realistic integrated examples",""]
    for example in manifest["realistic_examples"]:lines += [f"### {example['example']}","",example["statement"],""]
    lines += ["## Decision boundary","",* [f"- {rule}" for rule in manifest["transaction_rules"]],"","## Claim ceiling","",manifest["claim_ceiling"]]
    (ROOT/"ADMISSION-REVIEW.md").write_text("\n".join(lines).rstrip()+"\n",encoding="utf-8")


if __name__=="__main__":main()
