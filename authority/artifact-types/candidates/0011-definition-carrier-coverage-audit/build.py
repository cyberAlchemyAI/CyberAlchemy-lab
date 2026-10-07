#!/usr/bin/env python3
"""Audit Artifact Type carrier coverage for all 60 integrated Definitions."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent;LAB=ROOT.parents[3]
DEFS=LAB/"authority/definitions/candidates/0013-integrated-lab-definition-model/candidate.json"
DEF_REG=LAB/"authority/definitions/registry.json"
REG=LAB/"authority/artifact-types/candidates/0010-step5-postimage-registry/registry.json"
STEP7=LAB/"authority/ontology-integration/candidates/0002-carrier-materialization/carrier-postimages.json"
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:Path,v:Any)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
NONCARRIER={
 "actor":{"classification":"abstract-participation-class","realization":"Represent each concrete participant through its governed carrier, then classify the exact revision through Classification Scheme, Classification Value, and Classification Assignment.","reason":"The admitted Definition explicitly says Actor is an abstract participation classification and does not require one universal Actor carrier."},
 "agent":{"classification":"abstract-operational-actor-class","realization":"Represent concrete operation through Agent Instance inside Agent Session, then classify the exact instance through the governed Agent actor-kind Scheme and Assignment.","reason":"The admitted Definition explicitly says Agent is an operational Actor classification and concrete operation requires Agent Instance plus Agent Session."},
 "session-memory":{"classification":"ephemeral-runtime-value","realization":"Closed Session Memory schema embedded in Agent Session runtime; persistence is forbidden and no durable Artifact Type instance is permitted.","reason":"The Definition makes Session Memory ephemeral, owned by one Session, and expired at termination."},
 "operational-learning-cycle":{"classification":"governed-method","realization":"Represent the selected method through Governed Model or Workflow plus its concrete Lesson, Application, Assessment, and Improvement artifacts.","reason":"The cycle is a method connecting record types rather than an independently versioned occurrence record."},
 "classification":{"classification":"abstract-act-and-result","realization":"Classification Scheme defines the contract; Classification Assignment records the governed result; Classification Value supplies allowed answers.","reason":"A separate Classification record would duplicate the Assignment identity and result."},
 "failure":{"classification":"abstract-condition","realization":"Failure Mode defines the possible boundary violation; Failure Occurrence records evidence of an episode; Failure Assessment evaluates it.","reason":"A separate Failure artifact would collapse the design-time mode, observed occurrence, and assessment axes."},
}
def main()->None:
 defs=load(DEFS)["definitions"];reg=load(REG);step7=load(STEP7);defreg=load(DEF_REG)
 bound={}
 for d in reg["descriptors"]:
  for ref in d.get("semantic_definition_refs",[]):bound.setdefault(ref,[]).append({"artifact_type_ref":d["artifact_type_ref"],"path":d["descriptor_path"],"state":d["effective_state"]})
 for e in step7["entries"]:
  a=load(LAB/e["artifact_path"])
  for ref in a["semantic_definition_refs"]:bound.setdefault(ref,[]).append({"artifact_type_ref":a["artifact_type_ref"],"path":e["artifact_path"],"state":"candidate-unadmitted"})
 entries=[]
 for d in defs:
  name=d["definition_id"].removeprefix("cal.definition.");ref=f"{d['definition_id']}@{d['version']}";definition=load(LAB/d["path"]);current=defreg["current_lookup"].get(d["definition_id"])
  if ref in bound:
   posture="carrier-backed";action="preserve-reviewed-carrier";carrier_refs=sorted({x["artifact_type_ref"] for x in bound[ref]});carrier_paths=sorted({x["path"] for x in bound[ref]});rationale="At least one visible reviewed carrier binds this exact current admitted Definition."
  elif name in NONCARRIER:
   posture="no-standalone-carrier";action="declare-noncarrier-realization";carrier_refs=[];carrier_paths=[];rationale=NONCARRIER[name]["reason"]
  else:
   posture="carrier-required-missing";action="materialize-new-carrier";carrier_refs=[f"cal.artifact-type.{name}/v1"];carrier_paths=[];rationale="The Definition describes an independently identified, attributable, versioned, lifecycle-bearing, or immutable governed identity or record that must be instantiated without collapsing into neighboring artifacts."
  entries.append({"definition_ref":ref,"definition_path":d["path"],"definition_sha256":sha(LAB/d["path"]),"definition_current":current==ref,"family":d["family"],"term":definition["term"],"applicability":definition["scope"]["applicability"],"posture":posture,"action":action,"carrier_refs":carrier_refs,"carrier_paths":carrier_paths,"rationale":rationale,"noncarrier_contract":NONCARRIER.get(name)})
 postures=Counter(x["posture"] for x in entries);families={family:dict(Counter(x["posture"] for x in entries if x["family"]==family)) for family in sorted({x["family"] for x in entries})}
 audit={"schema_version":"cyberalchemy-lab-definition-carrier-coverage-audit/v1","audit_id":"CAL-INTEGRATED-60-DEFINITION-CARRIER-COVERAGE-0011","status":"candidate-complete-awaiting-owner-review","authority_effect":"none","inputs":{"integrated_definition_candidate":{"path":str(DEFS.relative_to(LAB)),"sha256":sha(DEFS)},"definition_registry":{"path":str(DEF_REG.relative_to(LAB)),"sha256":sha(DEF_REG)},"artifact_registry":{"path":str(REG.relative_to(LAB)),"sha256":sha(REG)},"step7_carriers":{"path":str(STEP7.relative_to(LAB)),"sha256":sha(STEP7)}},"classification_rule":"A standalone carrier is required when an admitted Definition denotes an independently identified, attributable, versioned, lifecycle-bearing, immutable, or separately challengeable governed identity or record. An abstract class, condition, method, act/result umbrella, or explicitly ephemeral session value must instead name its exact realization and must not receive a duplicate durable identity.","entries":entries,"counts":{"integrated_definitions":len(entries),"carrier_backed":postures["carrier-backed"],"carrier_required_missing":postures["carrier-required-missing"],"no_standalone_carrier":postures["no-standalone-carrier"],"projected_carrier_backed_after_actions":postures["carrier-backed"]+postures["carrier-required-missing"],"projected_artifact_types_in_decision_0069":53+6+postures["carrier-required-missing"]},"family_counts":families,"noncarrier_realizations":[{"definition_ref":x["definition_ref"],**x["noncarrier_contract"]} for x in entries if x["posture"]=="no-standalone-carrier"],"required_actions":[{"definition_ref":x["definition_ref"],"artifact_type_ref":x["carrier_refs"][0],"family":x["family"],"definition_path":x["definition_path"],"definition_sha256":x["definition_sha256"]} for x in entries if x["posture"]=="carrier-required-missing"],"decision_0069_effect":"After owner approval and carrier materialization, replace the provisional 53-entry review with one definition-complete 93-entry Artifact Type admission review: six Step 7 additions plus 34 remaining Definition carriers, while preserving all pre-admission predecessors and exclusions.","claim_ceiling":"This audit classifies carrier coverage for the exact 60 admitted integrated Definitions against current candidate material. It does not materialize the 34 remaining carriers, amend Decision 0069, admit anything, create instances or relations, or activate a runtime."}
 dump(ROOT/"audit.json",audit)
 lines=["<!-- GENERATED FILE: canonical data is audit.json. -->","","# Integrated 60 Definition carrier coverage audit","",f"- Integrated Definitions: `{audit['counts']['integrated_definitions']}`",f"- Carrier backed: `{audit['counts']['carrier_backed']}`",f"- Carrier required and missing: `{audit['counts']['carrier_required_missing']}`",f"- No standalone carrier: `{audit['counts']['no_standalone_carrier']}`",f"- Projected carrier backed after actions: `{audit['counts']['projected_carrier_backed_after_actions']}`",f"- Projected Decision 0069 admission set: `{audit['counts']['projected_artifact_types_in_decision_0069']}`","- Authority effect: `none`","","## Complete coverage matrix","","| Definition | Family | Posture | Artifact Type or realization |","| --- | --- | --- | --- |"]
 for x in entries:
  target=", ".join(f"`{r}`" for r in x["carrier_refs"]) if x["carrier_refs"] else x["noncarrier_contract"]["realization"]
  lines.append(f"| `{x['definition_ref']}` | `{x['family']}` | `{x['posture']}` | {target} |")
 lines += ["",f"## {audit['counts']['no_standalone_carrier']} definitions without standalone carriers",""]
 for x in audit["noncarrier_realizations"]:lines += [f"### `{x['definition_ref']}`","",f"Classification: `{x['classification']}`","",x["reason"],"",f"Realization: {x['realization']}",""]
 lines += ["## Decision 0069 impact","",audit["decision_0069_effect"],"","## Claim ceiling","",audit["claim_ceiling"],""];(ROOT/"COVERAGE-AUDIT.md").write_text("\n".join(lines),encoding="utf-8")
if __name__=="__main__":main()
