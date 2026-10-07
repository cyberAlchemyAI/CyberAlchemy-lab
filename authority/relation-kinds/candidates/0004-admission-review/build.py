#!/usr/bin/env python3
"""Build the exact 23 Relation Kind collective admission review."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[3]
SOURCE=LAB/"authority/relation-kinds/candidates/0003-admission-ready-instances"
DECISION_0069=LAB/"authority/artifact-types/candidates/0010-step5-postimage-registry/admission-manifest.json"
DEFINITIONS=LAB/"authority/definitions/registry.json"
PROPOSED_DECISION="CAL-DECISION-0070-RELATION-KIND-MODEL-ADMISSION"
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:Path,v:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def main()->None:
 model=load(LAB/"authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json")
 review_0069=load(DECISION_0069); definitions=load(DEFINITIONS)
 carrier_entries={x["artifact_type_ref"]:x for x in review_0069["entries"]}
 rows=[]
 for item in model["entries"]:
  rid=item["relation_kind_id"];slug=rid.removeprefix("relation.");path=SOURCE/f"instances/relation-kinds/{slug}.json";record=load(path)
  rows.append({"relation_kind_ref":rid,"axis_id":item["axis_id"],"record_path":str(path.relative_to(LAB)),"record_sha256":sha(path),"carrier_ref":"cal.artifact-type.relation-kind/v2","required_qualifier_axes":item["required_qualifier_axes"],"exact_endpoint_pair_count":len(item["allowed_endpoint_pairs"]),"forbidden_inferences":item["forbidden_inferences"],"admission_action":"new-current"})
 manifest={"schema_version":"cyberalchemy-lab-relation-kind-collective-admission-review/v1","manifest_id":"CAL-RELATION-KIND-ADMISSION-REVIEW-0001","proposed_decision_id":PROPOSED_DECISION,"status":"candidate-awaiting-artifact-type-admission-and-owner-review","authority_effect":"none","prerequisites":[{"decision_ref":"CAL-DECISION-0064-TYPED-CONNECTION-EXTENSION-RULE-ADMISSION","state":"satisfied","evidence":"authority/definitions/registry.json","definition_ref":"cal.definition.typed-connection-extension-rule@1.0.0-candidate.1","definition_current":definitions["current_lookup"].get("cal.definition.typed-connection-extension-rule")=="cal.definition.typed-connection-extension-rule@1.0.0-candidate.1"},{"decision_ref":"CAL-DECISION-0069-COMPLETE-ARTIFACT-TYPE-MODEL-ADMISSION","state":"pending-owner-authorization","evidence":str(DECISION_0069.relative_to(LAB)),"required_carriers":[{"artifact_type_ref":ref,"artifact_path":carrier_entries[ref]["artifact_path"],"artifact_sha256":carrier_entries[ref]["artifact_sha256"]} for ref in ["cal.artifact-type.relation-kind/v2","cal.artifact-type.typed-relation/v2"]]}],"counts":{"relation_kinds_to_admit":23,"exact_endpoint_pairs_to_admit":147,"typed_relations_to_admit":0,"artifact_types_to_admit":0,"ontology_assertions_to_admit":0,"consumer_activations":0,"runtime_activations":0},"entries":rows,"transaction_rules":["Admit only the exact 23 Relation Kind record bytes listed here after Decision 0069 is applied.","Each admitted record opens only its 147 collectively enumerated exact ordered endpoint pairs; wildcards and Cartesian inference remain forbidden.","Each Typed Relation must independently match one admitted pair and the selected Relation Kind's closed qualifier contract.","Do not admit the 23 illustrative Typed Relation examples.","Do not infer connections, endpoint equality, authority transfer, ontology truth, consumer activation, or runtime effect."],"claim_ceiling":"This manifest binds 23 exact candidate Relation Kind records, 147 exact ordered endpoint pairs, and closed qualifier contracts. It has authority effect none and cannot admit anything before its prerequisites and a separate explicit owner decision."}
 dump(ROOT/"admission-manifest.json",manifest)
 lines=["<!-- GENERATED FILE: canonical data is admission-manifest.json. -->","","# Relation Kind model — collective admission review","",f"- Proposed decision: `{PROPOSED_DECISION}`","- Relation Kinds: `23`","- Exact ordered endpoint pairs: `147`","- Typed Relations admitted: `0`","- Wildcards: `0`","- Authority effect: `none`","","## Dependency gate","","Decision 0069 must first admit `Relation Kind/v2` and `Typed Relation/v2`. That decision remains unapplied.","","## Complete admission set","","| Relation Kind | Axis | Pairs | Required qualifiers |","| --- | --- | ---: | --- |"]
 for row in rows:lines.append(f"| `{row['relation_kind_ref']}` | `{row['axis_id']}` | {row['exact_endpoint_pair_count']} | `{', '.join(row['required_qualifier_axes'])}` |")
 example=load(SOURCE/"instances/typed-relations/realizes.json")
 lines += ["","## Revised realistic example","","This example is review evidence only and is explicitly excluded from the proposed admission:","","```json",json.dumps(example["payload"],indent=2,sort_keys=True),"```","","The selected `relation.realizes` contract permits this exact `experiment-run → experiment-design` direction and requires exactly `realization_role` plus `exact_target_version_ref`. Reversing the endpoints, omitting either qualifier, or adding a new qualifier is rejected.","","## Transaction boundary",""]+[f"- {x}" for x in manifest["transaction_rules"]]+["","## Claim ceiling","",manifest["claim_ceiling"],""]
 (ROOT/"ADMISSION-REVIEW.md").write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":main()
