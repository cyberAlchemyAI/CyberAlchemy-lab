#!/usr/bin/env python3
"""Build the non-authoritative proposed Decision 0069 postimages."""

from __future__ import annotations
import copy,hashlib,json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[3]
REVIEW=LAB/"authority/artifact-types/candidates/0010-step5-postimage-registry/admission-manifest.json"
PREIMAGE=LAB/"authority/artifact-types/candidates/0010-step5-postimage-registry/registry.json"
ENDPOINT_PREIMAGE=LAB/"authority/artifact-types/candidates/0010-step5-postimage-registry/endpoint-inventory.json"
DECISION_ID="CAL-DECISION-0069-COMPLETE-ARTIFACT-TYPE-MODEL-ADMISSION"
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:Path,v:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def main()->None:
 manifest=load(REVIEW);registry=copy.deepcopy(load(PREIMAGE));endpoints=copy.deepcopy(load(ENDPOINT_PREIMAGE))
 by_path={row["descriptor_path"]:row for row in registry["descriptors"]}
 contracts={(row["artifact_type_ref"],row["artifact_path"]):row for row in registry["admitted_contracts"]}
 for entry in manifest["entries"]:
  descriptor=by_path[entry["artifact_path"]];descriptor["effective_state"]="admitted-current";descriptor["effective_decision_refs"]=[DECISION_ID];descriptor["semantic_binding_posture"]="current-as-declared";descriptor["proposed_primary_definition_ref"]=None
  predecessor=entry["predecessor_contract"]
  if predecessor:
   old=contracts[(predecessor["artifact_type_ref"],predecessor["path"])];old["lifecycle_state"]="admitted-historical"
   for row in registry["descriptors"]:
    if row["artifact_type_ref"]==predecessor["artifact_type_ref"] and row["descriptor_path"]==predecessor["path"] and row["descriptor_sha256"]==predecessor["sha256"]:
     row["effective_state"]="admitted-historical";row["effective_decision_refs"]=sorted(set(row["effective_decision_refs"]+[DECISION_ID]));row["semantic_binding_posture"]="current-as-declared";row["proposed_primary_definition_ref"]=None
  registry["admitted_contracts"].append({"admission_decision_ref":DECISION_ID,"artifact_path":entry["artifact_path"],"artifact_sha256":entry["artifact_sha256"],"artifact_type_ref":entry["artifact_type_ref"],"instance_discriminator":entry["instance_discriminator"],"lifecycle_state":"admitted-current","schema_path":entry["schema_path"],"schema_selector":None,"schema_sha256":entry["schema_sha256"],"semantic_definition_refs":entry["semantic_definition_refs"],"semantic_kind":entry["semantic_kind"]})
  registry["current_by_identity"][entry["artifact_type_id"]]=entry["artifact_type_ref"]
 registry["registry_id"]="CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0004";registry["version"]="2.0.0-candidate.4";registry["status"]="candidate-postimage";registry["authority_effect"]="none"
 registry["claim_ceiling"]="This exact proposed postimage represents the effects of Decision 0069 over 53 Artifact Type contracts and nine predecessor transitions. It does not apply the decision, admit an ordinary instance or relation, activate a consumer or runtime, or ingest its own decision-overlay digest."
 registry["source_direction"]={"canonical":"registry.json","generator_ref":"cal.generator.complete-artifact-type-admission-proposal/v1","human_projection":"REGISTRY.md","projection_policy":"generated-only"}
 states=Counter(row["effective_state"] for row in registry["descriptors"]);bindings=Counter(row["semantic_binding_posture"] for row in registry["descriptors"])
 registry["inventory"]={"admitted_contract_count":len(registry["admitted_contracts"]),"admitted_current_count":sum(row["lifecycle_state"]=="admitted-current" for row in registry["admitted_contracts"]),"admitted_historical_count":sum(row["lifecycle_state"]=="admitted-historical" for row in registry["admitted_contracts"]),"descriptor_count":len(registry["descriptors"]),"descriptor_declared_ref_count":len({row["artifact_type_ref"] for row in registry["descriptors"] if row["effective_state"]!="resolved-duplicate"}),"descriptor_identity_count":len({row["artifact_type_id"] for row in registry["descriptors"]}),"descriptor_resolved_ref_count":len({row["artifact_type_ref"] for row in registry["descriptors"]}),"duplicate_resolution_count":len(registry["duplicate_resolutions"]),"semantic_binding_counts":{"admitted-successor-required":bindings.get("admitted-successor-required",0),"candidate-rebind-required":bindings.get("candidate-rebind-required",0),"current-as-declared":bindings.get("current-as-declared",0)},"state_counts":dict(sorted(states.items()))}
 dump(ROOT/"registry-postimage.json",registry)
 admitted_refs={entry["artifact_type_ref"] for entry in manifest["entries"]}
 for row in endpoints["entries"]:
  if row.get("carrier_ref") in admitted_refs:
   row["lifecycle_state"]="admitted-current";row["admission_ref"]=DECISION_ID;row["lifecycle_evidence_path"]="docs/decisions/0069-complete-artifact-type-model-admission/proposal/registry-postimage.json";row.pop("note",None)
 endpoints["counts"]={"admitted-current":sum(row["lifecycle_state"]=="admitted-current" for row in endpoints["entries"]),"candidate-materialized":sum(row["lifecycle_state"]=="candidate-materialized" for row in endpoints["entries"]),"declared_endpoint_pairs":147,"named_endpoint_kinds":50,"referenced-no-canonical-carrier":0,"wildcard_tokens":0}
 endpoints["claim_ceiling"]="This proposed postimage represents 50 admitted-current endpoint carriers after Decision 0069. It does not apply the decision, admit Relation Kinds or Typed Relations, validate relation instances, or activate a consumer or runtime."
 dump(ROOT/"endpoint-inventory-postimage.json",endpoints)
 proposal={"schema_version":"cyberalchemy-lab-complete-artifact-type-model-admission-proposal/v1","decision_id":DECISION_ID,"title":"Complete Artifact Type model collective admission","status":"candidate-awaiting-owner-authorization","authority_effect":"none","authorization_present":False,"review_manifest":{"path":str(REVIEW.relative_to(LAB)),"sha256":sha(REVIEW)},"preimage_registry":{"path":str(PREIMAGE.relative_to(LAB)),"sha256":sha(PREIMAGE)},"proposed_postimages":{"registry":{"path":str((ROOT/"registry-postimage.json").relative_to(LAB)),"sha256":sha(ROOT/"registry-postimage.json")},"endpoint_inventory":{"path":str((ROOT/"endpoint-inventory-postimage.json").relative_to(LAB)),"sha256":sha(ROOT/"endpoint-inventory-postimage.json")}},"proposed_effects":{"artifact_types_admitted":53,"predecessors_transitioned_to_historical":9,"current_identity_mappings_written":53,"registry_instances_admitted":1,"prior_registry_instances_transitioned_to_historical":1,"ordinary_instances_admitted":0,"relation_kinds_admitted":0,"typed_relations_admitted":0,"consumer_activations":0,"runtime_activations":0},"excluded_effects":["No excluded candidate record is admitted.","No ordinary artifact instance is admitted.","No Relation Kind or Typed Relation is admitted.","No ontology assertion is promoted.","No implementation, consumer, Agent, session, or runtime is activated.","No predecessor bytes or previous registry snapshot bytes are rewritten."],"snapshot_policy":"Snapshot 0004 is the exact proposed admission postimage. Decision 0069 overlay-digest ingestion is deferred to a later immutable registry refresh to avoid a decision/postimage digest cycle.","claim_ceiling":"This proposal binds exact reviewed inputs and deterministic postimages. It has authority effect none and cannot admit or transition anything without explicit owner authorization and application of the final decision overlay."}
 dump(ROOT/"proposal.json",proposal)
 lines=["<!-- GENERATED FILE: canonical data is proposal.json. -->","","# Proposed Decision 0069 — Complete Artifact Type model admission","",f"- Status: `{proposal['status']}`",f"- Authority effect: `{proposal['authority_effect']}`","- Authorization present: `false`","", "## Exact proposed effects",""]
 for key,value in proposal["proposed_effects"].items():lines.append(f"- {key.replace('_',' ').title()}: `{value}`")
 lines += ["","## Resulting registry","",f"- Admitted contracts: `{registry['inventory']['admitted_contract_count']}`",f"- Current contracts: `{registry['inventory']['admitted_current_count']}`",f"- Historical contracts: `{registry['inventory']['admitted_historical_count']}`",f"- Remaining candidate descriptors: `{registry['inventory']['state_counts']['candidate-unadmitted']}`",f"- Endpoint carriers admitted-current: `{endpoints['counts']['admitted-current']}`",f"- Missing endpoint carriers: `{endpoints['counts']['referenced-no-canonical-carrier']}`","","## Realistic resulting connection","","After admission, `implementation:registry-validator` and `product-capability:effective-state-resolution` have admitted carrier contracts. Relation Kind/v2 can then define the exact `relation.realizes` endpoint and qualifier contract, while Typed Relation/v2 can carry a separately reviewed connection instance. Carrier admission alone creates no connection.","","## Excluded effects",""]+[f"- {item}" for item in proposal["excluded_effects"]]+["","## Claim ceiling","",proposal["claim_ceiling"]]
 (ROOT/"PROPOSAL.md").write_text("\n".join(lines).rstrip()+"\n",encoding="utf-8")

if __name__=="__main__":main()
