#!/usr/bin/env python3
"""Candidate-only Artifact Surface Foundation validator and inventory builder."""

from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
from typing import Any
import jsonschema

LAB=Path(__file__).resolve().parents[2]
ROOT_TYPE=LAB/"authority/artifact-types/artifact-type/v2/artifact.json"
ROOT_DECISION=LAB/"docs/decisions/0029-cml07-semantic-foundation-v1/decision.json"
DEFINITION_REGISTRY=LAB/"authority/definitions/registry.json"
GENERATOR=LAB/"tooling/generators/artifact_surface.py"

def load(p:Path)->dict[str,Any]: return json.loads(p.read_text())
def dump(p:Path,v:Any)->None: p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def generator_module():
    spec=importlib.util.spec_from_file_location("artifact_surface_generator",GENERATOR); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod

def validate_package(root:Path)->int:
    artifact=load(root/"artifact.json"); schema=load(root/"schema.json"); valid=root/artifact["validation_contract"]["positive_witness"]
    data=load(valid); checks=[]
    def check(cid,ok,detail): checks.append({"check_id":cid,"result":"PASS" if ok else "BLOCK","detail":detail})
    required={"schema_version","artifact_type_id","artifact_type_ref","version","name","status","authority_effect","classification","artifact_type_root_binding","semantic_owner_ref","semantic_definition_refs","semantic_definition_bindings","schema_ref","schema_digest","instance_contract","distinct_validation_purpose","orthogonality_rules","source_direction","four_facets","validation_contract","typed_residue","claim_ceiling"}
    check("artifact-contract-complete",set(artifact)==required,sorted(set(artifact)^required))
    check("candidate-non-effect",artifact.get("status")=="candidate-unadmitted" and artifact.get("authority_effect")=="none",{"status":artifact.get("status"),"authority_effect":artifact.get("authority_effect")})
    rb=artifact["artifact_type_root_binding"]; dec=load(ROOT_DECISION)
    check("artifact-type-v2-bound",rb["path"]==str(ROOT_TYPE.relative_to(LAB)) and rb["sha256"]==sha(ROOT_TYPE)==dec["admitted_artifact_type"]["sha256"] and rb["admission_decision_ref"]==dec["decision_id"],rb)
    check("schema-digest-current",artifact["schema_digest"]==sha(root/"schema.json"),{"declared":artifact["schema_digest"],"actual":sha(root/"schema.json")})
    check("closed-instance-schema",schema.get("type")=="object" and schema.get("additionalProperties") is False,{"type":schema.get("type"),"additionalProperties":schema.get("additionalProperties")})
    refs=set(artifact["semantic_definition_refs"]); binds={x["definition_ref"]:x for x in artifact["semantic_definition_bindings"]}; check("definition-ref-closure",refs==set(binds),{"refs":sorted(refs),"bindings":sorted(binds)})
    live={f"{x['definition_id']}@{x['version']}":x for x in load(DEFINITION_REGISTRY)["entries"] if x["lifecycle_state"]=="admitted"}; br=[]
    for ref,b in binds.items():
        p=LAB/b["path"]; actual=sha(p) if p.is_file() else "missing"; admitted=ref in live
        ok=p.is_file() and actual==b["sha256"] and ((admitted and b["admission_posture"]=="admitted") or (not admitted and b["admission_posture"]=="candidate-unadmitted"))
        br.append({"definition_ref":ref,"ok":ok,"admission_posture":b["admission_posture"],"actual":actual})
    check("semantic-bindings-current",all(x["ok"] for x in br),br)
    errors=sorted(x.message for x in jsonschema.Draft202012Validator(schema).iter_errors(data)); check("positive-witness-valid",not errors,errors)
    mod=generator_module(); artifact_md=root/"ARTIFACT.md"; witness_md=root/artifact["validation_contract"]["positive_projection"]
    check("artifact-projection-parity",artifact_md.is_file() and artifact_md.read_text()==mod.render_artifact(artifact),sha(artifact_md) if artifact_md.is_file() else "missing")
    check("witness-projection-parity",witness_md.is_file() and witness_md.read_text()==mod.render_instance(artifact,data),sha(witness_md) if witness_md.is_file() else "missing")
    gb=artifact["source_direction"]; check("shared-generator-current",gb["shared_generator_path"]==str(GENERATOR.relative_to(LAB)) and gb["shared_generator_sha256"]==sha(GENERATOR),gb)
    negative=[]
    for rel in artifact["validation_contract"]["negative_witnesses"]:
        p=root/rel; e=sorted(x.message for x in jsonschema.Draft202012Validator(schema).iter_errors(load(p))); negative.append({"path":rel,"rejected":bool(e),"errors":e})
    check("hostile-fixtures-rejected",bool(negative) and all(x["rejected"] for x in negative),negative)
    blocked=[x for x in checks if x["result"]=="BLOCK"]
    receipt={"schema_version":"cyberalchemy-lab-artifact-surface-type-validation/v1","subject":artifact["artifact_type_ref"],"result":"PASS" if not blocked else "BLOCK","authority_effect":"none","assessment":{"schema_conformance":"PASS" if not blocked else "NOT_ESTABLISHED","admission_posture":"candidate-unadmitted","implementation_conformance":"not_evaluable","runtime_conformance":"not_evaluable"},"checks":checks,"summary":{"passed":len(checks)-len(blocked),"blocked":len(blocked),"total":len(checks)},"materials":{"artifact_sha256":sha(root/"artifact.json"),"schema_sha256":sha(root/"schema.json"),"artifact_projection_sha256":sha(artifact_md) if artifact_md.is_file() else None,"positive_witness_sha256":sha(valid)},"claim_ceiling":"PASS proves candidate schema-and-contract behavior for this exact package and fixtures only. It does not admit the Artifact Type or any instance."}
    dump(root/"receipts/validation.json",receipt); print(f"{artifact['artifact_type_id'].upper().replace('.','_').replace('-','_')}={receipt['result']}"); return 0 if not blocked else 1

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("package",nargs="?"); args=ap.parse_args()
    if not args.package: ap.error("package path required")
    return validate_package(Path(args.package).resolve())

if __name__=="__main__": raise SystemExit(main())
